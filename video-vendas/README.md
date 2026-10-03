# Vídeo Vendas (V1)

Transforma 3 a 5 fotos/clipes **seus (ou autorizados)** de um produto em um
vídeo vertical 9:16 de 15 a 25 s para TikTok e Shopee Vídeo, e gera título,
legenda e hashtags com o link do anúncio. **Você posta manualmente.**

## Como funciona (resumo)

```
produtos/<produto>/  (suas fotos + produto.txt)   -->  saida/<produto>/video.mp4
                                                        saida/<produto>/postagem.txt
```

Seus arquivos originais **nunca** são alterados nem apagados. Se rodar de novo,
cria `video_2.mp4`, `postagem_2.txt`... sem sobrescrever.

## Passo a passo no Windows

**1. Python** — baixe em https://www.python.org/downloads/ e instale marcando
**"Add Python to PATH"**. Teste no Prompt de Comando: `python --version`

**2. FFmpeg** — no Prompt de Comando: `winget install Gyan.FFmpeg`. Feche e abra
o Prompt de novo. Teste: `ffmpeg -version` (deve mostrar a versão).

**3. Bibliotecas** — dentro da pasta `video-vendas`:
```
pip install -r requirements.txt
```

**4. Chave do Claude (para o texto)** — crie conta em https://console.anthropic.com,
gere uma chave de API e salve-a sozinha em um arquivo `chave_anthropic.txt` dentro
da pasta `video-vendas` (esse arquivo não vai para o GitHub). Custa centavos por produto.
Se não quiser IA agora: no `config.ini`, mude para `usar_ia = nao` (texto simples fixo).

**5. Celular (ntfy)** — instale o app **ntfy** (Android/iPhone), toque em "+" e
assine um nome secreto, por exemplo `bruno-videos-7x92kq`. Escreva o MESMO nome em
`ntfy_topico` no `config.ini`. Você recebe aviso de "pronto" e de erro.

**6. Músicas** — coloque 1 ou mais músicas sem direito autoral (.mp3/.m4a/.wav)
na pasta `musicas/`. Sem música, o vídeo sai mudo (com aviso).

**7. Seu produto** — copie a pasta `produtos/exemplo`, renomeie (ex.: `fone-x`),
coloque 3 a 5 fotos/clipes e preencha o `produto.txt` com dados **reais**.
Escreva `midia_autorizada: sim` somente se a mídia for sua ou autorizada.

**8. Rodar**
```
python video_vendas.py fone-x
```
Aparece:
```
[validar] 4 mídias, cadastro completo
[video] video.mp4 (música: minha-musica.mp3)
[validar-video] 1080x1920, 20.0s
[texto] postagem.txt
PRONTO! Veja a pasta: ...\saida\fone-x
```
Abra `saida\fone-x\postagem.txt` e copie o bloco "TEXTO PRONTO PARA COLAR".

## Escolher produtos mais vendidos (afiliado Shopee) - V1.5

Para você que já é afiliado. O programa pergunta à API oficial de afiliados da
Shopee quais produtos de **casa e festa** mais vendem, filtra e pontua, e cria
as pastas em `produtos/` já com nome, preço, **seu link de afiliado** e fatos
reais (vendas, nota, loja).

**Passo a passo (no PC):**
1. No painel de afiliados (affiliate.shopee.com.br) abra **Open API** e copie o
   **App ID** e o **Secret**. Crie `chave_shopee.txt` nesta pasta: linha 1 = App ID,
   linha 2 = Secret. (Não vai para o GitHub. Nunca cole o Secret em chats.)
2. Teste a conexão: `python testar_shopee.py`. Deve mostrar "OK! A Shopee devolveu...".
   **Se mostrar erro, copie a mensagem e me envie**: o código foi escrito sem acesso à
   documentação oficial e pode precisar de um pequeno ajuste de campo.
3. Escolher: `python escolher_produtos.py` (cria até 5 produtos novos, filtros no
   `config.ini` > `[shopee]`). Você recebe um aviso no celular.
4. **Única parada obrigatória:** em cada pasta nova, coloque 3 a 5 fotos/clipes
   **seus ou autorizados** e escreva `midia_autorizada: sim`. O programa NÃO baixa
   as imagens da Shopee (mídia de terceiros só com autorização).
5. Gerar tudo de uma vez: `python video_vendas.py --todos`. Faz os vídeos de todos os
   produtos que já têm mídia e `sim`, e avisa quantos ficaram aguardando mídia.
6. Poste manualmente usando o `postagem.txt`. **Confira o preço no anúncio antes de postar.**

Pontuação = vendas x (preço x comissão). Produtos já escolhidos não se repetem
(`fila/vistos.txt`); o ranking do dia fica em `fila/ranking_AAAA-MM-DD.csv`.

## O que o programa confere

- Pasta existe, 3 a 5 mídias, cadastro completo, `midia_autorizada: sim` (senão **para**).
- Vídeo abre, é 9:16 e tem de 15 a 30 s.
- Texto da IA: números e promessas ("garantia", "frete grátis", "melhor"...) que
  **não estão no cadastro** reprovam o texto (tenta de novo até 3 vezes).
- O link do anúncio está no `postagem.txt` (inserido pelo programa, não pela IA).
- Cada etapa vai para `log.csv` (abre no Excel).

## Erros comuns

| Mensagem | O que fazer |
|---|---|
| `'ffmpeg' não encontrado` | Refaça o passo 2 e abra um Prompt novo |
| `midia_autorizada não está como 'sim'` | Só escreva `sim` se a mídia for sua/autorizada |
| `Encontrei N fotos/clipes` | Deixe de 3 a 5 arquivos na pasta do produto |
| `Chave da API do Claude não encontrada` | Passo 4, ou `usar_ia = nao` |
| `Nenhuma fonte encontrada` | `config.ini` → `fonte` apontando para um `.ttf` |
| `Notificação desligada` | Passo 5 (só um aviso, o vídeo é gerado igual) |
| Texto reprovado 3 vezes | Deixe o `produto.txt` mais claro ou use `usar_ia = nao` |

## Próximas versões

- **V2:** agendamento (TikTok Content Posting API / Metricool / Shopee) — só depois
  de pesquisar a documentação oficial atual e você escolher o caminho.
- **V3:** métricas (views, cliques) e sugestão de quais produtos repetir.
