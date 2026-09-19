# -*- coding: utf-8 -*-
"""
CONFERIR-TABELAS.PY — confere as tabelas da calculadora nas fontes oficiais
============================================================================

PARA QUE SERVE
--------------
A calculadora usa tabelas oficiais (IRRF, INSS, Simples Nacional...). Este
script abre os sites oficiais, procura cada número que está no arquivo
js/tabelas.js e diz se ele confere ou não.

Ele faz uma conferência em DUAS PONTAS:
  1) o número está escrito em js/tabelas.js?
  2) o mesmo número aparece na página oficial do governo?

Se as duas pontas baterem, a tabela está certa. Se alguma falhar, o script
avisa e mostra exatamente qual número conferir na mão.

POR QUE RODAR NA SUA MÁQUINA
----------------------------
Os sites gov.br não abrem de dentro do ambiente onde a página foi criada.
Da sua rede eles abrem normalmente — por isso este script roda aí.

COMO RODAR (Windows)
--------------------
  Dê dois cliques em CONFERIR-TABELAS.bat

  Ou, pelo Prompt de Comando, dentro da pasta do projeto:
      python conferir-tabelas.py

  Precisa ter o Python instalado (python.org/downloads — na instalação,
  marque a caixinha "Add Python to PATH"). Não precisa instalar mais nada:
  o script usa só o que já vem junto com o Python.

O QUE ESPERAR NA TELA
---------------------
  [OK]    o número confere nas duas pontas
  [FALHA] o número está em js/tabelas.js mas NAO foi achado no site oficial
  [AVISO] não deu para abrir o site (fora do ar, sem internet, bloqueio)

No final aparece o resumo. Se der tudo OK, pode publicar a página.
"""

import html as _html
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ARQUIVO_TABELAS = PASTA / "js" / "tabelas.js"

