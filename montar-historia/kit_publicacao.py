"""
Kit de publicação: título, descrição, hashtags e checklist para YouTube e Instagram.

Gera um arquivo de texto pronto para copiar e colar, a partir do arquivo da história.
Não publica nada: você posta manualmente.

Uso (sem precisar do vídeo pronto):
    python kit_publicacao.py teste-5-cenas/pokemon.txt
Resultado: saida/<nome>/historia_publicacao.txt

Linhas opcionais no arquivo da história (as hashtags SEM o símbolo #):
    TITULO_VIDEO: A Emboscada na Floresta | Maria e o Raichu Samurai
    DESCRICAO: Texto curto que resume a história (se vazio, usa as falas)
    HASHTAGS: animacao, historia, aventura, anime
    LINK: meusite.com.br/contato
Se TITULO_VIDEO não existir, usa o TITULO_MINIATURA (sem os asteriscos).
"""

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
HASHTAGS_PADRAO = "historia, animacao, aventura"
LIMITE_TITULO_YT = 100       # caracteres
LIMITE_DESCRICAO_YT = 5000
LIMITE_TAGS_YT = 500
LIMITE_LEGENDA_IG = 2200
LIMITE_HASHTAGS_IG = 30


def limpar_titulo(txt):
    return re.sub(r"\s+", " ", txt.replace("*", "")).strip()


def normalizar_hashtags(txt):
    """'Anime, história épica' -> ['#anime', '#históriaépica'] (sem espaços, sem repetir)."""
    saida = []
    for pedaco in re.split(r"[,;\n]+", txt):
        palavra = re.sub(r"[^\w]", "", pedaco.strip().replace("#", ""), flags=re.UNICODE)
        if palavra and "#" + palavra.lower() not in [h.lower() for h in saida]:
            saida.append("#" + palavra)
    return saida


def sinopse(config, cenas):
    if config.get("descricao"):
        return config["descricao"].strip()
    falas = [c["fala"].strip() for c in cenas if c.get("fala")]
    return " ".join(falas)


