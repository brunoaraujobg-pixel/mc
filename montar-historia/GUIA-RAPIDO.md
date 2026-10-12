# Guia rápido: vídeo de história (YouTube + Instagram)

Resumo de tudo que o `montar-historia` faz e dos comandos para usar. Detalhes em `README.md`.

## O que ele entrega
A partir das cenas de vídeo geradas por IA (Kling, Runway, Luma), ele cria:

| Arquivo | Para quê |
|---|---|
| `historia.mp4` | Vídeo final: cenas na ordem, efeitos, música que abaixa na fala, voz, legenda animada, transição suave. Serve para **Instagram/Reels** |
| `historia.srt` | Legenda para enviar no **YouTube** (só se houver `FALA:`) |
| `historia_miniatura.jpg` | Miniatura/capa com título (só se houver `TITULO_MINIATURA:`) |
| `historia_publicacao.txt` | **Kit de publicação**: título, descrição, hashtags e passos para YouTube e Instagram (só se houver `TITULO_VIDEO:` ou `TITULO_MINIATURA:`) |
| `log.txt` | Histórico e avisos |

Tudo em `saida/<nome-do-arquivo-da-história>/`. Nunca sobrescreve: cria `historia_2.mp4` etc.

## Instalação (uma vez, Windows)
```
winget install Gyan.FFmpeg          (feche e abra o terminal depois)
cd C:\PROJETOS\mc
git pull
cd montar-historia
pip install -r requirements.txt
```
Voz offline (opcional): `pip install piper-tts==1.8.0` (Piper) ou `pip install pyttsx3==2.99` (voz do Windows).

## Testar com cenas de ensaio (sem gastar créditos)
```
python teste-5-cenas/gerar_arquivos_teste.py
python montar_historia.py teste-5-cenas/pokemon.txt
```

## Usar com cenas reais
1. Gere as cenas com os prompts de `teste-5-cenas/prompts_cenas.md` (**vertical 9:16**).
2. Salve em `cenas/` (`01_caminhada.mp4` ...). Sons em `sons/`, música em `musicas/` (só material livre).
3. Rode: `python montar_historia.py teste-5-cenas/pokemon.txt`

## Arquivo da história (resumo)
```
FORMATO: vertical                  # vertical | horizontal
MOTOR_VOZ: edge                    # edge (online) | piper (offline) | windows (offline)
VOZ: pt-BR-FranciscaNeural         # piper: pt_BR-faber-medium | windows: Maria
MUSICA: musica_heroica.mp3
VOLUME_MUSICA: 0.15
ABAIXAR_MUSICA: sim
TRANSICAO: fade                    # fade | corte
TITULO_MINIATURA: A *Emboscada* na Floresta   # *palavra* = amarelo
TITULO_VIDEO: A Emboscada na Floresta | Maria e Rummi
HASHTAGS: animacao, aventura, historia        # sem o símbolo #
LEGENDA: sim

CENA | 01_caminhada.mp4 | SOM: passos_mata.mp3@0 | FALA: Texto narrado
```
`SOM: arquivo@segundo` pode repetir. `FALA:` é opcional. Números por extenso ("oitenta e um mil").

## Ferramentas avulsas
```
python ouvir_voz.py "Seu texto"                 # ouve as 3 vozes antes de montar (toca e abre a pasta)
python ouvir_voz.py "Seu texto" --motor piper   # vozes offline
python miniatura.py video.mp4 "O *SEGREDO* da floresta" [--formato youtube|capa] [--quadro 12]
```
E, na pasta `legendas/`, legendas em lote para vídeos que você já tem (`.srt` + legenda animada).

## Publicar
- **Instagram/Reels:** `historia.mp4` + `historia_miniatura.jpg` (capa).
- **YouTube:** `historia.mp4` + enviar `historia.srt` em Studio > Legendas + miniatura. Revise o `.srt` antes.
- Postagem manual: os programas não publicam nada sozinhos.

## Já confirmado no seu PC
- [x] Voz em português (edge) e voz offline (Piper)
- [x] Miniatura automática
- [x] Teste de ponta a ponta com as 5 cenas de ensaio
- [x] `historia.srt` (legenda do YouTube)
- [x] `legendas/` (transcrição Whisper em lote)

## Ainda sem teste no seu PC
- [ ] Kit de publicação (`historia_publicacao.txt`)
- [ ] Cenas reais do Kling/Runway/Luma
- [ ] Sons e música reais de biblioteca livre

## Cuidados
- Pokémon, Raichu e Equipe Rocket são da Nintendo/The Pokémon Company: uso pessoal costuma ser tranquilo; em canal **monetizado** há risco de bloqueio. Para gerar renda, prefira personagens originais.
- O YouTube não monetiza conteúdo repetitivo e feito em massa.
- Não suba certificado digital, senhas ou chaves para o GitHub.

## Problemas comuns
| Mensagem | Solução |
|---|---|
| `'python' não é reconhecido` | Reinstale o Python marcando **Add Python to PATH** |
| `ffmpeg não encontrado` | `winget install Gyan.FFmpeg` e reabra o terminal |
| `Faltam estes vídeos de cena` | Coloque os arquivos listados em `cenas/` |
| Cena sem narração | Voz indisponível (internet no edge, ou motor offline não instalado) |
