# Calculadoras M Contabilidade

Página pública com duas calculadoras gratuitas, feita para o site
**mccontabilidadebrasil.com.br**. Serve como ferramenta de captação de leads:
o visitante usa de graça, vê a marca do escritório e tem um botão de WhatsApp
no final de cada cálculo.

- **Aba 1 — Imposto de Renda (Pessoa Física):** INSS, base do IRRF, alíquota,
  parcela a deduzir, redutor da Lei nº 15.270/2025 e salário líquido estimado.
- **Aba 2 — Enquadramento Tributário:** comparativo estimado entre Simples
  Nacional, Lucro Presumido e Lucro Real.
- **Aba 3 — Atualização Monetária:** corrige um valor do passado por IPCA, INPC,
  IGP-M, TR ou SELIC, com juros de mora e multa. Os índices são buscados na hora
  na API pública do Banco Central.

Tudo roda no navegador do visitante. **Não tem banco de dados, não tem
back-end, não guarda nenhum dado de ninguém.** É só HTML, CSS e JavaScript.

---

## ⚠️ LEIA ANTES DE PUBLICAR — CONFERÊNCIA OBRIGATÓRIA

As tabelas foram levantadas em **19/09/2026** cruzando várias publicações que
reproduzem as normas oficiais. **O ambiente onde esta página foi gerada não
conseguiu abrir os sites gov.br** (bloqueio de rede do ambiente), então a
conferência final na fonte oficial ainda não foi feita.

**Da sua rede os sites do governo abrem normalmente.** Por isso existe um
script que faz essa conferência automaticamente:

> **Dê dois cliques em `3-CONFERIR-TABELAS-NO-GOV.bat`.**

Ele abre os sites oficiais, procura cada número que está em `js/tabelas.js` e
mostra um relatório assim:

```
   [OK]    Limite da faixa isenta                   2.428,80
   [OK]    Parcela a deduzir — 27,5%                908,73
   [FALHA] Dedução mensal por dependente            189,59   (nao achei na pagina oficial)
```

A conferência é feita nas **duas pontas**: o número precisa estar em
`js/tabelas.js` **e** aparecer na página oficial. Se as duas baterem, está
certo. Se der `[FALHA]`, o script diz exatamente qual número conferir na mão.

Precisa do Python instalado. Se não tiver, o próprio `.bat` explica como
instalar. Sem Python, dá para conferir na mão pela lista abaixo:

| # | O que conferir | Onde conferir |
|---|---|---|
| 1 | Tabela progressiva mensal do IRRF (faixas, alíquotas, parcela a deduzir), dedução por dependente de R$ 189,59 e desconto simplificado de R$ 607,20 | Receita Federal → Meu Imposto de Renda → Tabelas → 2026 |
| 2 | Regra do redutor: zera até R$ 5.000,00 e fórmula `978,62 − (0,133145 × rendimento)` até R$ 7.350,00 | Receita Federal → notícia de dez/2025 sobre a Lei nº 15.270/2025 e a página "Exemplos de Aplicação" |
| 3 | Faixas e alíquotas do INSS (1.621,00 / 2.902,84 / 4.354,27 / 8.475,55) | Portaria Interministerial MPS/MF nº 13, de 09/01/2026 |
| 4 | Anexos I a V do Simples Nacional | LC nº 123/2006, Anexos I a V |
| 5 | Majoração de 10% na presunção do Lucro Presumido acima de R$ 1.250.000,00 por trimestre | LC nº 224/2025 e Perguntas e Respostas da Receita Federal |

Conferiu tudo? Então abra `js/tabelas.js` e troque:

```js
conferidoNaFonteOficial: false,   →   conferidoNaFonteOficial: true,
```

Se algum número estiver diferente do que está aqui, **corrija em
`js/tabelas.js`, rode os testes e só depois publique.**

---

## O que cada arquivo faz

