"""
Monta uma história em vídeo a partir de cenas já geradas (Kling, Runway, Luma...).

Junta as cenas na ordem, mistura efeitos sonoros nos tempos que você indicar,
põe música de fundo, e (opcional) narração com voz + legenda animada.

Uso:   python montar_historia.py exemplos/historia.txt
Saída: saida/<nome-do-arquivo>/historia.mp4   (nunca sobrescreve: cria historia_2.mp4...)
"""

import asyncio
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
FPS = 30
COR_TEXTO = "FFFFFF"
COR_DESTAQUE = "00D7FF"      # palavra falada (RRGGBB)
PALAVRAS_POR_BLOCO = 3
RESOLUCOES = {"vertical": (1080, 1920), "horizontal": (1920, 1080)}


# ------------------------------ utilidades ------------------------------

def rodar(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1200:])
    return r.stdout


def duracao(arquivo):
    out = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", str(arquivo)])
    return float(out.strip())


def achar(nome, pasta):
    """Procura o arquivo como foi escrito ou dentro da pasta padrão (cenas/sons/musicas)."""
    for cand in (Path(nome), BASE / pasta / nome):
        if cand.is_file():
            return cand.resolve()
    return None


def proximo_nome(pasta, base, ext):
    destino = pasta / f"{base}{ext}"
    n = 2
    while destino.exists():
        destino = pasta / f"{base}_{n}{ext}"
        n += 1
    return destino


# ------------------------------ leitura ------------------------------

def ler_historia(caminho):
    """Retorna (config, cenas). Cena = {'arquivo', 'sons': [(nome, seg)], 'fala'}."""
    config = {"formato": "vertical", "musica": "", "volume_musica": 0.15,
              "legenda": True, "voz": "pt-BR-FranciscaNeural"}
    cenas = []
    for n, bruta in enumerate(Path(caminho).read_text(encoding="utf-8-sig").splitlines(), 1):
        linha = bruta.split("#", 1)[0].strip()   # tira comentários
        if not linha:
            continue
        if linha.upper().startswith("CENA"):
            partes = [p.strip() for p in linha.split("|")]
            if len(partes) < 2 or not partes[1]:
                raise ValueError(f"Linha {n}: falta o arquivo da cena. Use: CENA | arquivo.mp4")
            cena = {"arquivo": partes[1], "sons": [], "fala": ""}
            for extra in partes[2:]:
                chave, _, valor = extra.partition(":")
                chave, valor = chave.strip().upper(), valor.strip()
                if chave == "SOM" and valor:
                    nome, _, seg = valor.partition("@")
                    try:
                        cena["sons"].append((nome.strip(), float(seg.replace(",", ".")) if seg else 0.0))
                    except ValueError:
                        raise ValueError(f"Linha {n}: tempo inválido em SOM: '{valor}'")
                elif chave == "FALA":
                    cena["fala"] = valor
                elif extra:
                    print(f"   ! linha {n}: opção ignorada '{extra}'")
            cenas.append(cena)
            continue
        chave, _, valor = linha.partition(":")
        chave, valor = chave.strip().lower(), valor.strip()
        if chave == "formato":
            if valor.lower() not in RESOLUCOES:
                raise ValueError(f"Linha {n}: FORMATO deve ser vertical ou horizontal")
            config["formato"] = valor.lower()
        elif chave == "musica":
            config["musica"] = valor
        elif chave == "volume_musica":
            config["volume_musica"] = float(valor.replace(",", "."))
        elif chave == "legenda":
            config["legenda"] = valor.lower() in ("sim", "s", "true", "1")
        elif chave == "voz":
            config["voz"] = valor
        else:
            print(f"   ! linha {n} não entendida: '{bruta.strip()}'")
    if not cenas:
        raise ValueError("Nenhuma linha CENA encontrada no arquivo.")
    return config, cenas


# ------------------------------ voz e legenda ------------------------------

def fazer_voz(texto, voz, destino):
    """Voz gratuita (edge-tts). Retorna True se deu certo."""
    try:
        import edge_tts

        async def _go():
            await edge_tts.Communicate(texto, voz).save(str(destino))

        asyncio.run(_go())
        return destino.is_file() and destino.stat().st_size > 0
    except Exception as e:
        print(f"   ! voz indisponível ({type(e).__name__}: {e}); cena fica sem narração")
        return False


