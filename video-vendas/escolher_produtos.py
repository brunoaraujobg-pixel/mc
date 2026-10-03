"""Escolhe os produtos mais vendidos de casa e festa e prepara as pastas.

Uso:  python escolher_produtos.py
Cria produtos/<produto>/produto.txt (SEM mídia e com midia_autorizada vazio).
Não baixa imagens da Shopee. Nunca sobrescreve pastas existentes.
"""
import configparser
import csv
import sys
from datetime import date
from pathlib import Path

from modulos import log, notificar
from modulos.erros import ErroAgente
from modulos.ranking import filtrar_e_pontuar, preco_br, slug
from modulos.shopee import buscar_ofertas

RAIZ = Path(__file__).resolve().parent
FILA = RAIZ / "fila"


def ler_vistos():
    arq = FILA / "vistos.txt"
    return set(arq.read_text(encoding="utf-8").split()) if arq.exists() else set()


def escrever_cadastro(pasta, p):
    pasta.mkdir(parents=True)
    # Só fatos que vieram da API da Shopee (nada inventado). Confira o preço antes de postar.
    (pasta / "produto.txt").write_text(
        f"# Fonte: Shopee Affiliate API em {date.today():%d/%m/%Y} (preço pode mudar: confira antes de postar)\n"
        f"# Comissão: {p['comissao'] * 100:.1f}% | Imagem do anúncio (NÃO baixada): {p['imagem']}\n"
        f"nome: {p['nome']}\npreco: {preco_br(p['preco'])}\nlink: {p['link']}\n"
        f"beneficio1: {p['vendas']} vendidos na Shopee\n"
        f"beneficio2: Avaliação {str(p['nota']).replace('.', ',')} de 5\n"
        f"beneficio3: Vendido por {p['loja']}\n"
        f"# Coloque de 3 a 5 fotos/clipes PRÓPRIOS ou autorizados aqui e escreva 'sim' abaixo:\n"
        f"midia_autorizada:\n", encoding="utf-8")


def main():
    cfg = configparser.ConfigParser()
    cfg.read(RAIZ / "config.ini", encoding="utf-8")
    s = cfg["shopee"]
    limites = {"preco_min": s.getfloat("preco_min"), "preco_max": s.getfloat("preco_max"),
               "comissao_min": s.getfloat("comissao_min"), "nota_min": s.getfloat("nota_min"),
               "vendas_min": s.getint("vendas_min")}
    palavras = [x.strip() for x in s["palavras"].split(",") if x.strip()]
    try:
        itens = []
        for palavra in palavras:
            achados = buscar_ofertas(palavra, s.getint("limite_por_palavra"))
            print(f"[shopee] '{palavra}': {len(achados)} produtos")
            itens += achados
        ranking = filtrar_e_pontuar(itens, limites, ler_vistos())
        novos = []
        for p in ranking:
            if len(novos) >= s.getint("quantos"):
                break
            pasta = RAIZ / cfg.get("pastas", "produtos") / slug(p["nome"], p["id"])
            if pasta.exists():
                continue
            escrever_cadastro(pasta, p)
            novos.append((pasta.name, p))
    except ErroAgente as e:
        log.registrar("-", e.etapa, "ERRO " + e.mensagem)
        print(f"\nERRO na etapa [{e.etapa}]: {e.mensagem}\nComo corrigir: {e.como_corrigir}")
        notificar.enviar(cfg, "Erro ao escolher produtos", e.mensagem[:300], prioridade=4, tags="warning")
        return 1

    FILA.mkdir(exist_ok=True)
    with open(FILA / f"ranking_{date.today():%Y-%m-%d}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["pasta", "nome", "preco", "vendas", "nota", "comissao", "pontos", "link"])
        for pasta, p in novos:
            w.writerow([pasta, p["nome"], preco_br(p["preco"]), p["vendas"], p["nota"],
                        f"{p['comissao'] * 100:.1f}%", f"{p['pontos']:.0f}", p["link"]])
    with open(FILA / "vistos.txt", "a", encoding="utf-8") as f:
        f.writelines(p["id"] + "\n" for _, p in novos)
    for pasta, _ in novos:
        log.registrar(pasta, "escolher", "ok cadastro criado, aguardando mídia")
        print(f"  + {pasta}")
    if not novos:
        print("Nenhum produto novo passou nos filtros. Ajuste a seção [shopee] do config.ini.")
    notificar.enviar(cfg, "Produtos escolhidos",
                     f"{len(novos)} novos em produtos/. Coloque a mídia autorizada e marque 'sim'."
                     if novos else "Nenhum produto novo hoje.", tags="shopping_cart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
