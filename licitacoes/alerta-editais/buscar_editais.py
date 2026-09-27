"""
Alerta de editais para a empresa ativa (modulo de licitacoes, V2).

Le a empresa marcada como "ativa" pelo modulo cadastro-empresas (e os
CNAEs dela), busca no PNCP (Portal Nacional de Contratacoes Publicas -
API publica oficial, sem autenticacao) os editais publicados nos
ultimos dias e avisa por e-mail quais parecem combinar com o ramo da
empresa, pela descricao do CNAE.

O PNCP nao tem filtro por CNAE - a comparacao aqui e por palavra-chave
da descricao do CNAE dentro do objeto da licitacao. E um ponto de
partida (heuristica simples), nao substitui revisar cada edital.
"""
import os
import re
import smtplib
import sqlite3
import sys
import unicodedata
from datetime import date, timedelta
from email.mime.text import MIMEText
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Ajuste estes valores conforme a necessidade do escritorio.
# ---------------------------------------------------------------------------
DIAS_RETROATIVOS = 1          # quantos dias pra tras buscar (1 = so ontem/hoje, pra rodar 1x por dia)
MODALIDADES = [6]             # 6 = Pregao Eletronico. Ver tabela no README pra outros codigos.
UF_FILTRO = ""                # ex: "PE" pra filtrar so por Pernambuco. Vazio = todo o Brasil.
TAMANHO_PAGINA = 50

# Configuracao de e-mail: NAO coloque a senha aqui no codigo. Defina como
# variavel de ambiente antes de rodar (ver README - "Como configurar o
# e-mail"). Se EMAIL_REMETENTE/EMAIL_SENHA_APP nao estiverem definidos, o
# script so mostra o resultado no console, sem tentar enviar.
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.environ.get("EMAIL_SENHA_APP", "")
EMAIL_DESTINATARIO = os.environ.get("EMAIL_DESTINATARIO", EMAIL_REMETENTE)
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_EMPRESAS = BASE_DIR.parent / "cadastro-empresas" / "empresas.db"
PNCP_BASE_URL = "https://pncp.gov.br/api/consulta"

STOPWORDS = {
    # palavras comuns do portugues
    "de", "da", "do", "das", "dos", "em", "e", "ou", "a", "o", "as", "os",
    "com", "para", "por", "na", "no", "nas", "nos", "que", "se", "sem",
    "sob", "sobre", "entre", "ate", "apos", "seus", "suas", "demais",
    # boilerplate tipico de descricao de CNAE - generico demais pra combinar
    "comercio", "atividades", "atividade", "especificadas", "especificada",
    "anteriormente", "outros", "outras", "outro", "outra", "geral", "gerais",
    "diversos", "diversas", "varejista", "varejo", "atacadista", "atacado",
    "nao", "fabricacao", "prestacao", "servicos", "servico", "produtos",
    "produto", "incluidas", "incluido", "relacionados", "relacionadas",
}


def normalizar(texto):
    """Minusculo e sem acento, pra comparar CNAE com objeto da licitacao."""
    texto = (texto or "").lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def extrair_palavras_chave(cnaes):
    palavras = set()
    for cnae in cnaes:
        for palavra in re.findall(r"[a-z]+", normalizar(cnae["descricao"])):
            if len(palavra) >= 5 and palavra not in STOPWORDS:
                palavras.add(palavra)
    return palavras


def carregar_empresa_ativa():
    if not DB_EMPRESAS.exists():
        print("Nao encontrei o banco de empresas. Rode primeiro o modulo")
        print("'cadastro-empresas' (../cadastro-empresas/cadastrar_empresa.py).")
        return None, []
    con = sqlite3.connect(DB_EMPRESAS)
    try:
        row = con.execute("SELECT id, razao_social FROM empresas WHERE ativa = 1").fetchone()
        if not row:
            print("Nenhuma empresa esta marcada como ativa. Abra o cadastro-empresas")
            print("e use a opcao 3 (selecionar empresa ativa) antes de rodar isto.")
            return None, []
        empresa_id, razao_social = row
        cnaes = con.execute(
            "SELECT codigo, descricao FROM cnaes WHERE empresa_id = ?", (empresa_id,)
        ).fetchall()
    finally:
        con.close()
    cnaes = [{"codigo": codigo, "descricao": descricao} for codigo, descricao in cnaes]
    return {"id": empresa_id, "razao_social": razao_social}, cnaes


