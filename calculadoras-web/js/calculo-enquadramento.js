/* =============================================================================
   CALCULO-ENQUADRAMENTO.JS — simulador comparativo de regime tributário
   -----------------------------------------------------------------------------
   ATENÇÃO: ESTIMATIVA EDUCATIVA. Não substitui planejamento tributário.
   Não contém valores de tabela — tudo vem de tabelas.js.
   Toda função devolve a MEMÓRIA DE CÁLCULO para conferência manual.
============================================================================= */

/* -----------------------------------------------------------------------------
   Alíquota efetiva do Simples Nacional
   Fórmula legal: ((RBT12 x alíquota nominal) - parcela a deduzir) / RBT12
----------------------------------------------------------------------------- */
function calcularAliquotaEfetivaSimples(rbt12, anexoChave) {
  var anexo = TABELAS.simples.anexos[anexoChave];
  var faixaEscolhida = null;
  var numeroFaixa = 0;

  for (var i = 0; i < anexo.faixas.length; i++) {
    if (rbt12 <= anexo.faixas[i].ate) {
      faixaEscolhida = anexo.faixas[i];
      numeroFaixa = i + 1;
      break;
    }
  }
  if (!faixaEscolhida) {
    faixaEscolhida = anexo.faixas[anexo.faixas.length - 1];
    numeroFaixa = anexo.faixas.length;
  }

  var efetiva = (rbt12 * faixaEscolhida.aliquota - faixaEscolhida.deduzir) / rbt12;
  efetiva = Math.max(0, efetiva);

  return {
    anexoChave: anexoChave,
    anexoNome: anexo.nome,
    numeroFaixa: numeroFaixa,
    limiteFaixa: faixaEscolhida.ate,
    aliquotaNominal: faixaEscolhida.aliquota,
    parcelaADeduzir: faixaEscolhida.deduzir,
    aliquotaEfetiva: efetiva
  };
}

/* -----------------------------------------------------------------------------
   Define o anexo do Simples a partir da atividade e do Fator R
----------------------------------------------------------------------------- */
function definirAnexoSimples(entrada) {
  var fatorR = null;
  var atingiuFatorR = null;

  if (entrada.atividade === 'comercio')  return { anexo: 'I',  fatorR: null, atingiuFatorR: null };
  if (entrada.atividade === 'industria') return { anexo: 'II', fatorR: null, atingiuFatorR: null };

  // serviços
  if (entrada.tipoServico === 'anexoIV') {
    return { anexo: 'IV', fatorR: null, atingiuFatorR: null };
  }
  if (entrada.tipoServico === 'anexoIII') {
    return { anexo: 'III', fatorR: null, atingiuFatorR: null };
  }
  // sujeito ao Fator R
  fatorR = entrada.faturamentoAnual > 0 ? (entrada.folhaAnual / entrada.faturamentoAnual) : 0;
  atingiuFatorR = fatorR >= TABELAS.simples.fatorR;
  return { anexo: atingiuFatorR ? 'III' : 'V', fatorR: fatorR, atingiuFatorR: atingiuFatorR };
}

/* -----------------------------------------------------------------------------
   CPP (INSS patronal + RAT + terceiros) sobre a folha
----------------------------------------------------------------------------- */
function calcularCPP(folhaAnual) {
  return arred2(folhaAnual * TABELAS.cpp.total);
}

