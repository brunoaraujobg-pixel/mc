"""Teste rápido da conexão com a Shopee. Uso:  python testar_shopee.py"""
from modulos.erros import ErroAgente
from modulos.shopee import buscar_ofertas

try:
    nos = buscar_ofertas("balão festa", 3)
except ErroAgente as e:
    print(f"FALHOU [{e.etapa}]: {e.mensagem}\nComo corrigir: {e.como_corrigir}")
    raise SystemExit(1)
print(f"OK! A Shopee devolveu {len(nos)} produtos. Primeiro:")
print(nos[0] if nos else "(lista vazia)")
