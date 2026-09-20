"""
ORGANIZAR DOCUMENTOS POR AGENTE/ASSUNTO
-----------------------------------------
O que este script faz:
  1. Olha para o NOME de cada arquivo dentro da pasta "documentos"
  2. Compara com palavras-chave de cada agente (Simples, Lucro Real, ICMS, etc.)
  3. MOVE o arquivo para a subpasta correta
  4. Se não reconhecer o assunto pelo nome, move para "outros_classificar"
     (assim você revisa só o que ficou de fora, e não precisa conferir tudo de novo)
  5. Grava um arquivo log_organizacao.txt com tudo que foi movido, pra você
     conferir ou desfazer se precisar.

NÃO EXCLUI NADA. Só move de lugar dentro da própria pasta "documentos".
"""

import os
import shutil
from datetime import datetime

# ============================================================
# 1) AJUSTE APENAS ESTA LINHA para o caminho real da sua pasta
# ============================================================
PASTA_DOCUMENTOS = r"C:\PROJETOS\Analista_Contabil\documentos"

# ============================================================
# 2) TRAVA DE SEGURANCA - nao mexa nesta lista sem pensar duas vezes
# ============================================================
# Estas pastas alimentam OUTROS sistemas (importacao de notas, EFD, Fronteira).
# Eles dependem do padrao de pastas e de arquivos soltos onde estao. Se este
# script rodar em uma delas, reorganiza tudo em subpastas e quebra a importacao
# — sem desfazer automatico. Por isso a execucao e recusada nesses caminhos.
PASTAS_PROIBIDAS = [
    r"c:\nota entrada",
    r"c:\nota saida",
    r"c:\nota saída",
    r"c:\fronteira",
    r"\efd",
    r"relatorios de api",
    r"relatórios de api",
]


def caminho_proibido(caminho):
    """Diz se o caminho informado (ou uma pasta acima dele) e de uso de outro sistema."""
    baixo = os.path.abspath(caminho).lower().replace("/", "\\")
    return [p for p in PASTAS_PROIBIDAS if p in baixo]

# Palavras-chave (em minúsculo) que identificam cada agente/assunto.
# Pode adicionar mais palavras nas listas conforme for precisando.
CATEGORIAS = {
    "simples_nacional": ["simples", "anexo", "csosn", "pgdas", "sn_"],
    "lucro_presumido":  ["presumido"],
    "lucro_real":       ["lucro_real", "lucroreal", "sped", "ecf", "ecd"],
    "icms_icms-st":     ["icms", "difal", "fronteira", "cest", "cfop", "ncm", "st_"],
    "pis_cofins":       ["pis", "cofins"],
    "esocial_folha":    ["esocial", "folha", "fgts", "inss", "ferias", "férias"],
    "federal":          ["irpj", "csll", "receita_federal", "pgfn", "decore"],
}

PASTA_OUTROS = "outros_classificar"


def escolher_categoria(nome_arquivo):
    nome = nome_arquivo.lower()
    for categoria, palavras in CATEGORIAS.items():
        for palavra in palavras:
            if palavra in nome:
                return categoria
    return PASTA_OUTROS


def mover_sem_sobrescrever(origem, pasta_destino):
    os.makedirs(pasta_destino, exist_ok=True)
    nome = os.path.basename(origem)
    destino = os.path.join(pasta_destino, nome)

    # Se já existir um arquivo com o mesmo nome, acrescenta um número
    contador = 1
    base, ext = os.path.splitext(nome)
    while os.path.exists(destino):
        destino = os.path.join(pasta_destino, f"{base}_{contador}{ext}")
        contador += 1

    shutil.move(origem, destino)
    return destino


def main():
    proibidas = caminho_proibido(PASTA_DOCUMENTOS)
    if proibidas:
        print("ERRO: esta pasta alimenta outro sistema e NAO pode ser reorganizada.")
        print(f"  Pasta informada: {PASTA_DOCUMENTOS}")
        print(f"  Regra atingida.: {', '.join(proibidas)}")
        print("")
        print("Mover arquivos daqui quebra a importacao de notas, a EFD ou a Fronteira.")
        print("Se realmente for necessario, faca manualmente, com backup antes.")
        return

    if not os.path.isdir(PASTA_DOCUMENTOS):
        print(f"ERRO: pasta não encontrada: {PASTA_DOCUMENTOS}")
        print("Ajuste a variável PASTA_DOCUMENTOS no início do script.")
        return

    log_linhas = [f"Organização executada em {datetime.now():%d/%m/%Y %H:%M}\n"]
    total = 0

    for nome_arquivo in os.listdir(PASTA_DOCUMENTOS):
        caminho_completo = os.path.join(PASTA_DOCUMENTOS, nome_arquivo)

        # Pula subpastas (só organiza arquivos soltos na raiz de "documentos")
        if os.path.isdir(caminho_completo):
            continue

        categoria = escolher_categoria(nome_arquivo)
        pasta_destino = os.path.join(PASTA_DOCUMENTOS, categoria)
        destino_final = mover_sem_sobrescrever(caminho_completo, pasta_destino)

        linha = f"{nome_arquivo}  ->  {categoria}/{os.path.basename(destino_final)}"
        print(linha)
        log_linhas.append(linha)
        total += 1

    log_linhas.append(f"\nTotal de arquivos organizados: {total}")

    caminho_log = os.path.join(PASTA_DOCUMENTOS, "log_organizacao.txt")
    with open(caminho_log, "w", encoding="utf-8") as f:
        f.write("\n".join(log_linhas))

    print(f"\nConcluído! {total} arquivo(s) organizado(s).")
    print(f"Log salvo em: {caminho_log}")
    print(f"Revise a pasta '{PASTA_OUTROS}' — são os arquivos que o nome não deixou claro o assunto.")


if __name__ == "__main__":
    main()
