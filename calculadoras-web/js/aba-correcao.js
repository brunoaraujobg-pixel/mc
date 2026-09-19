/* =============================================================================
   ABA-CORRECAO.JS — a tela da aba 3 (Atualização Monetária)
   -----------------------------------------------------------------------------
   Só cuida da tela: lê o formulário, chama a busca dos índices e monta o
   resultado. A matemática fica em calculo-correcao.js e os índices em tabelas.js.
============================================================================= */

function mesAnterior() {
  var d = new Date();
  d.setDate(1);
  d.setMonth(d.getMonth() - 1);
  var m = d.getMonth() + 1;
  return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m;
}

function indicePorChave(chave) {
  var l = TABELAS.indices.lista;
  for (var i = 0; i < l.length; i++) if (l[i].chave === chave) return l[i];
  return l[0];
}

function atualizarAjudaDoIndice() {
  var cfg = indicePorChave(document.getElementById('cor-indice').value);
  document.getElementById('cor-indice-uso').textContent = cfg.orgao + ' — ' + cfg.uso;
  document.getElementById('bloco-selic1').style.display = cfg.acrescentaUmPorCento ? '' : 'none';

  /* Alguns índices entraram com o código de série ainda não conferido na fonte.
     Em vez de esconder isso, a página avisa quem vai usar. */
  var alerta = document.getElementById('cor-aviso-serie');
  if (cfg.codigoAConferir) {
    alerta.innerHTML = '<strong>Índice ainda não conferido.</strong> O código da série do ' +
      cfg.nome + ' no Banco Central ainda não foi validado na fonte. ' +
      'Use como referência, mas <strong>não use em cálculo de processo</strong> sem conferir.';
    alerta.style.display = '';
  } else {
    alerta.style.display = 'none';
  }
}

function erroCorrecao(saida, mensagem) {
  saida.innerHTML = '<div class="aviso aviso-erro">' + mensagem + '</div>';
  saida.classList.add('visivel');
}

function fatorFormatado(f) {
  return Number(f).toLocaleString('pt-BR', { minimumFractionDigits: 8, maximumFractionDigits: 8 });
}

