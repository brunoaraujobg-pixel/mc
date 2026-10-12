# Teste de ponta a ponta (5 cenas)

Roda o fluxo inteiro: **cenas + sons + música + voz + legenda animada + transição + miniatura**.
Primeiro com arquivos de **ensaio** (sem gastar créditos de IA), depois com as cenas reais.

## Parte 1: ensaio (5 minutos, sem gerar nada no Kling)
Dentro da pasta `montar-historia`:
```
python teste-5-cenas/gerar_arquivos_teste.py
python montar_historia.py teste-5-cenas/pokemon.txt
```
**O que deve aparecer:** `Cena 1/5 ... Juntando as cenas... Colocando a música... Miniatura... PRONTO`,
e o vídeo abre sozinho. Os arquivos ficam em `saida/pokemon/`:
`historia.mp4` e `historia_miniatura.jpg`.

**Confira no vídeo de ensaio:**
- [ ] A voz fala o texto de cada cena (cena 3 e 4 também).
- [ ] A legenda animada aparece com a palavra falada em amarelo.
- [ ] Cada cena entra e sai do preto (transição suave).
- [ ] A música abaixa quando a voz fala.
- [ ] Os efeitos tocam nos segundos certos (passos, suspense, raio aos 1,5 s, decolagem aos 3,5 s).
- [ ] A miniatura tem o título com "Emboscada" em amarelo.
- [ ] O vídeo dura uns 23 a 25 s.

Se algum item falhar, anote qual e a mensagem que apareceu, e me mande.

## Parte 2: cenas reais
1. Gere as 5 cenas com os prompts de `prompts_cenas.md` (todas na vertical, 9:16).
2. Salve em `montar-historia/cenas/` com **os mesmos nomes** (`01_caminhada.mp4` ... `05_reencontro.mp4`).
   Isso substitui o ensaio.
3. Troque os sons de ensaio por sons reais em `sons/` (mesmos nomes) e a música em `musicas/`.
4. Rode de novo: `python montar_historia.py teste-5-cenas/pokemon.txt`.
   O resultado não sobrescreve o anterior: cria `historia_2.mp4`.

## Ajustes comuns (no arquivo `pokemon.txt`)
- Voz offline: `MOTOR_VOZ: piper` e `VOZ: pt_BR-faber-medium`.
- Sem narração em alguma cena: apague o trecho `| FALA: ...` dessa linha.
- Sem fade: `TRANSICAO: corte`. Música mais alta: `VOLUME_MUSICA: 0.3`.
- Outro título de miniatura: `TITULO_MINIATURA: ...` (palavra entre `*asteriscos*` = amarelo).
- Se a voz for mais longa que a cena, o último quadro da cena fica parado até ela terminar.
