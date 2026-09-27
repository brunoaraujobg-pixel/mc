"""
Cadastro de empresas para o modulo de licitacoes.

Voce digita o CNPJ, o script consulta a BrasilAPI (dados abertos da
Receita Federal) para buscar razao social e CNAEs automaticamente, salva
tudo num banco local (SQLite) e deixa marcar qual empresa fica "ativa" -
essa selecao e a base para os proximos modulos (alerta de edital e
consulta de preco por CNAE), que ainda nao existem.
"""
import re
import sqlite3
import sys
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "empresas.db"
BRASILAPI_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"


def conectar():
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnpj TEXT UNIQUE NOT NULL,
            razao_social TEXT,
            nome_fantasia TEXT,
            municipio TEXT,
            uf TEXT,
            ativa INTEGER NOT NULL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS cnaes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL REFERENCES empresas(id),
            codigo TEXT NOT NULL,
            descricao TEXT,
            principal INTEGER NOT NULL DEFAULT 0,
            origem TEXT NOT NULL DEFAULT 'receita'
        )
        """
    )
    return con


def limpar_cnpj(cnpj):
    return re.sub(r"\D", "", cnpj)


def consultar_cnpj(cnpj):
    """Consulta a BrasilAPI (dados abertos da Receita Federal / CNPJ)."""
    resp = requests.get(BRASILAPI_URL.format(cnpj=cnpj), timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def montar_cnaes_da_receita(dados):
    cnaes = []
    cod_principal = dados.get("cnae_fiscal")
    desc_principal = dados.get("cnae_fiscal_descricao")
    if cod_principal:
        cnaes.append(
            {"codigo": str(cod_principal), "descricao": desc_principal or "", "principal": 1, "origem": "receita"}
        )
    for sec in dados.get("cnaes_secundarios") or []:
        codigo = sec.get("codigo") or sec.get("code")
        descricao = sec.get("descricao") or sec.get("text") or sec.get("description")
        if codigo:
            cnaes.append({"codigo": str(codigo), "descricao": descricao or "", "principal": 0, "origem": "receita"})
    return cnaes


def perguntar_cnaes_manuais(cnaes):
    while True:
        add = input("\nAcrescentar outro CNAE manualmente? (codigo ou Enter para pular): ").strip()
        if not add:
            break
        desc = input("Descricao desse CNAE: ").strip()
        cnaes.append({"codigo": add, "descricao": desc, "principal": 0, "origem": "manual"})


def cadastrar_empresa(con):
    cnpj_bruto = input("Digite o CNPJ (com ou sem pontuacao): ").strip()
    cnpj = limpar_cnpj(cnpj_bruto)
    if len(cnpj) != 14:
        print("CNPJ invalido - precisa ter 14 numeros.")
        return

    if con.execute("SELECT id FROM empresas WHERE cnpj = ?", (cnpj,)).fetchone():
        print("Essa empresa ja esta cadastrada.")
        return

    print("Consultando CNAE na Receita Federal (via BrasilAPI)...")
    dados = None
    try:
        dados = consultar_cnpj(cnpj)
    except requests.RequestException as exc:
        print(f"Nao consegui consultar agora ({exc}).")
        print("Pode cadastrar com os dados manuais mesmo assim, ou tentar de novo depois.")

    if dados is None:
        razao_social = input("Digite a razao social manualmente: ").strip()
        nome_fantasia = ""
        municipio = ""
        uf = ""
        cnaes = []
    else:
        razao_social = dados.get("razao_social", "")
        nome_fantasia = dados.get("nome_fantasia") or ""
        municipio = dados.get("municipio") or ""
        uf = dados.get("uf") or ""
        cnaes = montar_cnaes_da_receita(dados)

        print(f"\nEncontrado: {razao_social} ({nome_fantasia or 'sem nome fantasia'}) - {municipio}/{uf}")
        print("CNAEs encontrados:")
        for c in cnaes:
            marca = " (principal)" if c["principal"] else ""
            print(f"  {c['codigo']} - {c['descricao']}{marca}")

    perguntar_cnaes_manuais(cnaes)

    confirmar = input("\nSalvar essa empresa? (S/n): ").strip().lower()
    if confirmar == "n":
        print("Cadastro cancelado.")
        return

    cur = con.execute(
        "INSERT INTO empresas (cnpj, razao_social, nome_fantasia, municipio, uf) VALUES (?, ?, ?, ?, ?)",
        (cnpj, razao_social, nome_fantasia, municipio, uf),
    )
    empresa_id = cur.lastrowid
    for c in cnaes:
        con.execute(
            "INSERT INTO cnaes (empresa_id, codigo, descricao, principal, origem) VALUES (?, ?, ?, ?, ?)",
            (empresa_id, c["codigo"], c["descricao"], c["principal"], c["origem"]),
        )
    con.commit()
    print(f"\nEmpresa '{razao_social}' cadastrada com {len(cnaes)} CNAE(s).")


def listar_empresas(con):
    empresas = con.execute("SELECT id, cnpj, razao_social, ativa FROM empresas ORDER BY razao_social").fetchall()
    if not empresas:
        print("Nenhuma empresa cadastrada ainda.")
        return []
    print("\nEmpresas cadastradas:")
    for empresa_id, cnpj, razao_social, ativa in empresas:
        marca = " <- ATIVA" if ativa else ""
        print(f"  [{empresa_id}] {razao_social} ({cnpj}){marca}")
    return empresas


def selecionar_ativa(con):
    empresas = listar_empresas(con)
    if not empresas:
        return
    ids_validos = {e[0] for e in empresas}
    escolha = input("\nDigite o numero [id] da empresa que fica ativa: ").strip()
    if not escolha.isdigit() or int(escolha) not in ids_validos:
        print("Numero invalido - use um dos ids mostrados entre [ ].")
        return
    con.execute("UPDATE empresas SET ativa = 0")
    con.execute("UPDATE empresas SET ativa = 1 WHERE id = ?", (int(escolha),))
    con.commit()
    print("Empresa ativa atualizada.")


def ver_cnaes_ativa(con):
    empresa = con.execute("SELECT id, razao_social FROM empresas WHERE ativa = 1").fetchone()
    if not empresa:
        print("Nenhuma empresa esta marcada como ativa. Use a opcao 3 primeiro.")
        return
    empresa_id, razao_social = empresa
    print(f"\nCNAEs de {razao_social}:")
    cnaes = con.execute(
        "SELECT codigo, descricao, principal FROM cnaes WHERE empresa_id = ?", (empresa_id,)
    ).fetchall()
    for codigo, descricao, principal in cnaes:
        marca = " (principal)" if principal else ""
        print(f"  {codigo} - {descricao}{marca}")


def menu():
    con = conectar()
    acoes = {
        "1": ("Cadastrar nova empresa (CNPJ -> CNAE automatico)", cadastrar_empresa),
        "2": ("Listar empresas cadastradas", listar_empresas),
        "3": ("Selecionar empresa ativa", selecionar_ativa),
        "4": ("Ver CNAEs da empresa ativa", ver_cnaes_ativa),
    }
    try:
        while True:
            print("\n=== Cadastro de Empresas - Licitacoes ===")
            for chave, (rotulo, _) in acoes.items():
                print(f"  {chave}. {rotulo}")
            print("  0. Sair")
            escolha = input("Escolha: ").strip()
            if escolha == "0":
                break
            acao = acoes.get(escolha)
            if not acao:
                print("Opcao invalida.")
                continue
            acao[1](con)
    finally:
        con.close()


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nSaindo.")
        sys.exit(0)
