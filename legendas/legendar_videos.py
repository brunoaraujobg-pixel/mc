"""
Legendas em lote para YouTube e Instagram.

Para cada vídeo da pasta ENTRADA gera, na pasta SAIDA:
  - nome.srt              -> legenda para subir no YouTube
  - nome_legendado.mp4    -> vídeo com legenda ANIMADA gravada (Instagram/Reels)
  - nome_link.txt         -> texto pronto para colar na descrição (se houver LINK)

Os vídeos originais nunca são alterados nem movidos.
Vídeos que já têm resultado na SAIDA são pulados (sem duplicar).
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ===================== CONFIGURAÇÕES (edite aqui) =====================

PASTA_BASE = Path(__file__).resolve().parent
ENTRADA = PASTA_BASE / "entrada"   # coloque aqui os vídeos
SAIDA = PASTA_BASE / "saida"       # resultados saem aqui

IDIOMA = "pt"                      # português
MODELO = "small"                   # tiny | base | small | medium | large-v3
                                   # (small = bom equilíbrio; medium = mais preciso, mais lento)

# --- Link (deixe "" para não usar) ---
LINK_TEXTO = ""                    # ex: "Link na bio" ou "meusite.com.br/contato"
LINK_SEGUNDOS_FINAL = 5            # mostra o link nos últimos N segundos do vídeo
LINK_NO_INICIO_SEGUNDOS = 3        # e também nos primeiros N segundos (0 = não mostrar)

# --- Aparência da legenda animada ---
PALAVRAS_POR_BLOCO = 3             # quantas palavras aparecem juntas na tela
FONTE = "Arial"
COR_TEXTO = "FFFFFF"               # branco
COR_DESTAQUE = "00D7FF"            # amarelo/dourado (a palavra falada fica nessa cor)
TAMANHO_FONTE_PCT = 0.045          # tamanho da fonte = 4,5% da altura do vídeo
POSICAO_VERTICAL_PCT = 0.72        # 72% da altura (de cima para baixo); fica acima da área
                                   # que o Instagram cobre com botões e descrição

EXTENSOES = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}

# ======================================================================


def log(msg, arquivo_log):
    linha = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(linha)
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def rodar(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def dimensoes_e_duracao(video):
    saida = rodar([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "default=nw=1:nk=1", str(video),
    ]).stdout.split()
    return int(saida[0]), int(saida[1]), float(saida[2])


# ---------------------------- transcrição ----------------------------

def transcrever(video, modelo):
    """Devolve lista de palavras: [{'t': texto, 'i': início_s, 'f': fim_s}, ...]."""
    segmentos, _ = modelo.transcribe(
        str(video), language=IDIOMA, word_timestamps=True, vad_filter=True
    )
    palavras = []
    for seg in segmentos:
        for p in seg.words or []:
            texto = p.word.strip()
            if texto:
                palavras.append({"t": texto, "i": p.start, "f": p.end})
    return palavras


# ------------------------------ SRT (YouTube) ------------------------------

def tempo_srt(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def blocos(palavras, n):
    """Agrupa palavras em blocos; quebra o bloco também após pontuação final/pausa."""
    resultado, atual = [], []
    for p in palavras:
        atual.append(p)
        fim_frase = p["t"][-1] in ".?!"
        if len(atual) >= n or fim_frase:
            resultado.append(atual)
            atual = []
    if atual:
        resultado.append(atual)
    return resultado


def gerar_srt(palavras, caminho):
    # No YouTube usamos linhas um pouco maiores (até 7 palavras).
    linhas = []
    for k, b in enumerate(blocos(palavras, 7), 1):
        linhas.append(str(k))
        linhas.append(f"{tempo_srt(b[0]['i'])} --> {tempo_srt(b[-1]['f'])}")
        linhas.append(" ".join(p["t"] for p in b))
        linhas.append("")
    caminho.write_text("\n".join(linhas), encoding="utf-8")


# ------------------------- ASS (legenda animada) -------------------------

def tempo_ass(s):
    cs = int(round(s * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def cor_ass(rgb_hex):
    """Converte RRGGBB para o formato do ASS (&HBBGGRR&)."""
    r, g, b = rgb_hex[0:2], rgb_hex[2:4], rgb_hex[4:6]
    return f"&H{b}{g}{r}&"


def gerar_ass(palavras, largura, altura, duracao, caminho):
    tam = int(altura * TAMANHO_FONTE_PCT)
    pos_x = largura // 2
    pos_y = int(altura * POSICAO_VERTICAL_PCT)
    margem = int(largura * 0.08)

    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {largura}
PlayResY: {altura}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,{FONTE},{tam},{cor_ass(COR_TEXTO)},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(3, tam // 12)},2,5,{margem},{margem},0,1
Style: Link,{FONTE},{int(tam * 0.7)},&H00FFFFFF,&H000000FF,&HB4000000,&HB4000000,-1,0,0,0,100,100,0,0,3,{max(6, tam // 6)},0,8,{margem},{margem},{int(altura * 0.06)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    eventos = []
    for b in blocos(palavras, PALAVRAS_POR_BLOCO):
        for k, atual in enumerate(b):
            ini = atual["i"]
            # a palavra fica em destaque até a próxima começar (sem "piscar")
            fim = b[k + 1]["i"] if k + 1 < len(b) else atual["f"]
            if fim <= ini:
                fim = ini + 0.05
            partes = []
            for j, p in enumerate(b):
                txt = p["t"].replace("{", "(").replace("}", ")").upper()
                if j == k:
                    # palavra falada: cor de destaque + "pulinho" (cresce e volta)
                    partes.append(
                        f"{{\\c{cor_ass(COR_DESTAQUE)}\\fscx80\\fscy80"
                        f"\\t(0,90,\\fscx118\\fscy118)\\t(90,180,\\fscx105\\fscy105)}}"
                        f"{txt}{{\\r}}"
                    )
                else:
                    partes.append(txt)
            texto = f"{{\\an5\\pos({pos_x},{pos_y})}}" + " ".join(partes)
            eventos.append(
                f"Dialogue: 0,{tempo_ass(ini)},{tempo_ass(fim)},Legenda,,0,0,0,,{texto}"
            )

    if LINK_TEXTO:
        link = LINK_TEXTO.replace("{", "(").replace("}", ")")
        janelas = []
        if LINK_NO_INICIO_SEGUNDOS > 0:
            janelas.append((0.0, min(LINK_NO_INICIO_SEGUNDOS, duracao)))
        if LINK_SEGUNDOS_FINAL > 0:
            janelas.append((max(0.0, duracao - LINK_SEGUNDOS_FINAL), duracao))
        for ini, fim in janelas:
            eventos.append(
                f"Dialogue: 1,{tempo_ass(ini)},{tempo_ass(fim)},Link,,0,0,0,,"
                f"{{\\fad(250,250)}} {link} "
            )

    caminho.write_text(cab + "\n".join(eventos) + "\n", encoding="utf-8-sig")


def gravar_legenda(video, ass, destino):
    # O filtro "subtitles" tem problemas com caminhos do Windows (C:\...).
    # Truque: rodar o ffmpeg DENTRO da pasta do .ass e usar só o nome do arquivo.
    rodar([
        "ffmpeg", "-y", "-i", str(video.resolve()),
        "-vf", f"subtitles={ass.name}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "copy", "-movflags", "+faststart",
        str(destino.resolve()),
    ], cwd=str(ass.parent))


# ------------------------------- principal -------------------------------

def processar(video, modelo, arquivo_log):
    nome = video.stem
    srt = SAIDA / f"{nome}.srt"
    final = SAIDA / f"{nome}_legendado.mp4"
    if srt.exists() and final.exists():
        log(f"PULADO (já processado): {video.name}", arquivo_log)
        return

    log(f"Transcrevendo: {video.name}", arquivo_log)
    palavras = transcrever(video, modelo)
    if not palavras:
        log(f"AVISO: nenhuma fala encontrada em {video.name}", arquivo_log)
        return

    largura, altura, duracao = dimensoes_e_duracao(video)
    gerar_srt(palavras, srt)

    ass = SAIDA / f"{nome}.ass"
    gerar_ass(palavras, largura, altura, duracao, ass)
    log(f"Gravando legenda animada: {final.name}", arquivo_log)
    gravar_legenda(video, ass, final)
    ass.unlink()  # arquivo temporário

    if LINK_TEXTO:
        (SAIDA / f"{nome}_link.txt").write_text(
            f"Link: {LINK_TEXTO}\n", encoding="utf-8"
        )
    log(f"OK: {video.name}", arquivo_log)


def main():
    ENTRADA.mkdir(exist_ok=True)
    SAIDA.mkdir(exist_ok=True)
    arquivo_log = SAIDA / "log_legendas.txt"

    videos = sorted(
        p for p in ENTRADA.iterdir() if p.suffix.lower() in EXTENSOES
    )
    if not videos:
        print(f"Nenhum vídeo encontrado em: {ENTRADA}")
        print("Coloque os vídeos nessa pasta e rode de novo.")
        return

    from faster_whisper import WhisperModel  # import aqui para o erro ser claro

    log(f"Carregando modelo '{MODELO}' (na 1ª vez baixa da internet)...", arquivo_log)
    modelo = WhisperModel(MODELO, device="auto", compute_type="int8")

    for v in videos:
        try:
            processar(v, modelo, arquivo_log)
        except Exception as e:  # um vídeo com erro não derruba o lote
            log(f"ERRO em {v.name}: {e}", arquivo_log)

    log("Fim.", arquivo_log)


if __name__ == "__main__":
    main()
