"""
Miniatura automática (capa) a partir do vídeo pronto.

Escolhe sozinho o quadro mais nítido e colorido do vídeo, escurece a parte de baixo e
escreve o título grande, com contorno. Palavras entre *asteriscos* ficam em amarelo.

Uso:
  python miniatura.py saida/historia/historia.mp4 "O *SEGREDO* da floresta"
  python miniatura.py video.mp4 "Título" --formato youtube   (1280x720; vídeo vertical ganha fundo desfocado)
  python miniatura.py video.mp4 "Título" --formato capa      (1080x1920, capa de Reels/Shorts)
  python miniatura.py video.mp4 "Título" --quadro 12         (usa o quadro do segundo 12, sem escolher sozinho)

Também roda sozinho no montar_historia.py se o arquivo da história tiver a linha
TITULO_MINIATURA: ... (veja o README).
"""

import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

AMARELO = (255, 214, 0)
BRANCO = (255, 255, 255)
TAMANHOS = {"youtube": (1280, 720), "capa": (1080, 1920)}
FONTES = ["impact.ttf", "Impact.ttf", "arialbd.ttf", "Arial Bold.ttf",
          "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-600:])
    return r.stdout


def duracao(video):
    return float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(video)]).strip())


def extrair_quadro(video, segundo, destino):
    rodar(["ffmpeg", "-y", "-ss", f"{segundo:.2f}", "-i", str(video),
           "-frames:v", "1", "-q:v", "2", str(destino)])


