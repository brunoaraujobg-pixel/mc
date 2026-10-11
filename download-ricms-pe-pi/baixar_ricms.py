# Baixa, valida e organiza o RICMS-PE e o RICMS-PI a partir das fontes
# oficiais das SEFAZ estaduais (sem resumir ou editar o conteúdo do decreto).
#
# IMPORTANTE (Piauí): o Decreto nº 13.500/2008 foi REVOGADO. O RICMS-PI
# vigente hoje é o Decreto nº 21.866, de 06/03/2023 (vigora desde 08/03/2023).
# Isso foi confirmado por busca à fonte oficial antes de escrever este script
# — não presuma 13.500/2008 como vigente.

import hashlib
import os
import sys
import urllib.request
import urllib.error
from datetime import date

# Ajuste este caminho se sua pasta do acervo for outra.
PASTA_DESTINO = r"C:\PROJETOS\Documento Analista\Credito Tributario"

DOCUMENTOS = [
    {
        "uf": "PE",
        "decreto": "44.650/2017",
        "data_publicacao": "30/06/2017",
        "vigente_desde": "01/10/2017 (art. 3º-A e demais efeitos do novo RICMS)",
        "url_pdf": (
            "https://www.sefaz.pe.gov.br/Legislacao/Tributaria/Documents/"
            "Legislacao/44650/Para%20Download/Regulamento.pdf"
        ),
        "url_referencia": (
            "https://www.sefaz.pe.gov.br/Legislacao/Tributaria/Documents/"
            "Legislacao/44650/Texto/Dec44650_2017.htm"
        ),
        "arquivo_pdf": "RICMS_PE_Decreto_44650_2017.pdf",
        "arquivo_txt": "PE_RICMS_44650_texto_para_busca.txt",
        "observacao": "",
    },
    {
        "uf": "PI",
        "decreto": "21.866/2023",
        "data_publicacao": "06/03/2023",
        "vigente_desde": "08/03/2023",
        "url_pdf": (
            "https://portaldalegislacao.sefaz.pi.gov.br/Arquivos/"
            "ARQUIVOS_CHRONUS/ARQUIVO_PRINCIPAL_LEGISLACAO/1400/"
            "Decreto_n_21.866_2023_-_REGULAMENTO_DO_ICMS_DO_ESTADO_DO_PIAUI.pdf"
        ),
        "url_referencia": "https://webas.sefaz.pi.gov.br/legislacao/ricms-2023/",
        "arquivo_pdf": "RICMS_PI_Decreto_21866_2023.pdf",
        "arquivo_txt": "PI_RICMS_21866_texto_para_busca.txt",
        "observacao": (
            "Revoga o Decreto nº 13.500/2008 (RICMS-PI antigo, vigente até "
            "07/03/2023). Não baixar mais o 13.500/2008 como se fosse o vigente."
        ),
    },
]


def baixar_pdf(url, destino):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (acervo-legal-mc/1.0)"}
    )
    with urllib.request.urlopen(request, timeout=60) as resposta:
        conteudo = resposta.read()
    if not conteudo.startswith(b"%PDF"):
        raise ValueError(
            "o arquivo baixado não começa com a assinatura %PDF — "
            "provavelmente não é um PDF (pode ser uma página de erro/HTML)."
        )
    with open(destino, "wb") as f:
        f.write(conteudo)
    return conteudo


def sha256(caminho):
    if not os.path.exists(caminho):
        return None
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def validar_pdf_integro(caminho):
    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "  [aviso] pacote 'pypdf' não instalado — pulei a validação de "
            "integridade e a extração de texto. Rode: pip install pypdf"
        )
        return None
    leitor = PdfReader(caminho)
    n_paginas = len(leitor.pages)
    if n_paginas == 0:
        raise ValueError("PDF abriu mas não tem nenhuma página — está truncado/corrompido.")
    return leitor


def extrair_texto_para_busca(leitor, caminho_txt):
    # Extrai por página e junta com separador claro, para não cortar artigo
    # no meio (cada página termina em quebra dupla, nunca no meio de uma linha).
    partes = []
    for i, pagina in enumerate(leitor.pages, start=1):
        texto = pagina.extract_text() or ""
        partes.append(f"\n\n===== Página {i} =====\n\n{texto.strip()}")
    conteudo = "".join(partes).strip() + "\n"
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(conteudo)


