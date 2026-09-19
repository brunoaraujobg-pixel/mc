/* =============================================================================
   CALCULO-IR.JS — motor de cálculo do IRRF da pessoa física (folha mensal)
   -----------------------------------------------------------------------------
   NÃO contém nenhum valor de tabela. Todos os números vêm de tabelas.js.
   Toda função devolve também a MEMÓRIA DE CÁLCULO, para conferência manual.
============================================================================= */

/* Arredonda para 2 casas com "meio para cima", como manda a prática contábil.
   Em JavaScript, 1621 x 0,075 resulta em 121,57499999999999 (e não 121,575),
   porque 0,075 não tem representação binária exata. Sem tratar isso, o INSS
   dessa faixa sairia como R$ 121,57 em vez dos R$ 121,58 corretos.
   O toPrecision(12) descarta esse ruído antes de arredondar. */
function arred2(valor) {
  var n = Number(valor);
  if (!isFinite(n)) return n;
  var negativo = n < 0;
  n = Math.abs(n);
  if (n === 0) return 0;
  var limpo = Number(n.toPrecision(12));
  var r = Math.round(limpo * 100 + 1e-8) / 100;
  return negativo ? -r : r;
}

/* -----------------------------------------------------------------------------
   INSS — contribuição do segurado empregado (progressiva por faixas sucessivas)
   Entrada: salário bruto mensal
   Saída:   { valor, baseLimitada, atingiuTeto, aliquotaEfetiva, memoria[] }
----------------------------------------------------------------------------- */
function calcularINSS(salarioBruto) {
  var cfg = TABELAS.inss;
  var base = Math.min(salarioBruto, cfg.teto);
  var total = 0;
  var pisoAnterior = 0;
  var memoria = [];

  for (var i = 0; i < cfg.faixas.length; i++) {
    var faixa = cfg.faixas[i];
    if (base <= pisoAnterior) break;

    var topoDaFaixa = Math.min(base, faixa.ate);
    var parcela = topoDaFaixa - pisoAnterior;
    var valor = parcela * faixa.aliquota;
    total += valor;

    memoria.push({
      de: pisoAnterior,
      ate: topoDaFaixa,
      parcela: arred2(parcela),
      aliquota: faixa.aliquota,
      valor: arred2(valor)
    });

    pisoAnterior = faixa.ate;
  }

  total = arred2(total);

  return {
    valor: total,
    baseLimitada: arred2(base),
    atingiuTeto: salarioBruto > cfg.teto,
    teto: cfg.teto,
    aliquotaEfetiva: salarioBruto > 0 ? total / salarioBruto : 0,
    memoria: memoria
  };
}

/* -----------------------------------------------------------------------------
   Aplica a tabela progressiva mensal do IRRF sobre uma base de cálculo.
   Saída: { imposto, faixa: {ate, aliquota, deduzir} }
----------------------------------------------------------------------------- */
function aplicarTabelaIRRF(baseCalculo) {
  var faixas = TABELAS.irrf.faixas;
  for (var i = 0; i < faixas.length; i++) {
    if (baseCalculo <= faixas[i].ate) {
      var imposto = baseCalculo * faixas[i].aliquota - faixas[i].deduzir;
      return { imposto: arred2(Math.max(0, imposto)), faixa: faixas[i], indice: i };
    }
  }
  var ultima = faixas[faixas.length - 1];
  return {
    imposto: arred2(Math.max(0, baseCalculo * ultima.aliquota - ultima.deduzir)),
    faixa: ultima,
    indice: faixas.length - 1
  };
}

/* -----------------------------------------------------------------------------
   Redutor da Lei nº 15.270/2025 (vigente desde 01/01/2026).
   Entrada: rendimento tributável BRUTO do mês e o imposto já apurado na tabela.
   Saída:   { valor, regra, formula }
----------------------------------------------------------------------------- */
function calcularRedutor2026(rendimentoBruto, impostoApurado) {
  var r = TABELAS.irrf.redutor2026;

  if (rendimentoBruto <= r.limiteIsencaoTotal) {
    return {
      valor: impostoApurado, // zera o imposto
      regra: 'isencao_total',
      formula: 'Rendimento de até ' + formatarMoeda(r.limiteIsencaoTotal) +
               ': a redução zera o imposto apurado (redução de até ' +
               formatarMoeda(r.reducaoMaxima) + ').'
    };
  }

  if (rendimentoBruto <= r.limiteReducaoParcial) {
    var bruto = r.constante - (r.coeficiente * rendimentoBruto);
    var valor = Math.max(0, Math.min(arred2(bruto), impostoApurado));
    return {
      valor: valor,
      regra: 'reducao_parcial',
      formula: formatarMoeda(r.constante) + ' − (' +
               r.coeficiente.toLocaleString('pt-BR', { minimumFractionDigits: 6 }) +
               ' × ' + formatarMoeda(rendimentoBruto) + ') = ' + formatarMoeda(arred2(bruto))
    };
  }

  return {
    valor: 0,
    regra: 'sem_reducao',
    formula: 'Rendimento acima de ' + formatarMoeda(r.limiteReducaoParcial) +
             ': não há redução. Aplica-se somente a tabela progressiva.'
  };
}

