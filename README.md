# mc

Repositório de projetos e automações do escritório contábil.

Cada pasta na raiz é um projeto independente, com seu próprio `README.md`.

## Projetos

- [`organizar-documentos/`](organizar-documentos/) — organiza automaticamente
  os documentos do escritório em subpastas por agente/assunto (Simples
  Nacional, Lucro Presumido, Lucro Real, ICMS/ICMS-ST, PIS/COFINS,
  eSocial/Folha, Federal).
- [`download-ricms-pe-pi/`](download-ricms-pe-pi/) — baixa, valida e
  organiza os Regulamentos do ICMS de Pernambuco (Decreto 44.650/2017) e
  do Piauí (Decreto 21.866/2023) a partir das fontes oficiais da SEFAZ.
- [`inova-v2/`](inova-v2/) — sistema próprio de licitações, separado do
  Inova original (que continua intocado): cadastro de empresas com CNAE
  automático, alerta de edital por e-mail (via PNCP), notificação por
  WhatsApp e consulta de preço praticado (via Compras.gov.br) já
  prontos; robô de lances/precificação avaliado em conversa, ainda não
  construído (decisão em aberto: assinar/revender um serviço existente
  em vez de construir do zero).