def gerar_kit(config, cenas, destino):
    destino = Path(destino)
    titulo = limpar_titulo(config.get("titulo_video") or config.get("titulo_miniatura") or "")
    if not titulo:
        raise ValueError("defina TITULO_VIDEO ou TITULO_MINIATURA no arquivo da história")
    texto = sinopse(config, cenas)
    tags = normalizar_hashtags(config.get("hashtags") or HASHTAGS_PADRAO)
    link = config.get("link", "").strip()
    avisos = []

    # ---------- YouTube ----------
    desc_yt = texto
    if link:
        desc_yt += f"\n\nSaiba mais: {link}"
    desc_yt += "\n\nVídeo com imagens e voz criadas com inteligência artificial."
    desc_yt += "\n\n" + " ".join(tags[:15])
    tags_yt = ", ".join(t.lstrip("#") for t in tags)
    if len(titulo) > LIMITE_TITULO_YT:
        avisos.append(f"Título do YouTube com {len(titulo)} caracteres (limite {LIMITE_TITULO_YT}): encurte.")
    if len(desc_yt) > LIMITE_DESCRICAO_YT:
        avisos.append("Descrição do YouTube acima do limite: encurte.")
    if len(tags_yt) > LIMITE_TAGS_YT:
        avisos.append("Palavras-chave do YouTube acima do limite: remova algumas.")

    # ---------- Instagram ----------
    gancho = next((c["fala"].strip() for c in cenas if c.get("fala")), titulo)
    legenda_ig = f"{titulo}\n\n{texto}"
    if link:
        legenda_ig += "\n\nLink na bio."
    legenda_ig += "\n\n" + " ".join(tags[:LIMITE_HASHTAGS_IG])
    if len(legenda_ig) > LIMITE_LEGENDA_IG:
        avisos.append(f"Legenda do Instagram com {len(legenda_ig)} caracteres (limite {LIMITE_LEGENDA_IG}): encurte a descrição.")
    if len(tags) > LIMITE_HASHTAGS_IG:
        avisos.append(f"{len(tags)} hashtags: o Instagram aceita até {LIMITE_HASHTAGS_IG}.")

    nome = destino.stem.replace("_publicacao", "")
    linhas = [
        f"KIT DE PUBLICAÇÃO — {titulo}",
        "=" * 60,
        "",
        "ARQUIVOS (na mesma pasta deste arquivo)",
        f"  Vídeo ......... {nome}.mp4",
        f"  Legenda ....... {nome}.srt   (só YouTube)",
        f"  Miniatura ..... {nome}_miniatura.jpg",
        "",
        "-" * 60,
        "YOUTUBE",
        "-" * 60,
        "TÍTULO:",
        titulo,
        f"({len(titulo)}/{LIMITE_TITULO_YT} caracteres)",
        "",
        "DESCRIÇÃO:",
        desc_yt,
        "",
        "PALAVRAS-CHAVE (campo 'Tags' em Mais opções):",
        tags_yt,
        "",
        "PASSOS:",
        "  1. YouTube Studio > Criar > Enviar vídeos > escolha o .mp4",
        "  2. Cole título e descrição. Envie a miniatura (.jpg).",
        "  3. Em 'Legendas', envie o .srt (idioma: Português do Brasil).",
        "  4. Responda a pergunta sobre conteúdo alterado/sintético conforme as regras atuais do YouTube.",
        "  5. Público: marque se o vídeo é ou não 'para crianças' (o YouTube exige essa resposta).",
        "",
        "-" * 60,
        "INSTAGRAM (Reels)",
        "-" * 60,
        "LEGENDA:",
        legenda_ig,
        f"({len(legenda_ig)}/{LIMITE_LEGENDA_IG} caracteres, {min(len(tags), LIMITE_HASHTAGS_IG)} hashtags)",
        "",
        "TEXTO DE GANCHO (primeira frase, aparece antes do 'mais'):",
        gancho,
        "",
        "PASSOS:",
        "  1. Instagram > + > Reel > escolha o .mp4 (a legenda animada já está gravada no vídeo).",
        "  2. Capa: use a miniatura (.jpg) em 'Editar capa > Adicionar da galeria'.",
        "  3. Cole a legenda acima.",
        "  4. Marque o conteúdo como gerado/feito com IA, se a opção aparecer (confira as regras atuais).",
        "",
        "-" * 60,
        "ANTES DE POSTAR (confira)",
        "-" * 60,
        "  [ ] Assisti o vídeo inteiro com som e a legenda está correta",
        "  [ ] Revisei o .srt (nomes e termos escritos certos)",
        "  [ ] Sons e música são de biblioteca livre ou criados por mim",
        "  [ ] Personagens: se forem de terceiros (ex.: Pokémon), sei do risco de bloqueio em canal monetizado",
        "  [ ] Não há dado pessoal, senha ou informação de cliente no vídeo",
        "",
        "Observação: limites e regras (tamanho de título, rótulo de IA, Shorts/Reels) mudam com o tempo.",
        "Confira nas páginas de ajuda oficiais do YouTube e do Instagram.",
    ]
    if avisos:
        linhas += ["", "AVISOS:"] + [f"  ! {a}" for a in avisos]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return destino


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.path.insert(0, str(BASE))
    from montar_historia import ler_historia
    arquivo = Path(sys.argv[1])
    if not arquivo.is_file():
        print(f"Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    config, cenas = ler_historia(arquivo)
    destino = BASE / "saida" / arquivo.stem / "historia_publicacao.txt"
    n = 2
    while destino.exists():
        destino = destino.with_name(f"historia_publicacao_{n}.txt")
        n += 1
    print(f"Kit de publicação: {gerar_kit(config, cenas, destino)}")


if __name__ == "__main__":
    main()
