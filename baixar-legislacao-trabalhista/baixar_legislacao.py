# -*- coding: utf-8 -*-
r"""
BAIXAR LEGISLAÇÃO TRABALHISTA — V1 (versão mínima funcionando)
================================================================
O QUE ESTE SCRIPT FAZ:
  - Baixa o texto oficial ATUALIZADO/COMPILADO da CLT e de leis trabalhistas
    correlatas, diretamente do site do Planalto (fonte oficial).
  - Salva tudo organizado em pastas, com um arquivo de log.

O QUE ESTE SCRIPT *NÃO* FAZ (ainda) NESTA V1:
  - Não baixa decisões do STF/STJ automaticamente. Os portais de
    jurisprudência do STF e do STJ carregam o conteúdo via JavaScript
    (não é uma página HTML simples), então não dá pra baixar só com
    "requests" — precisaria de outra ferramenta (Selenium), que fica
    pra V2. Por enquanto, deixei abaixo uma lista JÁ PRONTA das
    súmulas/temas mais relevantes pra transporte de cargas e motorista
    profissional, com o link oficial de cada uma, pra você conferir
    manualmente enquanto a V2 não fica pronta.

COMO USAR (passo a passo):
  1. Instale o Python (se ainda não tiver): https://www.python.org/downloads/
     Ao instalar, marque a caixinha "Add Python to PATH".
  2. Abra o "Prompt de Comando" (cmd) do Windows.
  3. Instale a única biblioteca extra que este script usa:
         pip install -r requirements.txt
  4. Coloque este arquivo numa pasta (ex.: C:\BibliotecaTrabalhista\)
  5. No cmd, entre na pasta e rode:
         python baixar_legislacao.py
  6. O script vai criar a pasta "biblioteca_trabalhista" ao lado dele,
     com tudo baixado e organizado.

O QUE DEVE APARECER:
  - Mensagens no próprio cmd dizendo o que está baixando.
  - No final, um resumo: quantos arquivos baixou, quantos falharam.
  - Um arquivo "log_coleta.txt" dentro da pasta de saída.

SE DER ERRO:
  - "pip não é reconhecido" -> o Python não foi instalado com PATH.
    Reinstale marcando a opção "Add Python to PATH".
  - "ModuleNotFoundError: requests" -> rode "pip install -r requirements.txt"
    de novo, na mesma pasta/terminal.
  - Erro de conexão numa lei específica -> normal, o site pode estar
    temporariamente fora do ar; o script pula e segue pras outras,
    e registra a falha no log.

IMPORTANTE SOBRE A LEI 12.619/2012:
  Essa lei (que criou as primeiras regras de jornada/descanso do
  motorista profissional) foi REVOGADA pela Lei 13.103/2015, que é a
  que está em vigor hoje sobre o tema. Ela é baixada aqui só como
  referência histórica (ex.: para entender ações judiciais de períodos
  antigos), não deve ser usada como base para situações atuais. Veja o
  README.md desta pasta para mais detalhes.
"""

import os
import json
import datetime
import time
import requests

# --------------------------------------------------------------------
# CONFIGURAÇÃO — pode editar esta lista pra adicionar mais leis depois
# --------------------------------------------------------------------

PASTA_SAIDA = "biblioteca_trabalhista"

# Texto oficial CONSOLIDADO (já com todas as alterações vigentes).
CLT_URL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452compilado.htm"

LEIS_CORRELATAS = {
    "lei_13103_2015_motorista_profissional": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13103.htm",
    "lei_605_1949_repouso_semanal_remunerado": "https://www.planalto.gov.br/ccivil_03/leis/l0605.htm",
    "lei_8036_1990_fgts": "https://www.planalto.gov.br/ccivil_03/leis/l8036consol.htm",
    "lei_8213_1991_beneficios_inss": "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm",
    "lei_12619_2012_motorista_profissional_REVOGADA_ver_readme": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12619.htm",
    "lei_13467_2017_reforma_trabalhista": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/lei/l13467.htm",
}

# --------------------------------------------------------------------
# Lista curada de súmulas/temas do STF/STJ relevantes (V1 = manual,
# conferida por fonte oficial; a V2 vai buscar isso automaticamente).
# --------------------------------------------------------------------

JURISPRUDENCIA_RELEVANTE = [
    {
        "tribunal": "STF",
        "tipo": "Repercussão Geral",
        "referencia": "Tema 725",
        "assunto": "Terceirização de atividade-fim - licitude",
        "link_oficial": "https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?incidente=4664162",
    },
    {
        "tribunal": "STJ",
        "tipo": "Súmula",
        "referencia": "A confirmar número exato no site oficial",
        "assunto": "Verificar se há súmula específica sobre ajuda de custo/diária de viagem de motorista",
        "link_oficial": "https://scon.stj.jus.br/",
    },
    # ATENÇÃO: esta lista é só um ponto de partida. Ela precisa ser
    # revisada e ampliada manualmente, ou pela V2 (Selenium), antes de
    # ser usada como fonte definitiva em qualquer parecer.
]


# --------------------------------------------------------------------
# FUNÇÕES
# --------------------------------------------------------------------

