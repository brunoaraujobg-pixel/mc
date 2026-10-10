# Canal Dark — gerador de vídeo 100% gratuito (versão 1)

Transforma um **roteiro de texto** em um **vídeo .mp4** (voz + imagens + zoom suave),
sem pagar nenhuma ferramenta.

## Contexto e objetivo (decisão do Bruno)
- **Objetivo:** criar uma fonte de **renda fora do escritório** com um canal dark.
- **Não há dívida.** O ponto é o medo de gastar e não ter retorno. Por isso a versão 1 usa só ferramentas gratuitas.
- **Regra de investimento:** só gastar dinheiro depois que o teste de 30 dias mostrar sinal de retorno (ver "Regras do canal").
- Gastos futuros possíveis, um de cada vez e só se o canal pegar: voz melhor, banco de imagens/vídeos, edição.

## O que usa (tudo grátis)
| Etapa | Ferramenta | Observação |
|---|---|---|
| Voz | `edge-tts` (vozes Microsoft pt-BR) | grátis, sem cadastro, qualidade boa |
| Imagem | Pollinations.ai | grátis, sem cadastro; qualidade média |
| Slide de texto | Pillow | plano B se a imagem falhar |
| Montagem | FFmpeg | grátis |

Se a voz ou a imagem falharem, o app **não quebra**: usa silêncio / slide de texto e avisa na tela.

## Instalar (Windows, uma vez só)
1. Instale o Python: https://www.python.org/downloads/ (marque **"Add Python to PATH"**).
2. Instale o FFmpeg: abra o PowerShell e rode `winget install Gyan.FFmpeg`. Feche e abra o PowerShell de novo.
3. Na pasta `canal-dark`, rode: `pip install -r requirements.txt`

## Usar
```
python gerar_video.py exemplos/roteiro.txt
```
Resultado: `saida/roteiro/video.mp4`.

## Formato do roteiro
Cada cena é um bloco separado por linha em branco:
```
TITULO: texto grande que aparece no slide (opcional)
IMAGEM: descrição da imagem em inglês (opcional)
Texto que será narrado.
```
- Com `IMAGEM:` → tenta gerar a imagem; sem ela (ou se falhar) → slide de texto.
- Escreva números por extenso na narração ("oitenta e um mil") para a voz ler certo.

## Regras para o canal (teste de 30 dias)
1. **Revise todo roteiro fiscal.** IA erra alíquota e regra; confira na fonte oficial.
2. Vídeos de 3 a 6 minutos, mesmo nicho, 2 a 3 por semana, mínimo 8 vídeos.
3. Só use imagem/vídeo/música livres ou gerados por você (evita bloqueio de direitos).
4. O YouTube não monetiza conteúdo em massa e repetitivo: cada vídeo precisa de análise real.
5. Métricas depois de 30 dias: CTR da miniatura (>4%), retenção (>40%), inscritos.

## Testado
- Geração do vídeo com slides e silêncio (plano B): OK.
- Voz e imagem online: NÃO testados no ambiente da sessão (rede bloqueada). **Teste no seu PC** e me diga o resultado.

## Próximas versões
- V2: legendas queimadas no vídeo e música de fundo livre; imagens de banco gratuito (Pexels API).
- V3: agente de IA que gera o roteiro e a pesquisa de temas.
- V4: miniatura automática e agendamento de postagem.
