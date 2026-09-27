# Cadastro de Empresas (com CNAE automático)

Script em Python que cadastra as empresas do escritório pelo CNPJ,
busca automaticamente o CNAE (principal e secundários) e guarda tudo num
banco local. Serve de base para os outros módulos do Inova v2 (alerta
de edital, WhatsApp e consulta de preço) — este script só cuida do
cadastro.

## O que ele faz

1. Você digita o CNPJ.
2. Ele consulta a [BrasilAPI](https://brasilapi.com.br/docs) — que
   publica os dados abertos da Receita Federal (CNPJ) — e traz razão
   social, nome fantasia, município/UF e os CNAEs (principal e
   secundários).
3. Mostra o que encontrou e permite **acrescentar CNAE manualmente**
   (código + descrição), caso falte algum ou a consulta falhe.
4. Pergunta o e-mail e o telefone (com DDD) da empresa, pra saber pra
   quem mandar os alertas — por e-mail e por WhatsApp (módulo
   [`notificar-whatsapp`](../notificar-whatsapp/)). Os dois são
   opcionais (Enter pula) e podem ser cadastrados/editados depois pela
   opção **5** do menu.
5. Salva tudo num banco SQLite local (`empresas.db`, criado na primeira
   vez que você roda o script — não fica no Git, veja abaixo).
6. Deixa marcar qual empresa está **ativa** — essa é a que os módulos
   futuros (alerta de edital, WhatsApp, sugestão de preço) usam.

Se você já tinha uma `empresas.db` de uma versão anterior (sem e-mail
e telefone), não tem problema: o script acrescenta essas colunas
sozinho na primeira vez que você abrir, sem apagar nada do que já
estava cadastrado.

Nenhum dado é enviado pra fora além da própria consulta do CNPJ na
BrasilAPI. Nada aqui altera o sistema Inova ou qualquer outro projeto
deste repositório.

## Por que a BrasilAPI e não a Receita Federal direto

Existe uma API realmente oficial no [catálogo gov.br/conecta](https://www.gov.br/conecta/catalogo/apis/consulta-cnpj)
para consulta de CNPJ, mas ela exige cadastro como instituição
consumidora e autenticação via conta gov.br (Prata/Ouro, com certificado
digital ou CPF+senha) — burocracia grande pra uma primeira versão. A
BrasilAPI é gratuita, sem cadastro, e republica os mesmos dados abertos
do CNPJ que a Receita Federal já disponibiliza publicamente (não é
informação sigilosa). Se um dia precisar de SLA garantido ou volume
grande, migrar pra API oficial do gov.br é a evolução natural — o script
já isola a consulta numa função só (`consultar_cnpj`), pra trocar sem
reescrever o resto.

## Como usar

1. Instale o Python 3 (Windows: https://www.python.org/downloads/,
   marque "Add Python to PATH" na instalação).
2. Instale a dependência (abra o cmd/PowerShell nesta pasta):
   ```
   pip install -r requirements.txt
   ```
3. Rode:
   ```
   python cadastrar_empresa.py
   ```
4. Use o menu:
   - **1** cadastra uma empresa nova pelo CNPJ.
   - **2** lista as empresas já cadastradas.
   - **3** escolhe qual fica ativa.
   - **4** mostra e-mail, telefone e CNAEs da empresa ativa.
   - **5** edita e-mail/telefone de uma empresa já cadastrada.

## ⚠️ Pendência de verificação

Este script foi escrito num ambiente de desenvolvimento (sandbox) cuja
política de rede bloqueia o domínio `brasilapi.com.br` — não consegui
testar a consulta real de CNPJ por aqui (só o fluxo manual, sem
internet, que funciona). O código foi escrito conforme a documentação
pública da BrasilAPI (campos `cnae_fiscal`, `cnae_fiscal_descricao`,
`cnaes_secundarios`), mas **na primeira vez que rodar na sua máquina**
(que tem internet normal), cadastre uma empresa conhecida e confira se
os CNAEs retornados batem com o que você já sabe dela — se algum nome de
campo tiver mudado na API, me avise o erro exato que aparecer.

## Próximos passos (evolução futura)

- ~~Módulo de alerta de edital~~ — pronto, ver
  [`alerta-editais/`](../alerta-editais/).
- ~~Alerta por WhatsApp~~ — pronto, ver
  [`notificar-whatsapp/`](../notificar-whatsapp/).
- ~~Módulo de consulta de preço~~ — pronto, ver
  [`consulta-preco/`](../consulta-preco/).
- Trocar a tela de texto por uma interface mais simples (web local ou
  desktop), se o cadastro por menu ficar incômodo no dia a dia.
- Se o volume de empresas crescer muito, avaliar migrar a consulta de
  CNPJ pra API oficial do gov.br/conecta.
