"""
Cria arquivos de ENSAIO para testar o fluxo inteiro sem gastar créditos de IA.

  - 5 cenas de teste (cartões coloridos com o número e o nome da cena) em cenas/
  - sons de teste (tons e ruído) em sons/ e uma música de teste em musicas/

NUNCA sobrescreve: se você já colocou uma cena ou som de verdade com o mesmo nome,
ele é mantido. Depois, para o vídeo real, é só trocar os arquivos de ensaio pelos
verdadeiros (mesmo nome) e rodar de novo.

Uso (dentro da pasta montar-historia):
    python teste-5-cenas/gerar_arquivos_teste.py
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJETO = Path(__file__).resolve().parent.parent      # pasta montar-historia
CENAS = PROJETO / "cenas"
SONS = PROJETO / "sons"
MUSICAS = PROJETO / "musicas"

# nome do arquivo, título, duração em segundos (iguais aos prompts de vídeo), cor de fundo
CENAS_TESTE = [
    ("01_caminhada.mp4", "A Caminhada na Mata", 4.5, (34, 120, 60)),
    ("02_rummi_perdida.mp4", "Rummi se Perde", 3.5, (60, 50, 110)),
    ("03_emboscada.mp4", "A Emboscada da Equipe Rocket", 5.0, (140, 40, 40)),
    ("04_raichu.mp4", "Raichu Samurai e o Golpe", 5.5, (200, 150, 20)),
    ("05_reencontro.mp4", "Reencontro e Desafio", 5.0, (30, 100, 160)),
]
# nome, comando lavfi (fonte de som), duração
SONS_TESTE = [
    ("passos_mata.mp3", "sine=f=140:d=3", 3),
    ("suspense.mp3", "sine=f=90:d=4", 4),
    ("raio.mp3", "anoisesrc=d=1:c=white:a=0.6", 1),
    ("decolagem.mp3", "sine=f=700:d=2", 2),
]


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-600:])


def fonte(tamanho):
    for nome in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            pass
    return ImageFont.load_default(size=tamanho)


def cartao(numero, titulo, cor, destino):
    img = Image.new("RGB", (1080, 1920), cor)
    d = ImageDraw.Draw(img)
    d.rectangle((60, 60, 1020, 1860), outline=(255, 255, 255), width=8)
    d.text((540, 700), f"CENA {numero}", font=fonte(180), fill=(255, 255, 255), anchor="mm")
    # título em até 3 linhas
    palavras, linhas, atual = titulo.split(), [], ""
    for p in palavras:
        if len(atual + " " + p) > 18 and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = (atual + " " + p).strip()
    linhas.append(atual)
    for i, linha in enumerate(linhas):
        d.text((540, 960 + i * 100), linha, font=fonte(90), fill=(255, 255, 255), anchor="mm")
    d.text((540, 1600), "ARQUIVO DE ENSAIO", font=fonte(60), fill=(255, 255, 255), anchor="mm")
    d.text((540, 1680), "troque pela cena real", font=fonte(50), fill=(230, 230, 230), anchor="mm")
    img.save(destino)


def main():
    for pasta in (CENAS, SONS, MUSICAS):
        pasta.mkdir(exist_ok=True)
    criados, mantidos = [], []

    for i, (nome, titulo, dur, cor) in enumerate(CENAS_TESTE, 1):
        destino = CENAS / nome
        if destino.exists():
            mantidos.append(f"cenas/{nome}")
            continue
        png = CENAS / f"_ensaio_{i}.png"
        cartao(i, titulo, cor, png)
        rodar(["ffmpeg", "-y", "-loop", "1", "-i", str(png), "-t", str(dur),
               "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "23", str(destino)])
        png.unlink()
        criados.append(f"cenas/{nome}")

    for nome, fonte_som, dur in SONS_TESTE:
        destino = SONS / nome
        if destino.exists():
            mantidos.append(f"sons/{nome}")
            continue
        rodar(["ffmpeg", "-y", "-f", "lavfi", "-i", fonte_som, "-af",
               f"afade=t=out:st={max(0.0, dur - 0.3)}:d=0.3,volume=0.5", str(destino)])
        criados.append(f"sons/{nome}")

    musica = MUSICAS / "musica_heroica.mp3"
    if musica.exists():
        mantidos.append("musicas/musica_heroica.mp3")
    else:
        rodar(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=262:d=30", "-af", "volume=0.4", str(musica)])
        criados.append("musicas/musica_heroica.mp3")

    print("Criados (ensaio):")
    for c in criados:
        print("  +", c)
    if mantidos:
        print("Mantidos (já existiam, não mexi):")
        for m in mantidos:
            print("  =", m)
    print("\nPróximo passo:  python montar_historia.py teste-5-cenas/pokemon.txt")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("FFmpeg não encontrado. Instale com: winget install Gyan.FFmpeg (e reabra o terminal)")
        sys.exit(1)
