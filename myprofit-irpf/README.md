# myProfit → Apoio à Declaração de IR e Evolução da Carteira

Ferramenta para tirar o máximo dos relatórios exportados do myProfit
(PDF/Excel) para duas coisas: (1) montar a Ficha de Bens e Direitos da
declaração do ano seguinte, comparando com a declaração anterior, e (2)
acompanhar a evolução da carteira de investimentos ao longo do tempo.

## O que NÃO faz (e por quê)

Não gera um arquivo `.DEC` pronto para importar direto no programa da
Receita Federal. O `.DEC` é um formato proprietário, **não documentado
publicamente** e que muda de versão para versão do programa (PGD) — não
existe forma segura de gerar esse arquivo por fora sem risco real de
corromper a declaração do cliente ou entregar valor errado à Receita.
Em vez disso, a ferramenta gera uma **planilha de apoio** já organizada,
para você digitar manualmente na ficha — sem esse risco.

## Objetivo

1. Ler os relatórios do myProfit (posição consolidada, proventos,
   operações e/ou relatório de IR, em PDF ou Excel).
2. Cruzar com os dados da declaração do ano anterior (Ficha de Bens e
   Direitos — vindos do Domínio ou de PDF/planilha da declaração
   entregue).
3. Gerar uma planilha de conciliação: ativo, situação em 31/12 do ano
   anterior x situação atual, discriminação, e o que mudou (ativo novo,
   quantidade/custo diferente, ativo baixado/vendido totalmente).
4. Gerar visões de acompanhamento da carteira: evolução patrimonial mês a
   mês, dividendos recebidos (por ano/mês/ativo), alocação por
   segmento e ativo (ex.: ações x FIIs), maiores perdas/ganhos.

## Arquitetura (primeira versão)

- **Importador** (`importar_myprofit.py`): lê o(s) arquivo(s) exportado(s)
  do myProfit e normaliza os dados (ativo, quantidade, preço médio, custo
  total, proventos, data).
- **Dados da declaração anterior**: por ora, entrada manual em planilha
  (`declaracao_anterior.xlsx`) com uma linha por bem (código, discriminação,
  situação em 31/12 do ano anterior) — você preenche a partir do Domínio ou
  da ficha já entregue. Não lemos o `.DEC` diretamente (ver seção acima).
- **Conciliação** (`conciliar_declaracao.py`): cruza os dois e gera
  `planilha_apoio_declaracao_<ano>.xlsx`.
- **Evolução da carteira** (`evolucao_carteira.py`): a partir do histórico
  do myProfit, gera `evolucao_carteira_<ano>.xlsx` com abas de patrimônio
  mensal, dividendos e alocação.

## Dados necessários (para eu conseguir codar o importador de verdade)

Preciso de pelo menos um exemplo real exportado do myProfit (pode
anonimizar valores/nomes de ativos, mas mantenha a estrutura de colunas/
layout):

- Relatório de **Posição Consolidada** (Excel ou PDF).
- Relatório de **Proventos** (Excel ou PDF).
- Se tiver, o **relatório de IR** que o próprio myProfit gera.

E como você tem a Ficha de Bens e Direitos da declaração anterior
disponível hoje (export do Domínio, PDF da ficha entregue, ou outra
planilha) — para eu montar o formato de entrada certo.

## Como usar (Windows)

1. Instale o Python 3 (https://www.python.org/downloads/, marcando
   "Add Python to PATH").
2. Nesta pasta, instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. (a definir junto com o importador, depois que eu tiver o arquivo de
   exemplo real do myProfit)

## Versões

- **V1** (em andamento): importar 1 relatório de posição + proventos do
  myProfit de uma carteira, gerar planilha de conciliação com a
  declaração anterior e 3 visões básicas de evolução da carteira.
- **V2**: incluir histórico de compra/venda, ranking de maiores
  perdas/ganhos.
- **V3**: simulador de meta patrimonial (ex.: "chegar a R$ 1 milhão") e
  sugestão de rebalanceamento por segmento/ativo (cálculo de alocação
  atual x meta — não envia ordem para corretora).
- **V4**: painel web interativo, suporte a múltiplos clientes/carteiras.

## Riscos e limitações

- Layout dos relatórios do myProfit pode variar por plano/versão — o
  importador é ajustado contra arquivo real, não por suposição.
- Dados da declaração anterior não vêm do `.DEC` (ver seção acima); a
  qualidade da conciliação depende da planilha de entrada estar correta.
- Nenhum dado fiscal é inventado: o que não for encontrado no arquivo é
  reportado como pendência, não estimado.
