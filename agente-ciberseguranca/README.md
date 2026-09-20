# Agente de Ciberseguranca

Agente especializado em seguranca para o escritorio contabil. Faz tres coisas:

1. **Mantem um acervo de referencias oficiais** sobre ciberseguranca, protecao de rede e
   Vulnerabilidades e Exposicoes Comuns (CVE/CWE), baixado de MITRE, NIST, CISA, OWASP,
   CERT.br e ANPD — em PDF, XML, XML.zip, JSON e CSV. Atualizacao a cada 3 meses.
2. **Audita seus projetos** procurando falhas que um invasor usaria (senha no codigo,
   certificado digital no repositorio, SQL injection, XXE em XML de NF-e, TLS desligado etc).
3. **Bloqueia publicacao insegura**: ao final de cada projeto ou antes de subir para a web,
   entrega um parecer com veredito.

---

## 1. Instalacao (uma unica vez)

### Passo 1 — Instalar o Python

1. Baixe em https://www.python.org/downloads/ (versao 3.10 ou mais nova).
2. Na primeira tela do instalador, **marque "Add python.exe to PATH"**.
3. Conclua a instalacao.
4. Para conferir, abra o Prompt de Comando (tecla Windows, digite `cmd`) e rode:

```
python --version
```

Deve aparecer algo como `Python 3.12.4`. Se aparecer "python nao e reconhecido",
o PATH nao foi marcado: reinstale marcando a opcao.

> Nao e preciso instalar mais nada. Os scripts usam apenas a biblioteca padrao do Python.

### Passo 2 — Colocar a pasta no lugar certo

Copie esta pasta para dentro da pasta de agentes:

```
C:\agentes cyber\agente-ciberseguranca
```

Se a pasta `C:\agentes cyber` ainda nao existir, crie antes: abra o Prompt de Comando
(tecla Windows, digite `cmd`) e rode `mkdir "C:\agentes cyber"`. As aspas sao necessarias
por causa do espaco no nome.

Qualquer outro caminho funciona igual — inclusive com espaco e acento no nome da pasta.
Todos os scripts se localizam sozinhos e usam aspas nos caminhos (testado com caminho
contendo espaco, tanto no download quanto na auditoria). Se usar outro lugar, apenas
troque o caminho nos comandos abaixo.

### Passo 3 — Baixar o acervo pela primeira vez

Abra a pasta `windows` e de **dois cliques em `atualizar_acervo.bat`**.

Ou, pelo Prompt de Comando:

```
cd C:\agentes cyber\agente-ciberseguranca
python baixar_acervo.py --somente-essenciais
```

