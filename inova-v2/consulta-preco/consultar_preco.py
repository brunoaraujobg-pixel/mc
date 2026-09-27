"""
Consulta de preco pratcado pelo governo (Inova v2, modulo V3).

Dado um codigo CATMAT (material) ou CATSER (servico), busca no
Compras.gov.br - Dados Abertos (API oficial, publica, sem autenticacao)
o historico de compras publicas homologadas com esse item, e resume
menor/maior/media/mediana de preco unitario pra ajudar a decidir o
valor a ofertar numa licitacao.

Isso e apoio a decisao, nao decide o preco por voce - sempre revise os
registros antes de usar o numero.
"""
import sys
from datetime import date, timedelta

import requests

BASE_URL = "https://dadosabertos.compras.gov.br/modulo-pesquisa-preco"
TAMANHO_PAGINA = 100
JANELA_DIAS = 365  # so considera compras dos ultimos 12 meses, por padrao

ENDPOINTS = {
    "material": "1_consultarMaterial",
    # 'servico' segue o mesmo padrao tipo/codigo do 'material' (confirmado
    # pela documentacao e por codigo real que consome a API), mas eu nao
    # consegui confirmar o nome exato deste endpoint numa chamada real -
    # confira no Swagger (https://dadosabertos.compras.gov.br/swagger-ui/)
    # antes de confiar nele.
    "servico": "3_consultarServico",
}


def buscar_precos(codigo, categoria="material", tipo="codigoItemCatalogo", dias=JANELA_DIAS):
    if categoria not in ENDPOINTS:
        raise ValueError(f"categoria precisa ser 'material' ou 'servico', recebi '{categoria}'")

    hoje = date.today()
    data_inicio = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
    data_fim = hoje.strftime("%Y-%m-%d")

    resultados = []
    pagina = 1
    while True:
        params = {
            "tipo": tipo,
            "codigo": codigo,
            "pagina": pagina,
            "tamanhoPagina": TAMANHO_PAGINA,
            "dataCompraInicio": data_inicio,
            "dataCompraFim": data_fim,
        }
        resp = requests.get(f"{BASE_URL}/{ENDPOINTS[categoria]}", params=params, timeout=30)
        resp.raise_for_status()
        dados = resp.json()
        pagina_resultados = dados.get("resultado") or []
        resultados.extend(pagina_resultados)
        if len(pagina_resultados) < TAMANHO_PAGINA:
            break
        pagina += 1
    return resultados


def resumir_precos(registros):
    precos = sorted(
        r["precoUnitario"] for r in registros if r.get("precoUnitario") not in (None, 0)
    )
    if not precos:
        return None
    n = len(precos)
    meio = n // 2
    mediana = precos[meio] if n % 2 else (precos[meio - 1] + precos[meio]) / 2
    return {
        "quantidade_registros": n,
        "menor_preco": precos[0],
        "maior_preco": precos[-1],
        "media": sum(precos) / n,
        "mediana": mediana,
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python consultar_preco.py <codigo> [material|servico] [codigoItemCatalogo|codigoPdm]")
        print("Exemplo: python consultar_preco.py 443990 material codigoItemCatalogo")
        return

    codigo = sys.argv[1]
    categoria = sys.argv[2] if len(sys.argv) > 2 else "material"
    tipo = sys.argv[3] if len(sys.argv) > 3 else "codigoItemCatalogo"

    print(f"Consultando precos de {categoria} (codigo {codigo}, tipo {tipo}) nos ultimos {JANELA_DIAS} dias...")
    try:
        registros = buscar_precos(codigo, categoria=categoria, tipo=tipo)
    except requests.RequestException as exc:
        print(f"Erro consultando o Compras.gov.br: {exc}")
        return

    print(f"\n{len(registros)} registro(s) de compra encontrados.")
    resumo = resumir_precos(registros)
    if not resumo:
        print("Nenhum preco valido pra resumir (registros sem precoUnitario).")
        return

    print(f"  Menor preco:  R$ {resumo['menor_preco']:.2f}")
    print(f"  Mediana:      R$ {resumo['mediana']:.2f}")
    print(f"  Media:        R$ {resumo['media']:.2f}")
    print(f"  Maior preco:  R$ {resumo['maior_preco']:.2f}")
    print(f"  ({resumo['quantidade_registros']} registro(s) usados no calculo)")

    print("\nUltimas compras encontradas (revise antes de usar):")
    for r in registros[:10]:
        preco = r.get("precoUnitario")
        preco_fmt = f"R$ {preco:.2f}" if preco else "-"
        print(
            f"  {r.get('dataCompra', '-')} | {r.get('nomeUasg', '-')} | "
            f"{preco_fmt} | qtd {r.get('quantidade', '-')} | fornecedor {r.get('niFornecedor', '-')}"
        )
    print(
        "\nIsso e referencia de preco praticado, nao decide o valor por voce - "
        "considere seu custo e margem antes de ofertar."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompido.")
        sys.exit(0)