```
calculadoras-web/
│
│   ATALHOS (dois cliques, no Windows)
├── 1-ABRIR-CALCULADORA.bat        Abre a calculadora no navegador
├── 2-CONFERIR-CALCULOS.bat        Confere as contas (deve dar 47/47)
├── 3-CONFERIR-TABELAS-NO-GOV.bat  Confere as tabelas nos sites do governo
│
│   PÁGINA
├── index.html                     A página que o visitante vê (as duas abas)
├── css/
│   └── estilo.css                 Todo o visual (tema escuro, marca, celular)
├── img/
│   ├── logo.svg                   LOGO PROVISÓRIO — troque pelo real
│   └── LEIA-ME.txt                Como colocar o logo do escritório
└── js/
    ├── tabelas.js                 >>> TODAS AS TABELAS OFICIAIS FICAM AQUI <<<
    ├── calculo-ir.js              Cálculo do INSS e do IRRF
    ├── calculo-enquadramento.js   Simples, Lucro Presumido e Lucro Real
    ├── app.js                     Liga a tela aos cálculos e monta os resultados
    └── testes.js                  Os casos de teste com os valores conferidos na mão
│
│   USO INTERNO (não precisa subir para a hospedagem)
├── testes.html                    Página de conferência dos cálculos
├── rodar-testes.js                A mesma conferência, pelo terminal
├── conferir-tabelas.py            Confere as tabelas nos sites do gov.br
├── testar-conferidor.py           Testes do próprio conferidor acima
├── testes-navegador.js            Abre a página num navegador e confere a tela
└── teste-api-indices.html         Testa se as APIs de índices respondem aqui
```

**A regra mais importante do projeto:** nenhum valor de tabela pode ser escrito
fora de `js/tabelas.js`. Os arquivos de cálculo só sabem a *fórmula*; os
*números* vêm todos do arquivo de configuração. É isso que faz a atualização
anual ser rápida e segura.

Cada bloco do `tabelas.js` tem, em comentário, a **fonte oficial**, a **data de
vigência** e a **data da última conferência**.

---

## Como rodar na sua máquina (Windows)

Não precisa instalar nada para usar a calculadora. Não precisa de servidor,
não precisa de internet.

1. Baixe a pasta `calculadoras-web` para o seu computador
   (por exemplo, `C:\Sites\calculadoras-web`).
2. Abra a pasta no Explorador de Arquivos.
3. **Dê dois cliques em `1-ABRIR-CALCULADORA.bat`.**
   A página abre no seu navegador padrão.

   (Se preferir, dá no mesmo dar dois cliques direto em `index.html`.)

4. Teste a Aba 1 com um salário de que você já tem o contracheque e confira
   linha por linha na "Memória de cálculo".
5. Teste a Aba 2 com uma empresa cujos números você já conhece.

### Os três atalhos, na ordem de uso

| Arquivo | O que faz | Quando usar |
|---|---|---|
| `1-ABRIR-CALCULADORA.bat` | Abre a página no navegador | Sempre que quiser usar ou mostrar a calculadora |
| `2-CONFERIR-CALCULOS.bat` | Confere as contas contra valores feitos na mão | Depois de qualquer alteração em `js/tabelas.js` |
| `3-CONFERIR-TABELAS-NO-GOV.bat` | Confere as tabelas nos sites oficiais | Antes de publicar, e a cada mudança de legislação |

O atalho 2 abre uma página que precisa mostrar, no topo:

```
47 testes | 47 passaram | 0 falharam.
```

Se aparecer alguma falha em vermelho, **não publique a página** — algum número
de `js/tabelas.js` está divergindo dos valores conferidos manualmente.

> Se você tiver o Node.js instalado, dá para rodar o mesmo teste pelo terminal
> com `node rodar-testes.js`. É opcional — o atalho 2 faz a mesma coisa.

---

## Como colocar o logo do escritório

O logo que aparece na página hoje é **provisório**. Ele está na pasta `img`, em
duas versões do mesmo desenho: `logo.png` (a que a página usa) e `logo.svg`.

Para trocar pelo logo de verdade, **não precisa editar código nenhum**:

> Apague o `img/logo.png` provisório, coloque o logo do escritório no lugar
> com esse mesmo nome, e atualize a página no navegador (tecla **F5**).

Se o seu logo for em vetor (`.svg`), salve como `img/logo.svg` e **apague o
`img/logo.png`** — senão o provisório continua ganhando.

A página procura os arquivos nesta ordem:

1. `img/logo.png` — se existir, usa este;
2. `img/logo.svg` — se não achar o `.png`, usa este;
3. desenho embutido — se não achar nenhum dos dois, desenha um "MC" simples.

Ou seja, **a página nunca fica sem logo** e você nunca precisa mexer no HTML.

### Cuidados com o arquivo do logo

- **Fundo transparente.** O site é escuro; logo com fundo branco fica com um
  retângulo branco em volta.
- **Altura de pelo menos 200 pixels**, senão fica borrado em celular e em tela
  de alta resolução.