TEMPO_LIMITE = 45  # segundos por site
NAVEGADOR = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# O QUE CONFERIR
#
# Cada item é: (descrição, valor como aparece no site, valor como está no .js)
# "bloqueante": se falhar, NÃO publique a página.
# ---------------------------------------------------------------------------
VERIFICACOES = [
    {
        "grupo": "IRRF — tabela progressiva mensal e deduções",
        "norma": "Lei nº 15.191/2025",
        "bloqueante": True,
        "urls": [
            "https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/2026",
        ],
        "valores": [
            ("Limite da faixa isenta",              "2.428,80",   "2428.80"),
            ("Limite da faixa de 7,5%",             "2.826,65",   "2826.65"),
            ("Limite da faixa de 15%",              "3.751,05",   "3751.05"),
            ("Limite da faixa de 22,5%",            "4.664,68",   "4664.68"),
            ("Parcela a deduzir — 7,5%",            "182,16",     "182.16"),
            ("Parcela a deduzir — 15%",             "394,16",     "394.16"),
            ("Parcela a deduzir — 22,5%",           "675,49",     "675.49"),
            ("Parcela a deduzir — 27,5%",           "908,73",     "908.73"),
            ("Dedução mensal por dependente",       "189,59",     "189.59"),
            ("Desconto simplificado mensal",        "607,20",     "607.20"),
        ],
    },
    {
        "grupo": "Redutor do IR — isenção até R$ 5.000",
        "norma": "Lei nº 15.270/2025",
        "bloqueante": True,
        "urls": [
            "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2025/dezembro/"
            "receita-federal-orienta-fontes-pagadoras-e-contribuintes-a-calcular-a-reducao-"
            "do-imposto-de-renda-a-partir-de-1o-de-janeiro-de-2026",
            "https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/"
            "exemplos-de-aplicacao-da-lei-15-270-2025",
        ],
        "valores": [
            ("Teto da isenção total",               "5.000,00",   "5000.00"),
            ("Teto da redução parcial",             "7.350,00",   "7350.00"),
            ("Redução máxima",                      "312,89",     "312.89"),
            ("Constante da fórmula",                "978,62",     "978.62"),
            ("Coeficiente da fórmula",              "0,133145",   "0.133145"),
        ],
    },
    {
        "grupo": "INSS — faixas de contribuição do segurado",
        "norma": "Portaria Interministerial MPS/MF nº 13, de 09/01/2026",
        "bloqueante": True,
        "urls": [
            "https://www.gov.br/inss/pt-br/direitos-e-deveres/inscricao-e-contribuicao/"
            "tabela-de-contribuicao-mensal",
        ],
        "valores": [
            ("Fim da faixa de 7,5% (salário mínimo)", "1.621,00", "1621.00"),
            ("Fim da faixa de 9%",                    "2.902,84", "2902.84"),
            ("Fim da faixa de 12%",                   "4.354,27", "4354.27"),
            ("Teto do salário de contribuição",       "8.475,55", "8475.55"),
        ],
    },
    {
        "grupo": "Simples Nacional — parcelas a deduzir dos Anexos I a V",
        "norma": "LC nº 123/2006, Anexos I a V",
        "bloqueante": True,
        "urls": [
            "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm",
        ],
        "valores": [
            ("Anexo I — 2ª faixa",     "5.940,00",   "5940.00"),
            ("Anexo I — 3ª faixa",    "13.860,00",  "13860.00"),
            ("Anexo I — 4ª faixa",    "22.500,00",  "22500.00"),
            ("Anexo I — 5ª faixa",    "87.300,00",  "87300.00"),
            ("Anexo I — 6ª faixa",   "378.000,00", "378000.00"),
            ("Anexo II — 5ª faixa",   "85.500,00",  "85500.00"),
            ("Anexo II — 6ª faixa",  "720.000,00", "720000.00"),
            ("Anexo III — 2ª faixa",   "9.360,00",   "9360.00"),
            ("Anexo III — 3ª faixa",  "17.640,00",  "17640.00"),
            ("Anexo III — 4ª faixa",  "35.640,00",  "35640.00"),
            ("Anexo III — 5ª faixa", "125.640,00", "125640.00"),
            ("Anexo III — 6ª faixa", "648.000,00", "648000.00"),
            ("Anexo IV — 2ª faixa",    "8.100,00",   "8100.00"),
            ("Anexo IV — 3ª faixa",   "12.420,00",  "12420.00"),
            ("Anexo IV — 4ª faixa",   "39.780,00",  "39780.00"),
            ("Anexo IV — 5ª faixa",  "183.780,00", "183780.00"),
            ("Anexo IV — 6ª faixa",  "828.000,00", "828000.00"),
            ("Anexo V — 2ª faixa",     "4.500,00",   "4500.00"),
            ("Anexo V — 3ª faixa",     "9.900,00",   "9900.00"),
            ("Anexo V — 4ª faixa",    "17.100,00",  "17100.00"),
            ("Anexo V — 5ª faixa",    "62.100,00",  "62100.00"),
            ("Anexo V — 6ª faixa",   "540.000,00", "540000.00"),
        ],
    },
    {
        "grupo": "Lucro Presumido — majoração de 10% na presunção",
        "norma": "LC nº 224/2025",
        "bloqueante": False,  # informativo: a redação da lei pode não trazer o número literal
        "urls": [
            "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp224.htm",
        ],
        "valores": [
            ("Limite trimestral da majoração", "1.250.000,00", "1250000.00"),
        ],
    },
]


# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ---------------------------------------------------------------------------

def baixar(url):
    """Baixa uma página e devolve o texto limpo, sem as marcações de HTML."""
    pedido = urllib.request.Request(url, headers={
        "User-Agent": NAVEGADOR,
        "Accept": "text/html,application/xhtml+xml,*/*",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })
    contexto = ssl.create_default_context()
    with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE, context=contexto) as resposta:
        bruto = resposta.read()

    for codificacao in ("utf-8", "latin-1"):
        try:
            texto = bruto.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    else:
        texto = bruto.decode("utf-8", errors="ignore")

    texto = re.sub(r"<(script|style)\b.*?</\1>", " ", texto, flags=re.S | re.I)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = _html.unescape(texto)
    texto = texto.replace("\xa0", " ").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", texto)


def contem_numero(texto, valor):
    """Procura o número evitando casar no meio de um número maior.
    Ex.: procurar 4.500,00 não pode casar dentro de 84.500,00."""
    padrao = r"(?<![\d.,])" + re.escape(valor) + r"(?![\d])"
    return re.search(padrao, texto) is not None


