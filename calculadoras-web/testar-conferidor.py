# -*- coding: utf-8 -*-
"""
TESTAR-CONFERIDOR.PY — testes do conferidor de tabelas
============================================================================

O conferir-tabelas.py faz duas coisas delicadas:
  1) transforma o HTML de uma página do governo em texto limpo;
  2) procura um número nesse texto SEM casar no meio de um número maior.

Este arquivo testa as duas coisas com uma página de mentira, montada no
formato que as páginas do gov.br usam (tabela HTML, &nbsp;, entidades,
<script> no meio). Assim, se alguém mexer no conferidor e quebrar a
extração, o teste acusa — sem depender de internet.

Como rodar:
    python testar-conferidor.py

Não precisa de internet. Não instala nada.
"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

PASTA = Path(__file__).resolve().parent


def carregar_conferidor():
    caminho = PASTA / "conferir-tabelas.py"
    spec = importlib.util.spec_from_file_location("conferidor", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# Página de mentira no formato das páginas do gov.br.
PAGINA_FALSA = """<html><head><style>.x{color:red}</style></head><body>
<script>var ruido = "9.999,99";</script>
<table>
  <tr><td>At&eacute;&nbsp;R$&nbsp;2.428,80</td><td>-</td><td>-</td></tr>
  <tr><td>De R$ 2.428,81 at&eacute; R$ 2.826,65</td><td>7,5%</td><td>R$&nbsp;182,16</td></tr>
  <tr><td>Acima de R$ 4.664,68</td><td>27,5%</td><td>R$ 908,73</td></tr>
</table>
<p>Dedu&ccedil;&atilde;o por dependente: R$ 189,59</p>
<p>Valor de controle, bem maior: R$ 84.500,00</p>
</body></html>"""


def main():
    conferidor = carregar_conferidor()

    arquivo = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
    arquivo.write(PAGINA_FALSA)
    arquivo.close()

    try:
        texto = conferidor.baixar("file://" + arquivo.name)
    finally:
        os.unlink(arquivo.name)

    resultados = []

    def conferir(nome, obtido, esperado):
        resultados.append((nome, obtido == esperado, esperado, obtido))

    # --- extração do texto -------------------------------------------------
    conferir("HTML: removeu as marcacoes <table>/<td>", "<td>" not in texto, True)
    conferir("HTML: removeu o conteudo de <style>", "color:red" not in texto, True)
    conferir("HTML: removeu o conteudo de <script>", "var ruido" not in texto, True)
    conferir("HTML: traduziu a entidade &ccedil;&atilde;o", "Dedução" in texto, True)
    conferir("HTML: trocou &nbsp; por espaco comum", "\xa0" not in texto, True)

    # --- busca dos números -------------------------------------------------
    achou = lambda v: conferidor.contem_numero(texto, v)

    conferir("acha 2.428,80 mesmo colado num &nbsp;", achou("2.428,80"), True)
    conferir("acha 182,16 dentro de uma celula", achou("182,16"), True)
    conferir("acha 908,73", achou("908,73"), True)
    conferir("acha 189,59 depois de entidade HTML", achou("189,59"), True)

    conferir("NAO acha 4.500,00 dentro de 84.500,00", achou("4.500,00"), False)
    conferir("NAO acha 500,00 dentro de 84.500,00", achou("500,00"), False)
    conferir("NAO acha 9.999,99 que so existia no <script>", achou("9.999,99"), False)
    conferir("NAO acha 2.826,6 como pedaco de 2.826,65", achou("2.826,6"), False)
    conferir("NAO acha 3.751,05 que nao esta na pagina", achou("3.751,05"), False)

    # --- lado do js/tabelas.js --------------------------------------------
    js = conferidor.carregar_tabelas_js()
    no_js = lambda v: conferidor.contem_numero(js, v)

    conferir("js/tabelas.js tem 2428.80", no_js("2428.80"), True)
    conferir("js/tabelas.js tem 908.73", no_js("908.73"), True)
    conferir("js/tabelas.js tem 0.133145", no_js("0.133145"), True)
    conferir("js/tabelas.js tem 1250000.00", no_js("1250000.00"), True)
    conferir("js/tabelas.js NAO casa 428.80 dentro de 2428.80", no_js("428.80"), False)
    conferir("js/tabelas.js NAO tem 999.99", no_js("999.99"), False)

    # --- a lista de verificacoes esta coerente com o js -------------------
    fora_do_js = []
    for bloco in conferidor.VERIFICACOES:
        for descricao, _no_site, no_arquivo_js in bloco["valores"]:
            if not no_js(no_arquivo_js):
                fora_do_js.append(bloco["grupo"] + " -> " + descricao + " (" + no_arquivo_js + ")")
    conferir("todo valor da lista VERIFICACOES existe em js/tabelas.js",
             fora_do_js, [])

    # --- resultado ---------------------------------------------------------
    falhas = 0
    for nome, ok, esperado, obtido in resultados:
        if not ok:
            falhas += 1
            print("  FALHA | " + nome)
            print("          esperado: " + repr(esperado))
            print("          obtido:   " + repr(obtido))
        else:
            print("  OK    | " + nome)

    print()
    print(str(len(resultados)) + " testes | " + str(len(resultados) - falhas) +
          " passaram | " + str(falhas) + " falharam")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
