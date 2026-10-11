"""Baixa videos do Instagram usando o Instaloader.

Uso so para estudo/uso pessoal: os arquivos ficam apenas no seu PC,
na pasta "videos_baixados" (ao lado deste script).

Como usar:
    1. Coloque os links (um por linha) no arquivo links.txt
    2. python baixar_videos.py
    Ou passe os links direto:
    python baixar_videos.py "https://www.instagram.com/reel/XXXX/"

Tambem baixa todos os videos de um perfil:
    python baixar_videos.py --perfil nome_do_perfil

Se o Instagram pedir login (uma vez so):
    instaloader --login SEU_USUARIO
    python baixar_videos.py --usuario SEU_USUARIO
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import instaloader
except ImportError:
    sys.exit("Instaloader nao instalado. Rode: pip install -r requirements.txt")

PASTA_SCRIPT = Path(__file__).resolve().parent
PASTA_VIDEOS = PASTA_SCRIPT / "videos_baixados"
ARQUIVO_LINKS = PASTA_SCRIPT / "links.txt"
ARQUIVO_HISTORICO = PASTA_SCRIPT / "historico.txt"

# pega o codigo do post em /p/CODIGO/, /reel/CODIGO/ ou /tv/CODIGO/
PADRAO_LINK = re.compile(r"instagram\.com/(?:[\w.]+/)?(?:p|reel|reels|tv)/([\w-]+)")


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


def criar_loader():
    """So videos: sem fotos, sem comentarios, sem arquivos extras."""
    return instaloader.Instaloader(
        dirname_pattern=str(PASTA_VIDEOS / "{target}"),
        filename_pattern="{date_utc:%Y-%m-%d}_{shortcode}",
        download_pictures=False,
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        post_metadata_txt_pattern="{caption}",  # salva a legenda em .txt
    )


def baixar_links(loader, links):
    historico = ler_historico()
    ok, falhas = 0, []
    for link in links:
        if link in historico:
            print(f"[pulado] ja baixado antes: {link}")
            continue
        achou = PADRAO_LINK.search(link)
        if not achou:
            print(f"[erro] link nao reconhecido: {link}")
            falhas.append(link)
            continue
        try:
            post = instaloader.Post.from_shortcode(loader.context, achou.group(1))
            loader.download_post(post, target=post.owner_username)
        except Exception as erro:  # um link com erro nao para os outros
            print(f"[erro] {link}\n       {erro}")
            falhas.append(link)
            continue
        ok += 1
        with ARQUIVO_HISTORICO.open("a", encoding="utf-8") as f:
            f.write(link + "\n")
    return ok, falhas


def baixar_perfil(loader, nome):
    perfil = instaloader.Profile.from_username(loader.context, nome)
    ok = 0
    for post in perfil.get_posts():
        if not post.is_video:
            continue
        loader.download_post(post, target=nome)
        ok += 1
    return ok, []


def main():
    parser = argparse.ArgumentParser(description="Baixa videos do Instagram.")
    parser.add_argument("links", nargs="*", help="links dos videos/reels")
    parser.add_argument("--perfil", help="baixa todos os videos deste perfil")
    parser.add_argument(
        "--usuario",
        help="seu usuario do Instagram (depois de rodar: instaloader --login USUARIO)",
    )
    args = parser.parse_args()

    PASTA_VIDEOS.mkdir(exist_ok=True)
    loader = criar_loader()
    if args.usuario:
        loader.load_session_from_file(args.usuario)

    if args.perfil:
        ok, falhas = baixar_perfil(loader, args.perfil)
    else:
        links = ler_links(args.links)
        if not links:
            sys.exit("Nenhum link. Coloque em links.txt ou passe na linha de comando.")
        ok, falhas = baixar_links(loader, links)

    print(f"\nBaixados: {ok} | Com erro: {len(falhas)}")
    print(f"Pasta: {PASTA_VIDEOS}")
    for link in falhas:
        print(f"  falhou: {link}")


if __name__ == "__main__":
    main()