def tempo_ass(s):
    cs = int(round(s * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def cor_ass(rgb):
    return f"&H{rgb[4:6]}{rgb[2:4]}{rgb[0:2]}&"


def gerar_ass(texto, inicio, fim, largura, altura, caminho):
    """Legenda animada: palavra falada em destaque. Tempo de cada palavra proporcional ao tamanho."""
    palavras = texto.split()
    pesos = [len(p) + 2 for p in palavras]
    total = sum(pesos)
    marcas, t = [], inicio
    for p, w in zip(palavras, pesos):
        fim_p = t + (fim - inicio) * w / total
        marcas.append((p, t, fim_p))
        t = fim_p

    tam = int(altura * 0.045) if altura >= largura else int(altura * 0.06)
    x, y = largura // 2, int(altura * (0.72 if altura >= largura else 0.85))
    margem = int(largura * 0.08)
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {largura}
PlayResY: {altura}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,Arial,{tam},{cor_ass(COR_TEXTO)},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(3, tam // 12)},2,5,{margem},{margem},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    eventos = []
    for i in range(0, len(marcas), PALAVRAS_POR_BLOCO):
        bloco = marcas[i:i + PALAVRAS_POR_BLOCO]
        # encolhe a fonte se o bloco não couber na largura (palavras longas)
        chars = sum(len(p) for p, _, _ in bloco) + len(bloco) - 1
        tam_bloco = min(tam, int(largura * 0.88 / (0.68 * chars)))
        for k, (_, ini, fim_p) in enumerate(bloco):
            partes = []
            for j, (p, _, _) in enumerate(bloco):
                txt = p.replace("{", "(").replace("}", ")").upper()
                if j == k:
                    partes.append(
                        f"{{\\c{cor_ass(COR_DESTAQUE)}\\fscx80\\fscy80"
                        f"\\t(0,90,\\fscx118\\fscy118)\\t(90,180,\\fscx105\\fscy105)}}{txt}{{\\r\\fs{tam_bloco}}}")
                else:
                    partes.append(txt)
            eventos.append(f"Dialogue: 0,{tempo_ass(ini)},{tempo_ass(fim_p)},Legenda,,0,0,0,,"
                           f"{{\\an5\\pos({x},{y})\\fs{tam_bloco}}}" + " ".join(partes))
    caminho.write_text(cab + "\n".join(eventos) + "\n", encoding="utf-8-sig")


# ------------------------------ montagem ------------------------------

def montar_cena(cena, clip, sons, voz, config, temp, indice):
    """Gera temp/cena_NN.mp4 (vídeo normalizado + áudio da cena)."""
    largura, altura = RESOLUCOES[config["formato"]]
    dur_clip = duracao(clip)
    atraso_voz = 0.2
    dur_voz = duracao(voz) if voz else 0.0
    dur = max(dur_clip, dur_voz + atraso_voz + 0.3 if voz else 0.0)

    vf = (f"scale={largura}:{altura}:force_original_aspect_ratio=increase,"
          f"crop={largura}:{altura},fps={FPS},setsar=1")
    if dur > dur_clip + 0.01:   # voz maior que o clipe: congela o último quadro
        vf += f",tpad=stop_mode=clone:stop_duration={dur - dur_clip:.3f}"
    if voz and config["legenda"] and cena["fala"]:
        ass = temp / f"cena_{indice:02}.ass"
        gerar_ass(cena["fala"], atraso_voz, atraso_voz + dur_voz, largura, altura, ass)
        vf += f",subtitles={ass.name}"
    vf += ",format=yuv420p"

    entradas = ["-i", str(clip), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    filtros = [f"[0:v]{vf}[v]"]
    rotulos = ["[1:a]"]
    prox = 2
    for arq, seg in sons:
        entradas += ["-i", str(arq)]
        ms = int(seg * 1000)
        filtros.append(f"[{prox}:a]aresample=44100,aformat=channel_layouts=stereo,"
                       f"adelay={ms}|{ms}[s{prox}]")
        rotulos.append(f"[s{prox}]")
        prox += 1
    if voz:
        entradas += ["-i", str(voz)]
        ms = int(atraso_voz * 1000)
        filtros.append(f"[{prox}:a]aresample=44100,aformat=channel_layouts=stereo,"
                       f"adelay={ms}|{ms}[vz]")
        rotulos.append("[vz]")
    filtros.append("".join(rotulos) +
                   f"amix=inputs={len(rotulos)}:normalize=0:duration=longest,"
                   f"alimiter=limit=0.95[a]")

    saida = temp / f"cena_{indice:02}.mp4"
    rodar(["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(filtros),
           "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
           str(saida)], cwd=str(temp))
    return saida


def juntar(cenas_mp4, destino, temp):
    lista = temp / "lista.txt"
    lista.write_text("".join(f"file '{c.name}'\n" for c in cenas_mp4), encoding="utf-8")
    rodar(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "lista.txt",
           "-c", "copy", str(destino.resolve())], cwd=str(temp))


def por_musica(video, musica, volume, destino):
    total = duracao(video)
    fade = min(2.0, total / 2)
    rodar(["ffmpeg", "-y", "-i", str(video), "-stream_loop", "-1", "-i", str(musica),
           "-filter_complex",
           f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume={volume},"
           f"afade=t=out:st={total - fade:.3f}:d={fade:.3f}[m];"
           f"[0:a][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-t", f"{total:.3f}", str(destino)])


def main():
    if len(sys.argv) < 2:
        print("Uso: python montar_historia.py exemplos/historia.txt")
        sys.exit(1)
    arquivo = Path(sys.argv[1])
    if not arquivo.is_file():
        print(f"Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    for prog in ("ffmpeg", "ffprobe"):
        if not shutil.which(prog):
            print(f"'{prog}' não encontrado. Instale o FFmpeg (veja o README).")
            sys.exit(1)

    config, cenas = ler_historia(arquivo)

    # Confere TODOS os arquivos antes de começar (evita descobrir erro no meio)
    faltando = []
    for c in cenas:
        c["clip"] = achar(c["arquivo"], "cenas")
        if not c["clip"]:
            faltando.append(f"cenas/{c['arquivo']}")
    if faltando:
        print("Faltam estes vídeos de cena (coloque na pasta indicada e rode de novo):")
        for f in faltando:
            print("  -", f)
        sys.exit(1)
    musica = None
    if config["musica"]:
        musica = achar(config["musica"], "musicas")
        if not musica:
            print(f"   ! música não encontrada (musicas/{config['musica']}); vídeo sai sem música")

    pasta = BASE / "saida" / arquivo.stem
    temp = pasta / "_temp"
    temp.mkdir(parents=True, exist_ok=True)
    log_txt = pasta / "log.txt"
    avisos = []

    def log(msg):
        linha = f"{datetime.now():%H:%M:%S}  {msg}"
        print(linha)
        with open(log_txt, "a", encoding="utf-8") as f:
            f.write(linha + "\n")

    log(f"História '{arquivo.name}': {len(cenas)} cenas, formato {config['formato']}")
    prontas = []
    try:
        for i, c in enumerate(cenas, 1):
            log(f"Cena {i}/{len(cenas)}: {c['arquivo']}")
            sons = []
            for nome, seg in c["sons"]:
                s = achar(nome, "sons")
                if s:
                    sons.append((s, seg))
                else:
                    avisos.append(f"cena {i}: som não encontrado (sons/{nome}) - ignorado")
            voz = None
            if c["fala"]:
                alvo = temp / f"voz_{i:02}.mp3"
                if fazer_voz(c["fala"], config["voz"], alvo):
                    voz = alvo
                else:
                    avisos.append(f"cena {i}: sem narração (voz indisponível)")
            prontas.append(montar_cena(c, c["clip"], sons, voz, config, temp, i))

        log("Juntando as cenas...")
        sem_musica = temp / "sem_musica.mp4"
        juntar(prontas, sem_musica, temp)
        destino = proximo_nome(pasta, "historia", ".mp4")
        if musica:
            log("Colocando a música de fundo...")
            por_musica(sem_musica, musica, config["volume_musica"], destino)
        else:
            shutil.copy(sem_musica, destino)
    except Exception as e:
        log(f"ERRO: {e}")
        print(f"\nO erro completo está em {log_txt}. Arquivos temporários mantidos em {temp}")
        sys.exit(1)

    shutil.rmtree(temp, ignore_errors=True)
    for a in avisos:
        log("AVISO: " + a)
    log(f"PRONTO: {destino}  ({duracao(destino):.1f}s)")


if __name__ == "__main__":
    main()
