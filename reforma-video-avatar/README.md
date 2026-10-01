# Reforma no seu bolso — Agente de Vídeo (avatar)

Transforma um roteiro APROVADO em vídeo vertical 9:16 (1080x1920) do avatar
do escritório falando com a voz do Bruno. A saída é só um arquivo para
aprovação humana: este projeto NUNCA publica nem agenda nada.

## Status

- [x] Estrutura criada
- [ ] Serviço de voz e de avatar confirmados (comparar na documentação oficial)
- [ ] Versão 1: gerar só o áudio (`saida\audio_AAAA-MM-DD.mp3`)
- [ ] Versão 2: vídeo do avatar com legenda (`saida\video_AAAA-MM-DD.mp4`)
- [ ] Versão 3: rotina por episódio

## Pastas no Windows

```
C:\reforma-no-seu-bolso\
  entrada\   avatar.png, voz_referencia.mp3/wav, roteiro.txt, .env
  saida\     audio_AAAA-MM-DD.mp3, video_AAAA-MM-DD.mp4
  log.csv    data, roteiro, serviço, duração, custo estimado, status
```

## Regras

1. Só a voz do próprio Bruno, com a gravação dele.
2. Falar exatamente o `roteiro.txt`; número/regra sem fonte oficial anotada: parar e avisar.
3. Todo vídeo do avatar é "conteúdo gerado por IA" (`isAiGenerated` no Metricool). Não substitui Reel.
4. Proibido publicar ou agendar.
5. Chaves só no `.env` (já ignorado pelo Git).

## Como conferir se o Windows está pronto

No Prompt de Comando: `python --version` e `ffmpeg -version`.
Se algum der erro, o agente explica a instalação passo a passo.
