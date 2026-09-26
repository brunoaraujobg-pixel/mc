# Análise do cadastro de estoque — Lucro Presumido + IBS/CBS

Lê a exportação do cadastro de produtos (CSV separado por `;`, layout
`ID;CODIGO;NOME;CODIGONCM;CST;CSOSN;ALIQECF;CSTPIS...;CCLASSTRIB;`) e gera
um relatório com tudo que está errado ou precisa de conferência para uma
empresa do **Lucro Presumido**, incluindo a parametrização do **IBS/CBS**.

Não altera o arquivo original — só lê e gera relatório.

## Como usar (Windows)

1. Instale o Python (python.org) marcando "Add Python to PATH".
2. Abra o Prompt de Comando nesta pasta.
3. Rode:

   ```
   python analisar_estoque.py C:\caminho\estoque26.csv
   ```

4. Ao lado do CSV aparecem:
   - `estoque26_relatorio.csv` — uma linha por problema (abre no Excel);
   - `estoque26_resumo.txt` — total de produtos por regra.

Não precisa instalar nenhuma biblioteca extra.

## O que é conferido

| Área | Regra | Gravidade |
|---|---|---|
| PIS/COFINS | Alíquota de débito diferente de 0,65 / 3,00 (cumulativo) | ERRO |
| PIS/COFINS | CST de entrada com crédito (50–56) e alíquota de crédito ≠ 0 | ERRO |
| PIS/COFINS | CST inexistente (ex.: `00`) | ERRO |
| PIS/COFINS | CST 04–09 sem natureza da receita | ERRO |
| PIS/COFINS | Mesmo NCM com CST de saída diferentes | ERRO |
| PIS/COFINS | NCM de grupo monofásico com CST 01 | VERIFICAR |
| ICMS | CST 060 sem CEST; CST x CFOP incoerente; CFOP vazio | ERRO |
| ICMS | CST 010/020 no varejo; alíquota ≠ 20,5% (PE) | VERIFICAR |
| IBS/CBS | cClassTrib vazio ou inválido (NF-e rejeitada) | ERRO |
| IBS/CBS | 200035 (Anexo VIII) em NCM fora do anexo | ERRO |
| IBS/CBS | NCM do Anexo VIII sem 200035; conferir descrição | VERIFICAR |
| IBS/CBS | NCM 3808/31 — redução de insumo agropecuário (Anexo IX) | VERIFICAR |
| Cadastro | Nome com `;` que quebra as colunas | AVISO |

O CST do IBS/CBS são os 3 primeiros dígitos do cClassTrib
(`000001` → CST 000; `200035` → CST 200).

## Limitações (versão 1)

- A lista do Anexo VIII está fixa no script; se a lei mudar, atualizar `ANEXO_VIII`.
- Monofásico e insumo agropecuário são só "VERIFICAR": o script aponta o
  candidato, a decisão final é do contador.
- Alíquota interna de ICMS considera Pernambuco (20,5%).

## Evolução

- V2: gerar CSV corrigido pronto para reimportar no sistema.
- V3: tabelas oficiais (cClassTrib, 4.3.10, CEST) baixadas e cruzadas automaticamente.
