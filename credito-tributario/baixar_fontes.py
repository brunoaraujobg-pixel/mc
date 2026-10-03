"""
Baixa fontes OFICIAIS sobre exclusao do ICMS da base do PIS/COFINS (Tema 69 STF).

- Salva em PASTA_DESTINO com nome AAAA-MM-DD_ORGAO_TIPO-NUMERO_assunto.ext
- Nao baixa duplicado (confere INDICE.md e arquivos existentes)
- Nunca apaga nem sobrescreve arquivo existente
- Acrescenta linhas ao INDICE.md (nunca reescreve o que ja existe)
- Fontes sem URL confirmada ficam como PENDENTE (preencha a URL na lista FONTES)

Uso:  python baixar_fontes.py            (baixa tudo)
      python baixar_fontes.py --simular  (so mostra o que faria)
Usa apenas a biblioteca padrao do Python (nada para instalar).
"""
import argparse
import hashlib
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURACAO
# ---------------------------------------------------------------------------
PASTA_DESTINO = Path(r"C:\PROJETOS\Documento Analista\Credito Tributario")

# Somente dominios oficiais permitidos.
DOMINIOS_OFICIAIS = (
    "planalto.gov.br", "gov.br", "normas.receita.fazenda.gov.br",
    "pgfn.gov.br", "stf.jus.br", "stj.jus.br", "sefaz.pe.gov.br",
    "legislacao.sefaz.pe.gov.br", "nfe.fazenda.gov.br",
)

