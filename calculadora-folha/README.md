# calculadora-folha

Calculadora web de **folha mensal, férias, 13º salário e rescisão**, em um único
arquivo HTML. Abre com duplo clique no Windows, funciona offline e também no
celular. Serve para conferir o que o sistema de folha calculou, simular um
desligamento antes de fazer e explicar o número para o cliente — cada resultado
vem com a **memória de cálculo linha a linha**.

## Como usar

1. Baixe o arquivo `index.html`.
2. Dê duplo clique. Abre no navegador (Chrome, Edge, Firefox), sem instalar nada.
3. Escolha a aba, digite os valores e o resultado aparece na hora.
4. Botão **Copiar memória** joga o cálculo em texto para colar no e-mail, no
   WhatsApp ou no processo. Botão **Imprimir** gera o PDF pelo navegador.

Não há servidor, banco de dados nem envio de informação para fora: tudo é
calculado dentro do navegador.

## O que cada aba calcula

| Aba | O que entra | O que sai |
|---|---|---|
| **Folha mensal** | salário, horas extras, adicional noturno, insalubridade, periculosidade, DSR, faltas, VT, pensão, dependentes | proventos, INSS, IRRF, descontos, líquido, FGTS e custo do empregador |
| **Férias** | salário, médias, dias de gozo, venda de 1/3, adiantamento do 13º | férias + 1/3, abono, INSS, IRRF, líquido e FGTS |
| **13º salário** | salário, médias, avos, adiantamento pago | 13º bruto, INSS e IRRF em apuração separada, 2ª parcela |
| **Rescisão** | admissão, saída, motivo, tipo de aviso, férias vencidas, saldo do FGTS | saldo de salário, aviso, 13º e férias proporcionais, férias vencidas, INSS/IRRF, líquido do TRCT, FGTS e multa |
| **Tabelas** | INSS, IRRF, redutor, dependente, simplificado, FGTS, terceiros | tabelas editáveis, salvas no navegador |

## Regras aplicadas

- **INSS**: tabela progressiva faixa a faixa, limitada ao teto. Apuração do 13º
  em separado do salário do mês.
- **IRRF**: compara as deduções legais (INSS + dependentes + pensão) com o
  desconto simplificado e usa a mais vantajosa; aplica o **redutor da Lei
  15.270/2025**, que zera o imposto até R$ 5.000,00 e se extingue em R$ 7.350,00.
- **Isenções na rescisão**: aviso prévio indenizado e férias indenizadas
  (vencidas e proporcionais, com o terço) não sofrem INSS nem IRRF
  (Súmula 386 do STJ); o abono pecuniário das férias também é isento.
- **Aviso prévio**: 30 dias + 3 por ano trabalhado, limitado a 90
  (Lei 12.506/2011); metade no acordo do art. 484-A; o indenizado **projeta**
  o contrato e gera avos adicionais de férias e 13º.
- **Justa causa**: sem 13º proporcional e sem férias proporcionais; férias
  vencidas continuam devidas.
- **FGTS**: 8% sobre saldo de salário, 13º e aviso indenizado (não incide sobre
  férias indenizadas). Multa de 40% (sem justa causa) ou 20% (acordo) sobre o
  saldo da conta informado + FGTS da rescisão — depositada na conta vinculada,
  por isso **não** entra no líquido do TRCT.
- **Avos**: cada mês com 15 dias ou mais de trabalho vale 1/12.

## Tabelas — vigência 2026 (valores padrão)

- Salário mínimo: **R$ 1.621,00**
- INSS: 7,5% até 1.621,00 · 9% até 2.902,84 · 12% até 4.354,27 · 14% até o teto
  de **8.475,55** (desconto máximo R$ 988,09)
- IRRF mensal (mantida desde maio/2025): isento até 2.428,80 · 7,5% (ded.
  182,16) · 15% (394,16) · 22,5% (675,49) · 27,5% (908,73)
- Dependente: R$ 189,59 · Desconto simplificado: R$ 607,20
- Redutor da Lei 15.270/2025: **R$ 978,62 − (0,133145 × rendimento tributável)**,
  aplicado de R$ 5.000,01 a R$ 7.350,00; abaixo disso o imposto é zerado

**As tabelas mudam.** Na aba *Tabelas* dá para editar todas as faixas, alíquotas
e parâmetros e clicar em *Salvar* — os valores ficam gravados no navegador e
passam a valer em todas as abas. Sempre confirme na fonte oficial (Portaria
interministerial do MPS/MF para o INSS, IN da Receita Federal para o IRRF) antes
de usar em fechamento.

## Limitações desta versão

Não estão contemplados: salário-família, contribuição sindical, convenção
coletiva, média de horas extras nas férias/13º calculada automaticamente,
término antecipado de contrato de experiência (arts. 479 e 480 da CLT),
estabilidade, afastamento, aposentadoria, múltiplos vínculos e rescisão
complementar. Os valores são de conferência e não substituem o sistema de folha.

## Próximas versões

1. **V2** — salário-família, médias automáticas de variáveis, escolha do regime
   de tributação do IRRF nas férias, exportação do resultado em PDF formatado.
2. **V3** — importar a folha do Domínio (TXT/planilha) e conferir empresa
   inteira de uma vez, apontando divergências linha a linha.
3. **V4** — virar serviço do orquestrador (Agente Folha/eSocial), cruzando com
   os eventos do eSocial e gerando alertas de fechamento.

## Nota técnica

O arquivo é HTML puro, sem dependências além da fonte do Google (se não carregar,
o navegador usa a fonte do sistema e nada quebra). A versão publicada na web é
gerada a partir deste mesmo arquivo.