def carregar_tabelas_js():
    if not ARQUIVO_TABELAS.exists():
        print("ERRO: nao encontrei o arquivo " + str(ARQUIVO_TABELAS))
        print("Rode este script de dentro da pasta do projeto.")
        sys.exit(2)
    return ARQUIVO_TABELAS.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# PROGRAMA
# ---------------------------------------------------------------------------

def principal():
    print()
    print("=" * 74)
    print(" CONFERENCIA DAS TABELAS OFICIAIS - Calculadoras M Contabilidade")
    print("=" * 74)

    js = carregar_tabelas_js()
    total = ok = falhas = avisos = 0
    falhas_bloqueantes = 0
    pendencias = []

    for bloco in VERIFICACOES:
        print()
        print("-" * 74)
        print(" " + bloco["grupo"])
        print(" Norma: " + bloco["norma"])
        print("-" * 74)

        texto = ""
        erros_site = []
        for url in bloco["urls"]:
            try:
                texto += " " + baixar(url)
                print("   site lido: " + url[:64] + ("..." if len(url) > 64 else ""))
            except (urllib.error.URLError, urllib.error.HTTPError, ssl.SSLError, OSError) as erro:
                erros_site.append(url + "  ->  " + str(erro))

        if not texto.strip():
            avisos += len(bloco["valores"])
            total += len(bloco["valores"])
            print()
            print("   [AVISO] nao consegui abrir nenhum site deste grupo.")
            for e in erros_site:
                print("           " + e)
            print("           Confira estes valores na mao:")
            for descricao, no_site, _ in bloco["valores"]:
                print("           - " + descricao + ": " + no_site)
            pendencias.append(bloco["grupo"] + " (site nao abriu)")
            continue

        print()
        for descricao, no_site, no_js in bloco["valores"]:
            total += 1
            esta_no_js = contem_numero(js, no_js)
            esta_no_site = contem_numero(texto, no_site)

            if esta_no_js and esta_no_site:
                ok += 1
                print("   [OK]    " + descricao.ljust(38) + no_site)
            else:
                falhas += 1
                if bloco["bloqueante"]:
                    falhas_bloqueantes += 1
                motivo = []
                if not esta_no_js:
                    motivo.append("nao achei em js/tabelas.js")
                if not esta_no_site:
                    motivo.append("nao achei na pagina oficial")
                print("   [FALHA] " + descricao.ljust(38) + no_site +
                      "   (" + "; ".join(motivo) + ")")
                pendencias.append(bloco["grupo"] + " -> " + descricao)

        if not bloco["bloqueante"]:
            print()
            print("   Obs.: este grupo e informativo. A lei nem sempre traz o numero")
            print("         escrito por extenso, entao [FALHA] aqui pede leitura na mao,")
            print("         nao significa necessariamente que a tabela esta errada.")

    # ------------------------------ RESUMO ------------------------------
    print()
    print("=" * 74)
    print(" RESUMO: " + str(total) + " conferencias | " + str(ok) + " OK | " +
          str(falhas) + " com divergencia | " + str(avisos) + " sem acesso ao site")
    print("=" * 74)

    if pendencias:
        print()
        print(" Pontos a verificar na mao:")
        for p in pendencias:
            print("   - " + p)

    print()
    if falhas_bloqueantes == 0 and avisos == 0 and falhas == 0:
        print(" TUDO CONFERIDO. Pode publicar a pagina.")
        print()
        print(" Ultimo passo: abra js/tabelas.js e troque")
        print("     conferidoNaFonteOficial: false")
        print(" por")
        print("     conferidoNaFonteOficial: true")
        codigo = 0
    elif falhas_bloqueantes > 0:
        print(" NAO PUBLIQUE AINDA. Ha divergencia em tabela obrigatoria.")
        print(" Abra o site oficial, confira o numero e corrija js/tabelas.js.")
        print(" Depois de corrigir, rode os testes (arquivo testes.html) e este")
        print(" script de novo.")
        codigo = 1
    else:
        print(" Conferencia incompleta. Resolva os pontos acima antes de publicar.")
        codigo = 1

    print()
    return codigo


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except KeyboardInterrupt:
        print("\nInterrompido.")
        sys.exit(130)
