# -*- coding: utf-8 -*-
"""
conferir_inventario.py - Cruza o que o escritorio usa (inventario.json) com o
catalogo CISA KEV: as vulnerabilidades que atacantes JA estao explorando.

Nao acessa a internet: le o acervo que ja foi baixado. Rode depois de atualizar
o acervo.

Uso (Prompt de Comando do Windows):
    python conferir_inventario.py
    python conferir_inventario.py --desde 2026-01-01
    python conferir_inventario.py --salvar

Codigos de saida:
    0 = nada do inventario aparece no catalogo
    1 = ha item do escritorio com vulnerabilidade em exploracao
    3 = erro (inventario ou acervo ausente)
"""

import argparse
import datetime as dt
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
ARQ_INVENTARIO = os.path.join(RAIZ, "inventario.json")
ARQ_KEV = os.path.join(RAIZ, "acervo", "vulnerabilidades", "cisa_kev.json")
DIR_RELATORIOS = os.path.join(RAIZ, "relatorios")


def carregar(caminho, oquee):
    if not os.path.exists(caminho):
        print("ERRO: %s nao encontrado em %s" % (oquee, caminho))
        if oquee == "catalogo CISA KEV":
            print("Baixe o acervo primeiro: python baixar_acervo.py --somente-essenciais")
        return None
    with io.open(caminho, encoding="utf-8") as f:
        return json.load(f)


def cruzar(inventario, kev, desde=None):
    vulns = kev.get("vulnerabilities", [])
    resultado = []
    for item in inventario["itens"]:
        termos = [t.lower() for t in item.get("termos", []) if t]
        achados = []
        for v in vulns:
            alvo = ("%s %s" % (v.get("vendorProject", ""), v.get("product", ""))).lower()
            if not any(t in alvo for t in termos):
                continue
            if desde and (v.get("dateAdded") or "") < desde:
                continue
            achados.append(v)
        achados.sort(key=lambda v: v.get("dateAdded", ""), reverse=True)
        resultado.append((item, achados))
    return resultado


def main():
    p = argparse.ArgumentParser(
        description="Cruza o inventario do escritorio com o catalogo CISA KEV.")
    p.add_argument("--desde", help="considerar so o que a CISA incluiu a partir desta data (AAAA-MM-DD). "
                                    "Padrao: ultimos 12 meses")
    p.add_argument("--tudo", action="store_true",
                   help="mostra o catalogo inteiro, inclusive falhas antigas (desde 2021)")
    p.add_argument("--salvar", action="store_true", help="grava o relatorio em relatorios/")
    args = p.parse_args()

    # Falha de 2008 em Windows ja foi corrigida ha muito tempo por qualquer
    # maquina atualizada. O que interessa no dia a dia e o que entrou no
    # catalogo recentemente.
    if not args.desde and not args.tudo:
        args.desde = (dt.date.today() - dt.timedelta(days=365)).isoformat()

    inventario = carregar(ARQ_INVENTARIO, "inventario")
    kev = carregar(ARQ_KEV, "catalogo CISA KEV")
    if inventario is None or kev is None:
        return 3

    resultado = cruzar(inventario, kev, args.desde)
    com_achado = [(i, a) for i, a in resultado if a]
    linhas = []

    def diz(s=""):
        print(s)
        linhas.append(s)

    diz("=" * 74)
    diz("INVENTARIO x VULNERABILIDADES EM EXPLORACAO (CISA KEV)")
    diz("=" * 74)
    diz("Catalogo KEV..: versao %s, %s vulnerabilidades" % (kev.get("catalogVersion"), kev.get("count")))
    diz("Inventario....: %s itens (%s)" % (len(inventario["itens"]), inventario.get("atualizado_em", "sem data")))
    if args.desde:
        diz("Periodo.......: a partir de %s (use --tudo para o catalogo inteiro)" % args.desde)
    else:
        diz("Periodo.......: catalogo inteiro")
    diz("")

    if not com_achado:
        diz("NENHUM item do inventario aparece no catalogo.")
        diz("")
        diz("Isso NAO quer dizer que esta tudo seguro: quer dizer que nao ha, hoje,")
        diz("vulnerabilidade publicamente explorada catalogada para o que voce declarou.")
        diz("Equipamento de uso domestico costuma ter pouca cobertura de CVE.")
    else:
        diz("ATENCAO: %s item(ns) do escritorio com vulnerabilidade em exploracao." % len(com_achado))
        diz("")
        diz("Leia assim: se o item esta com atualizacao automatica ligada e em dia, ele")
        diz("provavelmente ja esta corrigido. A lista serve para CONFERIR isso, e para")
        diz("agir onde a atualizacao depende de alguem (operadora, suporte, voce).")
        diz("")
        for item, achados in com_achado:
            marca = "[CRITICO PARA O ESCRITORIO] " if item.get("critico") else ""
            diz("%s%s" % (marca, item["nome"]))
            diz("  atualizado por: %s" % item.get("atualizado_por", "nao informado"))
            for v in achados[:6]:
                rw = " | USADA EM RANSOMWARE" if v.get("knownRansomwareCampaignUse") == "Known" else ""
                diz("  - %s (%s) %s%s" % (v.get("cveID"), v.get("dateAdded"),
                                          v.get("vulnerabilityName", "")[:60], rw))
                diz("      corrigir ate: %s | acao: %s" %
                    (v.get("dueDate", "-"), (v.get("requiredAction", "") or "")[:80]))
            if len(achados) > 6:
                diz("  ... e mais %s no periodo" % (len(achados) - 6))
            diz("")

    pendentes = [i["nome"] for i in inventario["itens"] if i["id"].startswith("PREENCHER")]
    if pendentes:
        diz("-" * 74)
        diz("INVENTARIO INCOMPLETO - %s item(ns) a preencher em inventario.json:" % len(pendentes))
        for n in pendentes:
            diz("  - %s" % n)
        diz("Um item nao declarado nunca sera conferido.")

    if args.salvar:
        os.makedirs(DIR_RELATORIOS, exist_ok=True)
        cam = os.path.join(DIR_RELATORIOS,
                           "inventario_kev_%s.md" % dt.datetime.now().strftime("%Y%m%d_%H%M"))
        with io.open(cam, "w", encoding="utf-8") as f:
            f.write("# Inventario x CISA KEV\n\n```\n" + "\n".join(linhas) + "\n```\n")
        print("")
        print("Relatorio: %s" % cam)

    return 1 if com_achado else 0


if __name__ == "__main__":
    sys.exit(main())
