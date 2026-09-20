# -*- coding: utf-8 -*-
"""
auditor.py - Revisa um projeto procurando falhas que um invasor poderia usar.

Somente LEITURA: nunca altera, move ou apaga arquivo do projeto analisado.

Exemplos de uso (Prompt de Comando do Windows):
    python auditor.py --projeto "C:\\projetos\\importar-notas"
    python auditor.py --projeto . --online
    python auditor.py --projeto "C:\\projetos\\fronteira" --saida "C:\\projetos\\agente-ciberseguranca\\relatorios"

Codigos de saida (uteis para bloquear publicacao automaticamente):
    0 = nenhum achado CRITICO ou ALTO
    1 = encontrou CRITICO ou ALTO (nao publicar sem corrigir)
    3 = erro de execucao
"""

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_REGRAS = os.path.join(RAIZ, "regras")
DIR_RELATORIOS = os.path.join(RAIZ, "relatorios")
ARQ_ESTADO_ACERVO = os.path.join(RAIZ, "acervo", "_estado", "estado.json")

ORDEM_SEVERIDADE = ["CRITICO", "ALTO", "MEDIO", "BAIXO", "INFO"]

PASTAS_IGNORADAS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".idea", ".vscode",
    "site-packages", ".next", ".tox", "acervo", "relatorios", ".claude",
}

EXTENSOES_TEXTO = {
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
    ".ini", ".cfg", ".conf", ".toml", ".env", ".bat", ".cmd", ".ps1", ".sh", ".sql",
    ".html", ".htm", ".css", ".md", ".txt", ".java", ".cs", ".php", ".rb", ".go", ".vbs",
}

# Pastas que alimentam outros sistemas: o auditor nunca entra nem grava nada nelas.
PASTAS_PROIBIDAS = [
    r"c:\nota entrada", r"c:\nota saida", r"c:\fronteira", r"\efd",
]

# Documentacao: procuramos segredo colado no texto, mas nao aplicamos as regras de
# codigo inseguro (senao a propria explicacao da falha vira achado).
EXTENSOES_DOCUMENTACAO = {".md", ".txt"}

LIMITE_BYTES_LEITURA = 2 * 1024 * 1024  # 2 MB por arquivo


# ----------------------------------------------------------------------
def agora():
    return dt.datetime.now().replace(microsecond=0)


def carregar_regras():
    pacote = {}
    for nome in ("segredos.json", "codigo.json", "arquivos.json"):
        caminho = os.path.join(DIR_REGRAS, nome)
        if not os.path.exists(caminho):
            raise SystemExit("ERRO: arquivo de regras nao encontrado: %s" % caminho)
        with open(caminho, "r", encoding="utf-8") as f:
            pacote[nome.replace(".json", "")] = json.load(f)
    for grupo in ("segredos", "codigo"):
        for regra in pacote[grupo]["regras"]:
            regra["_re"] = re.compile(regra["regex"])
    return pacote


def caminho_proibido(caminho):
    baixo = caminho.lower().replace("/", "\\")
    return any(p in baixo for p in PASTAS_PROIBIDAS)


def mascarar(texto):
    """Esconde o valor dos segredos antes de escrever no relatorio."""
    def troca(m):
        valor = m.group(2)
        if len(valor) <= 4:
            return m.group(0)
        return "%s%s%s%s" % (m.group(1), valor[:3], "*" * 8, m.group(3))
    texto = re.sub(r"([\"'])([^\"']{5,})([\"'])", troca, texto)
    texto = re.sub(r"(-----BEGIN[^-]*-----).*", r"\1 [conteudo omitido]", texto)
    return texto.strip()[:220]


def achado(**kw):
    kw.setdefault("cwe", "")
    kw.setdefault("owasp", "")
    kw.setdefault("linha", 0)
    kw.setdefault("trecho", "")
    return kw


