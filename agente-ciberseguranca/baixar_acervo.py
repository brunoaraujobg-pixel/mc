# -*- coding: utf-8 -*-
"""
baixar_acervo.py - Baixa e mantem atualizado o acervo de ciberseguranca.

Usa somente a biblioteca padrao do Python (nao precisa instalar nada).

Exemplos de uso (no Prompt de Comando do Windows):
    python baixar_acervo.py --listar
    python baixar_acervo.py --somente-essenciais
    python baixar_acervo.py
    python baixar_acervo.py --categoria vulnerabilidades
    python baixar_acervo.py --id cisa-kev-json --forcar
    python baixar_acervo.py --verificar-validade

Codigos de saida:
    0 = tudo certo
    1 = uma ou mais fontes falharam
    2 = acervo vencido (usado com --verificar-validade)
    3 = erro de configuracao
"""

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
ARQ_FONTES = os.path.join(RAIZ, "fontes.json")
DIR_ACERVO = os.path.join(RAIZ, "acervo")
DIR_ESTADO = os.path.join(DIR_ACERVO, "_estado")
DIR_LOGS = os.path.join(DIR_ACERVO, "_logs")
ARQ_ESTADO = os.path.join(DIR_ESTADO, "estado.json")

# Alguns sites oficiais (cwe.mitre.org, nvlpubs.nist.gov) respondem 403 a
# programas com User-Agent desconhecido. Sao documentos publicos; usamos um
# User-Agent de navegador para nao ser recusado.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
CABECALHOS_PADRAO = {
    "User-Agent": UA,
    "Accept": "*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Connection": "close",
}
# Cabecalhos usados na 2a chance, quando o site devolve 403/406 (filtro de robo).
CABECALHOS_NAVEGADOR = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Upgrade-Insecure-Requests": "1",
}
CODIGOS_FILTRO_ROBO = (403, 406, 429)

TENTATIVAS = 3
ESPERA_BASE = 2  # segundos: 2, 4, 8

# Preenchido por --ca-bundle (certificado da empresa/antivirus que intercepta TLS)
CA_BUNDLE = None


# ----------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------
def agora_iso():
    return dt.datetime.now().replace(microsecond=0).isoformat()


class Log:
    def __init__(self, caminho):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        self.f = open(caminho, "a", encoding="utf-8")
        self.caminho = caminho

    def __call__(self, msg):
        linha = "[%s] %s" % (agora_iso(), msg)
        print(linha, flush=True)
        self.f.write(linha + "\n")
        self.f.flush()

    def fechar(self):
        self.f.close()


def carregar_json(caminho, padrao):
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao


def salvar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(tmp, caminho)


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 256), b""):
            h.update(bloco)
    return h.hexdigest()


def tamanho_legivel(n):
    for unidade in ("B", "KB", "MB", "GB"):
        if n < 1024 or unidade == "GB":
            return "%.1f %s" % (n, unidade)
        n /= 1024.0


def contexto_ssl():
    # Respeita certificados extras informados por --ca-bundle ou pelo ambiente
    # (antivirus/proxy que intercepta TLS), mas NUNCA desliga a verificacao.
    ca = CA_BUNDLE or os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if ca and os.path.exists(ca):
        return ssl.create_default_context(cafile=ca)
    return ssl.create_default_context()


# ----------------------------------------------------------------------
# download
# ----------------------------------------------------------------------
def abrir_url(url, cabecalhos=None, timeout=120, base=None):
    req = urllib.request.Request(url, headers=dict(base or CABECALHOS_PADRAO))
    for k, v in (cabecalhos or {}).items():
        if v:
            req.add_header(k, v)
    return urllib.request.urlopen(req, timeout=timeout, context=contexto_ssl())