- **Versão para fundo escuro.** Se o logo do escritório for escuro, peça ao
  designer a versão clara — quase todo logo tem as duas.
- **Formato deitado** (mais largo que alto) encaixa melhor no cabeçalho.
- Se você tiver o logo em vetor (`.ai`, `.eps`, `.svg`), peça o `.svg` ao
  designer e salve como `img/logo.svg` — fica perfeito em qualquer tamanho.

O detalhamento completo está em `img/LEIA-ME.txt`.

O ícone que aparece na aba do navegador (favicon) é um desenho separado, dentro
do `index.html`. Me avise se quiser que eu gere ele a partir do logo real.

---

## Verificação automática (CI)

Toda vez que alguém envia código para o GitHub, o arquivo
`.github/workflows/testes.yml` roda a conferência sozinho. São dois trabalhos,
porque eles pegam problemas diferentes:

| Trabalho | O que confere | Por que existe |
|---|---|---|
| **Cálculos e sintaxe** | os 47 testes de cálculo, os 21 testes do conferidor de tabelas e a sintaxe de todos os arquivos `.js` e `.py` do repositório | pega erro de conta e arquivo quebrado; é rápido e não instala nada |
| **Página no navegador** | abre o `index.html` num Chromium de verdade, preenche os dois formulários, confere os valores na tela, o logo, a troca de abas, o celular e exige zero erro de JavaScript | pega o que o outro não pega |

O segundo trabalho existe por um motivo concreto: **as contas podem estar certas
e a página quebrada ao mesmo tempo.** Isso foi testado de propósito — quebrando
o `app.js`, os 47 testes de cálculo continuaram dando "47 passaram", porque eles
não abrem a página. Só o teste de navegador acusou o problema.

O que cada sabotagem de teste provocou:

| Sabotagem | Quem acusou |
|---|---|
| Trocar uma parcela a deduzir da tabela do IR | 8 testes de cálculo + 2 do conferidor |
| Quebrar o `app.js` | só o teste de navegador (cálculos passaram normalmente) |
| Apagar o logo do HTML | 3 testes de navegador |

Se o CI ficar vermelho num PR, o GitHub mostra qual passo falhou e com qual
valor. **Não mescle com o CI vermelho.**

Para rodar o teste de navegador na sua máquina (opcional — o CI já faz isso):

```
npm install playwright
npx playwright install chromium
node testes-navegador.js
```

---

## A aba 3 é diferente das outras duas

As abas 1 e 2 usam **tabelas guardadas** em `js/tabelas.js`, que você atualiza à
mão quando a lei muda. A aba 3 não tem tabela nenhuma: ela **busca os índices no
Banco Central na hora do cálculo**.

A vantagem é grande: IPCA, INPC, IGP-M, TR e SELIC mudam todo mês, e essa aba
**nunca desatualiza** — não tem manutenção mensal.

O que fica em `js/tabelas.js` é só o *código da série* de cada índice no sistema
do Banco Central, e a regra de acumulação de cada um:

| Índice | Série | Como acumula |
|---|---|---|
| IPCA | 433 | composto — cada mês incide sobre o valor já corrigido |
| INPC | 188 | composto |
| IGP-M | 189 | composto |
| TR | 226 | composto |
| SELIC | 4390 | **soma** das taxas + 1% do mês do pagamento (tributos federais) |

A SELIC é a exceção: para tributos federais, a lei manda **somar** as taxas
mensais, sem capitalizar, e acrescentar 1% referente ao mês do pagamento
(Lei nº 9.430/1996, art. 61, § 3º). A página faz isso e deixa o 1% como uma
opção que você pode desmarcar.

### Os códigos das séries precisam da sua conferência

Rode o `4-TESTAR-APIS-DE-INDICES.bat`: ele mostra os últimos valores que cada
série devolve, para você comparar com o índice que conhece. Se algum código
estiver trocado, corrija em `js/tabelas.js` e marque
`codigosConferidos: true`.

### Se o Banco Central não responder

A página não quebra. Ela explica o que houve e abre um campo para você informar
o **índice acumulado do período** à mão — o cálculo sai do mesmo jeito, e o
resultado avisa que foi feito com o percentual informado, não com os índices
oficiais buscados.

---

## Como colocar no ar (mccontabilidadebrasil.com.br)

A página é 100% estática, então dá para hospedar em qualquer lugar. Três
caminhos, do mais simples ao mais completo:

### Opção A — Hospedagem que você já contratou com o domínio (cPanel)

É o caminho mais provável se você comprou domínio + hospedagem juntos.

