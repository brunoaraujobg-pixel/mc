"""Conversa com a Shopee Affiliate Open API (GraphQL) - Brasil.

ATENÇÃO: escrito a partir de informações públicas, SEM acesso à documentação
oficial. Se a Shopee reclamar de algum campo, rode `python testar_shopee.py`,
veja a mensagem e ajuste CAMPOS / ORDENACAO_VENDAS abaixo.
"""
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path

from .erros import ErroAgente

URL = "https://open-api.affiliate.shopee.com.br/graphql"
PASTA = Path(__file__).resolve().parent.parent
ORDENACAO_VENDAS = 2  # sortType: mais vendidos (confirmar no explorador da Shopee)
CAMPOS = ("itemId productName priceMin priceMax commissionRate sales ratingStar "
          "shopName offerLink productLink imageUrl")


def credenciais():
    """App ID e Secret: variáveis SHOPEE_APP_ID / SHOPEE_SECRET ou chave_shopee.txt (2 linhas)."""
    app_id = os.environ.get("SHOPEE_APP_ID", "").strip()
    secret = os.environ.get("SHOPEE_SECRET", "").strip()
    arq = PASTA / "chave_shopee.txt"
    if (not app_id or not secret) and arq.exists():
        linhas = [x.strip() for x in arq.read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(linhas) >= 2:
            app_id, secret = linhas[0], linhas[1]
    if not app_id or not secret:
        raise ErroAgente("shopee", "Credenciais da Shopee não encontradas.",
                         "Crie chave_shopee.txt nesta pasta: linha 1 = App ID, linha 2 = Secret "
                         "(painel de afiliados > Open API). Não cole o Secret em chats.")
    return app_id, secret


def assinar(app_id, secret, timestamp, corpo):
    """Assinatura SHA256 de: AppID + timestamp + corpo + Secret."""
    return hashlib.sha256(f"{app_id}{timestamp}{corpo}{secret}".encode("utf-8")).hexdigest()


def consultar(query, app_id=None, secret=None, enviar=None):
    """Envia uma consulta GraphQL. 'enviar' existe só para testes."""
    if app_id is None:
        app_id, secret = credenciais()
    corpo = json.dumps({"query": query}, ensure_ascii=False, separators=(",", ":"))
    ts = str(int(time.time()))
    cabecalhos = {"Content-Type": "application/json",
                  "Authorization": f"SHA256 Credential={app_id}, Timestamp={ts}, "
                                   f"Signature={assinar(app_id, secret, ts, corpo)}"}
    try:
        if enviar:
            resp = enviar(corpo, cabecalhos)
        else:
            req = urllib.request.Request(URL, data=corpo.encode("utf-8"), headers=cabecalhos)
            resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ErroAgente("shopee", f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}",
                         "Confira App ID/Secret e rode python testar_shopee.py")
    except Exception as e:
        raise ErroAgente("shopee", f"Falha de rede/Shopee: {e}", "Confira a internet e tente de novo.")
    if resp.get("errors"):
        raise ErroAgente("shopee", "A Shopee recusou a consulta: " + json.dumps(resp["errors"], ensure_ascii=False)[:400],
                         "Rode python testar_shopee.py e me envie a mensagem para ajustar o código.")
    return resp.get("data", {})


def buscar_ofertas(palavra, limite=20, consulta=consultar):
    q = (f"{{ productOfferV2(keyword: {json.dumps(palavra, ensure_ascii=False)}, "
         f"sortType: {ORDENACAO_VENDAS}, page: 1, limit: {int(limite)}) "
         f"{{ nodes {{ {CAMPOS} }} }} }}")
    return (consulta(q).get("productOfferV2") or {}).get("nodes") or []