# ----------------------------------------------------------------------
# coleta de arquivos
# ----------------------------------------------------------------------
def listar_arquivos(raiz, ignorar_extra):
    arquivos, ignorados = [], 0
    for pasta_atual, subpastas, nomes in os.walk(raiz):
        if caminho_proibido(pasta_atual):
            subpastas[:] = []
            continue
        subpastas[:] = [d for d in subpastas
                        if d not in PASTAS_IGNORADAS
                        and not any(fnmatch.fnmatch(d, pad) for pad in ignorar_extra)]
        for nome in nomes:
            completo = os.path.join(pasta_atual, nome)
            if any(fnmatch.fnmatch(nome, pad) for pad in ignorar_extra):
                ignorados += 1
                continue
            arquivos.append(completo)
    return arquivos, ignorados


# ----------------------------------------------------------------------
# verificacoes
# ----------------------------------------------------------------------
def verificar_nomes_de_arquivo(arquivos, raiz, regras_arquivos):
    achados = []
    for regra in regras_arquivos["regras"]:
        positivos = [p for p in regra["padroes"] if not p.startswith("!")]
        excecoes = [p[1:] for p in regra["padroes"] if p.startswith("!")]
        for caminho in arquivos:
            nome = os.path.basename(caminho)
            if not any(fnmatch.fnmatch(nome.lower(), p.lower()) for p in positivos):
                continue
            if any(fnmatch.fnmatch(nome.lower(), p.lower()) for p in excecoes):
                continue
            try:
                tam = os.path.getsize(caminho)
            except OSError:
                tam = 0
            achados.append(achado(
                id=regra["id"], nome=regra["nome"], severidade=regra["severidade"],
                categoria="arquivo-sensivel", cwe=regra.get("cwe", ""),
                arquivo=os.path.relpath(caminho, raiz),
                trecho="arquivo de %s bytes" % tam,
                recomendacao=regra["recomendacao"]))
    return achados


def verificar_conteudo(arquivos, raiz, regras):
    achados = []
    grupos = [("segredo", regras["segredos"]), ("codigo-inseguro", regras["codigo"])]
    analisados = 0
    for caminho in arquivos:
        ext = os.path.splitext(caminho)[1].lower()
        nome = os.path.basename(caminho).lower()
        if ext not in EXTENSOES_TEXTO and not nome.startswith(".env"):
            continue
        # nao auditar os proprios arquivos de regra deste agente
        if os.path.abspath(os.path.dirname(caminho)) == DIR_REGRAS:
            continue
        try:
            if os.path.getsize(caminho) > LIMITE_BYTES_LEITURA:
                continue
            with open(caminho, "r", encoding="utf-8", errors="replace") as f:
                linhas = f.readlines()
        except OSError:
            continue
        analisados += 1
        rel = os.path.relpath(caminho, raiz)
        for categoria, pacote in grupos:
            if categoria == "codigo-inseguro" and ext in EXTENSOES_DOCUMENTACAO:
                continue
            ignorar_se = pacote.get("ignorar_linha_se_contem", [])
            for regra in pacote["regras"]:
                exts = regra.get("extensoes", ["*"])
                if "*" not in exts and ext not in exts:
                    continue
                for n, linha in enumerate(linhas, 1):
                    if len(linha) > 4000:
                        continue
                    if not regra["_re"].search(linha):
                        continue
                    if categoria == "segredo" and any(t in linha for t in ignorar_se):
                        continue
                    if categoria != "segredo" and any(t in linha for t in ignorar_se):
                        continue
                    achados.append(achado(
                        id=regra["id"], nome=regra["nome"], severidade=regra["severidade"],
                        categoria=categoria, cwe=regra.get("cwe", ""), owasp=regra.get("owasp", ""),
                        arquivo=rel, linha=n,
                        trecho=mascarar(linha) if categoria == "segredo" else linha.strip()[:220],
                        recomendacao=regra["recomendacao"]))
    return achados, analisados


OBRIGATORIOS_GITIGNORE = [
    (".env", "CRITICO", "arquivo com credenciais"),
    ("*.pfx", "CRITICO", "certificado digital A1"),
    ("*.p12", "ALTO", "certificado digital"),
    ("*.pem", "ALTO", "chave/certificado"),
    ("*.key", "ALTO", "chave privada"),
    ("*.log", "BAIXO", "logs de execucao"),
    ("__pycache__", "INFO", "cache do Python"),
]