1. Entre no painel da hospedagem (normalmente `seudominio.com.br/cpanel` ou o
   link que a empresa mandou por e-mail).
2. Abra o **Gerenciador de Arquivos** (File Manager).
3. Entre na pasta **`public_html`**. É a pasta que fica visível na internet.
4. Se quiser a calculadora em `mccontabilidadebrasil.com.br/calculadoras`,
   crie dentro de `public_html` uma pasta chamada `calculadoras`.
   Se quiser que ela seja a página principal do site, use a própria
   `public_html` (mas aí ela substitui o site atual — cuidado).
5. Envie os arquivos mantendo a estrutura de pastas:
   - `index.html`
   - a pasta `css` inteira
   - a pasta `js` inteira
   - a pasta `img` inteira (é onde está o logo)
   - (`testes.html`, `rodar-testes.js`, `conferir-tabelas.py` e os três
     arquivos `.bat` são de uso interno — **não precisa subir**, e é melhor
     não subir mesmo)
6. Abra `https://mccontabilidadebrasil.com.br/calculadoras/` no navegador.

**Se a página abrir sem cor nenhuma e sem funcionar:** as pastas `css` e `js`
não subiram junto ou subiram no lugar errado. Confira se ficou
`calculadoras/css/estilo.css` e `calculadoras/js/tabelas.js`.

**Se o logo sumir depois de publicar:** a pasta `img` não subiu. A página cai
no desenho de reserva, então ela continua funcionando — mas suba a pasta.

### Opção B — Hospedagem gratuita (Netlify)

Serve bem se o domínio ainda não tem hospedagem contratada.

1. Crie uma conta em `netlify.com`.
2. Na tela inicial, arraste a pasta `calculadoras-web` para a área escrita
   "Drag and drop your site output folder here".
3. Em segundos o site fica no ar num endereço tipo `algo-aleatorio.netlify.app`.
4. Em **Domain settings → Add custom domain**, cadastre
   `mccontabilidadebrasil.com.br` e siga as instruções de DNS que aparecem
   (você precisa alterar o DNS no painel onde o domínio foi registrado).

### Opção C — WordPress (se o site do escritório for WordPress)

Não cole o código dentro de um post. Suba os arquivos por FTP para uma pasta
dentro de `public_html` (igual à Opção A) e crie um item de menu apontando para
`https://mccontabilidadebrasil.com.br/calculadoras/`.

### Depois de publicar

- Teste no **celular** — boa parte dos visitantes vai entrar pelo telefone.
- Teste o botão de WhatsApp: ele abre uma conversa com **(81) 9 8774-7434**
  já com uma mensagem pronta dizendo de onde a pessoa veio. É assim que você
  identifica o lead.
- Se quiser trocar o número, o endereço ou o nome, é só editar o bloco
  `escritorio` no final de `js/tabelas.js`. Não precisa mexer no HTML.

---

## Segurança da página

A página passou por uma revisão de segurança. Como ela é estática, não tem
banco de dados, não tem login e não guarda nada de ninguém, a superfície de
ataque é pequena — mas duas proteções foram colocadas:

**1. Trava do que a página pode fazer (Content-Security-Policy).**
No topo do `index.html` existe uma política que diz ao navegador: só carregue
script, estilo e imagem desta própria pasta, e só converse com
`https://api.bcb.gov.br`. Se um dia alguém conseguir injetar código na página,
ele não roda; e a página não consegue mandar dado nenhum para outro servidor.

> **Se você acrescentar uma biblioteca externa** (Google Fonts, Analytics,
> jQuery, um chat) **ou outra API, precisa liberar o endereço nessa política**,
> senão o navegador bloqueia **em silêncio** — a página simplesmente para de
> funcionar sem dizer por quê. É o erro mais comum com CSP.

**2. Texto vindo de fora entra escapado.**
Quase tudo que a página mostra é número formatado por ela mesma. A exceção é
o que vem da API do Banco Central e as mensagens de erro do navegador — esses
passam por uma função que neutraliza marcação HTML antes de aparecer na tela.

### Opcional, na hospedagem

Uma proteção não cabe dentro do HTML e só funciona por cabeçalho HTTP: impedir
que outro site coloque a sua página dentro de um quadro (para se passar por
você). Se a sua hospedagem for cPanel/Apache, dá para ligar criando um arquivo
chamado `.htaccess` na mesma pasta, com:

