"""Baixa videos (Instagram e outros sites) usando o yt-dlp.

Uso so para estudo/uso pessoal: os arquivos ficam apenas no seu PC,
na pasta "videos_baixados" (ao lado deste script).

Como usar:
    1. Coloque os links (um por linha) no arquivo links.txt
    2. python baixar_videos.py
    Ou passe os links direto:
    python baixar_videos.py "https://www.instagram.com/reel/XXXX/"

Se o Instagram pedir login, use o navegador onde voce ja esta logado:
    python baixar_videos.py --navegador chrome
"""

import argparse
import sys
from pathlib import Path

try:
    from yt_dlp import YoutubeDL
except ImportError:
    sys.exit("yt-dlp nao instalado. Rode: pip install -r requirements.txt")

PASTA_SCRIPT = Path(__file__).resolve().parent
PASTA_VIDEOS = PASTA_SCRIPT / "videos_baixados"
ARQUIVO_LINKS = PASTA_SCRIPT / "links.txt"
ARQUIVO_HISTORICO = PASTA_SCRIPT / "historico.txt"


def ler_links(argumentos):
    """Links vindos da linha de comando ou, se nao houver, do links.txt."""
    if argumentos:
        return argumentos
    if not ARQUIVO_LINKS.exists():
        return []
    linhas = ARQUIVO_LINKS.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in linhas if l.strip() and not l.startswith("#")]


def ler_historico():
    if not ARQUIVO_HISTORICO.exists():
        return set()
    return set(ARQUIVO_HISTORICO.read_text(encoding="utf-8").split())


def main():
    parser = argparse.ArgumentParser(description="Baixa videos para estudo.")
    parser.add_argument("links", nargs="*", help="links dos videos")
    parser.add_argument(
        "--navegador",
        help="usa o login deste navegador (chrome, edge, firefox...)",
    )
    args = parser.parse_args()

    links = ler_links(args.links)
    if not links:
        sys.exit("Nenhum link. Coloque em links.txt ou passe na linha de comando.")

    PASTA_VIDEOS.mkdir(exist_ok=True)
    historico = ler_historico()

    opcoes = {
        "outtmpl": str(PASTA_VIDEOS / "%(uploader)s - %(title).80s [%(id)s].%(ext)s"),
        "restrictfilenames": False,
        "ignoreerrors": False,
        "noplaylist": True,
    }
    if args.navegador:
        opcoes["cookiesfrombrowser"] = (args.navegador,)

    ok, falhas = 0, []
    with YoutubeDL(opcoes) as ydl:
        for link in links:
            if link in historico:
                print(f"[pulado] ja baixado antes: {link}")
                continue
            try:
                ydl.download([link])
            except Exception as erro:  # um link com erro nao para os outros
                print(f"[erro] {link}\n       {erro}")
                falhas.append(link)
                continue
            ok += 1
            with ARQUIVO_HISTORICO.open("a", encoding="utf-8") as f:
                f.write(link + "\n")

    print(f"\nBaixados: {ok} | Com erro: {len(falhas)}")
    print(f"Pasta: {PASTA_VIDEOS}")
    for link in falhas:
        print(f"  falhou: {link}")


if __name__ == "__main__":
    main()
