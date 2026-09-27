# Inova v2

Sistema próprio de automações do fluxo de licitações do escritório —
**separado do Inova original**, que continua intocado (este projeto não
lê nem escreve no banco de dados nem em nenhuma tela do Inova atual). O
nome é porque a ideia nasceu de evoluir o que o Inova faz hoje (avisar
data de licitação, ajudar a precificar), só que construído do zero,
por fora do sistema existente.

Pensado pra crescer por módulos, cada um numa subpasta.

## Módulos

- [`cadastro-empresas/`](cadastro-empresas/) — **pronto (V1)**. Cadastra
  empresa pelo CNPJ, busca o CNAE automaticamente, guarda e-mail e
  telefone (WhatsApp) e marca qual empresa está ativa. Base pros
  módulos abaixo.
- [`alerta-editais/`](alerta-editais/) — **pronto (V2)**. Busca no PNCP
  (API oficial) os editais publicados nos últimos dias, compara com os
  CNAEs da empresa ativa e avisa por e-mail o que combinar.
- [`notificar-whatsapp/`](notificar-whatsapp/) — **pronto**. Manda a
  mesma notificação por WhatsApp (API oficial da Meta), usando o
  telefone cadastrado. Exige configurar uma conta Meta Business antes
  de funcionar de verdade — ver README do módulo.
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
