# zeramento-dominio

Analisa balancetes exportados do Domínio (um arquivo por empresa) e gera uma
planilha com: resumo por empresa, lançamentos sugeridos de zeramento e
mapeamento de contas (de/para) entre as empresas.

**Versão 1:** NÃO acessa nem altera o Domínio. Só lê arquivos exportados e
gera uma planilha para você conferir antes de lançar.

## Como usar

1. Instalar o Python e as dependências: `pip install -r requirements.txt`
2. No Domínio, exportar o balancete de cada empresa (Excel ou CSV) e colocar
   todos em uma pasta, um arquivo por empresa (o nome do arquivo vira o nome
   da empresa). Colunas aceitas: conta/código, classificação, descrição,
   saldo, natureza (D/C, opcional). Saldo negativo = credor.
3. Rodar:

```
python zeramento_dominio.py C:\balancetes --contrapartida 2.3.01.001 --data 31/12/2025
```

Opções: `--prefixos 3,4` (classificações a zerar; confira no seu plano de
contas), `--saida arquivo.xlsx`.

## Planilha gerada

- **Resumo** – contas lidas, contas a zerar, totais devedor/credor por empresa.
- **Zeramento** – débito/crédito/valor/histórico de cada conta analítica com saldo.
- **Mapeamento** – classificação × empresa, indicando "igual", "descrição
  diferente" ou "só em uma empresa".

## Limites e próximos passos

- A conta de contrapartida e os prefixos (3,4) são sua decisão contábil.
- O layout de importação de lançamentos do Domínio ainda não foi validado;
  a planilha é de conferência. Versão 2: gerar o layout exato de importação.
- Testar primeiro com 1 ou 2 empresas.
