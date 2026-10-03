"""Filtra e pontua os produtos devolvidos pela Shopee."""
import re
import unicodedata


def _num(v, padrao=0.0):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return padrao


def preco_br(v):
    return f"{_num(v):.2f}".replace(".", ",")


def slug(nome, item_id):
    t = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:40].strip("-")
    return f"{t}-{str(item_id)[-5:]}"


def normalizar(no):
    """Converte um item da API em dicionário simples (ou None se faltar o essencial)."""
    link = no.get("offerLink")
    nome = (no.get("productName") or "").strip()
    preco = _num(no.get("priceMin")) or _num(no.get("price"))
    if not (link and nome and preco and no.get("itemId")):
        return None
    return {"id": str(no["itemId"]), "nome": nome, "preco": preco, "link": link,
            "comissao": _num(no.get("commissionRate")), "vendas": int(_num(no.get("sales"))),
            "nota": _num(no.get("ratingStar")), "loja": (no.get("shopName") or "").strip(),
            "imagem": no.get("imageUrl", "")}


def filtrar_e_pontuar(itens, cfg, vistos=()):
    """cfg: dict com preco_min, preco_max, comissao_min, nota_min, vendas_min.
    Pontuação = vendas x (preço x comissão): volume x ganho por venda."""
    vistos, unicos = set(vistos), {}
    for no in itens:
        p = normalizar(no)
        if not p or p["id"] in vistos or p["id"] in unicos:
            continue
        if not (cfg["preco_min"] <= p["preco"] <= cfg["preco_max"]):
            continue
        if p["comissao"] < cfg["comissao_min"] or p["nota"] < cfg["nota_min"] or p["vendas"] < cfg["vendas_min"]:
            continue
        if not p["loja"]:  # precisamos de 3 fatos reais para o cadastro
            continue
        p["pontos"] = p["vendas"] * p["preco"] * p["comissao"]
        unicos[p["id"]] = p
    return sorted(unicos.values(), key=lambda x: x["pontos"], reverse=True)