def baixar_arquivo(url, destino, meta_anterior, log, timeout=120, max_mb=None, forcar=False,
                   referer=None):
    """Baixa url para destino. Retorna (situacao, meta).

    situacao: 'novo' | 'atualizado' | 'sem-mudanca' | 'erro'
    Usa ETag / Last-Modified para nao baixar de novo o que nao mudou.
    """
    cabecalhos = {}
    if not forcar and os.path.exists(destino) and meta_anterior:
        cabecalhos["If-None-Match"] = meta_anterior.get("etag")
        cabecalhos["If-Modified-Since"] = meta_anterior.get("last_modified")

    ultimo_erro = None
    base = None          # None = CABECALHOS_PADRAO
    tentou_navegador = False
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resp = abrir_url(url, cabecalhos, timeout, base=base)
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return "sem-mudanca", meta_anterior
            # 403/406/429 costumam ser filtro de robo: vale uma 2a chance
            # com cabecalhos de navegador completos.
            if e.code in CODIGOS_FILTRO_ROBO and not tentou_navegador:
                tentou_navegador = True
                base = dict(CABECALHOS_NAVEGADOR)
                if referer:
                    base["Referer"] = referer
                log("   HTTP %s (site recusou o programa). Tentando como navegador..." % e.code)
                continue
            # 4xx nao melhora com nova tentativa
            if 400 <= e.code < 500:
                dica = ""
                if e.code == 404:
                    dica = " - o endereco mudou; confira a pagina oficial da fonte"
                elif e.code in CODIGOS_FILTRO_ROBO:
                    dica = " - o site recusou o download automatico; baixe pelo navegador"
                return "erro", {"erro": "HTTP %s%s" % (e.code, dica), "url": url}
            ultimo_erro = "HTTP %s" % e.code
        except ssl.SSLError as e:
            return "erro", {
                "erro": "falha de certificado TLS (%s) - rode 'python baixar_acervo.py "
                        "--diagnostico' para confirmar e veja a secao de certificado no README" % e,
                "url": url,
            }
        except Exception as e:
            ultimo_erro = "%s: %s" % (type(e).__name__, e)
        else:
            with resp:
                tam_informado = resp.headers.get("Content-Length")
                if max_mb and tam_informado and int(tam_informado) > max_mb * 1024 * 1024:
                    return "erro", {
                        "erro": "arquivo maior que o limite de %s MB (%s)"
                        % (max_mb, tamanho_legivel(int(tam_informado))),
                        "url": url,
                    }
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                parcial = destino + ".part"
                baixado = 0
                limite = (max_mb or 0) * 1024 * 1024
                with open(parcial, "wb") as f:
                    while True:
                        bloco = resp.read(1024 * 256)
                        if not bloco:
                            break
                        baixado += len(bloco)
                        if limite and baixado > limite:
                            f.close()
                            os.remove(parcial)
                            return "erro", {
                                "erro": "download passou do limite de %s MB" % max_mb,
                                "url": url,
                            }
                        f.write(bloco)
                existia = os.path.exists(destino)
                hash_antigo = meta_anterior.get("sha256") if meta_anterior else None
                os.replace(parcial, destino)
                novo_hash = sha256_arquivo(destino)
                meta = {
                    "url": url,
                    "etag": resp.headers.get("ETag"),
                    "last_modified": resp.headers.get("Last-Modified"),
                    "content_type": resp.headers.get("Content-Type"),
                    "bytes": os.path.getsize(destino),
                    "sha256": novo_hash,
                    "baixado_em": agora_iso(),
                }
                if existia and hash_antigo == novo_hash:
                    return "sem-mudanca", meta
                return ("atualizado" if existia else "novo"), meta

        if tentativa < TENTATIVAS:
            espera = ESPERA_BASE ** tentativa
            log("   tentativa %s falhou (%s). Nova tentativa em %ss..." % (tentativa, ultimo_erro, espera))
            time.sleep(espera)

    return "erro", {"erro": ultimo_erro or "falha desconhecida", "url": url}


def url_de_release_github(repo, padrao_asset, log, timeout=60):
    """Descobre a URL do asset mais recente de um release do GitHub."""
    api = "https://api.github.com/repos/%s/releases/latest" % repo
    try:
        with abrir_url(api, {"Accept": "application/vnd.github+json"}, timeout) as r:
            dados = json.load(r)
    except Exception as e:
        log("   nao foi possivel consultar a API do GitHub (%s)" % e)
        return None
    regex = re.compile(padrao_asset or ".*")
    for asset in dados.get("assets", []):
        if regex.search(asset.get("name", "")):
            log("   release %s -> asset %s" % (dados.get("tag_name"), asset["name"]))
            return asset["browser_download_url"]
    log("   nenhum asset do release %s casou com o padrao '%s'" % (dados.get("tag_name"), padrao_asset))
    return None


