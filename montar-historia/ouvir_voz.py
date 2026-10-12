"""
Ouça as vozes ANTES de montar o vídeo.

Gera o mesmo texto com cada voz em português e abre a pasta para você ouvir.

Uso:
  python ouvir_voz.py                              (usa um texto de exemplo)
  python ouvir_voz.py "Seu texto aqui"             (usa o seu texto)
  python ouvir_voz.py exemplos/historia.txt        (usa a 1ª FALA do arquivo da história)
  python ouvir_voz.py "Seu texto" --velocidade -10 (10% mais devagar; use +10 para mais rápido)

Resultado: saida/teste_voz/voz_francisca.mp3, voz_antonio.mp3, voz_thalita.mp3
"""

import asyncio
import sys
from pathlib import Path

from montar_historia import abrir, ler_historia

BASE = Path(__file__).resolve().parent
SAIDA = BASE / "saida" / "teste_voz"
VOZES = {
    "francisca": "pt-BR-FranciscaNeural",
    "antonio": "pt-BR-AntonioNeural",
    "thalita": "pt-BR-ThalitaNeural",
}
TEXTO_EXEMPLO = "Maria e suas amigas caminhavam alegres pela floresta, quando tudo mudou."


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

    try:
        import edge_tts
    except ImportError:
        print("Falta instalar: pip install -r requirements.txt")
        sys.exit(1)

    texto = escolher_texto(args)
    SAIDA.mkdir(parents=True, exist_ok=True)
    print(f"Texto: {texto}\n")

    async def gerar(codigo, destino):
        await edge_tts.Communicate(texto, codigo, rate=f"{velocidade:+d}%").save(str(destino))

    feitos = 0
    for nome, codigo in VOZES.items():
        destino = SAIDA / f"voz_{nome}.mp3"
        try:
            asyncio.run(gerar(codigo, destino))
            print(f"  OK  {destino.name}")
            feitos += 1
        except Exception as e:
            print(f"  ERRO em {nome}: {type(e).__name__}: {e}")

    if feitos == 0:
        print("\nNenhuma voz foi gerada. Confira a internet e tente de novo.")
        sys.exit(1)
    print(f"\nPronto: {feitos} voz(es) em {SAIDA}")
    abrir(SAIDA)


if __name__ == "__main__":
    main()