/* -----------------------------------------------------------------------------
   SIMPLES NACIONAL
----------------------------------------------------------------------------- */
function simularSimplesNacional(entrada) {
  var cfg = TABELAS.simples;
  var rbt12 = entrada.faturamentoAnual;

  if (rbt12 > cfg.limiteAnual) {
    return {
      regime: 'Simples Nacional',
      permitido: false,
      motivo: 'Faturamento acima do teto do Simples Nacional (' +
              formatarMoeda(cfg.limiteAnual) + ' por ano). A empresa não pode optar por este regime.',
      total: null
    };
  }

  var escolha = definirAnexoSimples(entrada);
  var calc = calcularAliquotaEfetivaSimples(rbt12, escolha.anexo);
  var das = arred2(rbt12 * calc.aliquotaEfetiva);

  var itens = [{ nome: 'DAS (guia única do Simples)', valor: das }];
  var avisos = [];

  // Anexo IV: a CPP NÃO está incluída no DAS
  var cppForaDoDas = 0;
  if (escolha.anexo === 'IV' && entrada.folhaAnual > 0) {
    cppForaDoDas = calcularCPP(entrada.folhaAnual);
    itens.push({ nome: 'CPP sobre a folha (fora do DAS — Anexo IV)', valor: cppForaDoDas });
    avisos.push('No Anexo IV a contribuição previdenciária patronal é recolhida FORA do DAS, em GPS/DARF próprio.');
  }

  // Acima do sublimite, ICMS/ISS saem do DAS e vão para a apuração estadual/municipal
  var icmsIssFora = 0;
  if (rbt12 > cfg.sublimiteIcmsIss) {
    if (entrada.atividade === 'servico' && entrada.issAliquota > 0) {
      icmsIssFora = arred2(rbt12 * entrada.issAliquota);
      itens.push({ nome: 'ISS fora do DAS (acima do sublimite)', valor: icmsIssFora });
    } else if (entrada.atividade !== 'servico' && entrada.icmsEfetivo > 0) {
      icmsIssFora = arred2(rbt12 * entrada.icmsEfetivo);
      itens.push({ nome: 'ICMS fora do DAS (acima do sublimite)', valor: icmsIssFora });
    }
    avisos.push('Faturamento acima do sublimite de ' + formatarMoeda(cfg.sublimiteIcmsIss) +
                ': o ICMS/ISS sai do DAS e passa a ser apurado pelas regras normais do estado/município.');
  } else {
    avisos.push('ICMS e ISS já estão dentro do DAS (faturamento abaixo do sublimite de ' +
                formatarMoeda(cfg.sublimiteIcmsIss) + ').');
  }

  var total = arred2(das + cppForaDoDas + icmsIssFora);

  return {
    regime: 'Simples Nacional',
    permitido: true,
    anexo: calc.anexoNome,
    anexoChave: calc.anexoChave,
    numeroFaixa: calc.numeroFaixa,
    aliquotaNominal: calc.aliquotaNominal,
    parcelaADeduzir: calc.parcelaADeduzir,
    aliquotaEfetivaDAS: calc.aliquotaEfetiva,
    fatorR: escolha.fatorR,
    atingiuFatorR: escolha.atingiuFatorR,
    itens: itens,
    avisos: avisos,
    total: total,
    cargaSobreFaturamento: rbt12 > 0 ? total / rbt12 : 0,
    memoria: [
      'RBT12 (receita bruta dos últimos 12 meses) = ' + formatarMoeda(rbt12),
      calc.anexoNome + ' — ' + calc.numeroFaixa + 'ª faixa',
      'Alíquota efetiva = ((' + formatarMoeda(rbt12) + ' × ' + formatarPercentual(calc.aliquotaNominal) +
        ') − ' + formatarMoeda(calc.parcelaADeduzir) + ') ÷ ' + formatarMoeda(rbt12) +
        ' = ' + formatarPercentual(calc.aliquotaEfetiva),
      'DAS anual = ' + formatarMoeda(rbt12) + ' × ' + formatarPercentual(calc.aliquotaEfetiva) +
        ' = ' + formatarMoeda(das)
    ]
  };
}