def resolver_urls(fonte, log, timeout):
    """Devolve a lista de URLs a tentar, na ordem."""
    tipo = fonte.get("tipo", "arquivo")
    if tipo == "arquivo":
        return [u for u in (fonte.get("url"), fonte.get("url_alternativa")) if u]
    if tipo == "repo_zip":
        repo = fonte["repo"]
        branch = fonte.get("branch", "main")
        return [
            "https://codeload.github.com/%s/zip/refs/heads/%s" % (repo, branch),
            "https://github.com/%s/archive/refs/heads/%s.zip" % (repo, branch),
        ]
    if tipo == "release_github":
        u = url_de_release_github(fonte["repo"], fonte.get("padrao_asset"), log, timeout)
        return [u] if u else []
    return []


# ----------------------------------------------------------------------
# indice e estado
# ----------------------------------------------------------------------
def gerar_indice(catalogo, estado):
    linhas = [
        "# Indice do acervo de ciberseguranca",
        "",
        "Gerado automaticamente por `baixar_acervo.py` em %s." % agora_iso(),
        "",
        "Nao edite este arquivo a mao: ele e reescrito a cada atualizacao.",
        "",
    ]
    por_cat = {}
    for f in catalogo["fontes"]:
        por_cat.setdefault(f["categoria"], []).append(f)

    nomes_cat = {
        "vulnerabilidades": "Vulnerabilidades e Exposicoes Comuns (CVE / CWE / KEV / EPSS)",
        "ataques": "Tecnicas de ataque (MITRE ATT&CK / CAPEC)",
        "owasp": "Seguranca de aplicacoes e APIs (OWASP)",
        "rede": "Protecao de rede",
        "frameworks": "Frameworks e controles de seguranca",
        "brasil": "Brasil (CERT.br, LGPD/ANPD, fisco)",
    }

    for cat in sorted(por_cat):
        linhas.append("## %s" % nomes_cat.get(cat, cat))
        linhas.append("")
        linhas.append("| Arquivo | Fonte oficial | Formato | Tamanho | Baixado em | Situacao |")
        linhas.append("|---|---|---|---|---|---|")
        for f in sorted(por_cat[cat], key=lambda x: x["nome"]):
            e = estado.get("fontes", {}).get(f["id"], {})
            if f.get("tipo") == "referencia":
                linhas.append(
                    "| (download manual) %s | [%s](%s) | - | - | - | manual |"
                    % (f["nome"], f["fonte_oficial"], f.get("pagina", ""))
                )
                continue
            arq = f.get("arquivo", "-")
            tam = tamanho_legivel(e["bytes"]) if e.get("bytes") else "-"
            quando = (e.get("baixado_em") or "-")[:16].replace("T", " ")
            sit = e.get("situacao", "nao baixado")
            linhas.append(
                "| `%s` | [%s](%s) | %s | %s | %s | %s |"
                % (arq, f["fonte_oficial"], f.get("pagina", ""), f.get("formato", "-"), tam, quando, sit)
            )
        linhas.append("")
        for f in sorted(por_cat[cat], key=lambda x: x["nome"]):
            linhas.append("- **%s**: %s" % (f["nome"], f.get("descricao", "")))
        linhas.append("")

    caminho = os.path.join(DIR_ACERVO, "INDICE.md")
    os.makedirs(DIR_ACERVO, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas))
    return caminho


def verificar_validade(periodicidade_dias):
    estado = carregar_json(ARQ_ESTADO, {})
    ultima = estado.get("ultima_execucao")
    if not ultima:
        print("Acervo nunca foi baixado. Execute: python baixar_acervo.py --somente-essenciais")
        return 2
    d_ultima = dt.datetime.fromisoformat(ultima)
    dias = (dt.datetime.now() - d_ultima).days
    restam = periodicidade_dias - dias
    print("Ultima atualizacao: %s (%s dias atras)" % (ultima[:10], dias))
    print("Periodicidade configurada: %s dias" % periodicidade_dias)
    if restam <= 0:
        print("SITUACAO: VENCIDO ha %s dias. Rode 'python baixar_acervo.py' para atualizar." % abs(restam))
        return 2
    print("SITUACAO: em dia. Proxima atualizacao em %s dias (%s)."
          % (restam, (d_ultima + dt.timedelta(days=periodicidade_dias)).date()))
    return 0