function renderizarResultadoCorrecao(r, cfg, origem, aviso) {
  var html = '';
  if (aviso) html += '<div class="aviso aviso-forte">' + aviso + '</div>';

  /* ---------------- cartões ---------------- */
  html += '<div class="resultado-destaques">';
  html += cartaoDestaque('Valor original', formatarMoeda(r.valorOriginal), '');
  html += cartaoDestaque('Correção monetária', '+ ' + formatarMoeda(r.correcao),
            formatarPercentual(r.percentualCorrecao) + ' em ' + r.meses + (r.meses === 1 ? ' mês' : ' meses'));
  if (r.juros > 0 || r.multa > 0) {
    html += cartaoDestaque('Juros e multa', '+ ' + formatarMoeda(arred2(r.juros + r.multa)),
              (r.juros > 0 ? 'juros ' + formatarMoeda(r.juros) : '') +
              (r.juros > 0 && r.multa > 0 ? ' · ' : '') +
              (r.multa > 0 ? 'multa ' + formatarMoeda(r.multa) : ''));
  }
  html += cartaoDestaque('Valor atualizado', formatarMoeda(r.total),
            formatarPercentual(r.variacaoTotal) + ' sobre o original', true);
  html += '</div>';

  html += '<h3 class="titulo-secao">Memória de cálculo</h3>';

  /* ---------------- passo 1: fator ---------------- */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">1</span> Fator de correção acumulado</div>';
  if (r.metodo === 'soma') {
    html += '<p class="formula">Soma das taxas do período' +
            (r.acrescimoUmPorCento ? ' + 1% do mês do pagamento' : '') +
            ' = <strong>' + formatarPercentual(r.fatorAcumulado - 1) + '</strong></p>';
    if (cfg.observacao) html += '<p class="obs">' + cfg.observacao + '</p>';
  } else {
    html += '<p class="formula">(1 + i₁) × (1 + i₂) × … × (1 + i<sub>n</sub>) = <strong>' +
            fatorFormatado(r.fatorAcumulado) + '</strong></p>';
    html += '<p class="obs">Cada índice mensal incide sobre o valor já corrigido pelos meses anteriores.</p>';
  }
  html += '<p class="obs">Valor corrigido = ' + formatarMoeda(r.valorOriginal) + ' × ' +
          fatorFormatado(r.fatorAcumulado) + ' = <strong>' + formatarMoeda(r.valorCorrigido) + '</strong></p>';
  html += '</div>';

  /* ---------------- passo 2: juros e multa ---------------- */
  var temEncargos = (r.juros > 0 || r.multa > 0);
  if (temEncargos) {
    html += '<div class="passo">';
    html += '<div class="passo-titulo"><span class="passo-num">2</span> Juros de mora e multa</div>';
    if (r.juros > 0) {
      html += '<p class="formula">' + (r.jurosCompostos
        ? formatarMoeda(r.valorCorrigido) + ' × ((1 + ' +
          (r.jurosMensal / 100).toLocaleString('pt-BR', { maximumFractionDigits: 6 }) + ')<sup>' + r.meses + '</sup> − 1)'
        : formatarMoeda(r.valorCorrigido) + ' × ' + formatarPercentual(r.jurosMensal / 100) + ' × ' + r.meses + ' meses') +
        ' = <strong>' + formatarMoeda(r.juros) + '</strong></p>';
      html += '<p class="obs">Juros ' + (r.jurosCompostos ? 'compostos' : 'simples') + ' de ' +
              formatarPercentual(r.jurosMensal / 100) + ' ao mês, sobre o valor já corrigido.</p>';
    }
    if (r.multa > 0) {
      html += '<p class="formula">' + formatarMoeda(r.valorCorrigido) + ' × ' +
              formatarPercentual(r.multaPercentual / 100) + ' = <strong>' + formatarMoeda(r.multa) + '</strong></p>';
    }
    html += '</div>';
  }

  /* ---------------- resultado ---------------- */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">' + (temEncargos ? '3' : '2') + '</span> Resultado</div>';
  html += '<table class="tabela"><tbody>';
  html += '<tr><td>Valor original</td><td>' + formatarMoeda(r.valorOriginal) + '</td></tr>';
  html += '<tr><td>(+) Correção monetária</td><td>' + formatarMoeda(r.correcao) + '</td></tr>';
  if (r.juros > 0) html += '<tr><td>(+) Juros de mora</td><td>' + formatarMoeda(r.juros) + '</td></tr>';
  if (r.multa > 0) html += '<tr><td>(+) Multa</td><td>' + formatarMoeda(r.multa) + '</td></tr>';
  html += '<tr class="linha-total"><td>Valor atualizado</td><td>' + formatarMoeda(r.total) + '</td></tr>';
  html += '</tbody></table>';
  html += '</div>';

  /* ---------------- índices mês a mês ---------------- */
  if (origem === 'bcb' && r.taxas.length > 0) {
    html += '<div class="passo">';
    html += '<div class="passo-titulo">Índices usados, mês a mês</div>';
    html += '<p class="obs" style="margin-top:0">' + r.taxas.length +
            ' meses consultados no Banco Central. Confira qualquer linha na fonte oficial.</p>';
    html += '<div style="overflow-x:auto"><table class="tabela"><thead><tr><th>Mês</th><th>' +
            cfg.nome + '</th></tr></thead><tbody>';
    for (var i = 0; i < r.taxas.length; i++) {
      var d = String(r.taxas[i].data).split('/');
      html += '<tr><td>' + (d.length === 3 ? d[1] + '/' + d[2] : r.taxas[i].data) + '</td><td>' +
              r.taxas[i].valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 }) +
              '%</td></tr>';
    }
    html += '</tbody></table></div>';
    html += '<p class="obs">Fonte: ' + cfg.orgao + ' — série ' + cfg.serie +
            ' do Sistema Gerenciador de Séries Temporais do Banco Central, consultada agora.</p>';
    html += '</div>';
  }

  html += '<div class="aviso aviso-neutro">' +
          '<strong>Atenção:</strong> é um cálculo de referência. O índice, os juros e a multa corretos dependem ' +
          'do contrato, da lei aplicável ou da decisão judicial do seu caso. Em processo, vale o cálculo ' +
          'oficial pela tabela do tribunal.' +
          '</div>';

  html += blocoContato('Olá! Usei a calculadora de atualização monetária no site da M Contabilidade e gostaria de ajuda.');
  return html;
}

