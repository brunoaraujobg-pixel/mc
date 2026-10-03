"""Gera título, legenda e hashtags e BLOQUEIA dados que não estão no cadastro."""
import json
import os
import re
from pathlib import Path

from .erros import ErroAgente

PASTA = Path(__file__).resolve().parent.parent
# Termos que viram promessa/alegação. Só passam se já estiverem no cadastro.
TERMOS_PROIBIDOS = ["garantia", "garantid", "100%", "melhor", "milagr", "cura", "frete", "original",
                    "promoção", "promocao", "desconto", "oferta", "estoque", "últimas", "ultimas",
                    "grátis", "gratis", "resistente", "impermeável", "impermeavel", "anvisa",
                    "aprovado", "certificad", "sem risco"]

PROMPT = """Você escreve textos de venda curtos em português do Brasil para TikTok e Shopee Vídeo.
REGRAS OBRIGATÓRIAS:
- Use SOMENTE os dados do cadastro abaixo. Não invente preço, medidas, material, garantia, desconto, frete, estoque nem qualquer promessa.
- Não use números que não estejam no cadastro.
- Tom simples e honesto, sem exageros ("o melhor", "milagre", "100%" são proibidos).
- Não escreva o link (ele é adicionado depois).
Responda APENAS com JSON neste formato:
{"titulo": "até 80 caracteres", "legenda": "até 250 caracteres", "hashtags": ["#exemplo", "... de 5 a 8"]}

CADASTRO:
"""


def _numeros(txt):
    return {m.replace(",", ".") for m in re.findall(r"\d+(?:[.,]\d+)?", txt)}


def verificar_texto(texto, cadastro):
    """Retorna lista de problemas (vazia = texto aprovado)."""
    base = " ".join(cadastro.values()).lower()
    problemas = []
    extras = _numeros(texto) - _numeros(base)
    if extras:
        problemas.append("números que não estão no cadastro: " + ", ".join(sorted(extras)))
    for t in TERMOS_PROIBIDOS:
        if t in texto.lower() and t not in base:
            problemas.append(f"termo/promessa não presente no cadastro: '{t}'")
    return problemas


def _chave_api():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    arq = PASTA / "chave_anthropic.txt"
    if not k and arq.exists():
        k = arq.read_text(encoding="utf-8").strip()
    return k


def _limpar_hashtags(lista):
    saida = []
    for h in lista:
        h = "#" + re.sub(r"[^\w]", "", str(h).lstrip("#"))
        if len(h) > 1 and h.lower() not in [x.lower() for x in saida]:
            saida.append(h)
    return saida[:8]


def _texto_fixo(cad):
    return {"titulo": cad["nome"],
            "legenda": f"{cad['nome']}: {cad['beneficio1']}. {cad['beneficio2']}. {cad['beneficio3']}.",
            "hashtags": ["#shopee", "#achadinhos", "#tiktokshop"]}


def _pedir_ia(cad, modelo, problemas_anteriores):
    chave = _chave_api()
    if not chave:
        raise ErroAgente("texto-ia", "Chave da API do Claude não encontrada.",
                         "Crie o arquivo chave_anthropic.txt nesta pasta com a chave dentro "
                         "(veja README, passo 4) ou use usar_ia = nao no config.ini.")
    try:
        import anthropic
    except ImportError:
        raise ErroAgente("texto-ia", "Biblioteca 'anthropic' não instalada.",
                         "Rode: pip install -r requirements.txt")
    pedido = PROMPT + json.dumps(cad, ensure_ascii=False, indent=1)
    if problemas_anteriores:
        pedido += "\n\nA versão anterior foi REPROVADA por: " + "; ".join(problemas_anteriores) + ". Corrija."
    try:
        r = anthropic.Anthropic(api_key=chave).messages.create(
            model=modelo, max_tokens=600, messages=[{"role": "user", "content": pedido}])
    except Exception as e:
        raise ErroAgente("texto-ia", f"Falha ao chamar a IA: {e}",
                         "Confira a chave, o saldo da conta Anthropic e a internet.")
    bruto = r.content[0].text
    m = re.search(r"\{.*\}", bruto, re.S)
    if not m:
        raise ErroAgente("texto-ia", "A IA não devolveu JSON válido.", "Rode novamente.")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        raise ErroAgente("texto-ia", "A IA devolveu JSON quebrado.", "Rode novamente.")


def gerar_texto(cad, config, pedir=_pedir_ia):
    """Retorna dict titulo/legenda/hashtags aprovado pela checagem automática."""
    campos = {k: v for k, v in cad.items() if k not in ("link", "midia_autorizada")}
    if config.get("texto", "usar_ia", fallback="sim").strip().lower() != "sim":
        dados = _texto_fixo(cad)
    else:
        modelo = config.get("texto", "modelo", fallback="claude-haiku-4-5-20251001")
        problemas = []
        dados = None
        for _ in range(3):  # tenta até 3 vezes, devolvendo os problemas para a IA
            d = pedir(campos, modelo, problemas)
            d["hashtags"] = _limpar_hashtags(d.get("hashtags", []))
            texto = f"{d.get('titulo', '')} {d.get('legenda', '')} {' '.join(d['hashtags'])}"
            problemas = verificar_texto(texto, campos)
            if not d.get("titulo") or not d.get("legenda"):
                problemas.append("faltou título ou legenda")
            if not problemas:
                dados = d
                break
        if dados is None:
            raise ErroAgente("texto-ia", "O texto gerado ficou reprovado 3 vezes: " + "; ".join(problemas),
                             "Confira se o produto.txt está claro e tente de novo, ou use usar_ia = nao.")
    return dados
