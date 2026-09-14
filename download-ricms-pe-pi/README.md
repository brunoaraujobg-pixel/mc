# Download e Validação — RICMS-PE e RICMS-PI

Script em Python que baixa das fontes oficiais, valida e organiza os
Regulamentos do ICMS de Pernambuco e do Piauí, para o acervo legal
tributário do escritório. Não resume nem edita o conteúdo dos decretos —
baixa sempre o PDF integral.

## ⚠️ Achado importante sobre o Piauí

O pedido original citava o **Decreto nº 13.500/2008** para o RICMS-PI, mas
esse decreto foi **revogado**. O regulamento vigente hoje é o
**Decreto nº 21.866, de 06/03/2023**, em vigor desde 08/03/2023
(confirmado por busca à fonte oficial da SEFAZ-PI antes de escrever o
script). O script já baixa a versão correta (21.866/2023), não a antiga.

## Fontes oficiais usadas

| UF | Decreto | Fonte | URL |
|---|---|---|---|
| PE | 44.650/2017 (30/06/2017) | SEFAZ-PE | https://www.sefaz.pe.gov.br/Legislacao/Tributaria/Documents/Legislacao/44650/Para%20Download/Regulamento.pdf |
| PI | 21.866/2023 (06/03/2023, vigente desde 08/03/2023) | SEFAZ-PI (Portal da Legislação) | https://portaldalegislacao.sefaz.pi.gov.br/Arquivos/ARQUIVOS_CHRONUS/ARQUIVO_PRINCIPAL_LEGISLACAO/1400/Decreto_n_21.866_2023_-_REGULAMENTO_DO_ICMS_DO_ESTADO_DO_PIAUI.pdf |

Ambas são fontes oficiais (domínio `sefaz.pe.gov.br` e `sefaz.pi.gov.br`),
não são consolidações de terceiros.

**Pendência de verificação:** este ambiente de desenvolvimento (sandbox
onde o script foi escrito) tem o acesso à internet bloqueado para esses
domínios, então as URLs acima foram confirmadas por busca, mas **não pude
abrir os links diretamente daqui para conferir a última página de
consolidação/atualização do PDF**. Ao rodar o script na sua máquina (que
tem acesso normal à internet), ele mesmo baixa o arquivo direto da fonte —
confira a capa/primeira página do PDF baixado para validar número do
decreto e data, e registre no `INDICE.md` gerado se encontrar nota de
consolidação mais recente.

## O que o script faz

1. Baixa o PDF integral de cada decreto direto da URL oficial.
2. Confere se o arquivo baixado é mesmo um PDF (assinatura `%PDF`).
3. Abre o PDF com `pypdf` para confirmar que não está corrompido/truncado
   (conta as páginas).
4. Se já existir um PDF anterior com **conteúdo diferente**, guarda o
   antigo como backup (`_ANTERIOR_AAAA-MM-DD.pdf`) em vez de sobrescrever
   sem avisar. Se o conteúdo for idêntico, não baixa de novo.
5. Extrai o texto de cada página para um `.txt` de busca (UTF-8), separado
   por página, sem cortar artigo no meio.
6. Atualiza o `INDICE.md` da pasta com: arquivo, decreto, UF, data de
   publicação, vigência, data do download e URL de origem — sem apagar
   outras linhas já existentes no índice.

Nada é resumido, reescrito ou "limpo" no conteúdo dos decretos.

## Como usar

1. Instale o Python 3 (Windows: https://www.python.org/downloads/,
   marque "Add Python to PATH" na instalação).
2. Instale a dependência (abra o cmd/PowerShell nesta pasta):
   ```
   pip install -r requirements.txt
   ```
3. Confira a variável `PASTA_DESTINO` no topo de `baixar_ricms.py` — já
   está configurada para:
   ```
   C:\PROJETOS\Documento Analista\Credito Tributario
   ```
   Ajuste se sua pasta for outra.
4. Rode:
   ```
   python baixar_ricms.py
   ```
5. Acompanhe a saída no terminal. Ao final ele informa o que baixou, se
   validou corretamente, e lista qualquer pendência (ex.: site fora do ar).

## Estrutura gerada na pasta de destino

```
RICMS_PE_Decreto_44650_2017.pdf
PE_RICMS_44650_texto_para_busca.txt
RICMS_PI_Decreto_21866_2023.pdf
PI_RICMS_21866_texto_para_busca.txt
INDICE.md
```

## Se algo falhar

O script nunca inventa dado nem completa com estimativa: se não conseguir
baixar ou validar um PDF, ele imprime exatamente o que faltou, sugere a
URL de referência (página da legislação) como fonte alternativa oficial, e
não mexe nos arquivos já existentes daquele documento.

## Próximos passos (evolução futura)

- Checar automaticamente, a cada execução, se a SEFAZ publicou uma
  atualização/consolidação mais recente do mesmo decreto (comparando data
  de publicação da página com a última registrada no `INDICE.md`).
- Guardar o histórico de alterações de cada RICMS (decretos que alteram
  artigos), para permitir checagem de vigência por competência.
- Estender para outros estados usados no escritório.
