# Alerta de Editais (V2)

Script em Python que avisa por e-mail quando aparece um edital que
parece ter a ver com o ramo da empresa que está marcada como **ativa**
no módulo [`cadastro-empresas`](../cadastro-empresas/). Depende desse
módulo — rode-o primeiro e cadastre/selecione a empresa antes de usar
este script.

## O que ele faz

1. Lê a empresa ativa e os CNAEs dela no banco do `cadastro-empresas`
   (`../cadastro-empresas/empresas.db`).
2. Tira palavras-chave da descrição de cada CNAE (ignorando termos
   genéricos de boilerplate, tipo "comércio", "atividades não
   especificadas anteriormente").
3. Consulta o [PNCP](https://pncp.gov.br/) — Portal Nacional de
   Contratações Públicas, API pública oficial, gratuita e sem
   autenticação — buscando editais publicados nos últimos dias.
4. Compara o objeto de cada licitação com as palavras-chave da empresa.
5. Se achar algo, mostra no console **e** manda um e-mail com a lista
   (órgão, objeto, datas de abertura/encerramento da proposta e o link
   pra abrir o edital).

**O PNCP não tem filtro por CNAE** — a comparação aqui é por
palavra-chave, um ponto de partida. Pode trazer falso positivo (edital
parecido mas não relevante) ou deixar passar algo cuja descrição não
bateu com nenhuma palavra do CNAE. Revise antes de decidir participar.

## Como usar

1. Rode primeiro o [`cadastro-empresas`](../cadastro-empresas/) e
   selecione a empresa ativa.
2. Instale a dependência:
   ```
   pip install -r requirements.txt
   ```
3. Teste sem enviar e-mail (só mostra no console):
   ```
   python buscar_editais.py --teste
   ```
4. Configure o e-mail (veja abaixo) e rode de verdade:
   ```
   python buscar_editais.py
   ```
5. Agende no **Agendador de Tarefas do Windows** pra rodar 1x por dia
   de manhã (Painel de Controle → Ferramentas Administrativas →
   Agendador de Tarefas → Criar Tarefa Básica → aponte pro `python.exe`
   com o caminho deste script como argumento).

## Como configurar o e-mail

O script lê usuário/senha de **variável de ambiente** (nunca coloque
senha direto no código). No Windows, no PowerShell:

```powershell
setx EMAIL_REMETENTE "seuemail@gmail.com"
setx EMAIL_SENHA_APP "sua-senha-de-app-de-16-letras"
setx EMAIL_DESTINATARIO "quem.deve.receber@empresa.com.br"
```

Depois de rodar o `setx`, **abra um terminal novo** pra variável valer.

Se usar Gmail, não é a senha normal da conta — é uma "senha de app":
ative a verificação em duas etapas na conta Google, depois vá em
myaccount.google.com → Segurança → Senhas de app, gere uma senha só
pra isso e use ela no `EMAIL_SENHA_APP`. Se usar Outlook/Office 365 do
escritório, troque `SMTP_HOST`/`SMTP_PORT` (também via `setx`) pelo
servidor SMTP correspondente.

## Ajustar o que é buscado

No topo do `buscar_editais.py`:

- `DIAS_RETROATIVOS` — quantos dias pra trás buscar (1 = ontem até hoje,
  pra rodar diariamente).
- `MODALIDADES` — lista de códigos de modalidade do PNCP. O padrão é
  `[6]` (Pregão Eletrônico). Outros códigos usados pelo PNCP: 4/5
  Concorrência (eletrônica/presencial), 8 Dispensa de Licitação, 9
  Inexigibilidade, 12 Credenciamento.
- `UF_FILTRO` — sigla do estado (ex: `"PE"`) pra restringir a busca só
  a esse estado, ou vazio pra buscar no Brasil todo.

## ⚠️ Pendência de verificação

Assim como o módulo `cadastro-empresas`, este script foi escrito num
sandbox cuja política de rede bloqueia `pncp.gov.br` — não consegui
rodar a consulta real daqui. Testei offline: extração de palavra-chave,
comparação com o objeto da licitação e montagem do e-mail (com dados
simulados) funcionam. Os nomes de campo da API (`objetoCompra`,
`orgaoEntidade`, `unidadeOrgao`, `numeroControlePNCP` etc.) e a
estrutura de paginação (`data`, `paginasRestantes`) foram confirmados
pela documentação pública do PNCP, não por uma chamada real feita por
aqui. **Rode `python buscar_editais.py --teste` na sua máquina antes de
confiar no envio automático de e-mail**, e me avise se algum campo vier
diferente do esperado.

## Próximos passos (evolução futura)

- Registrar histórico dos editais já avisados (hoje, se rodar duas
  vezes no mesmo dia, pode repetir o e-mail).
- Rodar para mais de uma empresa por vez, não só a ativa.
- Cruzar com consulta de preço (próximo módulo) pra já vir com uma
  faixa de valor sugerida junto do alerta.
- Melhorar o casamento de palavra-chave (hoje é substring simples —
  poderia usar também o CATMAT/CATSER dos itens da compra, quando o
  PNCP trouxer isso, em vez de só o texto livre do objeto).
