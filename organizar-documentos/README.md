# Organizar Documentos por Agente/Assunto

Script em Python que organiza automaticamente os arquivos soltos de uma pasta
"documentos", movendo cada um para a subpasta do agente/assunto correspondente
(Simples Nacional, Lucro Presumido, Lucro Real, ICMS/ICMS-ST, PIS/COFINS,
eSocial/Folha, Federal), com base em palavras-chave no nome do arquivo.

## O que ele faz

1. Lê o nome de cada arquivo na raiz da pasta `documentos`.
2. Compara o nome com as palavras-chave de cada categoria.
3. **Move** (não copia) o arquivo para a subpasta correspondente.
4. Quando não reconhece o assunto pelo nome, move para `outros_classificar`
   — assim você revisa só o que ficou de fora.
5. Gera um `log_organizacao.txt` dentro da pasta `documentos` com tudo que
   foi movido, para conferência ou eventual reversão manual.
6. Nunca sobrescreve arquivos: se já existir um arquivo com o mesmo nome no
   destino, o script acrescenta um número ao final (`_1`, `_2`, ...).
7. Não mexe em subpastas já existentes — só organiza arquivos soltos na raiz.

Nada é excluído em nenhuma etapa.

## Como usar

1. Instale o Python 3 (Windows: baixe em https://www.python.org/downloads/,
   marcando a opção "Add Python to PATH" durante a instalação).
2. Abra o arquivo `organizar_documentos.py` e ajuste a linha:
   ```python
   PASTA_DOCUMENTOS = r"C:\PROJETOS\Analista_Contabil\documentos"
   ```
   para o caminho real da sua pasta de documentos.
3. Rode pelo terminal (cmd/PowerShell), na pasta onde o arquivo está:
   ```
   python organizar_documentos.py
   ```
4. Acompanhe a saída no terminal e revise `outros_classificar` e o
   `log_organizacao.txt` gerados dentro da pasta `documentos`.

## Ajustar as categorias

As palavras-chave de cada agente ficam no dicionário `CATEGORIAS`, no topo
do script. Para reconhecer mais padrões de nome de arquivo, basta acrescentar
palavras às listas existentes ou criar uma nova categoria.

## Próximos passos (evolução futura)

- Reconhecer o assunto também pelo conteúdo do arquivo (não só pelo nome),
  útil para PDFs escaneados ou nomes genéricos.
- Separar também por empresa, além de por assunto.
- Gerar relatório resumido (quantidade por categoria) além do log detalhado.
