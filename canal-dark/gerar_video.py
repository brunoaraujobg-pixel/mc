"""Gera um vídeo simples a partir de um roteiro, usando só ferramentas gratuitas.

Uso:  python gerar_video.py exemplos/roteiro.txt
Saída: saida/<nome-do-roteiro>/video.mp4
"""
import asyncio
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LARGURA, ALTURA, FPS = 1280, 720, 25
VOZ = "pt-BR-AntonioNeural"  # alternativas: pt-BR-FranciscaNeural, pt-BR-ThalitaNeural
CORES = [(20, 40, 90), (60, 20, 80), (10, 70, 70), (90, 40, 20)]


def ler_roteiro(caminho):
    """Retorna lista de cenas: {'titulo', 'imagem', 'texto'}."""
    cenas = []
    blocos = re.split(r"\n\s*\n", Path(caminho).read_text(encoding="utf-8"))
    for bloco in blocos:
        linhas = [l.strip() for l in bloco.splitlines() if l.strip() and not l.startswith("#")]
        if not linhas:
            continue
        cena = {"titulo": "", "imagem": "", "texto": ""}
        narracao = []
        for l in linhas:
            if l.upper().startswith("TITULO:"):
                cena["titulo"] = l.split(":", 1)[1].strip()
            elif l.upper().startswith("IMAGEM:"):
                cena["imagem"] = l.split(":", 1)[1].strip()
            else:
                narracao.append(l)
        cena["texto"] = " ".join(narracao)
        if cena["texto"]:
            cenas.append(cena)
    return cenas


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    return r.stdout


def duracao(arquivo):
    out = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", str(arquivo)])
    return float(out.strip())


def fazer_audio(texto, destino):
    """Voz gratuita (edge-tts). Se falhar, cria áudio silencioso do tamanho estimado."""
    try:
        import edge_tts

        async def _go():
            await edge_tts.Communicate(texto, VOZ).save(str(destino))

        asyncio.run(_go())
        return True
    except Exception as e:
        palavras = len(texto.split())
        seg = max(3.0, palavras / 2.5)  # ~150 palavras/minuto
        print(f"   ! voz indisponível ({type(e).__name__}); usando silêncio de {seg:.1f}s")
        rodar(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
               "-t", str(seg), "-q:a", "9", str(destino)])
        return False


def baixar_imagem(prompt, destino):
    """Imagem gratuita via Pollinations. Retorna True se deu certo."""
    try:
        import requests
        from urllib.parse import quote
        url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width={LARGURA}&height={ALTURA}&nologo=true"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        destino.write_bytes(r.content)
        Image.open(destino).verify()
        return True
    except Exception as e:
        print(f"   ! imagem indisponível ({type(e).__name__}); usando slide de texto")
        return False


def fonte(tamanho):
    for f in ("DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(f, tamanho)
        except OSError:
            pass
    return ImageFont.load_default()


def fazer_slide(titulo, texto, indice, destino):
    img = Image.new("RGB", (LARGURA, ALTURA), CORES[indice % len(CORES)])
    d = ImageDraw.Draw(img)
    principal = titulo or texto
    tam = 64 if len(principal) < 60 else 48
    linhas = textwrap.wrap(principal, width=28 if tam == 64 else 36)
    f = fonte(tam)
    y = (ALTURA - len(linhas) * (tam + 14)) // 2
    for l in linhas:
        w = d.textlength(l, font=f)
        d.text(((LARGURA - w) / 2, y), l, font=f, fill="white")
        y += tam + 14
    img.save(destino)


def preparar_imagem(origem, destino):
    """Garante 1280x720 (corta o excesso, sem esticar)."""
    img = Image.open(origem).convert("RGB")
    esc = max(LARGURA / img.width, ALTURA / img.height)
    img = img.resize((int(img.width * esc), int(img.height * esc)))
    x, y = (img.width - LARGURA) // 2, (img.height - ALTURA) // 2
    img.crop((x, y, x + LARGURA, y + ALTURA)).save(destino)


def fazer_clipe(imagem, audio, destino):
    seg = duracao(audio) + 0.4
    frames = int(seg * FPS)
    zoom = f"zoompan=z='min(zoom+0.0006,1.15)':d={frames}:s={LARGURA}x{ALTURA}:fps={FPS}"
    rodar(["ffmpeg", "-y", "-loop", "1", "-i", str(imagem), "-i", str(audio),
           "-vf", zoom, "-t", f"{seg:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-ar", "44100", "-ac", "2", str(destino)])


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python gerar_video.py exemplos/roteiro.txt")
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg não encontrado. Veja o README (como instalar no Windows).")
    roteiro = Path(sys.argv[1])
    pasta = Path("saida") / roteiro.stem
    tmp = pasta / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    cenas = ler_roteiro(roteiro)
    print(f"{len(cenas)} cenas encontradas.")
    clipes = []
    for i, c in enumerate(cenas, 1):
        print(f"Cena {i}/{len(cenas)}: {c['texto'][:50]}...")
        audio, bruta, final = tmp / f"{i}.mp3", tmp / f"{i}_raw.jpg", tmp / f"{i}.png"
        fazer_audio(c["texto"], audio)
        if c["imagem"] and baixar_imagem(c["imagem"], bruta):
            preparar_imagem(bruta, final)
        else:
            fazer_slide(c["titulo"], c["texto"], i, final)
        clipe = tmp / f"{i}.mp4"
        fazer_clipe(final, audio, clipe)
        clipes.append(clipe)

    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{c.name}'\n" for c in clipes), encoding="utf-8")
    video = pasta / "video.mp4"
    rodar(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(video)])
    print(f"\nPRONTO: {video}  ({duracao(video):.0f}s)")


if __name__ == "__main__":
    main()
