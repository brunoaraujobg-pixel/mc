# Baixar Legislação Trabalhista

Script em Python que baixa o texto oficial ATUALIZADO/COMPILADO da CLT e
de leis trabalhistas correlatas, direto do site do Planalto, para formar
uma biblioteca local de legislação trabalhista do escritório. Foco inicial
em transporte de cargas e motorista profissional, mas serve como base para
qualquer consulta trabalhista.

## ⚠️ Achado importante: Lei 12.619/2012 está REVOGADA

A Lei 12.619/2012 (que criou as primeiras regras de jornada e descanso do
motorista profissional) foi **revogada pela Lei 13.103/2015**, que é a
norma em vigor hoje sobre o tema. O script baixa a 12.619 mesmo assim,
mas só como **referência histórica** (por exemplo, para entender ações
judiciais referentes a períodos anteriores a 2015) — o arquivo já é salvo
com o nome `lei_12619_2012_motorista_profissional_REVOGADA_ver_readme.html`
para não ser confundido com norma vigente. **Não use a 12.619/2012 como
base para situações atuais**; use a Lei 13.103/2015.

## Fontes oficiais usadas (todas `planalto.gov.br`, domínio oficial)

| Norma | Assunto | URL |
|---|---|---|
| CLT (Decreto-Lei 5.452/1943), texto compilado | Consolidação das Leis do Trabalho, atualizada | https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452compilado.htm |
| Lei 13.103/2015 | Motorista profissional (norma vigente) | https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13103.htm |
| Lei 605/1949 | Repouso semanal remunerado | https://www.planalto.gov.br/ccivil_03/leis/l0605.htm |
| Lei 8.036/1990 (consolidada) | FGTS | https://www.planalto.gov.br/ccivil_03/leis/l8036consol.htm |
| Lei 8.213/1991 (consolidada) | Benefícios do INSS/Previdência | https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm |
| Lei 12.619/2012 | Motorista profissional — **REVOGADA**, só histórico | https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12619.htm |
| Lei 13.467/2017 | Reforma trabalhista (altera a CLT) | https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13467.htm |

**Pendência de verificação:** este ambiente de desenvolvimento (sandbox
onde o script foi escrito) tem o acesso à internet bloqueado para o
domínio `planalto.gov.br` por política da organização, então as URLs
acima foram confirmadas por busca (não abertas diretamente daqui). Ao
rodar o script na sua máquina (que tem acesso normal à internet), ele
mesmo baixa o HTML direto da fonte — confira o cabeçalho da página
baixada (data da última alteração consolidada) se for usar em algo
sensível como parecer ou processo judicial.

## O que o script faz nesta V1

1. Baixa o HTML oficial da CLT (versão compilada, já com todas as
   alterações vigentes) e das leis correlatas listadas acima.
2. Nunca derruba a execução inteira por causa de uma falha pontual: se um
   site estiver fora do ar, pula para o próximo e registra a falha no log.
3. Salva um `metadata.json` da CLT com fonte, data do download e se deu
   certo.
4. Salva uma lista curada **manualmente** (não automática) de
   súmulas/temas relevantes do STF/STJ para transporte de cargas e
   motorista profissional, com o link oficial de cada uma.
5. Gera `log_coleta.txt` com tudo que foi feito e um resumo final.

### O que esta V1 *não* faz ainda

- **Não baixa jurisprudência do STF/STJ automaticamente.** Os portais de
  jurisprudência desses tribunais carregam o conteúdo via JavaScript, não
  dá para baixar só com `requests` — precisaria de Selenium (fica para a
  V2). Por enquanto, a lista de súmulas/temas é curada manualmente e
  **precisa ser conferida e ampliada** antes de virar fonte definitiva em
  qualquer parecer.
- Não interpreta nem resume o conteúdo das leis — baixa o HTML integral,
  tal como publicado.

## Como usar

1. Instale o Python 3 (Windows: https://www.python.org/downloads/, marque
   "Add Python to PATH" na instalação).
2. Abra o cmd/PowerShell nesta pasta e instale a dependência:
   ```
   pip install -r requirements.txt
   ```
3. Rode:
   ```
   python baixar_legislacao.py
   ```
4. Confirme com `s` quando perguntado se pode continuar.
5. Acompanhe a saída no terminal. Ao final, ele mostra um resumo: quantos
   arquivos baixou, quantos falharam, e onde tudo foi salvo.

## Estrutura gerada (pasta `biblioteca_trabalhista/`)

```
biblioteca_trabalhista/
├── clt/
│   ├── clt_atualizada.html
│   └── metadata.json
├── leis/
│   ├── lei_13103_2015_motorista_profissional.html
│   ├── lei_605_1949_repouso_semanal_remunerado.html
│   ├── lei_8036_1990_fgts.html
│   ├── lei_8213_1991_beneficios_inss.html
│   ├── lei_12619_2012_motorista_profissional_REVOGADA_ver_readme.html
│   └── lei_13467_2017_reforma_trabalhista.html
├── stf/
│   └── Tema_725.json
├── stj/
│   └── A_confirmar_numero_exato_no_site_oficial.json
└── log_coleta.txt
```

## Se algo falhar

- `pip não é reconhecido`: o Python não foi instalado com a opção
  "Add Python to PATH". Reinstale marcando essa opção.
- `ModuleNotFoundError: requests`: rode `pip install -r requirements.txt`
  de novo, no mesmo terminal/pasta.
- Erro de conexão numa lei específica: normal, o site pode estar fora do
  ar temporariamente — o script pula, segue para as outras e registra a
  falha em `log_coleta.txt`.

## Próximos passos (evolução futura)

- **V2**: buscar automaticamente (via Selenium) jurisprudência relevante
  do STF/STJ sobre transporte de cargas e motorista profissional, em vez
  da lista curada manualmente.
- Detectar automaticamente quando o Planalto atualizar a CLT ou uma das
  leis (comparando data de consolidação com a última registrada).
- Extrair o texto limpo (sem HTML) para facilitar busca por palavra-chave,
  como já é feito no projeto `download-ricms-pe-pi/`.
- Ampliar a lista de leis correlatas conforme a necessidade do escritório
  (ex.: normas específicas de ICMS/DIFAL para frete, se fizer sentido
  integrar aqui ou em projeto separado).