def nota(img):
    """Nota do quadro: nitidez (bordas) + cores vivas. Maior = melhor para miniatura."""
    pequena = img.convert("RGB").resize((320, 320 * img.height // img.width or 1))
    bordas = ImageStat.Stat(pequena.convert("L").filter(ImageFilter.FIND_EDGES)).var[0]
    hsv = ImageStat.Stat(pequena.convert("HSV"))
    cor = hsv.mean[1] * 0.5 + hsv.mean[2] * 0.2        # saturação e brilho
    escuro_demais = 0 if hsv.mean[2] > 50 else -1000    # evita quadro preto (fade)
    return bordas + cor + escuro_demais


def melhor_quadro(video, pasta, n=12):
    total = duracao(video)
    melhor, melhor_nota = None, None
    for i in range(n):
        seg = total * (0.08 + 0.84 * i / max(1, n - 1))   # ignora começo e fim (fades)
        arq = pasta / f"_q{i:02}.jpg"
        extrair_quadro(video, seg, arq)
        img = Image.open(arq)
        v = nota(img)
        if melhor_nota is None or v > melhor_nota:
            melhor, melhor_nota = img.copy(), v
        arq.unlink()
    return melhor


def carregar_fonte(tamanho):
    for nome in FONTES:
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default(size=tamanho)


def preparar_fundo(img, formato):
    """Redimensiona o quadro para o formato. Vídeo vertical no formato youtube: fundo desfocado."""
    larg, alt = TAMANHOS[formato]
    img = img.convert("RGB")
    proporcao_alvo = larg / alt
    if abs(img.width / img.height - proporcao_alvo) < 0.05:
        return img.resize((larg, alt), Image.LANCZOS)
    if (img.width / img.height) > proporcao_alvo or formato == "capa":
        # preenche cortando as bordas
        escala = max(larg / img.width, alt / img.height)
        novo = img.resize((int(img.width * escala) + 1, int(img.height * escala) + 1), Image.LANCZOS)
        x, y = (novo.width - larg) // 2, (novo.height - alt) // 2
        return novo.crop((x, y, x + larg, y + alt))
    # quadro mais "em pé" que o youtube: fundo desfocado + quadro inteiro no centro
    escala = max(larg / img.width, alt / img.height)
    fundo = img.resize((int(img.width * escala) + 1, int(img.height * escala) + 1))
    x, y = (fundo.width - larg) // 2, (fundo.height - alt) // 2
    fundo = fundo.crop((x, y, x + larg, y + alt)).filter(ImageFilter.GaussianBlur(28))
    fundo = Image.blend(fundo, Image.new("RGB", fundo.size, (0, 0, 0)), 0.35)
    frente_esc = alt / img.height
    frente = img.resize((int(img.width * frente_esc), alt), Image.LANCZOS)
    fundo.paste(frente, ((larg - frente.width) // 2, 0))
    return fundo


def escurecer_embaixo(img, fracao=0.55):
    larg, alt = img.size
    sombra = Image.new("L", (1, alt))
    inicio = int(alt * (1 - fracao))
    for y in range(alt):
        sombra.putpixel((0, y), 0 if y < inicio else int(215 * (y - inicio) / (alt - inicio)))
    sombra = sombra.resize((larg, alt))
    return Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, sombra)


def palavras_do_titulo(titulo):
    """'O *SEGREDO* da floresta' -> [('O', branco), ('SEGREDO', amarelo), ...] (maiúsculas)."""
    saida, amarelo = [], False
    for pedaco in re.split(r"(\*)", titulo):
        if pedaco == "*":
            amarelo = not amarelo
            continue
        for p in pedaco.split():
            saida.append((p.upper(), AMARELO if amarelo else BRANCO))
    return saida


def quebrar_linhas(palavras, fonte, largura_max, contorno):
    linhas, atual = [], []
    for p in palavras:
        teste = atual + [p]
        texto = " ".join(x[0] for x in teste)
        if atual and fonte.getlength(texto) + 2 * contorno > largura_max:
            linhas.append(atual)
            atual = [p]
        else:
            atual = teste
    if atual:
        linhas.append(atual)
    return linhas


def escrever_titulo(img, titulo, formato):
    larg, alt = img.size
    palavras = palavras_do_titulo(titulo)
    if not palavras:
        return img
    margem = int(larg * 0.06)
    largura_max = larg - 2 * margem
    tamanho = int(alt * (0.17 if formato == "youtube" else 0.085))
    max_linhas = 3
    while True:
        contorno = max(4, tamanho // 11)
        fonte = carregar_fonte(tamanho)
        linhas = quebrar_linhas(palavras, fonte, largura_max, contorno)
        if len(linhas) <= max_linhas or tamanho <= 24:
            break
        tamanho = int(tamanho * 0.92)
    altura_linha = int(tamanho * 1.08)
    total = altura_linha * len(linhas)
    y = alt - margem - total if formato == "youtube" else int(alt * 0.80) - total // 2
    d = ImageDraw.Draw(img)
    for linha in linhas:
        texto = " ".join(p[0] for p in linha)
        comprimento = fonte.getlength(texto)
        x = margem if formato == "youtube" else (larg - comprimento) / 2
        for palavra, cor in linha:
            d.text((x, y), palavra, font=fonte, fill=cor, stroke_width=contorno,
                   stroke_fill=(0, 0, 0))
            x += fonte.getlength(palavra + " ")
        y += altura_linha
    return img


def gerar_miniatura(video, titulo, destino, formato="auto", segundo=None):
    """Cria a miniatura (.jpg). Devolve o caminho."""
    video, destino = Path(video), Path(destino)
    pasta = destino.parent
    pasta.mkdir(parents=True, exist_ok=True)
    if segundo is None:
        quadro = melhor_quadro(video, pasta)
    else:
        tmp = pasta / "_quadro.jpg"
        extrair_quadro(video, segundo, tmp)
        quadro = Image.open(tmp).copy()
        tmp.unlink()
    if formato == "auto":
        formato = "capa" if quadro.height > quadro.width else "youtube"
    img = escurecer_embaixo(preparar_fundo(quadro, formato))
    img = escrever_titulo(img, titulo, formato)
    img.save(destino, quality=92)
    return destino


def main():
    args = sys.argv[1:]
    formato, segundo = "auto", None
    if "--formato" in args:
        i = args.index("--formato")
        formato = args[i + 1] if i + 1 < len(args) else ""
        if formato not in ("auto", *TAMANHOS):
            print("Use: --formato youtube | capa | auto")
            sys.exit(1)
        del args[i:i + 2]
    if "--quadro" in args:
        i = args.index("--quadro")
        try:
            segundo = float(args[i + 1].replace(",", "."))
        except (IndexError, ValueError):
            print("Use: --quadro 12   (segundo do vídeo)")
            sys.exit(1)
        del args[i:i + 2]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    video, titulo = Path(args[0]), args[1]
    if not video.is_file():
        print(f"Vídeo não encontrado: {video}")
        sys.exit(1)
    destino = video.with_name(video.stem + "_miniatura.jpg")
    n = 2
    while destino.exists():          # nunca sobrescreve
        destino = video.with_name(f"{video.stem}_miniatura_{n}.jpg")
        n += 1
    print(f"Miniatura: {gerar_miniatura(video, titulo, destino, formato, segundo)}")


if __name__ == "__main__":
    main()