def diagnosticar(catalogo, timeout=30):
    """Testa a conexao com cada site do catalogo e explica o resultado.

    Serve para separar tres causas que dao a mesma mensagem de 'erro' na tela:
    endereco mudou (404), site recusando programa (403) e certificado
    interceptado por antivirus/proxy (falha de TLS).
    """
    import socket
    import urllib.parse

    hosts = {}
    for f in catalogo["fontes"]:
        for u in (f.get("url"), f.get("url_alternativa")):
            if not u:
                continue
            h = urllib.parse.urlparse(u).netloc
            hosts.setdefault(h, u)
    for f in catalogo["fontes"]:
        if f.get("tipo") == "repo_zip":
            hosts.setdefault("codeload.github.com", "https://codeload.github.com")
        if f.get("tipo") == "release_github":
            hosts.setdefault("api.github.com", "https://api.github.com")

    print("")
    print("=" * 78)
    print("DIAGNOSTICO DE CONEXAO - %s site(s)" % len(hosts))
    print("=" * 78)
    ca = CA_BUNDLE or os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    print("Python...........: %s" % sys.version.split()[0])
    print("Certificados.....: %s" % (ca if ca else "padrao do sistema"))
    print("Proxy do ambiente: %s" % (os.environ.get("HTTPS_PROXY")
                                     or os.environ.get("https_proxy") or "nenhum"))
    print("")

    contagem = {}
    for host in sorted(hosts):
        url = hosts[host]
        try:
            with abrir_url(url, {"Range": "bytes=0-0"}, timeout) as r:
                situacao, detalhe = "OK", "HTTP %s" % r.status
        except urllib.error.HTTPError as e:
            if e.code in (200, 206, 400, 416, 501):
                situacao, detalhe = "OK", "HTTP %s (site respondeu)" % e.code
            elif e.code == 404:
                situacao, detalhe = "ENDERECO", "HTTP 404 - arquivo mudou de lugar"
            elif e.code in CODIGOS_FILTRO_ROBO:
                situacao, detalhe = "BLOQUEIO", "HTTP %s - site recusou o programa" % e.code
            else:
                situacao, detalhe = "ERRO", "HTTP %s" % e.code
        except ssl.SSLError as e:
            situacao, detalhe = "CERTIFICADO", str(e)
        except socket.gaierror as e:
            situacao, detalhe = "DNS", str(e)
        except socket.timeout:
            situacao, detalhe = "TIMEOUT", "sem resposta em %ss" % timeout
        except Exception as e:
            msg = str(e)
            if "CERTIFICATE_VERIFY_FAILED" in msg or "certificate" in msg.lower():
                situacao, detalhe = "CERTIFICADO", msg
            elif "Tunnel connection failed" in msg or "proxy" in msg.lower():
                situacao, detalhe = "PROXY", msg
            elif "timed out" in msg.lower():
                situacao, detalhe = "TIMEOUT", msg
            else:
                situacao, detalhe = "ERRO", "%s: %s" % (type(e).__name__, msg)
        contagem[situacao] = contagem.get(situacao, 0) + 1
        print("  %-11s %-42s %s" % (situacao, host, detalhe[:110]))

    print("")
    print("-" * 78)
    print("COMO LER ESTE RESULTADO")
    print("-" * 78)
    total = len(hosts)
    if contagem.get("OK", 0) == total:
        print("  Todos os sites respondem. Se ainda houve erro no download, o problema e")
        print("  o endereco de um arquivo especifico (404), nao a conexao.")
    elif contagem.get("CERTIFICADO"):
        print("  CERTIFICADO: seu antivirus/firewall esta interceptando a conexao segura.")
        print("  Nao desligue a verificacao. Exporte o certificado da ferramenta e rode:")
        print("      python baixar_acervo.py --ca-bundle \"C:\\caminho\\certificado.pem\"")
        print("  Ou libere os sites nvlpubs.nist.gov e cwe.mitre.org no antivirus.")
    if contagem.get("BLOQUEIO"):
        print("  BLOQUEIO: o site recusa download automatico. Baixe pelo navegador e salve")
        print("  na pasta indicada no acervo/INDICE.md.")
    if contagem.get("ENDERECO"):
        print("  ENDERECO: o arquivo mudou de lugar. Corrija a URL em fontes.json")
        print("  (abra a pagina oficial da fonte, indicada no campo 'pagina').")
    if contagem.get("DNS"):
        print("  DNS: o computador nao resolveu o nome do site. Verifique a internet e,")
        print("  se houver proxy na empresa, a variavel HTTPS_PROXY.")
    if contagem.get("TIMEOUT"):
        print("  TIMEOUT: site lento ou bloqueado por firewall. Tente com --timeout 300.")
    if contagem.get("PROXY"):
        print("  PROXY: a rede exige proxy e ele recusou estes sites. Fale com quem cuida da")
        print("  rede/antivirus para liberar os dominios, ou rode de uma rede sem esse filtro.")
    if contagem.get("ERRO"):
        print("  ERRO: falha de rede nao classificada. Confira internet e firewall; se")
        print("  persistir, mande este resultado completo junto com o log de acervo\\_logs.")
    print("")
    print("Copie este resultado inteiro ao pedir ajuda.")
    print("")
    return 0 if contagem.get("OK", 0) == total else 1


