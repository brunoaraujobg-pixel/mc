"""
Analisa o cadastro de produtos (exportação do estoque em CSV ';') e aponta
o que está errado ou faltando para uma empresa do LUCRO PRESUMIDO,
incluindo a parametrização do IBS/CBS (cClassTrib).

Uso:
    python analisar_estoque.py estoque26.csv

Gera, na mesma pasta do CSV:
    <nome>_relatorio.csv   -> uma linha por problema encontrado (abre no Excel)
    <nome>_resumo.txt      -> totais por regra
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

N_COLUNAS = 24  # quantidade de colunas do layout (incluindo a vazia do final)

# --- Parâmetros do Lucro Presumido (PIS/COFINS cumulativo) -----------------
ALIQ_PIS_PRESUMIDO = "0,65"
ALIQ_COFINS_PRESUMIDO = "3"
CST_ENTRADA_COM_CREDITO = {"50", "51", "52", "53", "54", "55", "56"}
CST_PIS_VALIDOS = {"01", "02", "03", "04", "05", "06", "07", "08", "09", "49",
                   "50", "51", "52", "53", "54", "55", "56", "60", "61", "62",
                   "63", "64", "65", "66", "67", "70", "71", "72", "73", "74",
                   "75", "98", "99"}
CST_EXIGE_NATUREZA = {"04", "05", "06", "07", "08", "09"}

# --- ICMS --------------------------------------------------------------------
CFOP_SAIDA_ST = {"5405", "5403", "6404", "6403"}
CFOP_SAIDA_TRIBUTADA = {"5102", "6102"}

# --- IBS/CBS -----------------------------------------------------------------
# Anexo VIII da LC 214/2025 (higiene pessoal e limpeza - redução de 60%)
ANEXO_VIII = {
    "34011190": "sabões de toucador",
    "34011900": "sabões em barra",
    "33061000": "dentifrícios",
    "96032100": "escovas de dentes",
    "48181000": "papel higiênico",
    "28289011": "água sanitária",
    "96190000": "fraldas / absorventes",
}
CCLASS_HIGIENE = "200035"
CCLASS_AGRO = "200038"
PREFIXOS_AGRO = ("3808", "31")  # defensivos e fertilizantes (Anexo IX, com condições)

# NCMs que costumam ter PIS/COFINS monofásico e merecem conferência
PREFIXOS_MONOFASICO = {
    "2710": "combustíveis/lubrificantes (Lei 9.718 / Lei 10.865)",
    "3303": "perfumaria/higiene (Lei 10.147)", "3304": "perfumaria/higiene (Lei 10.147)",
    "3305": "perfumaria/higiene (Lei 10.147)", "3306": "perfumaria/higiene (Lei 10.147)",
    "3307": "perfumaria/higiene (Lei 10.147)",
    "4011": "pneus (Lei 10.485)", "4013": "câmaras de ar (Lei 10.485)",
    "8701": "veículos (Lei 10.485)", "8702": "veículos (Lei 10.485)",
    "8703": "veículos (Lei 10.485)", "8704": "veículos (Lei 10.485)",
}


def ler_csv(caminho):
    """Lê o CSV (Latin-1). Corrige linhas em que o NOME tinha ';' e 'quebrou' as colunas."""
    linhas_corrigidas = []
    with open(caminho, encoding="latin-1", newline="") as f:
        leitor = csv.reader(f, delimiter=";")
        cab = next(leitor)
        for campos in leitor:
            corrigida = False
            if len(campos) > N_COLUNAS:
                extra = len(campos) - N_COLUNAS
                campos = campos[:2] + [",".join(campos[2:3 + extra])] + campos[3 + extra:]
                corrigida = True
            reg = dict(zip(cab, campos))
            reg["_linha_quebrada"] = corrigida
            linhas_corrigidas.append(reg)
    return linhas_corrigidas


def analisar(produtos):
    problemas = []

    def add(p, grav, regra, msg, sugestao=""):
        problemas.append({
            "ID": p["ID"], "CODIGO": p["CODIGO"], "NOME": p["NOME"].strip(),
            "NCM": p["CODIGONCM"], "GRAVIDADE": grav, "AREA": regra.split(" ")[0],
            "REGRA": regra, "PROBLEMA": msg, "SUGESTAO": sugestao,
        })

    # CST PIS de saída por NCM (para achar NCM igual com tratamento diferente)
    cst_por_ncm = defaultdict(Counter)
    for p in produtos:
        if p["CSTPISSAIDA"] in CST_PIS_VALIDOS:  # CST inválido já é apontado à parte
            cst_por_ncm[p["CODIGONCM"]][p["CSTPISSAIDA"]] += 1

    for p in produtos:
        ncm = p["CODIGONCM"]
        cst = p["CST"]
        cclass = p["CCLASSTRIB"].strip()

        if p["_linha_quebrada"]:
            add(p, "AVISO", "CADASTRO nome com ';'",
                "O NOME contém ';' e desalinha as colunas na exportação.",
                "Trocar ';' por ',' no nome do produto.")

        # ---------------- PIS/COFINS (Presumido = cumulativo) ----------------
        for campo in ("CSTPISENTRADA", "CSTPISSAIDA", "CSTCOFINSENTRADA", "CSTCOFINSSAIDA"):
            if p[campo] not in CST_PIS_VALIDOS:
                add(p, "ERRO", "PIS/COFINS CST inválido",
                    f"{campo} = '{p[campo]}' não existe na tabela de CST de PIS/COFINS.",
                    "Saída: 01 (ou 04 se monofásico). Entrada: 70.")

        if p["CSTPISENTRADA"] in CST_ENTRADA_COM_CREDITO or p["CSTCOFINSENTRADA"] in CST_ENTRADA_COM_CREDITO:
            add(p, "ERRO", "PIS/COFINS entrada com crédito",
                f"CST entrada {p['CSTPISENTRADA']}/{p['CSTCOFINSENTRADA']} = direito a crédito "
                "(não cumulativo). Presumido não toma crédito.",
                "CST entrada 70 (aquisição sem direito a crédito), crédito 0.")

        if p["PISCREDITO"] not in ("0", "", "0,00") or p["COFINSCREDITO"] not in ("0", "", "0,00"):
            add(p, "ERRO", "PIS/COFINS alíquota de crédito",
                f"Crédito PIS {p['PISCREDITO']} / COFINS {p['COFINSCREDITO']}.",
                "Zerar alíquotas de crédito.")

        if p["CSTPISSAIDA"] == "01" and (p["PISDEBITO"] != ALIQ_PIS_PRESUMIDO
                                         or p["COFINSDEBITO"] != ALIQ_COFINS_PRESUMIDO):
            add(p, "ERRO", "PIS/COFINS alíquota de débito",
                f"Débito PIS {p['PISDEBITO']} / COFINS {p['COFINSDEBITO']} "
                "(1,65/7,6 é Lucro Real não cumulativo).",
                "PIS 0,65 / COFINS 3,00.")

        if p["CSTPISSAIDA"] in CST_EXIGE_NATUREZA and p["NATRECEITAPISCOFINS"].strip() in ("", "000"):
            add(p, "ERRO", "PIS/COFINS natureza da receita",
                f"CST {p['CSTPISSAIDA']} sem Natureza da Receita (obrigatória na EFD-Contribuições).",
                "Informar o código da tabela 4.3.10 (monofásico) conforme o NCM.")

        if len(cst_por_ncm[ncm]) > 1:
            add(p, "ERRO", "PIS/COFINS NCM com CST divergente",
                f"Mesmo NCM {ncm} tem CST de saída diferentes: {dict(cst_por_ncm[ncm])}.",
                "Padronizar: definir se o NCM é monofásico (04) ou tributado (01).")

        for pref, lei in PREFIXOS_MONOFASICO.items():
            if ncm.startswith(pref) and p["CSTPISSAIDA"] == "01":
                add(p, "VERIFICAR", "PIS/COFINS possível monofásico",
                    f"NCM {ncm} está em grupo com incidência monofásica: {lei}.",
                    "Confirmar na lei/tabela 4.3.10; se monofásico, CST 04 + natureza da receita.")
                break

        # ---------------- ICMS -----------------------------------------------
        if cst == "060" and not p["CEST"].strip():
            add(p, "ERRO", "ICMS ST sem CEST",
                "CST 060 (ST) sem CEST.", "Informar CEST (Conv. ICMS 142/18).")
        if cst == "060" and p["CFOPSI"] in CFOP_SAIDA_TRIBUTADA:
            add(p, "ERRO", "ICMS CST x CFOP", f"CST 060 com CFOP {p['CFOPSI']}.", "Usar 5405.")
        if cst == "000" and p["CFOPSI"] in CFOP_SAIDA_ST:
            add(p, "ERRO", "ICMS CST x CFOP", f"CST 000 com CFOP {p['CFOPSI']}.", "Usar 5102.")
        if cst == "000" and p["ALIQECF"] != "2050":
            add(p, "VERIFICAR", "ICMS alíquota",
                f"CST 000 com alíquota {p['ALIQECF']} (interna PE = 20,5%).", "Conferir.")
        if cst in ("010", "020", "030", "070", "090"):
            add(p, "VERIFICAR", "ICMS CST incomum no varejo",
                f"CST {cst}: 010 = a empresa é a substituta (retém ST na venda). "
                "No varejo que compra com ST retida o normal é 060.",
                "Conferir se a compra vem com ST retida (060) ou se a empresa é substituta.")
        for campo in ("CFOPEI", "CFOPEE", "CFOPSI", "CFOPSE"):
            if not p[campo].strip():
                add(p, "ERRO", "ICMS CFOP vazio", f"{campo} vazio.", "Preencher o CFOP.")

        # ---------------- IBS / CBS ------------------------------------------
        if not cclass:
            add(p, "ERRO", "IBS/CBS cClassTrib vazio",
                "Produto sem cClassTrib: a NF-e será rejeitada (regra UB12-10 / rej. 1115).",
                "Informar cClassTrib (padrão 000001).")
            continue
        if len(cclass) != 6 or not cclass.isdigit():
            add(p, "ERRO", "IBS/CBS cClassTrib inválido",
                f"cClassTrib '{cclass}' não tem 6 dígitos.", "Corrigir.")
            continue

        if cclass == CCLASS_HIGIENE and ncm not in ANEXO_VIII:
            add(p, "ERRO", "IBS/CBS redução indevida",
                f"cClassTrib 200035 (Anexo VIII, redução 60%) em NCM {ncm} fora do Anexo VIII.",
                "Usar 000001.")
        if ncm in ANEXO_VIII and cclass != CCLASS_HIGIENE:
            add(p, "VERIFICAR", "IBS/CBS redução não aplicada",
                f"NCM {ncm} ({ANEXO_VIII[ncm]}) está no Anexo VIII, mas cClassTrib = {cclass}.",
                "Se o produto for mesmo isso, usar 200035; se não for, o NCM está errado.")
        if ncm in ANEXO_VIII and cclass == CCLASS_HIGIENE:
            add(p, "VERIFICAR", "IBS/CBS conferir descrição",
                f"NCM {ncm} deve ser '{ANEXO_VIII[ncm]}'. Confira se o produto é isso mesmo.",
                "Se não for, o NCM está errado (e a redução é indevida).")
        if ncm.startswith(PREFIXOS_AGRO):
            add(p, "VERIFICAR", "IBS/CBS insumo agropecuário",
                f"NCM {ncm} pode ter redução de 60% (Anexo IX, cClassTrib 200038) só se for "
                "insumo agropecuário registrado no MAPA. Uso doméstico (ANVISA) não tem. "
                f"Hoje: {cclass}.",
                "Conferir registro MAPA na embalagem.")

    return problemas


def main():
    if len(sys.argv) < 2:
        print("Uso: python analisar_estoque.py <arquivo.csv>")
        sys.exit(1)
    origem = Path(sys.argv[1])
    produtos = ler_csv(origem)
    problemas = analisar(produtos)

    rel = origem.with_name(origem.stem + "_relatorio.csv")
    with open(rel, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(problemas[0].keys()) if problemas else ["ID"],
                           delimiter=";")
        w.writeheader()
        w.writerows(problemas)

    por_regra = Counter((x["GRAVIDADE"], x["REGRA"]) for x in problemas)
    prod_por_regra = defaultdict(set)
    for x in problemas:
        prod_por_regra[(x["GRAVIDADE"], x["REGRA"])].add(x["ID"])
    cclass = Counter(p["CCLASSTRIB"].strip() or "(vazio)" for p in produtos)

    linhas = [f"Arquivo: {origem.name}", f"Produtos: {len(produtos)}",
              f"Problemas: {len(problemas)}", "",
              "cClassTrib usados (CST IBS/CBS = 3 primeiros dígitos):"]
    linhas += [f"  {k}: {v}" for k, v in cclass.most_common()]
    linhas += ["", "Produtos afetados por regra:"]
    ordem = {"ERRO": 0, "VERIFICAR": 1, "AVISO": 2}
    for (g, r) in sorted(prod_por_regra, key=lambda k: (ordem[k[0]], -len(prod_por_regra[k]))):
        linhas.append(f"  [{g:9}] {r:40} {len(prod_por_regra[(g, r)]):>6}")
    res = origem.with_name(origem.stem + "_resumo.txt")
    res.write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas))
    print(f"\nRelatório: {rel}\nResumo:    {res}")


if __name__ == "__main__":
    main()
