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
5. Pegue o vídeo em `saida/historia/historia.mp4`. Se houver `FALA:`, sai também `historia.srt`, a **legenda para
   o YouTube** (Studio > Legendas > Enviar arquivo). A legenda animada gravada no vídeo serve para o Instagram.
   Os tempos do `.srt` acompanham as cenas e a voz; revise antes de subir, pois a divisão por palavra é aproximada. Se rodar de novo, cria `historia_2.mp4` (não sobrescreve).

**O que deve aparecer:** `Cena 1/5 ... Juntando as cenas... PRONTO`. Ao terminar, o vídeo **abre sozinho**
(para desligar, troque `ABRIR_AO_TERMINAR = True` por `False` no começo do `montar_historia.py`).

## Formato do arquivo da história
```
FORMATO: vertical            # vertical (1080x1920) ou horizontal (1920x1080)
MUSICA: musica_heroica.mp3   # opcional
VOLUME_MUSICA: 0.15          # 0.15 = baixa
TRANSICAO: fade              # fade = suave entre cenas; corte = corte seco (padrão)
TRANSICAO_SEGUNDOS: 0.3
ABAIXAR_MUSICA: sim          # música abaixa sozinha durante a narração (padrão: sim)
TITULO_MINIATURA: O *SEGREDO* da floresta   # opcional: cria a miniatura (palavra entre *asteriscos* = amarelo)
FORMATO_MINIATURA: auto      # auto | youtube (1280x720) | capa (1080x1920)
LEGENDA: sim                 # legenda animada onde houver FALA
MOTOR_VOZ: edge              # edge (online) | piper (offline) | windows (offline)
VOZ: pt-BR-FranciscaNeural   # nome da voz; depende do motor (veja abaixo)

CENA | 01_caminhada.mp4 | SOM: passos_mata.mp3@0 | FALA: Texto narrado
CENA | 04_raichu.mp4 | SOM: raio.mp3@1.5 | SOM: decolagem.mp3@3.5
```
- `SOM: arquivo@segundo` → toca naquele segundo da cena. Pode repetir `SOM:` várias vezes.
- `FALA:` é opcional. Escreva números por extenso ("oitenta e um mil").
- Linhas com `#` são comentários.
- Use o **mesmo formato** (vertical/horizontal) ao gerar as cenas; se for diferente, o programa corta as bordas.

## Ouvir as vozes antes de montar
Quer testar o texto e escolher a voz sem montar o vídeo inteiro?
```
python ouvir_voz.py "Maria e suas amigas caminhavam alegres pela floresta."
python ouvir_voz.py exemplos/historia.txt          (usa a 1ª FALA do arquivo)
python ouvir_voz.py "Seu texto" --velocidade -10   (10% mais devagar; +10 = mais rápido)
python ouvir_voz.py "Seu texto" --motor piper       (vozes offline; ou --motor windows)
```
Ele gera o mesmo texto com as 3 vozes (Francisca, Antonio, Thalita) em `saida/teste_voz/`,
**toca uma depois da outra** (diz o nome de cada uma na tela) e depois **abre a pasta**.
Para só gerar, sem tocar, acrescente `--mudo`. O som usa o `ffplay`, que já vem com o FFmpeg. Depois, coloque a voz escolhida na linha `VOZ:` do arquivo
da história (ex.: `VOZ: pt-BR-AntonioNeural`). Precisa de internet.

## Voz OFFLINE (sem internet)
O padrão (`MOTOR_VOZ: edge`) usa a voz da Microsoft e **precisa de internet**. Para trabalhar offline:

| Motor | Qualidade | Instalar | Linha no arquivo da história |
|---|---|---|---|
| `piper` | Boa (neural) | `pip install piper-tts==1.8.0` | `MOTOR_VOZ: piper` e `VOZ: pt_BR-faber-medium` |
| `windows` | Mais robótica | `pip install pyttsx3==2.99` | `MOTOR_VOZ: windows` e `VOZ: Maria` |

- **Piper:** na **primeira vez** ele baixa a voz (internet só nessa vez) para a pasta `vozes/`; depois funciona
  100% offline. Vozes em português do Brasil que eu conheço: `pt_BR-faber-medium`, `pt_BR-cadu-medium`,
  `pt_BR-jeff-medium`. Para ver a lista atual: `python -m piper.download_voices`. O Piper é licenciado
  como GPL-3.0 (sem problema para uso próprio).
- **Windows:** usa as vozes que já vêm no sistema. Se não achar voz em português, adicione em
  *Configurações > Hora e idioma > Fala > Adicionar vozes*.
- Para ouvir antes de montar: `python ouvir_voz.py "Seu texto" --motor piper` (ou `--motor windows`).
- Se a voz falhar, a cena fica sem narração e o programa avisa. Ele não trava.
- Os motores offline gravam `.wav`; o resto do programa funciona igual.

## Miniatura automática
Com a linha `TITULO_MINIATURA:` no arquivo da história, o programa cria uma `historia_miniatura.jpg`
ao lado do vídeo: escolhe sozinho o **quadro mais nítido e colorido das cenas originais** (assim a legenda
gravada no vídeo não aparece na miniatura), escurece a parte de baixo e escreve o
título grande com contorno. Palavras entre `*asteriscos*` ficam em **amarelo**.

Também funciona em qualquer vídeo, sem montar nada:
```
python miniatura.py saida/historia/historia.mp4 "O *SEGREDO* da floresta"
python miniatura.py video.mp4 "Título" --formato youtube   (1280x720; vídeo vertical ganha fundo desfocado)
python miniatura.py video.mp4 "Título" --formato capa      (1080x1920, capa de Reels/Shorts)
python miniatura.py video.mp4 "Título" --quadro 12         (usa o quadro do segundo 12)
```
- Precisa do `Pillow` (`pip install -r requirements.txt`).
- Nunca sobrescreve: se já existir, cria `_miniatura_2.jpg`.
- Dica: títulos curtos (3 a 6 palavras) funcionam melhor. O programa reduz a letra se o título for longo.
- A fonte usada é a Impact (ou Arial Negrito) do Windows; se não achar, usa outra.
- O quadro escolhido é automático e pode não ser o melhor: use `--quadro` para escolher o segundo.
- Rodando `miniatura.py` direto no vídeo final (com legenda gravada), a legenda pode aparecer no quadro:
  nesse caso use `--quadro` com um segundo sem legenda.

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
- **V2 (feita):** transição suave entre cenas e música que abaixa durante a fala.
- **V2.1 (feita):** voz offline (Piper e Windows). 
- **V2.2 (feita):** miniatura automática.
- **V3:** gerar as cenas automaticamente por API oficial de vídeo (Runway/Luma/Kling) a partir dos prompts.
- **V4:** roteiro por IA e rotina de publicação (com aprovação humana).