/* -----------------------------------------------------------------------------
   LUCRO PRESUMIDO (apuração trimestral, faturamento distribuído uniformemente)
----------------------------------------------------------------------------- */
function simularLucroPresumido(entrada) {
  var cfg = TABELAS.lucroPresumido;
  var receitaAnual = entrada.faturamentoAnual;
  var receitaTrim = receitaAnual / 4;

  var chaveAtividade = (entrada.atividade === 'servico') ? 'servico' : entrada.atividade;
  var pres = cfg.presuncao[chaveAtividade];

  var maj = cfg.majoracaoLC224;
  var usarMajoracao = maj.ativa && receitaTrim > maj.limiteTrimestral;
  var receitaAteLimite = Math.min(receitaTrim, maj.limiteTrimestral);
  var receitaExcedente = Math.max(0, receitaTrim - maj.limiteTrimestral);

  function baseTrimestral(percentual) {
    if (!usarMajoracao) return receitaTrim * percentual;
    return receitaAteLimite * percentual + receitaExcedente * percentual * maj.fator;
  }

  var baseIrpjTrim = baseTrimestral(pres.irpj);
  var baseCsllTrim = baseTrimestral(pres.csll);

  var irpjTrim = baseIrpjTrim * cfg.irpjAliquota +
                 Math.max(0, baseIrpjTrim - cfg.irpjAdicionalLimiteTrimestral) * cfg.irpjAdicionalAliquota;
  var csllTrim = baseCsllTrim * cfg.csllAliquota;

  var irpjAno = arred2(irpjTrim * 4);
  var csllAno = arred2(csllTrim * 4);
  var pisAno = arred2(receitaAnual * cfg.pisCumulativo);
  var cofinsAno = arred2(receitaAnual * cfg.cofinsCumulativo);
  var cppAno = entrada.folhaAnual > 0 ? calcularCPP(entrada.folhaAnual) : 0;

  var issAno = 0, icmsAno = 0;
  if (entrada.atividade === 'servico' && entrada.issAliquota > 0) {
    issAno = arred2(receitaAnual * entrada.issAliquota);
  }
  if (entrada.atividade !== 'servico' && entrada.icmsEfetivo > 0) {
    icmsAno = arred2(receitaAnual * entrada.icmsEfetivo);
  }

  var itens = [
    { nome: 'IRPJ (15% + adicional de 10%)', valor: irpjAno },
    { nome: 'CSLL (9%)', valor: csllAno },
    { nome: 'PIS cumulativo (0,65%)', valor: pisAno },
    { nome: 'COFINS cumulativa (3%)', valor: cofinsAno }
  ];
  if (cppAno > 0)  itens.push({ nome: 'CPP sobre a folha (' + formatarPercentual(TABELAS.cpp.total) + ')', valor: cppAno });
  if (issAno > 0)  itens.push({ nome: 'ISS', valor: issAno });
  if (icmsAno > 0) itens.push({ nome: 'ICMS (percentual informado)', valor: icmsAno });

  var total = arred2(irpjAno + csllAno + pisAno + cofinsAno + cppAno + issAno + icmsAno);

  var avisos = [];
  if (usarMajoracao) {
    avisos.push('Aplicada a majoração de 10% nos percentuais de presunção sobre a receita que excede ' +
                formatarMoeda(maj.limiteTrimestral) + ' por trimestre (LC nº 224/2025). ' + maj.observacao);
  }
  if (entrada.atividade !== 'servico' && icmsAno === 0) {
    avisos.push('ICMS NÃO foi incluído (percentual informado igual a zero). Como o Simples já inclui o ICMS no DAS, o comparativo fica incompleto — informe um ICMS efetivo estimado para uma comparação justa.');
  }

  var memoria = [
    'Receita trimestral = ' + formatarMoeda(receitaAnual) + ' ÷ 4 = ' + formatarMoeda(receitaTrim),
    'Base do IRPJ (presunção de ' + formatarPercentual(pres.irpj) + ') = ' + formatarMoeda(arred2(baseIrpjTrim)) + ' por trimestre',
    'Base da CSLL (presunção de ' + formatarPercentual(pres.csll) + ') = ' + formatarMoeda(arred2(baseCsllTrim)) + ' por trimestre',
    'IRPJ do trimestre = 15% × base + 10% sobre o que exceder ' + formatarMoeda(cfg.irpjAdicionalLimiteTrimestral) +
      ' = ' + formatarMoeda(arred2(irpjTrim)),
    'CSLL do trimestre = 9% × base = ' + formatarMoeda(arred2(csllTrim)),
    'PIS/COFINS no regime cumulativo = 3,65% sobre o faturamento = ' + formatarMoeda(arred2(pisAno + cofinsAno))
  ];

  return {
    regime: 'Lucro Presumido',
    permitido: true,
    itens: itens,
    avisos: avisos,
    memoria: memoria,
    total: total,
    cargaSobreFaturamento: receitaAnual > 0 ? total / receitaAnual : 0
  };
}