def gitignores_aplicaveis(raiz):
    """Lista os .gitignore que valem para este projeto.

    Um projeto costuma ser uma pasta dentro de um repositorio maior (e a convencao
    deste repositorio). Nesse caso o .gitignore da raiz do repositorio protege o
    projeto, e cobrar um .gitignore proprio seria ruido.
    """
    encontrados = []
    atual = os.path.abspath(raiz)
    while True:
        cand = os.path.join(atual, ".gitignore")
        if os.path.exists(cand):
            encontrados.append(cand)
        if os.path.isdir(os.path.join(atual, ".git")):
            break                      # chegou na raiz do repositorio
        pai = os.path.dirname(atual)
        if pai == atual:
            break                      # chegou na raiz do disco
        atual = pai
    return encontrados


def verificar_gitignore(raiz):
    achados = []
    arquivos_gi = gitignores_aplicaveis(raiz)
    if not arquivos_gi:
        achados.append(achado(
            id="GIT001", nome="Projeto sem .gitignore", severidade="ALTO",
            categoria="higiene-git", cwe="CWE-312", arquivo=".gitignore",
            trecho="nao existe .gitignore nem na pasta do projeto nem na raiz do repositorio",
            recomendacao="Crie um .gitignore com pelo menos: .env, *.pfx, *.p12, *.pem, *.key, *.log, __pycache__/, *.db. "
                         "Sem isso e facil enviar certificado e senha para o GitHub sem perceber."))
        return achados
    conteudo = ""
    for cam in arquivos_gi:
        with open(cam, "r", encoding="utf-8", errors="replace") as f:
            conteudo += f.read() + "\n"
    onde = ", ".join(os.path.relpath(c, raiz) for c in arquivos_gi)
    faltando = [(p, sev, desc) for p, sev, desc in OBRIGATORIOS_GITIGNORE if p not in conteudo]
    for padrao, sev, desc in faltando:
        achados.append(achado(
            id="GIT002", nome="Padrao ausente no .gitignore: %s (%s)" % (padrao, desc),
            severidade=sev, categoria="higiene-git", cwe="CWE-312", arquivo=onde,
            trecho="padrao nao encontrado em: %s" % onde,
            recomendacao="Acrescente a linha '%s' ao .gitignore (o do projeto ou o da raiz do "
                         "repositorio, que tambem vale)." % padrao))
    return achados