def buscar_contratacoes(data_inicial, data_final, modalidade, uf=None):
    """Busca paginada no PNCP. Nao autentica - endpoint publico."""
    resultados = []
    pagina = 1
    while True:
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "codigoModalidadeContratacao": modalidade,
            "pagina": pagina,
            "tamanhoPagina": TAMANHO_PAGINA,
        }
        if uf:
            params["uf"] = uf
        resp = requests.get(f"{PNCP_BASE_URL}/v1/contratacoes/publicacao", params=params, timeout=30)
        if resp.status_code == 204:
            break  # PNCP responde 204 (sem corpo) quando nao ha resultado, nao um array vazio
        resp.raise_for_status()
        dados = resp.json()
        resultados.extend(dados.get("data", []))
        if not dados.get("paginasRestantes"):
            break
        pagina += 1
    return resultados


def contratacao_combina(objeto_compra, palavras):
    objeto_norm = normalizar(objeto_compra)
    return sorted(p for p in palavras if p in objeto_norm)


def montar_corpo_email(empresa, encontrados):
    linhas = [f"Licitacoes encontradas para {empresa['razao_social']}:", ""]
    for contratacao, combinou in encontrados:
        orgao = (contratacao.get("orgaoEntidade") or {}).get("razaoSocial", "")
        unidade = contratacao.get("unidadeOrgao") or {}
        local = "/".join(x for x in [unidade.get("municipioNome"), unidade.get("ufSigla")] if x)
        link = contratacao.get("linkSistemaOrigem") or f"(sem link - nº controle PNCP {contratacao.get('numeroControlePNCP')})"
        linhas.append(f"* {orgao} ({local}) - {contratacao.get('modalidadeNome', '')}")
        linhas.append(f"  Objeto: {contratacao.get('objetoCompra')}")
        linhas.append(f"  Combinou com: {', '.join(combinou)}")
        linhas.append(
            f"  Proposta: abertura {contratacao.get('dataAberturaProposta') or '-'} / "
            f"encerramento {contratacao.get('dataEncerramentoProposta') or '-'}"
        )
        linhas.append(f"  Link: {link}")
        linhas.append("")
    linhas.append(
        "Revise cada item antes de decidir participar - o filtro e por palavra-chave "
        "do CNAE, pode trazer falso positivo (ou deixar passar algo)."
    )
    return "\n".join(linhas)


def enviar_email(assunto, corpo):
    if not EMAIL_REMETENTE or not EMAIL_SENHA_APP:
        print("\n(EMAIL_REMETENTE / EMAIL_SENHA_APP nao configurados - nao enviei e-mail,")
        print("so mostrei o resultado aqui no console. Ver README para configurar.)")
        return False
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
            smtp.send_message(msg)
    except smtplib.SMTPException as exc:
        print(f"Falha ao enviar e-mail: {exc}")
        return False
    return True


def main():
    modo_teste = "--teste" in sys.argv

    empresa, cnaes = carregar_empresa_ativa()
    if not empresa:
        return
    if not cnaes:
        print(f"{empresa['razao_social']} nao tem CNAE cadastrado - nada pra comparar.")
        return

    palavras = extrair_palavras_chave(cnaes)
    if not palavras:
        print("Os CNAEs cadastrados so tem termos genericos demais - nao sobrou")
        print("palavra-chave util pra comparar. Acrescente um CNAE mais especifico.")
        return

    hoje = date.today()
    data_final = hoje.strftime("%Y%m%d")
    data_inicial = (hoje - timedelta(days=DIAS_RETROATIVOS)).strftime("%Y%m%d")

    encontrados = []
    vistos = set()
    for modalidade in MODALIDADES:
        try:
            contratacoes = buscar_contratacoes(data_inicial, data_final, modalidade, UF_FILTRO or None)
        except requests.RequestException as exc:
            print(f"Erro consultando o PNCP (modalidade {modalidade}): {exc}")
            continue
        for contratacao in contratacoes:
            numero = contratacao.get("numeroControlePNCP")
            if numero in vistos:
                continue
            combinou = contratacao_combina(contratacao.get("objetoCompra"), palavras)
            if combinou:
                vistos.add(numero)
                encontrados.append((contratacao, combinou))

    print(
        f"\n{len(encontrados)} licitacao(oes) encontradas para {empresa['razao_social']} "
        f"entre {data_inicial} e {data_final}."
    )
    for contratacao, combinou in encontrados:
        print(f"- [{', '.join(combinou)}] {contratacao.get('objetoCompra')}")

    if not encontrados:
        return

    assunto = f"[Licitacoes] {len(encontrados)} edital(is) para {empresa['razao_social']}"
    corpo = montar_corpo_email(empresa, encontrados)

    if modo_teste:
        print("\n--modo teste (--teste): e-mail NAO enviado. Corpo seria:\n")
        print(corpo)
        return

    if enviar_email(assunto, corpo):
        print("\nE-mail enviado.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompido.")
        sys.exit(0)
