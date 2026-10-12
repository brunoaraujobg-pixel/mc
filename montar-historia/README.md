# Montar História (cenas + sons + música + voz + legenda)

Junta as cenas de vídeo que você gerou em um gerador de IA (Kling, Runway, Luma...)
em **um único vídeo**, com efeitos sonoros nos momentos certos, música de fundo e,
se quiser, **narração com voz em português e legenda animada**.

```
cenas/ (seus .mp4)  +  sons/ (efeitos)  +  musicas/  +  historia.txt
                              ↓
                  saida/historia/historia.mp4
```

> O programa **não gera** as imagens/vídeos das cenas. Isso é feito no Kling/Runway/Luma.
> Aqui você só **monta** o resultado. Seus arquivos originais nunca são alterados.

## Instalar (Windows, uma vez só)
1. Python: https://www.python.org/downloads/ (marque **"Add Python to PATH"**).
2. FFmpeg: no PowerShell, `winget install Gyan.FFmpeg`. Feche e abra o PowerShell. Teste: `ffmpeg -version`.
3. Na pasta `montar-historia`: `pip install -r requirements.txt` (só é preciso para a narração).

## Usar
1. Gere as cenas e salve os `.mp4` na pasta `cenas/` (ex.: `01_caminhada.mp4`).
2. Coloque os efeitos sonoros em `sons/` e a música em `musicas/` (**só material livre**:
   Pixabay, YouTube Audio Library).
3. Copie `exemplos/historia.txt`, ajuste os nomes e (opcional) as falas.
4. Rode:
   ```
   python montar_historia.py exemplos/historia.txt
   ```
5. Pegue o vídeo em `saida/historia/historia.mp4`. Se rodar de novo, cria `historia_2.mp4` (não sobrescreve).

**O que deve aparecer:** `Cena 1/5 ... Juntando as cenas... PRONTO`. Ao terminar, o vídeo **abre sozinho**
(para desligar, troque `ABRIR_AO_TERMINAR = True` por `False` no começo do `montar_historia.py`).

## Formato do arquivo da história
```
FORMATO: vertical            # vertical (1080x1920) ou horizontal (1920x1080)
MUSICA: musica_heroica.mp3   # opcional
VOLUME_MUSICA: 0.15          # 0.15 = baixa
LEGENDA: sim                 # legenda animada onde houver FALA
VOZ: pt-BR-FranciscaNeural   # ou pt-BR-AntonioNeural, pt-BR-ThalitaNeural

CENA | 01_caminhada.mp4 | SOM: passos_mata.mp3@0 | FALA: Texto narrado
CENA | 04_raichu.mp4 | SOM: raio.mp3@1.5 | SOM: decolagem.mp3@3.5
```
- `SOM: arquivo@segundo` → toca naquele segundo da cena. Pode repetir `SOM:` várias vezes.
- `FALA:` é opcional. Escreva números por extenso ("oitenta e um mil").
- Linhas com `#` são comentários.
- Use o **mesmo formato** (vertical/horizontal) ao gerar as cenas; se for diferente, o programa corta as bordas.

## Regras de proteção
- Antes de começar, confere se **todas as cenas existem**; se faltar alguma, lista e para.
- Som ou música que não for encontrado: **avisa e continua** sem ele.
- Voz indisponível (sem internet): a cena fica sem narração e o programa avisa.
- Em erro, os arquivos temporários ficam em `saida/<historia>/_temp` e o motivo em `log.txt`.

## Efeitos sugeridos (palavras para buscar nas bibliotecas livres)
passos na mata (`footsteps forest`), suspense (`suspense drone`), raio (`lightning thunder zap`),
decolagem/brilho no céu (`whoosh sparkle`), música heroica (`epic adventure`).

## Dicas para as cenas ficarem coerentes (geração)
- Repita em **todo prompt** a mesma descrição de cada personagem e dê o nome (Maria, Rummi...).
- Gere primeiro a imagem de cada cena e use como entrada do gerador de vídeo (image-to-video).
- Nomeie as evoluções do Eevee (Vaporeon, Jolteon...) em vez de "three Eevee evolutions".

## Direitos autorais
Personagens como Pokémon e Equipe Rocket pertencem à Nintendo/The Pokémon Company.
Para uso pessoal costuma ser tranquilo; em **canal monetizado** há risco de bloqueio ou
desmonetização. Para gerar renda, prefira personagens originais.

## Testado / não testado
- Testado: junção das cenas, sons nos tempos indicados, música com fade, legenda animada,
  formatos vertical e horizontal, avisos de arquivo faltando, narração (com voz simulada).
- **Não testado:** a voz real (edge-tts) — o ambiente não tem acesso. Teste no seu PC.

## Evolução
- **V2:** transição entre cenas (fade), abaixar a música durante a fala, miniatura automática.
- **V3:** gerar as cenas automaticamente por API oficial de vídeo (Runway/Luma/Kling) a partir dos prompts.
- **V4:** roteiro por IA e rotina de publicação (com aprovação humana).