function iniciarFormularioCorrecao() {
  var form = document.getElementById('form-cor');
  var saida = document.getElementById('resultado-cor');
  if (!form) return;

  /* a lista de índices vem do tabelas.js — a tela não conhece nenhum índice */
  var sel = document.getElementById('cor-indice');
  TABELAS.indices.lista.forEach(function (ind) {
    var o = document.createElement('option');
    o.value = ind.chave;
    o.textContent = ind.nome;
    sel.appendChild(o);
  });
  sel.addEventListener('change', atualizarAjudaDoIndice);
  atualizarAjudaDoIndice();

  function preencherPeriodoPadrao() {
    var fim = mesAnterior();
    document.getElementById('cor-fim').value = fim;
    document.getElementById('cor-inicio').value = (Number(fim.slice(0, 4)) - 1) + fim.slice(4);
  }
  preencherPeriodoPadrao();

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();

    var valor = parseNumeroBR(document.getElementById('cor-valor').value);
    var inicio = document.getElementById('cor-inicio').value;
    var fimSel = document.getElementById('cor-fim').value;

    if (valor === null || valor <= 0) return erroCorrecao(saida, 'Informe um valor original maior que zero.');
    if (!inicio || !fimSel) return erroCorrecao(saida, 'Informe o mês inicial e o mês final.');
    if (listarMeses(inicio, fimSel).length === 0) {
      return erroCorrecao(saida, 'O mês final não pode ser anterior ao mês inicial.');
    }

    var cfg = indicePorChave(sel.value);
    var entrada = {
      valorOriginal: valor,
      metodo: cfg.metodo,
      acrescentar1: !!cfg.acrescentaUmPorCento && document.getElementById('cor-selic1').checked,
      jurosMensal: parseNumeroBR(document.getElementById('cor-juros').value) || 0,
      jurosCompostos: document.querySelector('input[name="cor-tipo-juros"]:checked').value === 'compostos',
      multaPercentual: parseNumeroBR(document.getElementById('cor-multa').value) || 0
    };

    /* Modo manual: se o campo do acumulado está visível e preenchido, nem vai à internet. */
    var blocoManual = document.getElementById('bloco-manual');
    var acumulado = parseNumeroBR(document.getElementById('cor-acumulado').value);
    if (blocoManual.style.display !== 'none' && acumulado !== null) {
      entrada.taxas = [{ data: '—', valor: acumulado }];
      entrada.metodo = 'soma';
      entrada.acrescentar1 = false;
      var rm = calcularAtualizacao(entrada);
      rm.meses = listarMeses(inicio, fimSel).length;
      saida.innerHTML = renderizarResultadoCorrecao(rm, cfg, 'manual',
        'Cálculo feito com o percentual acumulado de <strong>' + formatarPercentual(acumulado / 100) +
        '</strong> que você informou — não com os índices buscados no Banco Central.');
      saida.classList.add('visivel');
      saida.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }

    saida.innerHTML = '<div class="aviso aviso-neutro">Buscando os índices no Banco Central…</div>';
    saida.classList.add('visivel');

    buscarIndiceNoBancoCentral(cfg.chave, inicio, fimSel)
      .then(function (res) {
        if (res.taxas.length === 0) {
          throw new Error('O Banco Central não devolveu nenhum índice para esse período. ' +
            'Os índices saem com cerca de um mês de atraso — tente um mês final anterior.');
        }
        entrada.taxas = res.taxas;
        var r = calcularAtualizacao(entrada);

        var avisoFalta = null;
        if (res.taxas.length < res.mesesPedidos.length) {
          avisoFalta = 'Você pediu ' + res.mesesPedidos.length + ' meses, mas o Banco Central só tem ' +
            res.taxas.length + ' divulgados. O cálculo usou os que existem — os índices saem com ' +
            'cerca de um mês de atraso.';
        }
        saida.innerHTML = renderizarResultadoCorrecao(r, cfg, 'bcb', avisoFalta);
        saida.scrollIntoView({ behavior: 'smooth', block: 'start' });
      })
      .catch(function (erro) {
        var semRede = String(erro && erro.message) === 'NAO_ALCANCOU';
        if (semRede) blocoManual.style.display = '';
        erroCorrecao(saida, semRede
          ? 'Não consegui falar com o Banco Central agora. Pode ser a sua conexão, a rede em que você ' +
            'está, ou o site do BCB fora do ar.<br><br>Abri um campo no formulário para você informar o ' +
            '<strong>índice acumulado do período</strong> à mão — preencha e calcule de novo.'
          : String(erro && erro.message || erro));
      });
  });

  form.addEventListener('reset', function () {
    saida.innerHTML = '';
    saida.classList.remove('visivel');
    setTimeout(function () {
      preencherPeriodoPadrao();
      atualizarAjudaDoIndice();
      document.getElementById('bloco-manual').style.display = 'none';
    }, 0);
  });
}