# ----------------------------------------------------------------------
# principal
# ----------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description="Baixa e mantem atualizado o acervo de ciberseguranca (fontes oficiais).")
    p.add_argument("--listar", action="store_true", help="mostra o catalogo de fontes e sai")
    p.add_argument("--categoria", help="baixa somente uma categoria (ex: vulnerabilidades, rede, owasp)")
    p.add_argument("--id", action="append", help="baixa somente as fontes com estes ids (pode repetir)")
    p.add_argument("--somente-essenciais", action="store_true",
                   help="baixa apenas as fontes marcadas como essenciais (recomendado na primeira vez)")
    p.add_argument("--forcar", action="store_true", help="baixa de novo mesmo se nada mudou")
    p.add_argument("--timeout", type=int, default=180, help="timeout de rede em segundos (padrao 180)")
    p.add_argument("--verificar-validade", action="store_true",
                   help="apenas informa se o acervo esta vencido (sai com codigo 2 se estiver)")
    p.add_argument("--diagnostico", action="store_true",
                   help="testa a conexao com cada site oficial e explica o que esta falhando")
    p.add_argument("--ca-bundle",
                   help="caminho de um certificado .pem da empresa/antivirus que intercepta TLS "
                        "(mantem a verificacao ligada, apenas confia tambem nele)")
    args = p.parse_args()

    global CA_BUNDLE
    if args.ca_bundle:
        if not os.path.exists(args.ca_bundle):
            print("ERRO: certificado nao encontrado: %s" % args.ca_bundle)
            return 3
        CA_BUNDLE = args.ca_bundle

    if not os.path.exists(ARQ_FONTES):
        print("ERRO: nao encontrei fontes.json em %s" % ARQ_FONTES)
        return 3
    catalogo = carregar_json(ARQ_FONTES, None)
    if not catalogo:
        print("ERRO: fontes.json invalido.")
        return 3
    periodicidade = catalogo.get("periodicidade_dias", 90)

    if args.diagnostico:
        return diagnosticar(catalogo, timeout=min(args.timeout, 45))

    if args.verificar_validade:
        return verificar_validade(periodicidade)

    if args.listar:
        print("%-32s %-18s %-9s %s" % ("ID", "CATEGORIA", "ESSENCIAL", "NOME"))
        print("-" * 110)
        for f in catalogo["fontes"]:
            print("%-32s %-18s %-9s %s" % (f["id"], f["categoria"],
                                           "sim" if f.get("essencial") else "nao", f["nome"]))
        print("\nTotal: %s fontes." % len(catalogo["fontes"]))
        return 0

    fontes = catalogo["fontes"]
    if args.categoria:
        fontes = [f for f in fontes if f["categoria"] == args.categoria]
    if args.id:
        fontes = [f for f in fontes if f["id"] in args.id]
    if args.somente_essenciais:
        fontes = [f for f in fontes if f.get("essencial")]
    if not fontes:
        print("Nenhuma fonte selecionada com esses filtros. Use --listar para ver os ids.")
        return 3

    os.makedirs(DIR_LOGS, exist_ok=True)
    log = Log(os.path.join(DIR_LOGS, "download_%s.log" % dt.datetime.now().strftime("%Y%m%d_%H%M%S")))
    estado = carregar_json(ARQ_ESTADO, {"fontes": {}})
    estado.setdefault("fontes", {})

    log("=" * 78)
    log("ATUALIZACAO DO ACERVO DE CIBERSEGURANCA - %s fonte(s) selecionada(s)" % len(fontes))
    log("Pasta de destino: %s" % DIR_ACERVO)
    log("=" * 78)

    resumo = []
    for i, f in enumerate(fontes, 1):
        log("")
        log("(%s/%s) %s" % (i, len(fontes), f["nome"]))

        if f.get("tipo") == "referencia":
            log("   -> FONTE MANUAL. Baixe da pagina oficial: %s" % f.get("pagina"))
            resumo.append((f["id"], "manual", f.get("pagina", "")))
            estado["fontes"][f["id"]] = {"situacao": "manual", "pagina": f.get("pagina")}
            continue

        destino = os.path.join(DIR_ACERVO, f["categoria"], f["arquivo"])
        meta_anterior = estado["fontes"].get(f["id"], {})
        urls = resolver_urls(f, log, args.timeout)
        if not urls:
            log("   -> ERRO: nao consegui determinar a URL de download.")
            resumo.append((f["id"], "erro", "sem URL"))
            estado["fontes"][f["id"]] = dict(meta_anterior, situacao="erro", erro="sem URL")
            continue

        situacao, meta = "erro", {"erro": "nao tentado"}
        for k, url in enumerate(urls):
            if k:
                log("   tentando endereco alternativo...")
            log("   URL: %s" % url)
            situacao, meta = baixar_arquivo(
                url, destino, meta_anterior, log,
                timeout=args.timeout, max_mb=f.get("max_mb"), forcar=args.forcar,
                referer=f.get("pagina"))
            if situacao != "erro":
                break

        if situacao == "erro":
            log("   -> ERRO: %s" % meta.get("erro"))
            log("      Confira manualmente a pagina oficial: %s" % f.get("pagina", "(nao informada)"))
            resumo.append((f["id"], "erro", str(meta.get("erro"))))
            estado["fontes"][f["id"]] = dict(meta_anterior, situacao="erro", erro=meta.get("erro"),
                                             verificado_em=agora_iso())
            continue

        if situacao == "sem-mudanca":
            log("   -> SEM MUDANCA (arquivo do acervo continua sendo a versao vigente)")
        else:
            log("   -> %s: %s (%s)" % (situacao.upper(), destino, tamanho_legivel(meta["bytes"])))

        meta["situacao"] = situacao
        meta["verificado_em"] = agora_iso()
        meta["arquivo"] = os.path.relpath(destino, RAIZ)
        estado["fontes"][f["id"]] = meta
        resumo.append((f["id"], situacao, tamanho_legivel(meta.get("bytes", 0))))

    estado["ultima_execucao"] = agora_iso()
    estado["proxima_prevista"] = (dt.datetime.now() + dt.timedelta(days=periodicidade)).replace(
        microsecond=0).isoformat()
    estado["periodicidade_dias"] = periodicidade
    salvar_json(ARQ_ESTADO, estado)
    indice = gerar_indice(catalogo, estado)

    erros = [r for r in resumo if r[1] == "erro"]
    log("")
    log("=" * 78)
    log("RESUMO")
    log("=" * 78)
    for ident, sit, extra in resumo:
        log("  %-32s %-12s %s" % (ident, sit, extra))
    log("")
    log("Indice atualizado: %s" % indice)
    log("Proxima atualizacao prevista: %s" % estado["proxima_prevista"][:10])
    if erros:
        log("")
        log("ATENCAO: %s fonte(s) falharam. Isso normalmente significa que a URL mudou." % len(erros))
        log("Abra a pagina oficial da fonte, pegue o novo endereco e corrija em fontes.json.")
    log("Log completo: %s" % log.caminho)
    log.fechar()
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
