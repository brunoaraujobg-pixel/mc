# Notificar por WhatsApp

Envia mensagem de WhatsApp usando o **telefone cadastrado** no módulo
[`cadastro-empresas`](../cadastro-empresas/) (campo telefone/WhatsApp),
pela **WhatsApp Business Platform (Cloud API)** — a API oficial da Meta.
Não usa WhatsApp Web, Selenium ou qualquer automação por fora do
oficial: esses métodos violam os termos de uso do WhatsApp e arriscam
banir o número usado.

Este módulo funciona **sozinho** (não altera `cadastro-empresas` nem
`alerta-editais`) — é a peça nova que falta pra alguém decidir *quando*
mandar WhatsApp pra qual empresa.

## Antes de usar — só funciona depois desta configuração

Diferente dos outros módulos, este **exige uma configuração fora do
código antes de mandar qualquer mensagem de verdade**. Não tem jeito
de pular essa parte — é assim que a Meta protege o WhatsApp de spam.

1. Crie uma conta em [developers.facebook.com](https://developers.facebook.com/)
   e um "App" do tipo Business.
2. Nesse App, adicione o produto **WhatsApp**. A Meta te dá de graça um
   número de teste e um `Phone Number ID` — dá pra testar antes de usar
   o número de WhatsApp real do escritório.
3. Gere um **token de acesso**: o de teste dura 24h (bom pra validar
   agora); pra rodar todo dia sem renovar token manualmente, precisa de
   um token permanente (usuário de sistema — exige verificação da
   empresa no Meta Business Manager, processo mais longo).
4. Defina as variáveis de ambiente (Windows, PowerShell):
   ```powershell
   setx WHATSAPP_TOKEN "seu-token-aqui"
   setx WHATSAPP_PHONE_NUMBER_ID "id-do-numero-aqui"
   ```
   (abra um terminal novo depois do `setx`, pra variável valer)
5. Teste a conexão com o template gratuito que a Meta já deixa
   pré-aprovado pra qualquer conta nova:
   ```
   python enviar_whatsapp.py --teste 81999998888
   ```
   Se aparecer "Mensagem aceita pela API do WhatsApp.", token e
   phone_number_id estão certos.

## Por que precisa de "template aprovado" pra alerta automático

O WhatsApp só deixa texto livre quando o destinatário escreveu pra você
nas últimas 24h. Como o alerta de licitação é a **empresa que inicia a
conversa** (o cliente não te escreveu antes), a Meta exige um
**template de mensagem aprovado por eles** (24-48h de análise) —
categoria "Utilidade" é a que se aplica aqui (lembrete/atualização de
status), custa bem menos que "Marketing" (hoje, algo como R$0,035 por
mensagem enviada, contra R$0,32 do Marketing — confira o preço atual no
seu Business Manager, isso muda).

Crie o template no Meta Business Manager (WhatsApp Manager → Modelos de
mensagem), ex:

```
Nome: alerta_licitacao
Categoria: Utilidade
Corpo: Nova licitação encontrada para {{1}}: {{2}}. Proposta até {{3}}.
```

Depois de aprovado, use:

```
python enviar_whatsapp.py --template 81999998888 alerta_licitacao "Empresa X" "Aquisição de uniformes" "30/09/2026"
```

## Comandos disponíveis

- `--teste <telefone>` — manda o template gratuito "hello_world" (só
  pra validar a configuração).
- `--texto <telefone> "mensagem"` — texto livre (só entrega dentro da
  janela de 24h ou pra número de teste cadastrado no painel da Meta).
- `--template <telefone> <nome_template> [parâmetro1 parâmetro2 ...]` —
  o caminho real para alerta automático, com um template seu já
  aprovado.

As funções (`enviar_teste`, `enviar_template`, `enviar_texto_livre`)
também podem ser importadas de outro script — é assim que dá pra ligar
isso no `alerta-editais` no futuro, sem duplicar código.

## ⚠️ Pendência de verificação

Não consegui testar nenhuma chamada real daqui — o sandbox onde este
código foi escrito bloqueia `graph.facebook.com` (mesma política de
rede que já impediu testar a BrasilAPI e o PNCP nos outros módulos).
Testei offline: sem credencial configurada (avisa e não tenta enviar),
normalização de telefone, e a chamada de rede real (que falha com erro
de conexão claro, sem travar o script) usando um token falso. **A
primeira validação de verdade precisa ser `--teste` na sua máquina**,
com token e phone_number_id reais.

## Próximos passos (evolução futura)

- Ligar isso no `alerta-editais`: quando achar edital combinando com o
  CNAE, mandar WhatsApp além do e-mail (usa o telefone que já está no
  cadastro da empresa).
- Trocar o token de teste (24h) pelo permanente, depois que a
  verificação de negócio no Meta Business Manager estiver pronta.
- Registrar no banco quando cada mensagem foi enviada, pra não repetir
  alerta do mesmo edital.
