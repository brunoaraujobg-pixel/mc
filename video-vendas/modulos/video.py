"""Monta o vídeo 9:16 com FFmpeg e confere o resultado com ffprobe."""
import json
import random
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from .erros import ErroAgente
from .validar import EXT_VIDEO

LARG, ALT = 1080, 1920
EXT_MUSICA = {".mp3", ".m4a", ".wav", ".aac"}
FONTES_ALTERNATIVAS = [  # só usadas se a fonte do config.ini não existir
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def _rodar(cmd, etapa, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise ErroAgente(etapa, "FFmpeg falhou: " + r.stderr.strip()[-600:],
                         "Confira se as fotos/clipes abrem normalmente e se o FFmpeg está atualizado.")
    return r


def checar_ffmpeg():
    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            raise ErroAgente("ffmpeg", f"'{prog}' não encontrado.",
                             "Instale o FFmpeg (veja o README, passo 2) e feche/abra o terminal. "
                             "Teste com: ffmpeg -version")


def escolher_fonte(config):
    candidatas = [config.get("video", "fonte", fallback="")] + FONTES_ALTERNATIVAS
    for c in candidatas:
        if c and Path(c).exists():
            return Path(c)
    raise ErroAgente("fonte", "Nenhuma fonte encontrada para o texto na tela.",
                     "No config.ini, em [video] fonte=, aponte para um arquivo .ttf existente.")


def escolher_musica(pasta_musicas):
    arquivos = [p for p in Path(pasta_musicas).glob("*") if p.suffix.lower() in EXT_MUSICA]
    return random.choice(arquivos) if arquivos else None


def _arquivo_texto(tmp, nome, texto, largura):
    caminho = tmp / nome
    caminho.write_text(textwrap.fill(texto, largura), encoding="utf-8")
    return nome  # relativo: o FFmpeg roda dentro da pasta temporária


def _drawtext(arquivo, tam, y, cor="white"):
    return (f"drawtext=fontfile=fonte.ttf:textfile={arquivo}:fontsize={tam}:fontcolor={cor}"
            f":box=1:boxcolor=black@0.6:boxborderw=18:line_spacing=10:x=(w-text_w)/2:y={y}")


def _preco_formatado(preco):
    return preco if preco.upper().startswith("R$") else f"R$ {preco}"


def montar_video(midias, cad, config, pasta_musicas, destino, aviso=print):
    """Cria o vídeo em 'destino'. Retorna a música usada (ou None)."""
    checar_ffmpeg()
    seg = config.getfloat("video", "segundos_por_midia", fallback=5)
    total = seg * len(midias)
    if not 15 <= total <= 30:
        raise ErroAgente("video", f"Duração prevista {total:.0f}s fora de 15-30s.",
                         "Ajuste segundos_por_midia no config.ini.")
    fonte = escolher_fonte(config)
    n = len(midias)
    inicio_benef = 1 if n == 5 else 0  # com 5 mídias, a 1ª é só a abertura (nome)
    beneficios = [cad["beneficio1"], cad["beneficio2"], cad["beneficio3"]]

    with tempfile.TemporaryDirectory(prefix="videovendas_") as t:
        tmp = Path(t)
        shutil.copy(fonte, tmp / "fonte.ttf")

        segmentos = []
        for i, m in enumerate(midias):
            filtros = [f"scale={LARG}:{ALT}:force_original_aspect_ratio=increase",
                       f"crop={LARG}:{ALT}", "setsar=1", "fps=30", "format=yuv420p"]
            filtros.append(_drawtext(_arquivo_texto(tmp, f"nome{i}.txt", cad["nome"], 24), 56, 220))
            k = i - inicio_benef
            if 0 <= k < 3:
                filtros.append(_drawtext(_arquivo_texto(tmp, f"ben{i}.txt", beneficios[k], 22), 60, 1000))
            if i == n - 1:  # preço no final
                filtros.append(_drawtext(_arquivo_texto(tmp, f"preco{i}.txt",
                                                       _preco_formatado(cad["preco"]), 20),
                                         84, 1300, "yellow"))
            entrada = (["-stream_loop", "-1"] if m.suffix.lower() in EXT_VIDEO
                       else ["-loop", "1", "-framerate", "30"]) + ["-i", str(m.resolve())]
            saida_seg = f"seg{i}.mp4"
            _rodar(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *entrada,
                    "-t", str(seg), "-vf", ",".join(filtros), "-an", "-r", "30",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-pix_fmt", "yuv420p", saida_seg], "video", cwd=tmp)
            segmentos.append(saida_seg)

        (tmp / "lista.txt").write_text("".join(f"file '{s}'\n" for s in segmentos), encoding="utf-8")
        _rodar(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", "lista.txt", "-c", "copy", "junto.mp4"], "video", cwd=tmp)

        musica = escolher_musica(pasta_musicas)
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        if musica:
            vol = config.getfloat("video", "volume_musica", fallback=0.25)
            _rodar(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", "junto.mp4", "-stream_loop", "-1", "-i", str(musica.resolve()),
                    "-filter_complex",
                    f"[1:a]volume={vol},afade=t=out:st={total - 2}:d=2[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                    "-t", str(total), str(destino.resolve())], "musica", cwd=tmp)
        else:
            aviso("  (aviso) Nenhuma música em 'musicas/'. O vídeo ficou SEM música.")
            shutil.copy(tmp / "junto.mp4", destino)
    return musica


def verificar_video(arquivo):
    """Confere: abre, 9:16 e duração de 15 a 30 s. Retorna (largura, altura, duração)."""
    r = _rodar(["ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height:format=duration",
                "-of", "json", str(arquivo)], "validar-video")
    info = json.loads(r.stdout)
    w, h = info["streams"][0]["width"], info["streams"][0]["height"]
    dur = float(info["format"]["duration"])
    if abs(w / h - 9 / 16) > 0.01:
        raise ErroAgente("validar-video", f"Proporção {w}x{h} não é 9:16.", "Avise o suporte: erro interno.")
    if not 15 <= dur <= 30.5:
        raise ErroAgente("validar-video", f"Duração {dur:.1f}s fora de 15-30s.",
                         "Ajuste segundos_por_midia no config.ini.")
    return w, h, dur
