"""
Motores de voz do montar-historia.

  edge     voz da Microsoft (melhor qualidade, PRECISA de internet)
  piper    voz neural local (boa qualidade, OFFLINE depois de baixar a voz 1 vez)
  windows  voz que já vem no Windows (simples, OFFLINE, qualidade mais robótica)

Cada motor recebe o texto e devolve o caminho do áudio gerado (ou None se falhar).
"""

import asyncio
import subprocess
import sys
import wave
from pathlib import Path

BASE = Path(__file__).resolve().parent
PASTA_VOZES = BASE / "vozes"          # onde o Piper guarda as vozes baixadas

MOTORES = ("edge", "piper", "windows")
VOZ_PADRAO = {
    "edge": "pt-BR-FranciscaNeural",
    "piper": "pt_BR-faber-medium",
    "windows": "Maria",               # trecho do nome da voz; vale também "Portuguese"
}


def voz_valida(motor, voz):
    """Evita usar o nome de voz de um motor em outro (ex.: nome do edge no piper)."""
    if not voz:
        return VOZ_PADRAO[motor]
    if motor != "edge" and voz.startswith("pt-BR-"):
        print(f"   ! '{voz}' é voz do motor edge; usando {VOZ_PADRAO[motor]} no motor {motor}")
        return VOZ_PADRAO[motor]
    if motor == "piper" and "_" not in voz:
        print(f"   ! '{voz}' não parece voz do Piper (ex.: pt_BR-faber-medium); "
              f"usando {VOZ_PADRAO['piper']}")
        return VOZ_PADRAO["piper"]
    return voz


# ------------------------------ edge ------------------------------

def _edge(texto, voz, destino, velocidade):
    import edge_tts

    async def _go():
        await edge_tts.Communicate(texto, voz, rate=f"{velocidade:+d}%").save(str(destino))

    asyncio.run(_go())
    return destino


# ------------------------------ piper ------------------------------

def _piper(texto, voz, destino, velocidade):
    from piper import PiperVoice, SynthesisConfig

    modelo = PASTA_VOZES / f"{voz}.onnx"
    if not modelo.is_file():
        PASTA_VOZES.mkdir(exist_ok=True)
        print(f"   Baixando a voz '{voz}' (só na primeira vez)...")
        r = subprocess.run([sys.executable, "-m", "piper.download_voices", voz,
                            "--data-dir", str(PASTA_VOZES)], capture_output=True, text=True)
        if r.returncode != 0 or not modelo.is_file():
            motivo = (r.stderr.strip().splitlines() or ["erro desconhecido"])[-1][:150]
            raise RuntimeError(f"não consegui baixar a voz '{voz}' (precisa de internet só nessa "
                               f"vez). Veja os nomes com: python -m piper.download_voices | {motivo}")
    destino = destino.with_suffix(".wav")
    # velocidade +10 = 10% mais rápido -> length_scale menor
    config = SynthesisConfig(length_scale=1.0 / (1.0 + velocidade / 100.0))
    with wave.open(str(destino), "wb") as arq:
        PiperVoice.load(str(modelo)).synthesize_wav(texto, arq, syn_config=config)
    return destino


# ------------------------------ windows ------------------------------

def vozes_windows():
    import pyttsx3
    motor = pyttsx3.init()
    return [v.name for v in motor.getProperty("voices")]


def _windows(texto, voz, destino, velocidade):
    import pyttsx3

    motor = pyttsx3.init()
    escolhida = None
    for v in motor.getProperty("voices"):
        if voz.lower() in v.name.lower():
            escolhida = v
            break
    if escolhida is None:   # cai para qualquer voz em português
        for v in motor.getProperty("voices"):
            if "portug" in v.name.lower() or "pt-br" in v.name.lower():
                escolhida = v
                break
    if escolhida is None:
        raise RuntimeError("nenhuma voz em português instalada no Windows "
                           "(Configurações > Hora e idioma > Fala > Adicionar vozes)")
    motor.setProperty("voice", escolhida.id)
    motor.setProperty("rate", int(motor.getProperty("rate") * (1 + velocidade / 100.0)))
    destino = destino.with_suffix(".wav")
    motor.save_to_file(texto, str(destino))
    motor.runAndWait()
    if not destino.is_file() or destino.stat().st_size == 0:
        raise RuntimeError("o Windows não gerou o áudio")
    return destino


# ------------------------------ entrada ------------------------------

def gerar_voz(texto, motor, voz, destino, velocidade=0):
    """Gera o áudio. Devolve o Path do arquivo criado, ou None se falhar (sem derrubar o programa)."""
    if motor not in MOTORES:
        print(f"   ! motor de voz '{motor}' desconhecido (use: {', '.join(MOTORES)})")
        return None
    voz = voz_valida(motor, voz)
    funcao = {"edge": _edge, "piper": _piper, "windows": _windows}[motor]
    try:
        saida = funcao(texto, voz, Path(destino), velocidade)
        return saida if saida.is_file() and saida.stat().st_size > 0 else None
    except ImportError as e:
        pacote = {"edge": "edge-tts", "piper": "piper-tts", "windows": "pyttsx3"}[motor]
        print(f"   ! falta instalar: pip install {pacote}  ({e})")
    except Exception as e:
        print(f"   ! voz indisponível no motor {motor} ({type(e).__name__}: {e})")
    return None