O que deve aparecer: uma linha por fonte, com `NOVO`, `ATUALIZADO`, `SEM MUDANCA` ou
`ERRO`, e no final um RESUMO. Os arquivos ficam em `acervo\`, organizados por categoria,
e o indice em `acervo\INDICE.md`.

Para baixar **tudo**, inclusive o que e opcional:

```
python baixar_acervo.py
```

Para baixar tambem a base **completa** de CVEs (arquivo grande, varios GB descompactado):

```
python baixar_acervo.py --id cve-lista-completa
```

### Passo 4 — Agendar a atualizacao a cada 3 meses

Abra o PowerShell **como Administrador** e rode:

```
powershell -ExecutionPolicy Bypass -File "C:\agentes cyber\agente-ciberseguranca\windows\agendar_trimestral.ps1"
```

Isso cria uma tarefa no Agendador do Windows que roda dia 1 de **janeiro, abril, julho e
outubro**, as 09:00. Conferir depois:

```
schtasks /Query /TN "Agente Ciberseguranca - Atualizar Acervo" /V /FO LIST
```

---

## 2. Uso no dia a dia

### Auditar um projeto

Forma mais simples: **arraste a pasta do projeto e solte sobre `windows\auditar_projeto.bat`**.

Pelo Prompt de Comando:

```
cd C:\agentes cyber\agente-ciberseguranca
python auditor.py --projeto "C:\projetos\importar-notas" --online
```

O que aparece na tela: quantidade de arquivos analisados, o placar por severidade
(CRITICO / ALTO / MEDIO / BAIXO / INFO), o veredito e a lista dos achados graves.

O relatorio completo fica em `relatorios\auditoria_<projeto>_<data>.md` (para ler) e
`.json` (para outro agente processar).

O que significa o veredito:

| Veredito | Significado |
|---|---|
| BLOQUEADO PARA PUBLICACAO | Ha achado CRITICO. Nao publique, nao entregue. |
| LIBERADO COM RESSALVAS | Ha achado ALTO. Corrija antes de expor na internet. |
| APROVADO COM OBSERVACOES | Nada grave. Trate os MEDIO na proxima versao. |
| APROVADO NA VERIFICACAO AUTOMATICA | Nada encontrado pelas regras. Ainda falta o checklist manual. |

O parametro `--online` consulta a base publica OSV.dev para saber se alguma dependencia
do `requirements.txt` tem vulnerabilidade publicada. Sem internet, o script avisa e segue.

**O auditor e somente leitura.** Ele nunca altera, move ou apaga arquivo do projeto, e
se recusa a entrar nas pastas protegidas (`C:\NOTA ENTRADA`, `C:\NOTA SAIDA`,
`C:\Fronteira`, pastas de EFD e de relatorios de API).

### Bloquear `git push` inseguro (opcional, recomendado)

```
powershell -ExecutionPolicy Bypass -File "C:\agentes cyber\agente-ciberseguranca\windows\instalar_hook_git.ps1" -Projeto "C:\projetos\importar-notas"
```

A partir daí, todo `git push` naquele projeto roda a auditoria primeiro e **cancela o envio**
se houver achado CRITICO ou ALTO.

### Usar o agente de IA

Abra `PROMPT-AGENTE.md`:

- **Parte 1**: o prompt do agente. Copie inteiro e cole como instrucao de sistema
  (Claude, ChatGPT, agente proprio). E o papel permanente do agente.
- **Parte 2**: prompts curtos de execucao, prontos para o dia a dia — auditoria completa,
  revisao antes de publicar, revisao de trecho de codigo, atualizacao trimestral,
  revisao de rede, incidente em andamento, analise de nova dependencia.

No Claude Code, dentro deste repositorio, tambem funciona o comando `/auditoria-seguranca`.

### Revisao manual (o que o script nao ve)

- `checklists\CHECKLIST-PRE-DEPLOY.md` — antes de publicar na web ou entregar ao cliente.
- `checklists\CHECKLIST-REDE.md` — protecao da rede do escritorio, revisar a cada 3 meses.

---

## 3. Conferir o que o escritorio usa contra o que esta sendo explorado

O acervo sozinho nao diz o que fazer hoje. Quem faz essa ponte e o `inventario.json`:
uma lista do que existe no escritorio (equipamento e programa). O script cruza essa
lista com o catalogo CISA KEV — as vulnerabilidades que atacantes **ja estao usando**.

```
python conferir_inventario.py
```

Por padrao mostra os ultimos 12 meses (falha de 2008 em maquina atualizada nao ajuda
ninguem). Para ver tudo: `--tudo`. Para gravar o relatorio: `--salvar`.

**Preencha o `inventario.json`.** Ele ja vem com Windows, navegador, Office, PDF,
Python e o roteador; falta dizer qual antivirus e qual a versao do sistema contabil.
Item nao declarado nunca sera conferido.

Para acrescentar um equipamento, copie um bloco existente e ajuste `termos` com as
palavras que aparecem no nome do fabricante e do produto:

```json
{
  "id": "impressora-multifuncional",
  "nome": "Impressora HP LaserJet",
  "categoria": "rede",
  "termos": ["hp laserjet", "hewlett packard"],
  "critico": false,
  "atualizado_por": "firmware pelo painel da impressora"
}
```

---

## 4. Estrutura da pasta

```
agente-ciberseguranca\
├── README.md                    este arquivo
├── PROMPT-AGENTE.md             prompt do agente + prompts de execucao
├── fontes.json                  catalogo das 26 fontes oficiais (editavel)
├── inventario.json              o que o escritorio usa (editavel - preencha!)
├── conferir_inventario.py       cruza o inventario com as falhas em exploracao
├── baixar_acervo.py             baixa e mantem o acervo atualizado
├── auditor.py                   audita um projeto (somente leitura)
├── regras\
│   ├── segredos.json            deteccao de senha, token, certificado, CPF/CNPJ
│   ├── codigo.json              padroes de codigo inseguro por linguagem
│   └── arquivos.json            arquivos que nao deveriam estar no projeto
├── checklists\
│   ├── CHECKLIST-PRE-DEPLOY.md  revisao antes de publicar
│   └── CHECKLIST-REDE.md        protecao de rede do escritorio
├── windows\
│   ├── atualizar_acervo.bat     dois cliques: atualiza o acervo
│   ├── auditar_projeto.bat      arraste a pasta do projeto aqui
│   ├── agendar_trimestral.ps1   cria a tarefa trimestral no Windows
│   └── instalar_hook_git.ps1    bloqueia git push inseguro
├── acervo\                      arquivos baixados (NAO vao para o Git)
│   ├── INDICE.md                indice gerado automaticamente
│   ├── vulnerabilidades\        CWE (XML.zip), CAPEC, CVE List, CISA KEV, EPSS
│   ├── ataques\                 MITRE ATT&CK
│   ├── owasp\                   Top 10, ASVS (PDF), Cheat Sheets, WSTG, API Security
│   ├── rede\                    NIST 800-41 firewall, 800-46 remoto, 800-207 zero trust
│   ├── frameworks\              NIST CSF 2.0, 800-53, 800-61, 800-63B, 800-34
│   ├── brasil\                  CERT.br, LGPD, ANPD
│   ├── _estado\estado.json      controle do que foi baixado e quando
│   └── _logs\                   log de cada execucao
└── relatorios\                  pareceres de auditoria (NAO vao para o Git)
```

`acervo\` e `relatorios\` ficam fora do Git de proposito: sao arquivos grandes e os
relatorios podem citar caminhos e trechos de codigo do escritorio.

---

## 5. O que cada comando faz

| Comando | Para que serve |
|---|---|
| `python baixar_acervo.py --listar` | mostra as 24 fontes do catalogo e seus ids |
| `python baixar_acervo.py --somente-essenciais` | baixa o essencial (primeira vez) |
| `python baixar_acervo.py` | baixa/atualiza tudo (menos o que exige download manual) |
| `python baixar_acervo.py --categoria rede` | baixa apenas uma categoria |
| `python baixar_acervo.py --id cisa-kev-json --forcar` | rebaixa uma fonte especifica |
| `python baixar_acervo.py --verificar-validade` | diz se o acervo esta vencido |
| `python baixar_acervo.py --diagnostico` | testa cada site e explica o que esta falhando |
| `python baixar_acervo.py --ca-bundle "C:\cert.pem"` | usa tambem o certificado do antivirus/proxy |
| `python auditor.py --projeto "CAMINHO" --online` | audita um projeto |
| `python conferir_inventario.py` | cruza o inventario do escritorio com o CISA KEV (ultimos 12 meses) |
| `python conferir_inventario.py --tudo --salvar` | catalogo inteiro, gravando relatorio |
| `python auditor.py --projeto "CAMINHO" --ignorar "*.min.js"` | audita ignorando padroes |

O downloader **nao baixa de novo o que nao mudou**: ele compara ETag/data do servidor e
o hash SHA-256 do arquivo, e registra tudo em `acervo\_estado\estado.json`.

---

## 6. Como ajustar sem mexer no codigo

- **Incluir uma fonte nova**: acrescente um item em `fontes.json` (copie um existente como
  modelo). Tipos aceitos: `arquivo` (URL direta), `repo_zip` (repositorio do GitHub em ZIP),
  `release_github` (ultimo release de um repositorio) e `referencia` (so registra a pagina,
  quando o download precisa ser manual).
- **Criar uma regra de auditoria**: acrescente um item em `regras\codigo.json` ou
  `regras\segredos.json` com `id`, `nome`, `severidade`, `regex`, `extensoes` e `recomendacao`.
- **Ignorar um falso positivo em uma linha**: escreva `# nosec` no final da linha do codigo.