/* -----------------------------------------------------------------------------
   CÁLCULO COMPLETO DO IRRF MENSAL
   Entrada (objeto):
     salarioBruto ....... obrigatório
     dependentes ........ nº de dependentes (padrão 0)
     inssInformado ...... valor do INSS já descontado, se o usuário souber
                          (null/undefined = a calculadora calcula pela tabela)
   Regra aplicada pela fonte pagadora:
     apura-se a base pelas DEDUÇÕES LEGAIS (INSS + dependentes) e pelo
     DESCONTO SIMPLIFICADO, e usa-se a que resultar em MENOR imposto.
----------------------------------------------------------------------------- */
function calcularIRRF(entrada) {
  var cfg = TABELAS.irrf;
  var salarioBruto = Number(entrada.salarioBruto) || 0;
  var dependentes = Math.max(0, parseInt(entrada.dependentes, 10) || 0);

  var inssCalculado = calcularINSS(salarioBruto);
  var inssInformadoValido =
    entrada.inssInformado !== null &&
    entrada.inssInformado !== undefined &&
    entrada.inssInformado !== '' &&
    !isNaN(Number(entrada.inssInformado));

  var inssValor = inssInformadoValido ? arred2(Number(entrada.inssInformado)) : inssCalculado.valor;
  var inssOrigem = inssInformadoValido ? 'informado' : 'calculado';

  // --- Caminho A: deduções legais -----------------------------------------
  var deducaoDependentes = arred2(dependentes * cfg.deducaoDependente);
  var baseLegais = arred2(Math.max(0, salarioBruto - inssValor - deducaoDependentes));
  var resultadoLegais = aplicarTabelaIRRF(baseLegais);

  // --- Caminho B: desconto simplificado ------------------------------------
  var baseSimplificado = arred2(Math.max(0, salarioBruto - cfg.descontoSimplificado));
  var resultadoSimplificado = aplicarTabelaIRRF(baseSimplificado);

  // --- Escolhe o mais vantajoso (menor imposto) ----------------------------
  var usouSimplificado = resultadoSimplificado.imposto < resultadoLegais.imposto;
  var escolhido = usouSimplificado ? resultadoSimplificado : resultadoLegais;
  var baseEscolhida = usouSimplificado ? baseSimplificado : baseLegais;

  // --- Redutor da Lei 15.270/2025 ------------------------------------------
  var redutor = calcularRedutor2026(salarioBruto, escolhido.imposto);
  var irrfFinal = arred2(Math.max(0, escolhido.imposto - redutor.valor));

  // --- Líquido --------------------------------------------------------------
  var liquido = arred2(salarioBruto - inssValor - irrfFinal);

  return {
    salarioBruto: arred2(salarioBruto),
    dependentes: dependentes,

    inss: {
      valor: inssValor,
      origem: inssOrigem,
      detalhe: inssCalculado
    },

    deducaoDependentes: deducaoDependentes,
    valorPorDependente: cfg.deducaoDependente,
    descontoSimplificado: cfg.descontoSimplificado,

    comparativo: {
      legais:       { base: baseLegais,       imposto: resultadoLegais.imposto,       faixa: resultadoLegais.faixa },
      simplificado: { base: baseSimplificado, imposto: resultadoSimplificado.imposto, faixa: resultadoSimplificado.faixa }
    },

    metodoEscolhido: usouSimplificado ? 'desconto simplificado' : 'deduções legais',
    baseCalculoIRRF: baseEscolhida,
    aliquotaAplicada: escolhido.faixa.aliquota,
    parcelaADeduzir: escolhido.faixa.deduzir,
    impostoPelaTabela: escolhido.imposto,

    redutor: redutor,
    irrf: irrfFinal,
    salarioLiquido: liquido,

    aliquotaEfetivaIRRF: salarioBruto > 0 ? irrfFinal / salarioBruto : 0,
    cargaTotal: arred2(inssValor + irrfFinal),
    aliquotaEfetivaTotal: salarioBruto > 0 ? (inssValor + irrfFinal) / salarioBruto : 0
  };
}
