# credito-tributario

Coleta fontes oficiais sobre a **exclusão do ICMS da base do PIS/COFINS**
(STF, RE 574.706, Tema 69) para Lucro Presumido e Lucro Real.

## O que o script faz (versão 1)

- Baixa as normas do Planalto (CTN, LC 118/2005, Leis 9.718, 10.637, 10.833, LC 214/2025).
- Salva em `C:\PROJETOS\Documento Analista\Credito Tributario\` com nome
  `AAAA-MM-DD_ORGAO_TIPO-NUMERO_assunto.ext`.
- Não baixa duplicado, não apaga e não sobrescreve nada.
- Acrescenta linhas ao `INDICE.md` (arquivo, órgão, norma, data do ato, data da consulta, link).
- Fontes **sem URL confirmada** (acórdão do STF, Parecer PGFN 14483/2021, IN RFB 2.055/2021,
  Soluções de Consulta COSIT, Tema 1.008 STJ, SEFAZ-PE) aparecem como **PENDENTES**,
  com a indicação de onde achar no site oficial.

## Como usar

1. Instale o Python (python.org), marcando "Add Python to PATH". Não precisa instalar mais nada.
2. Copie `baixar_fontes.py` para o seu computador.
3. Abra o Prompt de Comando na pasta do arquivo e rode:
   - `python baixar_fontes.py --simular` (só mostra o que faria)
   - `python baixar_fontes.py` (baixa)
4. Leia o RESUMO no final: baixados, já existentes, pendentes e erros.

## Completando os PENDENTES

1. Abra o site oficial indicado em "onde achar".
2. Copie o link direto do PDF/texto.
3. Cole em `url` na lista `FONTES` do script (e confira a `data` do ato).
4. Rode de novo: só os novos serão baixados.

Só são aceitos domínios oficiais (planalto, gov.br, STF, STJ, PGFN, SEFAZ-PE, NF-e).

## Próximo passo

Com os arquivos na pasta, envie-os (ou o `INDICE.md`) e a nota
`ICMS-BASE-PIS-COFINS_LP-LR.md` será gerada com FATO / INTERPRETAÇÃO / RECOMENDAÇÃO,
sem inventar nada fora dos arquivos.

## Limitações

- Não testado contra os sites reais (o ambiente de desenvolvimento bloqueia esses domínios).
  Se algum link falhar, aparece em "Erros"; corrija a URL.
- Datas dos atos pendentes (Parecer PGFN, IN 2.055) devem ser conferidas no próprio ato.
- Sites do governo às vezes bloqueiam download automático: baixe manualmente e salve com o nome padrão.
