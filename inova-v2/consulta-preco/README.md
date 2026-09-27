# Consulta de Preço (V3)

Dado o código **CATMAT** (material) ou **CATSER** (serviço) de um item de
licitação, busca no **Compras.gov.br — Dados Abertos** (API oficial,
pública, sem autenticação) o histórico de compras públicas homologadas
com esse item e resume menor/maior/média/mediana de preço — pra ajudar
a decidir o valor a ofertar. Isso é **apoio à decisão**, não substitui
olhar seu próprio custo e margem antes de fechar o preço.

Módulo independente — não altera `cadastro-empresas`, `alerta-editais`
nem `notificar-whatsapp`.

## Como descobrir o código CATMAT/CATSER de um item

Este script não busca por palavra-chave, só por código. Pra achar o
código do item de uma licitação:

1. Abra o [Painel de Preços](https://paineldeprecos.planejamento.gov.br/)
   e pesquise pelo nome do produto/serviço — ele mostra o código CATMAT
   (material) ou CATSER (serviço) de cada item.
2. Ou veja o edital/anexo da licitação — muitos já trazem o código do
   item do catálogo.

## Como usar

1. Instale a dependência:
   ```
   pip install -r requirements.txt
   ```
2. Rode:
   ```
   python consultar_preco.py <codigo> [material|servico] [codigoItemCatalogo|codigoPdm]
   ```
   Exemplo (material, código CATMAT 443990):
   ```
   python consultar_preco.py 443990
   ```
   Exemplo explícito com todos os parâmetros:
   ```
   python consultar_preco.py 443990 material codigoItemCatalogo
   ```

O script busca compras dos últimos 365 dias (ajustável na constante
`JANELA_DIAS` no topo do arquivo), mostra quantos registros achou, o
resumo estatístico e as últimas 10 compras encontradas (data, órgão,
preço, quantidade, fornecedor) pra você revisar.

## `codigoItemCatalogo` vs `codigoPdm`

- **`codigoItemCatalogo`** — o código específico do item (o mais comum).
- **`codigoPdm`** — código do "Padrão Descritivo de Material", um
  agrupamento mais genérico (várias variações do mesmo tipo de item).
  Use quando não achar resultado pelo código específico, ou quiser uma
  amostra maior.

## ⚠️ Pendência de verificação

- O endpoint de **material** (`1_consultarMaterial`, parâmetros
  `tipo`/`codigo`) foi confirmado por três fontes cruzadas (manual
  oficial, discussão de um bug real corrigido nessa mesma API, e código
  de um projeto que consome essa API de verdade) — mas **não pude
  rodar uma chamada real daqui**, porque este sandbox bloqueia
  `dadosabertos.compras.gov.br` (mesma política que já impediu testar
  a BrasilAPI, o PNCP e o WhatsApp nos outros módulos).
- O endpoint de **serviço** (`3_consultarServico`) segue por analogia o
  mesmo padrão `tipo`/`codigo` do material — isso é uma suposição
  razoável, mas **menos confirmada**. Antes de confiar nele, teste com
  um código CATSER conhecido, e se der erro 404, confira o nome exato
  do endpoint no Swagger oficial:
  https://dadosabertos.compras.gov.br/swagger-ui/index.html

Testei offline o resumo estatístico (menor, maior, média, mediana,
ignorando preço zero/vazio) com dados simulados — bateu certo.

## Próximos passos (evolução futura)

- Ligar isso no `alerta-editais`: quando um edital tiver código
  CATMAT/CATSER nos itens (o PNCP disponibiliza isso em outro endpoint,
  ainda não explorado), consultar o preço automaticamente e já incluir
  a faixa de valor no e-mail/WhatsApp de alerta.
- Buscar por palavra-chave em vez de exigir o código de antemão (exige
  confirmar se a API de catálogo do Compras.gov.br permite isso).
