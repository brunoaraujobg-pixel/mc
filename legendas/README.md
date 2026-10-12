# Legendas em Lote (YouTube + Instagram)

Script em Python que gera legendas em **português** para vários vídeos de uma vez.

Para cada vídeo da pasta `entrada/` ele cria na pasta `saida/`:

| Arquivo | Para quê |
|---|---|
| `nome.srt` | Legenda para subir no **YouTube** (Studio > Legendas > Enviar arquivo) |
| `nome_legendado.mp4` | Vídeo com **legenda animada** gravada (palavra falada em destaque, com "pulinho"). Use no **Instagram/Reels** |
| `nome_link.txt` | Link pronto para colar na descrição (só se você configurar o link) |
| `log_legendas.txt` | Histórico do que foi feito e erros |

- Os vídeos originais **não são alterados nem movidos**.
- Vídeo já processado é **pulado** (não duplica). Para refazer, apague os arquivos dele da `saida/`.
- Se um vídeo der erro, o script registra no log e continua com os outros.
- A transcrição roda **no seu computador** (offline depois de baixar o modelo). Nada é enviado para a internet.

## Sobre o "link"

O Instagram **não permite link clicável na legenda do post**. Por isso o script mostra um texto
(ex.: `Link na bio` ou `meusite.com.br/contato`) em uma faixa no topo do vídeo, nos primeiros e
últimos segundos. No YouTube, cole o link na descrição.

## Instalação (Windows) — uma vez só

1. **Python 3**: https://www.python.org/downloads/ (marque **"Add Python to PATH"** na instalação).
2. **FFmpeg**: abra o PowerShell e rode:
   ```
   winget install Gyan.FFmpeg
   ```
   Feche e abra o PowerShell de novo. Teste com `ffmpeg -version` (deve aparecer a versão).
3. Na pasta `legendas`, instale a biblioteca de transcrição:
   ```
   pip install -r requirements.txt
   ```

## Como usar

1. Coloque os vídeos (`.mp4`, `.mov`, `.mkv`...) na pasta `entrada/` (o script cria a pasta se não existir).
2. (Opcional) Abra `legendar_videos.py` e ajuste o bloco **CONFIGURAÇÕES** no começo:
   ```python
   LINK_TEXTO = "Link na bio"      # ou "meusite.com.br/contato"; "" = sem link
   MODELO = "small"                # "medium" é mais preciso, porém mais lento
   COR_DESTAQUE = "00D7FF"         # cor da palavra falada (RRGGBB)
   ```
3. Rode:
   ```
   python legendar_videos.py
   ```
4. Pegue os resultados em `saida/`.

**O que deve aparecer:** mensagens como `Transcrevendo: video1.mp4` → `Gravando legenda animada` → `OK`.
Na primeira execução ele baixa o modelo (~500 MB no `small`); depois não baixa mais.

## Problemas comuns

- `'ffmpeg' não é reconhecido` → FFmpeg não instalado ou terminal não reaberto (passo 2).
- `No module named faster_whisper` → rode o passo 3 de novo.
- Lento → normal sem placa de vídeo. Use `MODELO = "base"` para ganhar velocidade (menos precisão).
- Palavras técnicas erradas (ex.: "CFOP", "DIFAL") → revise o `.srt` antes de subir no YouTube.
  Evolução futura: dicionário de termos contábeis para corrigir automaticamente.

## Roteiro de evolução

- **V1 (esta):** pasta de entrada → SRT + vídeo com legenda animada + link.
- **V2:** dicionário de termos contábeis; vários estilos de legenda; formato 9:16 automático.
- **V3:** monitorar a pasta e processar sozinho quando chegar vídeo novo.
- **V4:** publicação automática via APIs oficiais (YouTube Data API; Instagram Graph API).

## Limitações

- A qualidade depende do áudio. Ruído e fala sobreposta geram erros.
- Não há API oficial do Instagram para enviar legenda separada: por isso a legenda é gravada no vídeo.