---

## 7. Quando uma fonte falhar no download

Isso acontece: sites de orgao publico mudam endereco e alguns recusam download
automatico. Erro em uma fonte **nao interrompe as outras**.

### Passo 1 — rodar o diagnostico

```
python baixar_acervo.py --diagnostico
```

Ele testa cada site e classifica o resultado. A leitura:

| Resultado | O que significa | O que fazer |
|---|---|---|
| `OK` | site respondeu | se houve erro, o problema e o endereco de um arquivo especifico |
| `ENDERECO` | HTTP 404: o arquivo mudou de lugar | abrir a pagina oficial da fonte e corrigir a URL em `fontes.json` |
| `BLOQUEIO` | HTTP 403/406: o site recusou o programa | o script ja tenta de novo como navegador; se insistir, baixar pelo navegador |
| `CERTIFICADO` | antivirus/firewall interceptando a conexao segura | ver passo 2 |
| `PROXY` | proxy da rede recusou o site | pedir liberacao do dominio a quem cuida da rede |
| `DNS` / `TIMEOUT` | sem resolucao de nome ou sem resposta | conferir internet; tentar `--timeout 300` |

### Passo 2 — se aparecer CERTIFICADO

Alguns antivirus (Kaspersky, Avast, ESET, Bitdefender) inspecionam conexoes HTTPS
substituindo o certificado do site. O Python nao reconhece esse certificado e recusa
a conexao — corretamente.

