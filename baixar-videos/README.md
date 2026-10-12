# Baixar Vídeos do Instagram (Instaloader)

Script simples em Python, baseado no **Instaloader**
(https://github.com/instaloader/instaloader), para baixar vídeos de links
(Reels e posts) ou de um perfil inteiro.

**Uso: somente estudo e uso pessoal.** Os vídeos ficam apenas no seu PC,
na pasta `videos_baixados/` (ela está no `.gitignore`, então nunca vai
para o GitHub). Não republique conteúdo de terceiros.

## Instalação (uma vez só)

1. Instale o Python em python.org (marque **"Add Python to PATH"**).
2. Abra o CMD dentro desta pasta e rode:
   `pip install -r requirements.txt`

## Como usar

1. Cole os links no arquivo `links.txt` (um por linha).
2. Rode: `python baixar_videos.py`
3. Os vídeos aparecem em `videos_baixados/`.

Também dá para passar o link direto:
`python baixar_videos.py "https://www.instagram.com/reel/XXXX/"`

## Baixar todos os vídeos de um perfil

`python baixar_videos.py --perfil nome_do_perfil`

## Se pedir login / der erro

1. Faça login uma vez: `instaloader --login SEU_USUARIO`
2. Use: `python baixar_videos.py --usuario SEU_USUARIO`
- Atualize o Instaloader (o Instagram muda sempre):
  `pip install -U instaloader`
- Use uma conta secundária: muitas baixadas seguidas podem bloquear a conta.

## O que o script faz

- Lê os links, baixa cada um e continua mesmo se um falhar.
- Guarda em `historico.txt` os links já baixados para não repetir.
- Salva a legenda de cada vídeo em um `.txt` (útil para estudo).
- Mostra no final quantos baixaram e quais falharam.

## Limitações

O Instagram não tem API oficial para isso; o Instaloader usa métodos
não oficiais e pode parar de funcionar até sair uma atualização.

## Evolução futura

- Versão 2: baixar só o áudio, ou transcrever o vídeo (para estudo).
- Versão 3: organizar por perfil/assunto e gerar resumo com IA.
