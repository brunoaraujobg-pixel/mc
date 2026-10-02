"""Agente Vídeo Vendas - V1.  Uso:  python video_vendas.py <nome-da-pasta-do-produto>"""
import configparser
import sys
from pathlib import Path

from modulos import log, notificar
from modulos.erros import ErroAgente
from modulos.texto_ia import gerar_texto
from modulos.validar import validar_produto
from modulos.video import montar_video, verificar_video

RAIZ = Path(__file__).resolve().parent


def proxima_versao(pasta_saida):
    """Nunca sobrescreve: video.mp4, video_2.mp4, video_3.mp4..."""
    n = 1
    while True:
        suf = "" if n == 1 else f"_{n}"
        v, t = pasta_saida / f"video{suf}.mp4", pasta_saida / f"postagem{suf}.txt"
        if not v.exists() and not t.exists():
            return v, t
        n += 1


def escrever_postagem(arquivo, dados, link):
    tags = " ".join(dados["hashtags"])
    arquivo.write_text(
        f"TÍTULO:\n{dados['titulo']}\n\nLEGENDA:\n{dados['legenda']}\n\nHASHTAGS:\n{tags}\n\n"
        f"LINK DO ANÚNCIO:\n{link}\n\n"
        f"----- TEXTO PRONTO PARA COLAR -----\n{dados['legenda']}\n\n{tags}\n\n{link}\n",
        encoding="utf-8")


def principal(produto, config):
    pasta_prod = RAIZ / config.get("pastas", "produtos") / produto
    pasta_saida = RAIZ / config.get("pastas", "saida") / produto
    pasta_mus = RAIZ / config.get("pastas", "musicas")

    def etapa(nome, msg=""):
        print(f"[{nome}] {msg}")
        log.registrar(produto, nome, "ok " + msg if msg else "ok")

    print(f"\n== Vídeo Vendas: {produto} ==")
    cad, midias = validar_produto(pasta_prod)
    etapa("validar", f"{len(midias)} mídias, cadastro completo")

    destino_video, destino_txt = proxima_versao(pasta_saida)
    musica = montar_video(midias, cad, config, pasta_mus, destino_video)
    etapa("video", f"{destino_video.name} (música: {musica.name if musica else 'nenhuma'})")

    w, h, dur = verificar_video(destino_video)
    etapa("validar-video", f"{w}x{h}, {dur:.1f}s")

    dados = gerar_texto(cad, config)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    escrever_postagem(destino_txt, dados, cad["link"])
    if cad["link"] not in destino_txt.read_text(encoding="utf-8"):
        raise ErroAgente("validar-texto", "Link ausente no texto final.", "Erro interno; avise o suporte.")
    etapa("texto", destino_txt.name)

    notificar.enviar(config, "Vídeo pronto", f"{produto}: {destino_video.name} em saida/{produto}/",
                     tags="white_check_mark")
    print(f"\nPRONTO! Veja a pasta: {pasta_saida}")
    return 0


def main():
    config = configparser.ConfigParser()
    config.read(RAIZ / "config.ini", encoding="utf-8")
    if len(sys.argv) != 2:
        pasta = RAIZ / config.get("pastas", "produtos")
        print("Uso: python video_vendas.py <pasta-do-produto>\nProdutos disponíveis:")
        for p in sorted(pasta.iterdir()) if pasta.exists() else []:
            if p.is_dir():
                print("  -", p.name)
        return 1
    produto = sys.argv[1]
    try:
        return principal(produto, config)
    except ErroAgente as e:
        log.registrar(produto, e.etapa, "ERRO " + e.mensagem)
        print(f"\nERRO na etapa [{e.etapa}]: {e.mensagem}\nComo corrigir: {e.como_corrigir}")
        notificar.enviar(config, "Erro no Vídeo Vendas", f"{produto} - etapa {e.etapa}: {e.mensagem}"[:300],
                         prioridade=4, tags="warning")
    except Exception as e:  # erro inesperado
        log.registrar(produto, "inesperado", f"ERRO {e!r}")
        print(f"\nERRO inesperado: {e!r}\nCopie esta mensagem e envie ao suporte.")
        notificar.enviar(config, "Erro inesperado no Vídeo Vendas", f"{produto}: {e!r}"[:300],
                         prioridade=4, tags="warning")
    return 1


if __name__ == "__main__":
    sys.exit(main())
