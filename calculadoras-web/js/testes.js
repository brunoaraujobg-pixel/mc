/* =============================================================================
   TESTES.JS — conferência dos cálculos contra valores apurados manualmente
   -----------------------------------------------------------------------------
   Cada teste traz o valor ESPERADO, calculado na mão a partir das tabelas
   oficiais. Se a tabela mudar em tabelas.js, os esperados abaixo precisam ser
   recalculados — é justamente isso que o teste protege.

   Como rodar:
     - No navegador: abra testes.html (dois cliques).
     - No terminal:  node rodar-testes.js
============================================================================= */

function rodarTestes() {
  var testes = [];

  function conferir(nome, obtido, esperado) {
    var ok = Math.abs(Number(obtido) - Number(esperado)) < 0.005;
    testes.push({ nome: nome, esperado: esperado, obtido: Number(obtido), ok: ok });
  }
  function conferirTexto(nome, obtido, esperado) {
    testes.push({ nome: nome, esperado: esperado, obtido: obtido, ok: obtido === esperado, texto: true });
  }

  /* ======================= INSS ======================= */
  // 1.621,00 x 7,5% = 121,575
  conferir('INSS — salário 1.621,00 (só 1ª faixa)', calcularINSS(1621.00).valor, 121.58);

  // 121,575 + (2.500 - 1.621) x 9% = 121,575 + 79,11 = 200,685
  conferir('INSS — salário 2.500,00', calcularINSS(2500).valor, 200.69);

  // 121,575 + 115,3656 + 11,6592 = 248,5998
  conferir('INSS — salário 3.000,00', calcularINSS(3000).valor, 248.60);

  // desconto máximo no teto: 121,575 + 115,3656 + 174,1716 + 576,9792 = 988,0914
  conferir('INSS — salário 20.000,00 (teto R$ 8.475,55)', calcularINSS(20000).valor, 988.09);
  conferir('INSS — salário exatamente no teto', calcularINSS(8475.55).valor, 988.09);

  /* ======================= IRRF ======================= */

  // Salário 3.000: base simplificada 2.392,80 -> isento
  var t1 = calcularIRRF({ salarioBruto: 3000, dependentes: 0, inssInformado: null });
  conferir('IRRF — salário 3.000,00: imposto', t1.irrf, 0);
  conferir('IRRF — salário 3.000,00: líquido (3.000 - 248,60)', t1.salarioLiquido, 2751.40);

  // Salário 3.036 (2 salários mínimos): base simplificada = 2.428,80 = limite da isenção
  var t2 = calcularIRRF({ salarioBruto: 3036, dependentes: 0, inssInformado: null });
  conferir('IRRF — salário 3.036,00 (2 mínimos): isento', t2.irrf, 0);
  conferir('IRRF — salário 3.036,00: base pelo desconto simplificado', t2.comparativo.simplificado.base, 2428.80);

  // Salário 5.000: imposto pela tabela 312,89, redutor zera
  var t3 = calcularIRRF({ salarioBruto: 5000, dependentes: 0, inssInformado: null });
  conferir('IRRF — salário 5.000,00: INSS', t3.inss.valor, 501.51);
  conferir('IRRF — salário 5.000,00: imposto pela tabela', t3.impostoPelaTabela, 312.89);
  conferir('IRRF — salário 5.000,00: redutor da Lei 15.270/2025', t3.redutor.valor, 312.89);
  conferir('IRRF — salário 5.000,00: imposto final (deve ser zero)', t3.irrf, 0);
  conferir('IRRF — salário 5.000,00: líquido', t3.salarioLiquido, 4498.49);

  // EXEMPLO DIVULGADO PELA RECEITA FEDERAL:
  // rendimento 6.000,00 com desconto simplificado de 607,20 -> base 5.392,80
  // imposto pela tabela = 574,29 | redutor = 978,62 - (0,133145 x 6.000) = 179,75
  var t4 = calcularIRRF({ salarioBruto: 6000, dependentes: 0, inssInformado: 0 });
  conferir('IRRF — exemplo RFB: base pelo desconto simplificado', t4.baseCalculoIRRF, 5392.80);
  conferir('IRRF — exemplo RFB: imposto pela tabela', t4.impostoPelaTabela, 574.29);
  conferir('IRRF — exemplo RFB: redutor', t4.redutor.valor, 179.75);
  conferir('IRRF — exemplo RFB: imposto final', t4.irrf, 394.54);

  // Salário 6.000 de empregado CLT (INSS calculado = 641,51)
  // base por deduções legais 5.358,49 -> imposto 564,85 | redutor 179,75 -> IRRF 385,10
  var t5 = calcularIRRF({ salarioBruto: 6000, dependentes: 0, inssInformado: null });
  conferir('IRRF — CLT 6.000,00: INSS', t5.inss.valor, 641.51);
  conferirTexto('IRRF — CLT 6.000,00: método escolhido', t5.metodoEscolhido, 'deduções legais');
  conferir('IRRF — CLT 6.000,00: imposto pela tabela', t5.impostoPelaTabela, 564.85);
  conferir('IRRF — CLT 6.000,00: imposto final', t5.irrf, 385.10);
  conferir('IRRF — CLT 6.000,00: líquido', t5.salarioLiquido, 4973.39);

  // Salário 7.350 (limite superior do redutor): redutor praticamente zero
  var t6 = calcularIRRF({ salarioBruto: 7350, dependentes: 0, inssInformado: null });
  conferir('IRRF — salário 7.350,00 (fim do redutor): redutor', t6.redutor.valor, 0.00);
  conferir('IRRF — salário 7.350,00: INSS', t6.inss.valor, 830.51);
  conferir('IRRF — salário 7.350,00: imposto final', t6.irrf, 884.13);

  // Salário 10.000 com 2 dependentes
  // INSS no teto 988,09 | dependentes 2 x 189,59 = 379,18 | base 8.632,73
  var t7 = calcularIRRF({ salarioBruto: 10000, dependentes: 2, inssInformado: null });
  conferir('IRRF — 10.000,00 com 2 dependentes: dedução de dependentes', t7.deducaoDependentes, 379.18);
  conferir('IRRF — 10.000,00 com 2 dependentes: base de cálculo', t7.baseCalculoIRRF, 8632.73);
  conferir('IRRF — 10.000,00 com 2 dependentes: redutor (acima de 7.350)', t7.redutor.valor, 0);
  conferir('IRRF — 10.000,00 com 2 dependentes: imposto', t7.irrf, 1465.27);
  conferir('IRRF — 10.000,00 com 2 dependentes: líquido', t7.salarioLiquido, 7546.64);

  // INSS informado pelo usuário deve prevalecer sobre o calculado
  var t8 = calcularIRRF({ salarioBruto: 6000, dependentes: 0, inssInformado: 700 });
  conferir('IRRF — INSS informado (700,00) é usado no lugar do calculado', t8.inss.valor, 700);

  /* ================= SIMPLES NACIONAL ================= */

  // Comércio, RBT12 600.000 -> Anexo I, 3ª faixa: (600.000 x 9,5% - 13.860) / 600.000 = 7,19%
  var s1 = calcularAliquotaEfetivaSimples(600000, 'I');
  conferir('Simples — Anexo I, RBT12 600.000: alíquota efetiva', s1.aliquotaEfetiva, 0.0719);

  var e1 = simularSimplesNacional({
    faturamentoAnual: 600000, atividade: 'comercio', tipoServico: 'fatorR',
    folhaAnual: 0, issAliquota: 0, icmsEfetivo: 0
  });
  conferir('Simples — Anexo I, 600.000: DAS anual', e1.total, 43140.00);

  // Serviço com Fator R alto (100.000 / 300.000 = 33,33%) -> Anexo III, 2ª faixa
  var e2 = simularSimplesNacional({
    faturamentoAnual: 300000, atividade: 'servico', tipoServico: 'fatorR',
    folhaAnual: 100000, issAliquota: 0.05, icmsEfetivo: 0
  });
  conferirTexto('Simples — Fator R 33,3% cai no Anexo III', e2.anexoChave, 'III');
  conferir('Simples — Anexo III, 300.000: DAS anual', e2.total, 24240.00);

  // Mesma empresa com folha menor (50.000 / 300.000 = 16,67%) -> Anexo V
  var e3 = simularSimplesNacional({
    faturamentoAnual: 300000, atividade: 'servico', tipoServico: 'fatorR',
    folhaAnual: 50000, issAliquota: 0.05, icmsEfetivo: 0
  });
  conferirTexto('Simples — Fator R 16,7% cai no Anexo V', e3.anexoChave, 'V');
  conferir('Simples — Anexo V, 300.000: DAS anual', e3.total, 49500.00);

  // Acima do teto do Simples
  var e4 = simularSimplesNacional({
    faturamentoAnual: 5000000, atividade: 'comercio', tipoServico: 'fatorR',
    folhaAnual: 0, issAliquota: 0, icmsEfetivo: 0
  });
  conferirTexto('Simples — 5.000.000 de faturamento: não permitido', String(e4.permitido), 'false');

  /* ================= LUCRO PRESUMIDO ================= */

  // Comércio, 600.000/ano -> trimestre 150.000
  // IRPJ: base 12.000 x 15% = 1.800/tri -> 7.200/ano (sem adicional)
  // CSLL: base 18.000 x 9%  = 1.620/tri -> 6.480/ano
  // PIS 0,65% = 3.900 | COFINS 3% = 18.000 | total 35.580
  var lp1 = simularLucroPresumido({
    faturamentoAnual: 600000, atividade: 'comercio', folhaAnual: 0,
    issAliquota: 0, icmsEfetivo: 0
  });
  conferir('Lucro Presumido — comércio 600.000: total anual', lp1.total, 35580.00);

  // Serviço, 600.000/ano -> presunção 32% -> base 48.000/tri (sem adicional)
  // IRPJ 7.200/tri -> 28.800/ano | CSLL 4.320/tri -> 17.280/ano | PIS+COFINS 21.900
  var lp2 = simularLucroPresumido({
    faturamentoAnual: 600000, atividade: 'servico', folhaAnual: 0,
    issAliquota: 0, icmsEfetivo: 0
  });
  conferir('Lucro Presumido — serviço 600.000: total anual', lp2.total, 67980.00);

  // Majoração da LC 224/2025: serviço, 8.000.000/ano -> 2.000.000/tri
  // base IRPJ = 1.250.000 x 32% + 750.000 x 35,2% = 400.000 + 264.000 = 664.000
  // IRPJ/tri = 15% x 664.000 + 10% x (664.000 - 60.000) = 99.600 + 60.400 = 160.000
  var lp3 = simularLucroPresumido({
    faturamentoAnual: 8000000, atividade: 'servico', folhaAnual: 0,
    issAliquota: 0, icmsEfetivo: 0
  });
  conferir('Lucro Presumido — LC 224/2025: IRPJ anual com majoração', lp3.itens[0].valor, 640000.00);

  /* =================== LUCRO REAL =================== */

  // 600.000 de faturamento, margem 10% -> lucro 60.000
  // IRPJ 9.000 | CSLL 5.400 | créditos 60% -> base PIS/COFINS 240.000
  // PIS 3.960 | COFINS 18.240 | total 36.600
  var lr1 = simularLucroReal({
    faturamentoAnual: 600000, atividade: 'comercio', folhaAnual: 0,
    issAliquota: 0, icmsEfetivo: 0, margemLucro: 0.10, creditosPisCofins: 0.60
  });
  conferir('Lucro Real — 600.000, margem 10%, créditos 60%: total anual', lr1.total, 36600.00);

  /* ======================= CPP ======================= */
  // 120.000 x 27,8% (20% patronal + 2% RAT + 5,8% terceiros) = 33.360
  conferir('CPP — folha de 120.000 a 27,8%', calcularCPP(120000), 33360.00);

  /* ============== ARREDONDAMENTO (meio para cima) ============== */
  conferir('Arredondamento — 121,575 deve virar 121,58', arred2(121.575), 121.58);
  conferir('Arredondamento — 1,005 deve virar 1,01', arred2(1.005), 1.01);
  conferir('Arredondamento — 2,675 deve virar 2,68', arred2(2.675), 2.68);

  return testes;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { rodarTestes: rodarTestes };
}
