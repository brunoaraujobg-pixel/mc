"""Lê e valida a pasta do produto."""
import unicodedata
from pathlib import Path

from .erros import ErroAgente

EXT_FOTO = {".jpg", ".jpeg", ".png"}
EXT_VIDEO = {".mp4", ".mov"}
CAMPOS = ["nome", "preco", "link", "beneficio1", "beneficio2", "beneficio3", "midia_autorizada"]


def _chave(txt):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return txt.strip().lower().replace(" ", "")


def ler_cadastro(arquivo):
    dados = {}
    for linha in Path(arquivo).read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        for sep in (":", "="):
            if sep in linha:
                k, v = linha.split(sep, 1)
                if sep == ":" and v.startswith("//"):  # não deve ocorrer na chave
                    continue
                dados[_chave(k)] = v.strip()
                break
    return dados


def validar_produto(pasta):
    pasta = Path(pasta)
    if not pasta.is_dir():
        raise ErroAgente("validar", f"Pasta não encontrada: {pasta}",
                         "Crie a pasta dentro de 'produtos' e coloque as fotos e o produto.txt.")
    arq = pasta / "produto.txt"
    if not arq.exists():
        raise ErroAgente("validar", f"Falta o arquivo produto.txt em {pasta}",
                         "Copie o modelo de produtos/exemplo/produto.txt e preencha.")
    cad = ler_cadastro(arq)

    faltam = [c for c in CAMPOS if c != "midia_autorizada" and not cad.get(c)]
    if faltam:
        raise ErroAgente("validar", "Campos faltando no produto.txt: " + ", ".join(faltam),
                         "Preencha com dados reais do anúncio (o programa não inventa nada).")
    if cad.get("midia_autorizada", "").strip().lower() != "sim":
        raise ErroAgente("validar", "midia_autorizada não está como 'sim'.",
                         "Escreva 'midia_autorizada: sim' SOMENTE se as fotos/clipes são seus "
                         "ou autorizados pelo fornecedor. Caso contrário, não use este produto.")
    if not cad["link"].lower().startswith("http"):
        raise ErroAgente("validar", "O link do anúncio não começa com http.",
                         "Cole o link completo da Shopee em 'link:'.")

    midias = sorted(p for p in pasta.iterdir()
                    if p.is_file() and p.suffix.lower() in EXT_FOTO | EXT_VIDEO)
    if not 3 <= len(midias) <= 5:
        raise ErroAgente("validar", f"Encontrei {len(midias)} fotos/clipes; o necessário é de 3 a 5.",
                         "Deixe de 3 a 5 arquivos (.jpg, .png, .mp4, .mov) na pasta do produto.")
    return cad, midias