**Nao desligue a verificacao.** Duas saidas seguras:

1. Liberar os dominios no antivirus (`nvlpubs.nist.gov`, `cwe.mitre.org`,
   `capec.mitre.org`, `www.cisa.gov`, `cartilha.cert.br`).
2. Exportar o certificado do antivirus em formato `.pem` e usar:

```
python baixar_acervo.py --ca-bundle "C:\caminho\certificado.pem"
```

A verificacao continua ligada; o script apenas passa a confiar tambem nesse certificado.

### Passo 3 — se for endereco mudado

1. Abra o arquivo `fontes.json`.
2. Ache a fonte pelo `id` que apareceu no erro.
3. Abra no navegador o endereco do campo `pagina` (e a pagina oficial da fonte).
4. Ache o link do arquivo, copie e substitua o valor do campo `url`.
5. Rode de novo apenas aquela fonte:

```
python baixar_acervo.py --id ID-DA-FONTE --forcar
```

### Passo 4 — download manual (ultimo recurso)

Se o site exigir navegador, baixe pelo navegador e salve com o nome que esta no
campo `arquivo`, dentro de `acervo\<categoria>\`. O acervo continua servindo; o
script apenas nao vai controlar a data daquele arquivo.

---

## 8. Limitacoes (leia antes de confiar)

1. **A auditoria e por padrao de texto (regex).** Ela pega os erros mais comuns, mas nao
   entende a regra de negocio. Nao substitui revisao humana nem teste de invasao.
2. **Pode dar falso positivo e falso negativo.** Todo achado deve ser conferido; a ausencia
   de achado nao prova que o sistema esta seguro.
3. **URLs de orgao publico mudam.** Quando uma fonte falhar, o script informa a URL, o erro
   e a pagina oficial — corrija o endereco em `fontes.json`. Isso e esperado, nao e defeito.
4. **A base completa de CVEs e grande.** Por padrao fica de fora; use o `--id cve-lista-completa`
   quando quiser consulta offline total. Para o dia a dia, o CISA KEV (lista do que realmente
   esta sendo explorado) resolve melhor.
5. **Este projeto nao testa sistemas de terceiros.** Serve para revisar o que e do escritorio.

---

## 9. Evolucao prevista

- **Versao 1 (atual)**: acervo automatizado + auditoria por regras + checklists + prompt
  do agente + agendamento trimestral + hook de `git push`.
- **Versao 2 (parcial, ja entregue)**: `inventario.json` + `conferir_inventario.py`
  cruzam o que o escritorio usa com o CISA KEV. Falta cruzar tambem o `requirements.txt`
  de cada projeto e gerar um relatorio unico semanal.
- **Versao 3**: integrar com o orquestrador de agentes; auditoria disparada automaticamente
  quando um projeto for marcado como concluido; alerta no Windows e no celular.
- **Versao 4**: analise de codigo por AST (nao so regex), painel com historico de achados
  por projeto e banco de dados dos pareceres.