def verificar_rastreados_no_git(raiz, regras_arquivos):
    """Arquivo sensivel JA versionado no Git e o caso mais grave: fica no historico."""
    achados = []
    if not os.path.isdir(os.path.join(raiz, ".git")):
        return achados
    try:
        saida = subprocess.run(["git", "-C", raiz, "ls-files"], capture_output=True,
                               text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return achados
    if saida.returncode != 0:
        return achados
    rastreados = [l.strip() for l in saida.stdout.splitlines() if l.strip()]
    criticos = [r for r in regras_arquivos["regras"] if r["severidade"] in ("CRITICO", "ALTO")]
    for regra in criticos:
        positivos = [p for p in regra["padroes"] if not p.startswith("!")]
        excecoes = [p[1:] for p in regra["padroes"] if p.startswith("!")]
        for arq in rastreados:
            base = os.path.basename(arq).lower()
            if not any(fnmatch.fnmatch(base, p.lower()) for p in positivos):
                continue
            if any(fnmatch.fnmatch(base, p.lower()) for p in excecoes):
                continue
            achados.append(achado(
                id="GIT003", nome="Arquivo sensivel versionado no Git (%s)" % regra["nome"],
                severidade="CRITICO", categoria="higiene-git", cwe="CWE-312", arquivo=arq,
                trecho="rastreado pelo Git (esta no historico de commits)",
                recomendacao="Remova do controle de versao (git rm --cached) E troque o segredo: quem ja clonou o "
                             "repositorio continua com a versao antiga. Apagar no commit seguinte NAO apaga do historico."))
    return achados


def verificar_dependencias(raiz, online):
    achados, pacotes = [], []
    req = os.path.join(raiz, "requirements.txt")
    if not os.path.exists(req):
        return achados, pacotes
    sem_versao = []
    with open(req, "r", encoding="utf-8", errors="replace") as f:
        for n, linha in enumerate(f, 1):
            item = linha.split("#")[0].strip()
            if not item or item.startswith("-"):
                continue
            m = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*==\s*([^\s;]+)", item)
            if m:
                pacotes.append((m.group(1).split("[")[0], m.group(2), n))
            else:
                sem_versao.append((item, n))
    for item, n in sem_versao:
        achados.append(achado(
            id="DEP001", nome="Dependencia sem versao fixada: %s" % item, severidade="MEDIO",
            categoria="dependencia", cwe="CWE-1104", arquivo="requirements.txt", linha=n,
            trecho=item,
            recomendacao="Fixe a versao (ex: %s==1.2.3). Sem isso a instalacao pode trazer uma versao diferente "
                         "da testada, inclusive uma com falha conhecida." % item))
    if online and pacotes:
        achados.extend(consultar_osv(pacotes))
    elif pacotes:
        achados.append(achado(
            id="DEP000", nome="Consulta de CVE das dependencias nao foi feita", severidade="INFO",
            categoria="dependencia", arquivo="requirements.txt",
            trecho="%s pacotes com versao fixada" % len(pacotes),
            recomendacao="Rode novamente com --online para consultar a base OSV.dev e saber se alguma dependencia "
                         "tem vulnerabilidade publicada."))
    return achados, pacotes


def consultar_osv(pacotes):
    """Consulta osv.dev (base publica de vulnerabilidades em dependencias)."""
    import urllib.request
    import urllib.error
    consultas = [{"package": {"name": nome, "ecosystem": "PyPI"}, "version": versao}
                 for nome, versao, _ in pacotes]
    corpo = json.dumps({"queries": consultas}).encode("utf-8")
    req = urllib.request.Request("https://api.osv.dev/v1/querybatch", data=corpo,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "AgenteCiberseguranca/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            dados = json.load(resp)
    except Exception as e:
        return [achado(
            id="DEP002", nome="Nao foi possivel consultar a base OSV.dev", severidade="INFO",
            categoria="dependencia", arquivo="requirements.txt",
            trecho="%s: %s" % (type(e).__name__, e),
            recomendacao="Verifique a internet/proxy e rode de novo com --online. "
                         "Alternativa local: pip install pip-audit && pip-audit -r requirements.txt")]
    achados = []
    for (nome, versao, linha), resultado in zip(pacotes, dados.get("results", [])):
        vulns = resultado.get("vulns") or []
        if not vulns:
            continue
        ids = ", ".join(v.get("id", "?") for v in vulns[:8])
        achados.append(achado(
            id="DEP003", nome="Dependencia com vulnerabilidade publicada: %s %s" % (nome, versao),
            severidade="ALTO", categoria="dependencia", cwe="CWE-1395", owasp="A06:2021",
            arquivo="requirements.txt", linha=linha,
            trecho="%s vulnerabilidade(s): %s" % (len(vulns), ids),
            recomendacao="Atualize %s para uma versao corrigida (consulte https://osv.dev/vulnerability/%s) e teste a "
                         "rotina depois da atualizacao." % (nome, vulns[0].get("id", ""))))
    return achados


def situacao_acervo():
    if not os.path.exists(ARQ_ESTADO_ACERVO):
        return "acervo ainda nao baixado (rode baixar_acervo.py --somente-essenciais)"
    with open(ARQ_ESTADO_ACERVO, "r", encoding="utf-8") as f:
        estado = json.load(f)
    ultima = estado.get("ultima_execucao", "")
    if not ultima:
        return "acervo sem registro de atualizacao"
    dias = (dt.datetime.now() - dt.datetime.fromisoformat(ultima)).days
    periodo = estado.get("periodicidade_dias", 90)
    aviso = " - VENCIDO, atualize o acervo" if dias > periodo else ""
    return "acervo atualizado em %s (%s dias atras)%s" % (ultima[:10], dias, aviso)


# ----------------------------------------------------------------------
# relatorio
# ----------------------------------------------------------------------
def veredito(placar):
    if placar.get("CRITICO"):
        return ("BLOQUEADO PARA PUBLICACAO",
                "Ha achado CRITICO. Nao publique na web e nao entregue ao cliente antes de corrigir.")
    if placar.get("ALTO"):
        return ("LIBERADO COM RESSALVAS",
                "Sem achado CRITICO, mas ha achado ALTO. Corrija antes de expor o sistema na internet.")
    if placar.get("MEDIO"):
        return ("APROVADO COM OBSERVACOES",
                "Nada grave encontrado. Trate os itens MEDIO na proxima versao.")
    return ("APROVADO NA VERIFICACAO AUTOMATICA",
            "Nenhum achado relevante nas regras aplicadas. Isso nao substitui a revisao do checklist manual.")


def gerar_relatorio_md(ctx, achados):
    placar = {}
    for a in achados:
        placar[a["severidade"]] = placar.get(a["severidade"], 0) + 1
    situacao, explicacao = veredito(placar)

    L = []
    L.append("# Relatorio de auditoria de seguranca")
    L.append("")
    L.append("| Item | Valor |")
    L.append("|---|---|")
    L.append("| Projeto | `%s` |" % ctx["projeto"])
    L.append("| Caminho | `%s` |" % ctx["caminho"])
    L.append("| Data da analise | %s |" % ctx["data"])
    L.append("| Arquivos encontrados | %s |" % ctx["total_arquivos"])
    L.append("| Arquivos com conteudo analisado | %s |" % ctx["analisados"])
    L.append("| Regras aplicadas | %s |" % ctx["total_regras"])
    L.append("| Consulta de CVE em dependencias | %s |" % ("sim (OSV.dev)" if ctx["online"] else "nao (use --online)"))
    L.append("| Acervo de referencia | %s |" % ctx["acervo"])
    L.append("")
    L.append("## Veredito")
    L.append("")
    L.append("**%s**" % situacao)
    L.append("")
    L.append(explicacao)
    L.append("")
    L.append("| Severidade | Achados |")
    L.append("|---|---|")
    for sev in ORDEM_SEVERIDADE:
        L.append("| %s | %s |" % (sev, placar.get(sev, 0)))
    L.append("")
    L.append("> Esta verificacao e automatizada e por padrao de texto. Ela encontra os erros mais comuns, "
             "mas nao entende a regra de negocio. Complete com o checklist "
             "`checklists/CHECKLIST-PRE-DEPLOY.md` antes de publicar.")
    L.append("")

    if not achados:
        L.append("## Achados")
        L.append("")
        L.append("Nenhum achado.")
    else:
        L.append("## Achados por severidade")
        L.append("")
        contador = 0
        for sev in ORDEM_SEVERIDADE:
            do_nivel = [a for a in achados if a["severidade"] == sev]
            if not do_nivel:
                continue
            L.append("### %s (%s)" % (sev, len(do_nivel)))
            L.append("")
            for a in sorted(do_nivel, key=lambda x: (x["arquivo"], x["linha"])):
                contador += 1
                local = a["arquivo"] + (":%s" % a["linha"] if a["linha"] else "")
                ref = " / ".join([x for x in (a.get("cwe"), a.get("owasp")) if x])
                L.append("#### %s. [%s] %s" % (contador, a["id"], a["nome"]))
                L.append("")
                L.append("- **FATO ENCONTRADO**: `%s`" % local)
                if a["trecho"]:
                    L.append("  ```")
                    L.append("  " + a["trecho"])
                    L.append("  ```")
                L.append("- **INTERPRETACAO (risco)**: %s" % a["nome"] +
                         (" - referencia %s" % ref if ref else ""))
                L.append("- **RECOMENDACAO**: %s" % a["recomendacao"])
                L.append("")

    L.append("## Proximos passos")
    L.append("")
    L.append("1. Corrija primeiro todos os itens CRITICO, comecando por credencial exposta.")
    L.append("2. Toda credencial que apareceu em codigo deve ser **trocada**, nao apenas removida.")
    L.append("3. Rode a auditoria de novo: `python auditor.py --projeto \"%s\" --online`" % ctx["caminho"])
    L.append("4. Percorra o `CHECKLIST-PRE-DEPLOY.md` e so entao publique.")
    L.append("")
    return "\n".join(L), placar, situacao


# ----------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Audita um projeto procurando falhas de seguranca (somente leitura).")
    p.add_argument("--projeto", default=".", help="pasta do projeto a auditar (padrao: pasta atual)")
    p.add_argument("--saida", default=DIR_RELATORIOS, help="pasta onde gravar o relatorio")
    p.add_argument("--online", action="store_true",
                   help="consulta a base OSV.dev para achar CVE nas dependencias do requirements.txt")
    p.add_argument("--ignorar", action="append", default=[],
                   help="padrao de arquivo/pasta a ignorar (pode repetir), ex: --ignorar \"*.min.js\"")
    p.add_argument("--silencioso", action="store_true", help="nao imprime os achados na tela")
    args = p.parse_args()

    raiz = os.path.abspath(args.projeto)
    if not os.path.isdir(raiz):
        print("ERRO: pasta nao encontrada: %s" % raiz)
        return 3
    if caminho_proibido(raiz):
        print("ERRO: essa pasta esta na lista de pastas protegidas (alimenta outros sistemas). Auditoria cancelada.")
        return 3

    regras = carregar_regras()
    total_regras = sum(len(regras[g]["regras"]) for g in ("segredos", "codigo", "arquivos")) \
        + len(OBRIGATORIOS_GITIGNORE) + 4

    arquivos, ignorados = listar_arquivos(raiz, args.ignorar)
    achados = []
    achados += verificar_nomes_de_arquivo(arquivos, raiz, regras["arquivos"])
    de_conteudo, analisados = verificar_conteudo(arquivos, raiz, regras)
    achados += de_conteudo
    achados += verificar_gitignore(raiz)
    achados += verificar_rastreados_no_git(raiz, regras["arquivos"])
    dep_achados, _pacotes = verificar_dependencias(raiz, args.online)
    achados += dep_achados

    ctx = {
        "projeto": os.path.basename(raiz) or raiz,
        "caminho": raiz,
        "data": agora().isoformat(sep=" "),
        "total_arquivos": len(arquivos),
        "analisados": analisados,
        "total_regras": total_regras,
        "online": args.online,
        "acervo": situacao_acervo(),
    }
    md, placar, situacao = gerar_relatorio_md(ctx, achados)

    os.makedirs(args.saida, exist_ok=True)
    base = "auditoria_%s_%s" % (re.sub(r"[^A-Za-z0-9_.-]", "-", ctx["projeto"]),
                                agora().strftime("%Y%m%d_%H%M"))
    caminho_md = os.path.join(args.saida, base + ".md")
    caminho_json = os.path.join(args.saida, base + ".json")
    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write(md)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump({"contexto": ctx, "veredito": situacao, "placar": placar, "achados": achados},
                  f, ensure_ascii=False, indent=2)

    print("")
    print("=" * 74)
    print("AUDITORIA DE SEGURANCA - %s" % ctx["projeto"])
    print("=" * 74)
    print("Arquivos: %s  |  conteudo analisado: %s  |  regras: %s" %
          (len(arquivos), analisados, total_regras))
    for sev in ORDEM_SEVERIDADE:
        if placar.get(sev):
            print("  %-8s %s" % (sev, placar[sev]))
    print("")
    print("VEREDITO: %s" % situacao)
    if not args.silencioso:
        for sev in ("CRITICO", "ALTO"):
            for a in [x for x in achados if x["severidade"] == sev]:
                local = a["arquivo"] + (":%s" % a["linha"] if a["linha"] else "")
                print("  [%s] %-9s %s -> %s" % (a["id"], sev, local, a["nome"]))
    print("")
    print("Relatorio: %s" % caminho_md)
    print("Dados....: %s" % caminho_json)
    return 1 if (placar.get("CRITICO") or placar.get("ALTO")) else 0


if __name__ == "__main__":
    sys.exit(main())
