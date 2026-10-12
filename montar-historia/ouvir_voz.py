"""
Ouça as vozes ANTES de montar o vídeo.

Gera o mesmo texto com cada voz em português e abre a pasta para você ouvir.

Uso:
  python ouvir_voz.py                              (usa um texto de exemplo)
  python ouvir_voz.py "Seu texto aqui"             (usa o seu texto)
  python ouvir_voz.py exemplos/historia.txt        (usa a 1ª FALA do arquivo da história)
  python ouvir_voz.py "Seu texto" --velocidade -10 (10% mais devagar; use +10 para mais rápido)
  python ouvir_voz.py "Seu texto" --motor piper    (vozes OFFLINE do Piper)
  python ouvir_voz.py "Seu texto" --motor windows  (vozes em português que já vêm no Windows)

Ao gerar, ele TOCA as vozes uma depois da outra (Francisca, Antonio, Thalita) e depois abre a pasta.
Para só gerar sem tocar, use --mudo.

Resultado: saida/teste_voz/voz_<nome>.mp3 (ou .wav nos motores offline)
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from montar_historia import abrir, ler_historia
from motores_voz import MOTORES, VOZ_PADRAO, gerar_voz, vozes_windows

BASE = Path(__file__).resolve().parent
SAIDA = BASE / "saida" / "teste_voz"
VOZES_EDGE = {
    "francisca": "pt-BR-FranciscaNeural",
    "antonio": "pt-BR-AntonioNeural",
    "thalita": "pt-BR-ThalitaNeural",
}
# Nomes de vozes pt_BR do Piper. Se alguma não existir mais, ela é só ignorada.
# Veja a lista atual com:  python -m piper.download_voices
VOZES_PIPER = {
    "faber": "pt_BR-faber-medium",
    "cadu": "pt_BR-cadu-medium",
    "jeff": "pt_BR-jeff-medium",
}
TEXTO_EXEMPLO = "Maria e suas amigas caminhavam alegres pela floresta, quando tudo mudou."


def tocar(arquivo):
    """Toca o áudio e espera terminar (usa o ffplay, que vem junto com o FFmpeg)."""
    try:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(arquivo)],
                       check=True)
        return True
    except Exception:
        return False


def escolher_texto(args):
    if not args:
        return TEXTO_EXEMPLO
    entrada = args[0]
    caminho = Path(entrada)
    if caminho.suffix.lower() == ".txt" and caminho.is_file():
        _, cenas = ler_historia(caminho)
        for c in cenas:
            if c["fala"]:
                return c["fala"]
        print("Esse arquivo não tem nenhuma FALA. Usando o texto de exemplo.")
        return TEXTO_EXEMPLO
    return entrada


def main():
    args = sys.argv[1:]
    velocidade = 0
    if "--velocidade" in args:
        i = args.index("--velocidade")
        try:
            velocidade = int(args[i + 1])
        except (IndexError, ValueError):
            print("Use assim: --velocidade -10   (ou +10)")
            sys.exit(1)
        del args[i:i + 2]

    mudo = "--mudo" in args
    if mudo:
        args.remove("--mudo")
    motor = "edge"
    if "--motor" in args:
        i = args.index("--motor")
        try:
            motor = args[i + 1].lower()
        except IndexError:
            motor = ""
        if motor not in MOTORES:
            print(f"Use assim: --motor {'|'.join(MOTORES)}")
            sys.exit(1)
        del args[i:i + 2]

    texto = escolher_texto(args)
    SAIDA.mkdir(parents=True, exist_ok=True)
    print(f"Motor: {motor}")
    print(f"Texto: {texto}\n")

    if motor == "edge":
        vozes = VOZES_EDGE
    elif motor == "piper":
        vozes = VOZES_PIPER
    else:
        try:
            achadas = [n for n in vozes_windows()
                       if "portug" in n.lower() or "pt-br" in n.lower() or "maria" in n.lower()]
        except Exception as e:
            print(f"Não consegui listar as vozes do Windows ({e}). Falta: pip install pyttsx3")
            sys.exit(1)
        vozes = {re.sub(r"\W+", "_", n).strip("_").lower(): n for n in achadas}
        if not vozes:
            print("Nenhuma voz em português encontrada no Windows.")
            sys.exit(1)

    feitos = []
    for nome, codigo in vozes.items():
        arq = gerar_voz(texto, motor, codigo, SAIDA / f"voz_{nome}.mp3", velocidade)
        if arq:
            print(f"  OK  {arq.name}")
            feitos.append((nome, arq))
        else:
            print(f"  --  {nome}: não gerou")

    if not feitos:
        print("\nNenhuma voz foi gerada. Veja as mensagens acima.")
        sys.exit(1)
    print(f"\nPronto: {len(feitos)} voz(es) em {SAIDA}")

    if not mudo and shutil.which("ffplay"):
        print("\nTocando uma depois da outra...")
        for nome, arq in feitos:
            print(f"  ▶ {nome.capitalize()}")
            if not tocar(arq):
                print("    (não consegui tocar; abra o arquivo pela pasta)")
                break
    elif not mudo:
        print("\n(ffplay não encontrado: abra os arquivos pela pasta. Ele vem com o FFmpeg.)")
    abrir(SAIDA)


if __name__ == "__main__":
    main()