/* -----------------------------------------------------------------------------
   LUCRO REAL (estimativa simplificada, anual)
   Depende fortemente da margem real e dos créditos de PIS/COFINS.
----------------------------------------------------------------------------- */
function simularLucroReal(entrada) {
  var cfg = TABELAS.lucroReal;
  var receitaAnual = entrada.faturamentoAnual;

  var lucroAntes = arred2(receitaAnual * entrada.margemLucro);
  var limiteAdicionalAno = cfg.irpjAdicionalLimiteMensal * 12;

  var irpjAno = arred2(
    lucroAntes * cfg.irpjAliquota +
    Math.max(0, lucroAntes - limiteAdicionalAno) * cfg.irpjAdicionalAliquota
  );
  var csllAno = arred2(lucroAntes * cfg.csllAliquota);

  var baseCreditos = arred2(receitaAnual * entrada.creditosPisCofins);
  var basePisCofins = Math.max(0, receitaAnual - baseCreditos);
  var pisAno = arred2(basePisCofins * cfg.pisNaoCumulativo);
  var cofinsAno = arred2(basePisCofins * cfg.cofinsNaoCumulativa);

  var cppAno = entrada.folhaAnual > 0 ? calcularCPP(entrada.folhaAnual) : 0;

  var issAno = 0, icmsAno = 0;
  if (entrada.atividade === 'servico' && entrada.issAliquota > 0) {
    issAno = arred2(receitaAnual * entrada.issAliquota);
  }
  if (entrada.atividade !== 'servico' && entrada.icmsEfetivo > 0) {
    icmsAno = arred2(receitaAnual * entrada.icmsEfetivo);
  }

  var itens = [
    { nome: 'IRPJ (15% + adicional de 10%) sobre o lucro', valor: irpjAno },
    { nome: 'CSLL (9%) sobre o lucro', valor: csllAno },
    { nome: 'PIS não cumulativo (1,65%)', valor: pisAno },
    { nome: 'COFINS não cumulativa (7,6%)', valor: cofinsAno }
  ];
  if (cppAno > 0)  itens.push({ nome: 'CPP sobre a folha (' + formatarPercentual(TABELAS.cpp.total) + ')', valor: cppAno });
  if (issAno > 0)  itens.push({ nome: 'ISS', valor: issAno });
  if (icmsAno > 0) itens.push({ nome: 'ICMS (percentual informado)', valor: icmsAno });

  var total = arred2(irpjAno + csllAno + pisAno + cofinsAno + cppAno + issAno + icmsAno);

  var avisos = [
    'O Lucro Real é o regime mais sensível aos números reais da empresa. O resultado acima muda completamente conforme a margem de lucro efetiva e o volume de créditos de PIS/COFINS. Se a empresa tiver prejuízo, não há IRPJ nem CSLL a pagar.',
    'Se a margem informada estiver errada, o resultado do Lucro Real estará errado. Esta é a maior limitação desta simulação.'
  ];
  if (entrada.atividade !== 'servico' && icmsAno === 0) {
    avisos.push('ICMS não incluído (percentual informado igual a zero) — o comparativo com o Simples fica incompleto.');
  }

  var memoria = [
    'Lucro antes do IRPJ/CSLL estimado = ' + formatarMoeda(receitaAnual) + ' × ' +
      formatarPercentual(entrada.margemLucro) + ' = ' + formatarMoeda(lucroAntes),
    'IRPJ = 15% × ' + formatarMoeda(lucroAntes) + ' + 10% sobre o que exceder ' +
      formatarMoeda(limiteAdicionalAno) + ' no ano = ' + formatarMoeda(irpjAno),
    'CSLL = 9% × ' + formatarMoeda(lucroAntes) + ' = ' + formatarMoeda(csllAno),
    'Créditos estimados de PIS/COFINS = ' + formatarMoeda(receitaAnual) + ' × ' +
      formatarPercentual(entrada.creditosPisCofins) + ' = ' + formatarMoeda(baseCreditos),
    'PIS/COFINS = 9,25% × (' + formatarMoeda(receitaAnual) + ' − ' + formatarMoeda(baseCreditos) +
      ') = ' + formatarMoeda(arred2(pisAno + cofinsAno))
  ];

  return {
    regime: 'Lucro Real',
    permitido: true,
    itens: itens,
    avisos: avisos,
    memoria: memoria,
    total: total,
    cargaSobreFaturamento: receitaAnual > 0 ? total / receitaAnual : 0
  };
}

/* -----------------------------------------------------------------------------
   COMPARATIVO COMPLETO
----------------------------------------------------------------------------- */
function simularEnquadramento(entrada) {
  var resultados = [
    simularSimplesNacional(entrada),
    simularLucroPresumido(entrada),
    simularLucroReal(entrada)
  ];

  var elegiveis = resultados.filter(function (r) { return r.permitido && r.total !== null; });
  var menor = null;
  if (elegiveis.length > 0) {
    menor = elegiveis.reduce(function (a, b) { return a.total <= b.total ? a : b; });
  }

  return {
    entrada: entrada,
    resultados: resultados,
    menorCarga: menor ? menor.regime : null
  };
}