def atualizar_indice(pasta, linhas_novas):
    caminho_indice = os.path.join(pasta, "INDICE.md")
    cabecalho = (
        "# Índice do acervo — Legislação (RICMS)\n\n"
        "| Arquivo | Decreto | UF | Data de publicação | Vigente desde | "
        "Data do download | URL de origem |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    linhas_existentes = {}
    if os.path.exists(caminho_indice):
        with open(caminho_indice, "r", encoding="utf-8") as f:
            for linha in f:
                if linha.startswith("| ") and not linha.startswith("| Arquivo"):
                    arquivo = linha.split("|")[1].strip()
                    linhas_existentes[arquivo] = linha.rstrip("\n")

    for linha in linhas_novas:
        arquivo = linha.split("|")[1].strip()
        linhas_existentes[arquivo] = linha

    with open(caminho_indice, "w", encoding="utf-8") as f:
        f.write(cabecalho)
        for linha in linhas_existentes.values():
            f.write(linha + "\n")
    return caminho_indice


def processar(doc, pasta):
    print(f"\n--- {doc['uf']}: Decreto {doc['decreto']} ---")
    caminho_pdf = os.path.join(pasta, doc["arquivo_pdf"])
    caminho_txt = os.path.join(pasta, doc["arquivo_txt"])

    hash_antigo = sha256(caminho_pdf)

    print(f"  Baixando de: {doc['url_pdf']}")
    try:
        baixar_pdf(doc["url_pdf"], caminho_pdf + ".novo")
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as erro:
        print(f"  [FALHOU] Não consegui baixar o PDF oficial: {erro}")
        print(f"  Fonte alternativa (Diário Oficial / portal de legislação): {doc['url_referencia']}")
        print("  Pendência registrada — nada foi sobrescrito. Verifique manualmente.")
        return None

    hash_novo = sha256(caminho_pdf + ".novo")
    if hash_antigo is not None and hash_antigo == hash_novo:
        print("  Conteúdo idêntico ao arquivo já existente — mantendo o arquivo atual.")
        os.remove(caminho_pdf + ".novo")
    else:
        if hash_antigo is not None:
            backup = caminho_pdf.replace(".pdf", f"_ANTERIOR_{date.today().isoformat()}.pdf")
            os.replace(caminho_pdf, backup)
            print(f"  Arquivo anterior era diferente — guardado como backup em: {backup}")
        os.replace(caminho_pdf + ".novo", caminho_pdf)
        print(f"  Salvo: {caminho_pdf}")

    try:
        leitor = validar_pdf_integro(caminho_pdf)
    except ValueError as erro:
        print(f"  [FALHOU] Validação de integridade: {erro}")
        return None

    if leitor is not None:
        print(f"  PDF íntegro: {len(leitor.pages)} páginas.")
        extrair_texto_para_busca(leitor, caminho_txt)
        print(f"  Texto de busca gerado: {caminho_txt}")

    if doc["observacao"]:
        print(f"  Observação: {doc['observacao']}")

    linha_indice = (
        f"| {doc['arquivo_pdf']} | {doc['decreto']} | {doc['uf']} | "
        f"{doc['data_publicacao']} | {doc['vigente_desde']} | "
        f"{date.today().isoformat()} | {doc['url_pdf']} |"
    )
    return linha_indice


def main():
    os.makedirs(PASTA_DESTINO, exist_ok=True)
    linhas = []
    for doc in DOCUMENTOS:
        linha = processar(doc, PASTA_DESTINO)
        if linha:
            linhas.append(linha)

    if linhas:
        caminho_indice = atualizar_indice(PASTA_DESTINO, linhas)
        print(f"\nINDICE.md atualizado em: {caminho_indice}")

    pendentes = len(DOCUMENTOS) - len(linhas)
    if pendentes:
        print(f"\n{pendentes} documento(s) com pendência — reveja as mensagens acima.")
    else:
        print("\nTudo baixado, validado e indexado com sucesso.")


if __name__ == "__main__":
    sys.exit(main())