# Cada fonte: data do ato, orgao, tipo-numero, assunto, url, ponto(s) da pesquisa.
# url = None  -> PENDENTE: abra o site oficial, copie o link direto do PDF/texto
# e cole aqui. Datas "None" -> informe quando conferir no ato.
FONTES = [
    {"data": "1966-10-25", "orgao": "PLANALTO", "tipo": "LEI-5172",
     "assunto": "CTN-art168-prazo-5-anos", "pontos": "5",
     "url": "https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm"},
    {"data": "2005-02-09", "orgao": "PLANALTO", "tipo": "LC-118",
     "assunto": "art3-interpretacao-prazo-repeticao", "pontos": "5",
     "url": "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp118.htm"},
    {"data": "1998-11-27", "orgao": "PLANALTO", "tipo": "LEI-9718",
     "assunto": "PIS-COFINS-cumulativo-base", "pontos": "3",
     "url": "https://www.planalto.gov.br/ccivil_03/leis/l9718compilada.htm"},
    {"data": "2002-12-30", "orgao": "PLANALTO", "tipo": "LEI-10637",
     "assunto": "PIS-nao-cumulativo", "pontos": "3",
     "url": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10637.htm"},
    {"data": "2003-12-29", "orgao": "PLANALTO", "tipo": "LEI-10833",
     "assunto": "COFINS-nao-cumulativo", "pontos": "3",
     "url": "https://www.planalto.gov.br/ccivil_03/leis/2003/l10.833.htm"},
    {"data": "2025-01-16", "orgao": "PLANALTO", "tipo": "LC-214",
     "assunto": "reforma-tributaria-IBS-CBS", "pontos": "8",
     "url": "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm"},

    # ---- PENDENTES: URL nao confirmada. Localize no site oficial e cole. ----
    {"data": "2017-03-15", "orgao": "STF", "tipo": "RE-574706",
     "assunto": "acordao-merito-tema69", "pontos": "1, 2",
     "url": None, "onde": "portal.stf.jus.br > Jurisprudencia > Repercussao Geral > Tema 69 > Inteiro teor do acordao"},
    {"data": "2021-05-13", "orgao": "STF", "tipo": "RE-574706-ED",
     "assunto": "embargos-modulacao-corte-15-03-2017", "pontos": "1",
     "url": None, "onde": "portal.stf.jus.br > Tema 69 > acordao dos embargos de declaracao (13/05/2021)"},
    {"data": "2021-06-01", "orgao": "PGFN", "tipo": "PARECER-SEI-14483",
     "assunto": "ICMS-base-PIS-COFINS-RE574706", "pontos": "2",
     "url": None, "onde": "gov.br/pgfn > Legislacao/Pareceres (confirme a data do ato no proprio parecer)"},
    {"data": "2021-12-06", "orgao": "RFB", "tipo": "IN-2055",
     "assunto": "restituicao-compensacao-PERDCOMP", "pontos": "5",
     "url": None, "onde": "normas.receita.fazenda.gov.br > pesquisar IN RFB 2055/2021 (confirme vigencia/alteracoes)"},
    {"data": None, "orgao": "RFB", "tipo": "SC-COSIT",
     "assunto": "ICMS-destacado-exclusao-PIS-COFINS", "pontos": "2, 3, 4",
     "url": None, "onde": "normas.receita.fazenda.gov.br > Solucoes de Consulta COSIT sobre ICMS/PIS/COFINS pos-Tema 69"},
    {"data": None, "orgao": "STJ", "tipo": "TEMA-1008",
     "assunto": "ICMS-base-IRPJ-CSLL-presumido", "pontos": "7",
     "url": None, "onde": "stj.jus.br > Precedentes Qualificados > Tema 1008 (acordao + tese)"},
    {"data": None, "orgao": "SEFAZ-PE", "tipo": "ORIENTACAO",
     "assunto": "ICMS-destacado-NFe-EFD", "pontos": "6",
     "url": None, "onde": "sefaz.pe.gov.br / legislacao.sefaz.pe.gov.br (se nao houver, registrar NAO ENCONTRADO)"},
]

CABECALHO_INDICE = (
    "# INDICE - Credito Tributario\n\n"
    "| Arquivo | Orgao | Norma/Numero | Data do ato | Data da consulta | Link de origem |\n"
    "|---|---|---|---|---|---|\n"
)
# ---------------------------------------------------------------------------


def url_oficial(url: str) -> bool:
    host = url.split("/")[2].lower()
    return any(host == d or host.endswith("." + d) for d in DOMINIOS_OFICIAIS)


def extensao(url: str, content_type: str) -> str:
    if "pdf" in content_type or url.lower().endswith(".pdf"):
        return ".pdf"
    return ".html"


def baixar(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "").lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true", help="nao baixa nem grava nada")
    args = ap.parse_args()

    hoje = date.today().isoformat()
    indice = PASTA_DESTINO / "INDICE.md"
    if not args.simular:
        PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
    texto_indice = indice.read_text(encoding="utf-8") if indice.exists() else ""

    baixados, pulados, pendentes, erros = [], [], [], []
    novas_linhas = []

    for f in FONTES:
        nome_base = f"{f['data'] or 'SEM-DATA'}_{f['orgao']}_{f['tipo']}_{f['assunto']}"
        url = f["url"]
        if not url:
            pendentes.append((nome_base, f.get("onde", "localizar manualmente")))
            continue
        if not url_oficial(url):
            erros.append((nome_base, "URL fora dos dominios oficiais - ignorada"))
            continue
        # duplicidade: URL ja no indice ou arquivo com mesmo nome-base na pasta
        ja_existe = url in texto_indice or any(PASTA_DESTINO.glob(nome_base + ".*"))
        if ja_existe:
            pulados.append(nome_base)
            continue
        if args.simular:
            print(f"[SIMULAR] baixaria {url} -> {nome_base}")
            continue
        try:
            dados, ctype = baixar(url)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            erros.append((nome_base, f"{url} -> {e}"))
            continue
        destino = PASTA_DESTINO / (nome_base + extensao(url, ctype))
        if destino.exists():  # seguranca extra: nunca sobrescrever
            pulados.append(destino.name)
            continue
        destino.write_bytes(dados)
        sha = hashlib.sha256(dados).hexdigest()[:12]
        novas_linhas.append(
            f"| {destino.name} | {f['orgao']} | {f['tipo']} | {f['data'] or 'CONFERIR'} "
            f"| {hoje} | {url} |  <!-- sha256:{sha} -->"
        )
        baixados.append(destino.name)
        print(f"[OK] {destino.name}")

    if novas_linhas and not args.simular:
        with indice.open("a", encoding="utf-8") as fh:
            if not texto_indice:
                fh.write(CABECALHO_INDICE)
            fh.write("\n".join(novas_linhas) + "\n")

    print("\n===== RESUMO =====")
    print(f"Baixados ({len(baixados)}):", *baixados, sep="\n  ")
    print(f"Ja existiam / pulados ({len(pulados)}):", *pulados, sep="\n  ")
    print(f"PENDENTES - preencher URL em FONTES ({len(pendentes)}):")
    for n, onde in pendentes:
        print(f"  {n}\n    onde achar: {onde}")
    print(f"Erros ({len(erros)}):", *[f"{n}: {m}" for n, m in erros], sep="\n  ")
    print("\nObs.: paginas do Planalto sao salvas como .html. A vigencia (alteracoes/"
          "revogacoes) deve ser conferida e anotada na nota de referencia.")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