```
Header always set Content-Security-Policy "frame-ancestors 'none'"
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

Não é obrigatório. A página funciona sem isso.

---

## Como atualizar quando a tabela mudar

Fluxo completo, todo ano (ou quando sair uma lei nova):

1. Abra `js/tabelas.js`.
2. Localize o bloco da tabela que mudou (cada um tem `FONTE`, `VIGENCIA` e
   `CONFERIDO EM` em comentário logo acima).
3. Troque os números e **atualize as três linhas do comentário**.
4. Atualize no topo do arquivo: `versao`, `atualizadoEm` e
   `conferidoNaFonteOficial`.
5. Atualize os valores esperados em `js/testes.js` refazendo a conta na mão.
6. Dê dois cliques em `2-CONFERIR-CALCULOS.bat` e confirme que está tudo
   passando.
7. Dê dois cliques em `3-CONFERIR-TABELAS-NO-GOV.bat` para conferir os números
   novos nos sites oficiais. Se você mudou valores, atualize também a lista
   `VERIFICACOES` dentro de `conferir-tabelas.py` — existe um teste que cobra
   isso, então o CI fica vermelho se você esquecer.
8. Atualize a lista "Fontes das tabelas utilizadas" no final do `index.html`.
9. Suba os arquivos alterados para a hospedagem.

### 📌 Revisões já previstas

| Quando | O que revisar |
|---|---|
| **Janeiro de todo ano** | Nova portaria do INSS (salário mínimo e teto mudam sempre) e eventual reajuste da tabela do IR |
| **Antes de janeiro/2027** | **Obrigatório.** PIS e COFINS são extintos e a CBS passa a ser cobrada de verdade (LC nº 214/2025). A Aba 2 fica desatualizada nesse dia. |
| Quando sair decisão do STF/STJ sobre a LC nº 224/2025 | A majoração de 10% na presunção do Lucro Presumido está sendo questionada na Justiça. Se cair, desligue em `tabelas.js`: `majoracaoLC224.ativa = false` |

---

## O que a página faz e o que ela não faz

### Aba 1 — Imposto de Renda

**Faz:** calcula o INSS progressivo por faixas, monta a base do IRRF comparando
as deduções legais (INSS + dependentes) com o desconto simplificado de
R$ 607,20 e usa a opção mais vantajosa, aplica a tabela progressiva, aplica o
redutor da Lei nº 15.270/2025 e mostra o líquido. Exibe cada passo.

**Não faz:** vale-transporte, plano de saúde, adiantamento, pensão alimentícia,
previdência privada, faltas, horas extras, adicionais, 13º, férias, rescisão,
IRRF de autônomo/RPA e ajuste anual. É o cálculo do INSS e do IRRF sobre o
salário informado.

### Aba 2 — Enquadramento Tributário

**Faz:** estima a carga anual nos três regimes, já incluindo a CPP patronal
sobre a folha nos regimes normais, o Fator R do Simples, a majoração da
LC nº 224/2025 no Lucro Presumido e os créditos de PIS/COFINS no Lucro Real.
Mostra a memória de cálculo de cada regime.

**Não faz:** ICMS-ST, monofásico, DIFAL, benefícios fiscais estaduais,
importação, IPI, atividades vedadas ou mistas, segregação de receitas,
retenções na fonte, créditos acumulados, prejuízo fiscal e situação societária.

**Cuidado específico com comércio e indústria:** o DAS do Simples **já inclui**
o ICMS, mas no Lucro Presumido e no Lucro Real o ICMS só entra se você digitar
um percentual efetivo no campo "ICMS efetivo estimado". Se deixar zero, o
comparativo favorece indevidamente os regimes normais — a página avisa isso na
tela, mas vale reforçar no atendimento.

**Esta aba não é planejamento tributário.** O cálculo definitivo de
enquadramento, com dados reais do cliente, é trabalho do Agente Simples
Nacional / Agente Regime Normal, não desta página.

---

## Próximas versões (ideias já mapeadas)

- **V2 — Captura de lead:** campo de e-mail/WhatsApp antes de liberar o
  resultado completo, com envio para uma planilha ou para o e-mail do
  escritório. Exige um back-end simples (ou um serviço de formulário).
- **V3 — Integração com o CRM do escritório:** cada simulação vira um registro
  com faturamento, atividade e regime sugerido, já pronto para abordagem
  comercial.
- **V4 — Novas calculadoras:** rescisão, férias, 13º, DAS do Simples por
  competência, Fator R isolado, e simulador de IBS/CBS para a transição.