def preparar_pastas():
    """Cria a estrutura de pastas de saída."""
    subpastas = ["clt", "leis", "stf", "stj"]
    for sub in subpastas:
        caminho = os.path.join(PASTA_SAIDA, sub)
        os.makedirs(caminho, exist_ok=True)
    return PASTA_SAIDA


def baixar_pagina(url, destino, log):
    """
    Baixa uma página HTML de uma URL e salva em disco.
    Retorna True se deu certo, False se falhou.
    Nunca derruba o script inteiro em caso de erro.
    """
    try:
        resposta = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ColetaLegislacao/1.0)"
        })
        resposta.raise_for_status()

        conteudo = resposta.text
        if not conteudo or len(conteudo.strip()) < 200:
            # Página vazia ou suspeita de bloqueio — não salva como sucesso
            log.append(f"[FALHA] {url} -> resposta vazia ou muito curta")
            return False

        with open(destino, "w", encoding="utf-8") as f:
            f.write(conteudo)

        log.append(f"[OK] {url} -> {destino}")
        return True

    except requests.exceptions.RequestException as erro:
        log.append(f"[FALHA] {url} -> {erro}")
        return False


def baixar_clt(pasta_saida, log):
    print("Baixando CLT atualizada (texto compilado)...")
    destino = os.path.join(pasta_saida, "clt", "clt_atualizada.html")
    ok = baixar_pagina(CLT_URL, destino, log)

    metadata = {
        "fonte": CLT_URL,
        "data_download": datetime.datetime.now().isoformat(),
        "sucesso": ok,
    }
    with open(os.path.join(pasta_saida, "clt", "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return ok


def baixar_leis(pasta_saida, log):
    print("Baixando leis trabalhistas correlatas...")
    sucessos = 0
    falhas = 0
    for nome, url in LEIS_CORRELATAS.items():
        destino = os.path.join(pasta_saida, "leis", f"{nome}.html")
        print(f"  - {nome}")
        ok = baixar_pagina(url, destino, log)
        if ok:
            sucessos += 1
        else:
            falhas += 1
        time.sleep(1)  # educado com o servidor do Planalto
    return sucessos, falhas


def salvar_jurisprudencia_curada(pasta_saida, log):
    """
    V1: salva a lista curada manualmente (ver JURISPRUDENCIA_RELEVANTE
    no topo do arquivo) como ponto de partida, separada por tribunal.
    """
    print("Salvando lista inicial de jurisprudência relevante (STF/STJ)...")
    for item in JURISPRUDENCIA_RELEVANTE:
        pasta_tribunal = item["tribunal"].lower()
        nome_arquivo = item["referencia"].replace(" ", "_").replace("/", "-") + ".json"
        destino = os.path.join(pasta_saida, pasta_tribunal, nome_arquivo)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
        log.append(f"[OK - CURADO MANUALMENTE, CONFERIR] {item['tribunal']} {item['referencia']} -> {destino}")


def gerar_log(pasta_saida, log, resumo):
    caminho_log = os.path.join(pasta_saida, "log_coleta.txt")
    with open(caminho_log, "w", encoding="utf-8") as f:
        f.write(f"LOG DE COLETA — {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        for linha in log:
            f.write(linha + "\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("RESUMO\n")
        for chave, valor in resumo.items():
            f.write(f"{chave}: {valor}\n")
    return caminho_log


def main():
    print("=" * 60)
    print("COLETA DE LEGISLAÇÃO TRABALHISTA — V1")
    print("=" * 60)
    print()
    print("Este script vai baixar arquivos de sites oficiais do governo.")
    resposta = input("Confirma que pode continuar? (s/n): ").strip().lower()
    if resposta != "s":
        print("Cancelado pelo usuário.")
        return

    log = []
    pasta_saida = preparar_pastas()

    clt_ok = baixar_clt(pasta_saida, log)
    leis_ok, leis_falha = baixar_leis(pasta_saida, log)
    salvar_jurisprudencia_curada(pasta_saida, log)

    resumo = {
        "CLT baixada com sucesso": "Sim" if clt_ok else "NÃO - verificar log",
        "Leis baixadas com sucesso": leis_ok,
        "Leis com falha": leis_falha,
        "Itens de jurisprudência salvos (lista curada V1)": len(JURISPRUDENCIA_RELEVANTE),
    }

    caminho_log = gerar_log(pasta_saida, log, resumo)

    print()
    print("=" * 60)
    print("CONCLUÍDO")
    print("=" * 60)
    for chave, valor in resumo.items():
        print(f"{chave}: {valor}")
    print()
    print(f"Tudo salvo em: {os.path.abspath(pasta_saida)}")
    print(f"Log completo em: {os.path.abspath(caminho_log)}")
    print()
    print("IMPORTANTE: a parte de STF/STJ nesta V1 é uma lista inicial")
    print("feita manualmente, não uma busca automática. Precisa ser")
    print("conferida e ampliada antes de usar como fonte definitiva.")
    print()
    print("IMPORTANTE: a Lei 12.619/2012 foi baixada só como referência")
    print("histórica — ela foi REVOGADA pela Lei 13.103/2015. Veja o")
    print("README.md desta pasta.")


if __name__ == "__main__":
    main()
