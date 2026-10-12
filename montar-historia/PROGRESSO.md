# Progresso: onde paramos

Arquivo para salvar o estado do trabalho (útil antes de reiniciar o Windows). Atualizado em 2026-10-12.

## Já pronto e TESTADO no seu PC
- [x] `montar-historia`: junta cenas + sons + música (abaixa na fala) + voz + legenda animada + transição suave
- [x] Voz em português: `edge` (online) e `piper` (offline)
- [x] Miniatura automática (`miniatura.py`)
- [x] Teste de ponta a ponta com as 5 cenas de ensaio (`teste-5-cenas/`)
- [x] `historia.srt` (legenda para o YouTube)
- [x] `legendas/` (transcrição Whisper em lote, `.srt` + legenda animada)
- [x] `ouvir_voz.py` (ouvir as vozes antes de montar)

## Pronto, MAS AINDA NÃO testado no seu PC
- [ ] **Kit de publicação** (`historia_publicacao.txt`): título, descrição, hashtags e passos para YouTube/Instagram.
      Está num PR aberto (veja abaixo). Depois de mesclar e `git pull`, rode o teste de ponta a ponta de novo e abra o `.txt`.

## O que falta fazer (depende de você)
1. **Gerar as 5 cenas reais** no Kling/Runway/Luma com `montar-historia/teste-5-cenas/prompts_cenas.md`
   (todas na vertical 9:16). Salvar em `montar-historia/cenas/` com os mesmos nomes do ensaio.
2. **Sons e música reais** de biblioteca livre (Pixabay, YouTube Audio Library) em `sons/` e `musicas/`.
3. Rodar de novo e conferir. Depois postar manualmente com o kit de publicação.
4. (Opcional) Instalar o Claude Code no PC: `irm https://claude.ai/install.ps1 | iex` (PowerShell), depois `claude --version`.

## Como retomar depois de reiniciar o Windows
```
cd C:\PROJETOS\mc
git pull
cd montar-historia
python montar_historia.py teste-5-cenas/pokemon.txt
```
O vídeo fica em `montar-historia\saida\pokemon\historia.mp4` (e abre sozinho). Guia completo: `GUIA-RAPIDO.md`.

Se o `git pull` disser que há mudanças locais: `git status` mostra o que mudou; os arquivos dentro de
`cenas/`, `sons/`, `musicas/`, `vozes/` e `saida/` são ignorados pelo Git e não atrapalham.

## Cuidados
- Pokémon, Raichu e Equipe Rocket são da Nintendo/The Pokémon Company: em canal **monetizado** há risco de bloqueio.
- Não suba certificado digital, senhas ou chaves para o GitHub.
- Os programas não publicam nada sozinhos.

## Histórico dos PRs (todos mesclados na `main`, exceto o último)
#18 legendas + montar-historia · #19 abrir resultado · #20 ouvir_voz · #21 V2 (transição/música) ·
#22 voz offline · #23 miniatura · #24 teste de ponta a ponta · #25 `.srt` YouTube + guia ·
**kit de publicação (PR aberto)**
