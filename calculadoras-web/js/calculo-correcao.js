/* =============================================================================
   CALCULO-CORRECAO.JS — atualização monetária de valores
   -----------------------------------------------------------------------------
   Separado em duas partes de propósito:

     A) A MATEMÁTICA — funções puras, que recebem a lista de taxas mensais já
        pronta e devolvem o resultado. Não sabem o que é internet. É isso que
        os testes automáticos conferem, sem depender de rede.

     B) A BUSCA DOS ÍNDICES — vai ao Banco Central pegar as taxas do período.
        Essa parte pode falhar (rede do escritório, API fora do ar), e por isso
        devolve um erro tratado em vez de quebrar a tela.

   Nenhum valor de tabela aqui: séries e regras vêm de tabelas.js.
============================================================================= */

/* =========================== A) A MATEMÁTICA ============================== */

/* Fator de correção acumulado.
     composto -> (1+i1) x (1+i2) x ... x (1+in)   [IPCA, INPC, IGP-M, TR]
     soma     -> 1 + (i1 + i2 + ... + in)         [SELIC de tributos federais]
   As taxas entram em PERCENTUAL ao mês (ex.: 0,52 para 0,52%). */
function calcularFatorAcumulado(taxasMensais, metodo) {
  var fator, i;
  if (metodo === 'soma') {
    var soma = 0;
    for (i = 0; i < taxasMensais.length; i++) soma += Number(taxasMensais[i]);
    fator = 1 + soma / 100;
  } else {
    fator = 1;
    for (i = 0; i < taxasMensais.length; i++) fator *= (1 + Number(taxasMensais[i]) / 100);
  }
  return fator;
}

/* Atualização completa de um valor.
   Entrada (objeto):
     valorOriginal ....... obrigatório
     taxas ............... [{ data:'01/03/2025', valor: 0.52 }, ...] em ordem
     metodo .............. 'composto' ou 'soma'
     acrescentar1 ........ true soma 1% (regra do mês do pagamento na SELIC)
     jurosMensal ......... % ao mês de juros de mora (opcional, 0 = sem juros)
     jurosCompostos ...... true = capitaliza; false = juros simples
     multaPercentual ..... % de multa sobre o valor corrigido (opcional)
*/
function calcularAtualizacao(entrada) {
  var valor = Number(entrada.valorOriginal) || 0;
  var taxas = entrada.taxas || [];
  var metodo = entrada.metodo || 'composto';
  var meses = taxas.length;

  var apenasValores = taxas.map(function (t) { return Number(t.valor); });
  var fator = calcularFatorAcumulado(apenasValores, metodo);

  var umPorCento = 0;
  if (entrada.acrescentar1) {
    umPorCento = 0.01;
    fator += 0.01;
  }

  var valorCorrigido = arred2(valor * fator);
  var correcao = arred2(valorCorrigido - valor);

  /* Juros de mora sobre o valor JÁ corrigido, que é a prática usual. */
  var taxaJuros = (Number(entrada.jurosMensal) || 0) / 100;
  var juros = 0;
  if (taxaJuros > 0 && meses > 0) {
    juros = entrada.jurosCompostos
      ? arred2(valorCorrigido * (Math.pow(1 + taxaJuros, meses) - 1))
      : arred2(valorCorrigido * taxaJuros * meses);
  }

  var taxaMulta = (Number(entrada.multaPercentual) || 0) / 100;
  var multa = taxaMulta > 0 ? arred2(valorCorrigido * taxaMulta) : 0;

  var total = arred2(valorCorrigido + juros + multa);

  return {
    valorOriginal: arred2(valor),
    meses: meses,
    metodo: metodo,
    fatorAcumulado: fator,
    acrescimoUmPorCento: umPorCento,
    percentualCorrecao: (fator - 1),
    valorCorrigido: valorCorrigido,
    correcao: correcao,
    jurosMensal: Number(entrada.jurosMensal) || 0,
    jurosCompostos: !!entrada.jurosCompostos,
    juros: juros,
    multaPercentual: Number(entrada.multaPercentual) || 0,
    multa: multa,
    total: total,
    variacaoTotal: valor > 0 ? (total - valor) / valor : 0,
    taxas: taxas
  };
}

/* Monta a lista de meses de um período, para conferência e para a consulta.
   Entrada: '2024-03' e '2026-08' (formato do campo <input type="month">) */
function listarMeses(mesInicial, mesFinal) {
  var a = String(mesInicial).split('-'), b = String(mesFinal).split('-');
  var ai = parseInt(a[0], 10), am = parseInt(a[1], 10);
  var bi = parseInt(b[0], 10), bm = parseInt(b[1], 10);
  if (!ai || !am || !bi || !bm) return [];

  var meses = [];
  var ano = ai, mes = am;
  var guarda = 0;
  while ((ano < bi || (ano === bi && mes <= bm)) && guarda++ < 1200) {
    meses.push({ ano: ano, mes: mes, rotulo: (mes < 10 ? '0' : '') + mes + '/' + ano });
    mes++;
    if (mes > 12) { mes = 1; ano++; }
  }
  return meses;
}

/* ====================== B) A BUSCA DOS ÍNDICES ============================ */

function buscarIndiceNoBancoCentral(chaveIndice, mesInicial, mesFinal) {
  var cfg = null;
  for (var i = 0; i < TABELAS.indices.lista.length; i++) {
    if (TABELAS.indices.lista[i].chave === chaveIndice) cfg = TABELAS.indices.lista[i];
  }
  if (!cfg) return Promise.reject(new Error('Índice desconhecido: ' + chaveIndice));

  var meses = listarMeses(mesInicial, mesFinal);
  if (meses.length === 0) return Promise.reject(new Error('Período inválido.'));

  var p = meses[0], u = meses[meses.length - 1];
  var inicio = '01/' + (p.mes < 10 ? '0' : '') + p.mes + '/' + p.ano;
  var ultimoDia = new Date(u.ano, u.mes, 0).getDate();
  var fim = ultimoDia + '/' + (u.mes < 10 ? '0' : '') + u.mes + '/' + u.ano;

  var url = TABELAS.indices.urlBase + cfg.serie + '/dados?formato=json' +
            '&dataInicial=' + inicio + '&dataFinal=' + fim;

  return fetch(url)
    .then(function (r) {
      if (!r.ok) throw new Error('O Banco Central respondeu ' + r.status + '.');
      return r.json();
    })
    .then(function (dados) {
      if (!Array.isArray(dados)) throw new Error('Resposta em formato inesperado.');
      var taxas = dados.map(function (d) {
        return { data: d.data, valor: Number(String(d.valor).replace(',', '.')) };
      }).filter(function (t) { return !isNaN(t.valor); });

      return { config: cfg, taxas: taxas, mesesPedidos: meses, url: url };
    })
    .catch(function (erro) {
      var msg = String(erro && erro.message || erro);
      if (/failed to fetch|networkerror|load failed/i.test(msg)) {
        throw new Error('NAO_ALCANCOU');
      }
      throw erro;
    });
}
