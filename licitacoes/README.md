# Licitações

Automações para o fluxo de licitações do escritório — pensado pra crescer
por módulos, cada um numa subpasta, sem depender do sistema Inova (fica
de fora, intocado).

## Módulos

- [`cadastro-empresas/`](cadastro-empresas/) — **pronto (V1)**. Cadastra
  empresa pelo CNPJ, busca o CNAE automaticamente e marca qual empresa
  está ativa. Base pros módulos abaixo.
- **Alerta de edital por e-mail** — avaliado, ainda não construído.
  Depende de decidir a fonte dos editais (PNCP tem API oficial; dá pra
  usar os CNAEs da empresa ativa cadastrada acima como filtro).
- **Robô de lances / precificação** — avaliado em conversa: já existem
  vários produtos maduros no mercado (ContrataX, Licitei, WaveCode,
  Lance Fácil, eLicitaDisputa) cobrando na faixa de R$70-400 por
  empresa/mês, incluindo planos multi-CNPJ pensados pra
  assessoria/contador com vários clientes. Decisão em aberto: assinar e
  revender esse serviço em vez de construir do zero (ver conta de
  precificação feita — calculadora publicada na conversa).
- **Consulta de preço** — futuro. Cruzar item da licitação com
  referência oficial (ex: Painel de Preços do governo) pra ajudar a
  decidir o valor a ofertar.

## Convenção

Cada módulo é uma subpasta com seu próprio `README.md`, script e
`requirements.txt`, seguindo a mesma regra do resto do repositório
(ver `CLAUDE.md` na raiz).
