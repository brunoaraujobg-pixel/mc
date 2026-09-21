/* =============================================================================
   APP.JS — formatação, troca de abas e ligação entre a tela e os cálculos
============================================================================= */

/* ------------------------------ FORMATAÇÃO ------------------------------- */

function formatarMoeda(valor) {
  if (valor === null || valor === undefined || isNaN(valor)) return '—';
  return Number(valor).toLocaleString('pt-BR', {
    style: 'currency', currency: 'BRL',
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
}

function formatarPercentual(fracao, casas) {
  if (fracao === null || fracao === undefined || isNaN(fracao)) return '—';
  var c = (casas === undefined) ? 2 : casas;
  return (Number(fracao) * 100).toLocaleString('pt-BR', {
    minimumFractionDigits: c, maximumFractionDigits: c
  }) + '%';
}

/* Escapa texto antes de colocar dentro de innerHTML.
   Quase tudo que a página mostra é número formatado, que é seguro por
   construção. A exceção é o que vem de FORA: a resposta da API do Banco
   Central e as mensagens de erro do navegador, que podem carregar um
   pedaço do corpo da resposta. Esses passam por aqui. */
function escaparHtml(texto) {
  if (texto === null || texto === undefined) return '';
  return String(texto)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* Lê um número digitado do jeito brasileiro.
   Aceita: 3500 | 3.500 | 3.500,00 | 3500,00 | R$ 3.500,00 | 1.234.567,89 | 3500.50

   O caso que exige cuidado é o ponto SEM vírgula. No Brasil "300.000" é
   trezentos mil, mas o Number() do JavaScript lê isso como 300 — e lê
   "1.000.000" como erro, porque tem dois pontos. Por isso, quando o texto
   tem a cara de separador de milhar (grupos de exatamente 3 dígitos), os
   pontos são removidos. Fora desse formato, o ponto continua valendo como
   separador decimal, para quem digita "3500.50" ou "4.5" num campo de
   percentual. */
function parseNumeroBR(texto) {
  if (texto === null || texto === undefined) return null;

  var s = String(texto).trim().replace(/[R$\s\u00a0]/g, '');
  if (s === '') return null;

  var negativo = s.charAt(0) === '-';
  if (negativo) s = s.slice(1);

  if (s.indexOf(',') > -1) {
    // Tem vírgula: ela é o separador decimal e os pontos são de milhar.
    s = s.replace(/\./g, '').replace(',', '.');
  } else if (/^\d{1,3}(\.\d{3})+$/.test(s)) {
    // "300.000", "1.000.000": pontos de milhar, sem centavos.
    s = s.replace(/\./g, '');
  }
  // Nos demais casos ("3500", "3500.50", "4.5") o texto já serve como está.

  if (!/^\d*\.?\d+$/.test(s)) return null;

  var n = Number(s);
  if (isNaN(n)) return null;
  return negativo ? -n : n;
}

/* ------------------------------ ABAS ------------------------------------- */

function iniciarAbas() {
  var botoes = document.querySelectorAll('.aba-botao');
  for (var i = 0; i < botoes.length; i++) {
    botoes[i].addEventListener('click', function () {
      var alvo = this.getAttribute('data-aba');
      var todos = document.querySelectorAll('.aba-botao');
      for (var j = 0; j < todos.length; j++) {
        todos[j].classList.remove('ativo');
        todos[j].setAttribute('aria-selected', 'false');
      }
      this.classList.add('ativo');
      this.setAttribute('aria-selected', 'true');

      var paineis = document.querySelectorAll('.aba-painel');
      for (var k = 0; k < paineis.length; k++) {
        paineis[k].classList.toggle('ativo', paineis[k].id === alvo);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

/* --------------------- BLOCO DE CHAMADA PARA CONTATO --------------------- */

function blocoContato(mensagem) {
  var e = TABELAS.escritorio;
  var texto = encodeURIComponent(mensagem);
  return '' +
    '<div class="cta">' +
      '<div class="cta-texto">' +
        '<strong>Quer conferir esse número com um contador?</strong>' +
        '<span>A ' + e.nome + ' analisa seu caso concreto e diz exatamente o que fazer.</span>' +
      '</div>' +
      '<div class="cta-botoes">' +
        '<a class="botao botao-whats" target="_blank" rel="noopener" ' +
          'href="https://wa.me/' + e.whatsapp + '?text=' + texto + '">Falar no WhatsApp</a>' +
        '<a class="botao botao-secundario" href="tel:+558132243472">' + e.telefoneFixo + '</a>' +
      '</div>' +
    '</div>';
}

/* ====================== ABA 1 — CALCULADORA DE IR ======================== */

function renderizarResultadoIR(r) {
  var html = '';

  html += '<div class="resultado-destaques">';
  html += cartaoDestaque('Salário bruto', formatarMoeda(r.salarioBruto), '');
  html += cartaoDestaque('INSS descontado', '− ' + formatarMoeda(r.inss.valor),
            formatarPercentual(r.inss.aliquotaEfetiva ? r.inss.aliquotaEfetiva : (r.inss.valor / r.salarioBruto)) + ' do bruto');
  html += cartaoDestaque('IRRF', '− ' + formatarMoeda(r.irrf),
            r.irrf === 0 ? 'Isento neste mês' : formatarPercentual(r.aliquotaEfetivaIRRF) + ' do bruto');
  html += cartaoDestaque('Salário líquido estimado', formatarMoeda(r.salarioLiquido), '', true);
  html += '</div>';

  /* ---------------- memória de cálculo ---------------- */
  html += '<h3 class="titulo-secao">Memória de cálculo</h3>';

  /* Passo 1 — INSS */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">1</span> INSS — contribuição do segurado</div>';
  if (r.inss.origem === 'informado') {
    html += '<p class="obs">Você informou o valor do INSS: <strong>' + formatarMoeda(r.inss.valor) + '</strong>. ' +
            'A calculadora usou esse valor em vez de calcular pela tabela.</p>';
  } else {
    html += '<table class="tabela"><thead><tr>' +
            '<th>Faixa do salário</th><th>Parcela</th><th>Alíquota</th><th>Valor</th>' +
            '</tr></thead><tbody>';
    for (var i = 0; i < r.inss.detalhe.memoria.length; i++) {
      var m = r.inss.detalhe.memoria[i];
      html += '<tr>' +
              '<td>' + formatarMoeda(m.de) + ' a ' + formatarMoeda(m.ate) + '</td>' +
              '<td>' + formatarMoeda(m.parcela) + '</td>' +
              '<td>' + formatarPercentual(m.aliquota, 1) + '</td>' +
              '<td>' + formatarMoeda(m.valor) + '</td></tr>';
    }
    html += '<tr class="linha-total"><td colspan="3">Total do INSS</td><td>' +
            formatarMoeda(r.inss.valor) + '</td></tr>';
    html += '</tbody></table>';
    if (r.inss.detalhe.atingiuTeto) {
      html += '<p class="obs">O salário ultrapassou o teto do INSS (' + formatarMoeda(r.inss.detalhe.teto) +
              '). A contribuição ficou travada no desconto máximo.</p>';
    }
  }
  html += '</div>';

  /* Passo 2 — base de cálculo */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">2</span> Base de cálculo do IRRF — a lei manda usar a opção mais vantajosa</div>';
  html += '<table class="tabela"><thead><tr><th>Opção</th><th>Como se chega na base</th><th>Base</th><th>Imposto pela tabela</th></tr></thead><tbody>';

  var linhaLegais = 'Bruto − INSS' + (r.dependentes > 0
      ? ' − ' + r.dependentes + ' dependente(s) × ' + formatarMoeda(r.valorPorDependente)
      : ' (sem dependentes)');
  html += '<tr' + (r.metodoEscolhido === 'deduções legais' ? ' class="linha-escolhida"' : '') + '>' +
          '<td>Deduções legais</td><td>' + linhaLegais + '</td>' +
          '<td>' + formatarMoeda(r.comparativo.legais.base) + '</td>' +
          '<td>' + formatarMoeda(r.comparativo.legais.imposto) + '</td></tr>';

  html += '<tr' + (r.metodoEscolhido === 'desconto simplificado' ? ' class="linha-escolhida"' : '') + '>' +
          '<td>Desconto simplificado</td><td>Bruto − ' + formatarMoeda(r.descontoSimplificado) + '</td>' +
          '<td>' + formatarMoeda(r.comparativo.simplificado.base) + '</td>' +
          '<td>' + formatarMoeda(r.comparativo.simplificado.imposto) + '</td></tr>';
  html += '</tbody></table>';
  html += '<p class="obs">Opção usada: <strong>' + r.metodoEscolhido + '</strong> — é a que resulta em menor imposto. ' +
          'Base de cálculo do IRRF: <strong>' + formatarMoeda(r.baseCalculoIRRF) + '</strong>.</p>';
  html += '</div>';

  /* Passo 3 — tabela progressiva */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">3</span> Aplicação da tabela progressiva mensal</div>';
  html += '<p class="formula">' + formatarMoeda(r.baseCalculoIRRF) + ' × ' +
          formatarPercentual(r.aliquotaAplicada, 1) + ' − ' + formatarMoeda(r.parcelaADeduzir) +
          ' = <strong>' + formatarMoeda(r.impostoPelaTabela) + '</strong></p>';
  html += '<p class="obs">Alíquota da faixa: ' + formatarPercentual(r.aliquotaAplicada, 1) +
          ' | Parcela a deduzir: ' + formatarMoeda(r.parcelaADeduzir) + '</p>';
  html += '</div>';

  /* Passo 4 — redutor */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">4</span> Redutor do imposto — Lei nº 15.270/2025 (desde 01/2026)</div>';
  html += '<p class="formula">' + r.redutor.formula + '</p>';
  html += '<p class="obs">Redução aplicada: <strong>' + formatarMoeda(r.redutor.valor) + '</strong></p>';
  html += '</div>';

  /* Passo 5 — resultado */
  html += '<div class="passo">';
  html += '<div class="passo-titulo"><span class="passo-num">5</span> Resultado</div>';
  html += '<table class="tabela"><tbody>';
  html += '<tr><td>Imposto pela tabela</td><td>' + formatarMoeda(r.impostoPelaTabela) + '</td></tr>';
  html += '<tr><td>(−) Redutor da Lei nº 15.270/2025</td><td>' + formatarMoeda(r.redutor.valor) + '</td></tr>';
  html += '<tr class="linha-total"><td>IRRF a recolher</td><td>' + formatarMoeda(r.irrf) + '</td></tr>';
  html += '</tbody></table>';
  html += '<table class="tabela" style="margin-top:12px"><tbody>';
  html += '<tr><td>Salário bruto</td><td>' + formatarMoeda(r.salarioBruto) + '</td></tr>';
  html += '<tr><td>(−) INSS</td><td>' + formatarMoeda(r.inss.valor) + '</td></tr>';
  html += '<tr><td>(−) IRRF</td><td>' + formatarMoeda(r.irrf) + '</td></tr>';
  html += '<tr class="linha-total"><td>Salário líquido estimado</td><td>' + formatarMoeda(r.salarioLiquido) + '</td></tr>';
  html += '</tbody></table>';
  html += '<p class="obs">Carga total (INSS + IRRF): ' + formatarMoeda(r.cargaTotal) +
          ' — ' + formatarPercentual(r.aliquotaEfetivaTotal) + ' do salário bruto.</p>';
  html += '</div>';

  html += '<div class="aviso aviso-neutro">' +
          '<strong>O que este cálculo não inclui:</strong> vale-transporte, plano de saúde, adiantamentos, ' +
          'pensão alimentícia, previdência privada, faltas, horas extras, adicionais e qualquer outro desconto ' +
          'ou provento do contracheque. É o cálculo do INSS e do IRRF sobre o salário informado.' +
          '</div>';

  html += blocoContato('Olá! Usei a calculadora de IR do site da M Contabilidade e gostaria de tirar uma dúvida.');

  return html;
}

function cartaoDestaque(rotulo, valor, complemento, principal) {
  return '<div class="cartao' + (principal ? ' cartao-principal' : '') + '">' +
         '<span class="cartao-rotulo">' + rotulo + '</span>' +
         '<span class="cartao-valor">' + valor + '</span>' +
         (complemento ? '<span class="cartao-obs">' + complemento + '</span>' : '') +
         '</div>';
}

function iniciarFormularioIR() {
  var form = document.getElementById('form-ir');
  var saida = document.getElementById('resultado-ir');
  if (!form) return;

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();

    var salario = parseNumeroBR(document.getElementById('ir-salario').value);
    if (salario === null || salario <= 0) {
      saida.innerHTML = '<div class="aviso aviso-erro">Informe um salário bruto mensal maior que zero.</div>';
      saida.classList.add('visivel');
      return;
    }

    /* Um erro de digitação (vírgula no lugar errado) fazia a página mostrar
       líquido negativo, ou líquido maior que o bruto, com a mesma cara de
       resultado válido. Agora ela recusa e explica. */
    var inssDigitado = parseNumeroBR(document.getElementById('ir-inss').value);
    if (inssDigitado !== null) {
      if (inssDigitado < 0) {
        saida.innerHTML = '<div class="aviso aviso-erro">O INSS descontado não pode ser negativo.</div>';
        saida.classList.add('visivel');
        return;
      }
      if (inssDigitado > salario) {
        saida.innerHTML = '<div class="aviso aviso-erro">O INSS informado (' +
          formatarMoeda(inssDigitado) + ') é maior que o salário bruto (' + formatarMoeda(salario) +
          '). Confira os dois valores — provavelmente há uma vírgula fora do lugar.</div>';
        saida.classList.add('visivel');
        return;
      }
    }

    var resultado = calcularIRRF({
      salarioBruto: salario,
      dependentes: document.getElementById('ir-dependentes').value,
      inssInformado: inssDigitado
    });

    saida.innerHTML = renderizarResultadoIR(resultado);
    saida.classList.add('visivel');
    saida.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  form.addEventListener('reset', function () {
    saida.innerHTML = '';
    saida.classList.remove('visivel');
  });
}

/* ================ ABA 2 — SIMULADOR DE ENQUADRAMENTO ==================== */

function atualizarCamposAtividade() {
  var atividade = document.querySelector('input[name="enq-atividade"]:checked');
  if (!atividade) return;
  var ehServico = atividade.value === 'servico';

  document.getElementById('bloco-tipo-servico').style.display = ehServico ? '' : 'none';
  document.getElementById('bloco-iss').style.display = ehServico ? '' : 'none';
  document.getElementById('bloco-icms').style.display = ehServico ? 'none' : '';

  // sugestão de créditos de PIS/COFINS conforme a atividade
  var campoCreditos = document.getElementById('enq-creditos');
  if (!campoCreditos.dataset.editado) {
    campoCreditos.value = ehServico ? '10' : (atividade.value === 'industria' ? '50' : '60');
  }
}

function renderizarResultadoEnquadramento(sim) {
  var e = sim.entrada;
  var html = '';

  html += '<div class="aviso aviso-forte">' +
          '<strong>Simulação simplificada.</strong> O enquadramento ideal depende de análise detalhada dos números ' +
          'reais da empresa (produtos, CFOP, ICMS-ST, monofásico, créditos, folha, benefícios fiscais e da própria ' +
          'atividade). Esta página é uma estimativa educativa — não use como base para trocar de regime. ' +
          'Fale com a ' + TABELAS.escritorio.nome + '.' +
          '</div>';

  html += '<div class="resultado-destaques">';
  for (var i = 0; i < sim.resultados.length; i++) {
    var r = sim.resultados[i];
    if (!r.permitido) {
      html += '<div class="cartao cartao-bloqueado">' +
              '<span class="cartao-rotulo">' + r.regime + '</span>' +
              '<span class="cartao-valor">Não permitido</span>' +
              '<span class="cartao-obs">' + r.motivo + '</span></div>';
    } else {
      var destaque = (sim.menorCarga === r.regime);
      html += '<div class="cartao' + (destaque ? ' cartao-principal' : '') + '">' +
              '<span class="cartao-rotulo">' + r.regime + (destaque ? ' — menor carga estimada' : '') + '</span>' +
              '<span class="cartao-valor">' + formatarMoeda(r.total) + '</span>' +
              '<span class="cartao-obs">' + formatarPercentual(r.cargaSobreFaturamento) + ' do faturamento anual</span>' +
              '</div>';
    }
  }
  html += '</div>';

  /* detalhamento */
  html += '<h3 class="titulo-secao">Memória de cálculo por regime</h3>';

  for (var j = 0; j < sim.resultados.length; j++) {
    var res = sim.resultados[j];
    html += '<div class="passo">';
    html += '<div class="passo-titulo">' + res.regime + '</div>';

    if (!res.permitido) {
      html += '<p class="obs">' + res.motivo + '</p></div>';
      continue;
    }

    if (res.regime === 'Simples Nacional') {
      html += '<p class="obs">Enquadramento: <strong>' + res.anexo + '</strong> — ' + res.numeroFaixa + 'ª faixa.';
      if (res.fatorR !== null) {
        html += ' Fator R = folha ÷ faturamento = ' + formatarPercentual(res.fatorR) +
                (res.atingiuFatorR
                  ? ' (igual ou acima de 28% → Anexo III).'
                  : ' (abaixo de 28% → Anexo V).');
      }
      html += '</p>';
    }

    html += '<ul class="lista-formula">';
    for (var m = 0; m < res.memoria.length; m++) {
      html += '<li>' + res.memoria[m] + '</li>';
    }
    html += '</ul>';

    html += '<table class="tabela"><thead><tr><th>Tributo / encargo</th><th>Valor anual estimado</th></tr></thead><tbody>';
    for (var k = 0; k < res.itens.length; k++) {
      html += '<tr><td>' + res.itens[k].nome + '</td><td>' + formatarMoeda(res.itens[k].valor) + '</td></tr>';
    }
    html += '<tr class="linha-total"><td>Total estimado no ano</td><td>' + formatarMoeda(res.total) + '</td></tr>';
    html += '</tbody></table>';

    for (var a = 0; a < res.avisos.length; a++) {
      html += '<p class="obs">• ' + res.avisos[a] + '</p>';
    }
    html += '</div>';
  }

  /* premissas */
  html += '<div class="passo">';
  html += '<div class="passo-titulo">Premissas usadas nesta simulação</div>';
  html += '<ul class="lista-formula">';
  html += '<li>Faturamento anual: ' + formatarMoeda(e.faturamentoAnual) + ', distribuído de forma uniforme nos 12 meses.</li>';
  html += '<li>Folha anual (salários + pró-labore, base da CPP e do Fator R): ' + formatarMoeda(e.folhaAnual) + '.</li>';
  html += '<li>CPP no regime normal: ' + formatarPercentual(TABELAS.cpp.total) + ' sobre a folha (20% patronal + ' +
          formatarPercentual(TABELAS.cpp.ratMedio) + ' de RAT presumido + ' +
          formatarPercentual(TABELAS.cpp.terceirosMedio) + ' de terceiros). O percentual real depende do FPAS/RAT/FAP da empresa.</li>';
  if (e.atividade === 'servico') {
    html += '<li>ISS: ' + formatarPercentual(e.issAliquota) + ' (alíquota municipal informada).</li>';
  } else {
    html += '<li>ICMS efetivo informado: ' + formatarPercentual(e.icmsEfetivo) + '.</li>';
  }
  html += '<li>Margem de lucro para o Lucro Real: ' + formatarPercentual(e.margemLucro) + '.</li>';
  html += '<li>Créditos de PIS/COFINS no Lucro Real: ' + formatarPercentual(e.creditosPisCofins) + ' do faturamento.</li>';
  html += '<li>IBS/CBS não entram no cálculo: em 2026 são cobrados em fase de teste (CBS 0,9% e IBS 0,1%), ' +
          'compensáveis com PIS/COFINS, sem custo adicional para quem cumpre as obrigações acessórias (LC nº 214/2025). ' +
          '<strong>A partir de 2027 isso muda.</strong></li>';
  html += '</ul>';
  html += '</div>';

  html += '<div class="aviso aviso-neutro">' +
          '<strong>O que esta simulação não considera:</strong> ICMS-ST, produtos monofásicos, benefícios fiscais ' +
          'estaduais, DIFAL, importação, IPI, atividades vedadas ou mistas, segregação de receitas, retenções na fonte, ' +
          'créditos acumulados, prejuízo fiscal e a situação societária da empresa. Todos esses pontos mudam o resultado.' +
          '</div>';

  html += blocoContato('Olá! Simulei o enquadramento tributário no site da M Contabilidade e gostaria de uma análise do meu caso.');

  return html;
}

function iniciarFormularioEnquadramento() {
  var form = document.getElementById('form-enq');
  var saida = document.getElementById('resultado-enq');
  if (!form) return;

  var radios = document.querySelectorAll('input[name="enq-atividade"]');
  for (var i = 0; i < radios.length; i++) {
    radios[i].addEventListener('change', atualizarCamposAtividade);
  }
  document.getElementById('enq-creditos').addEventListener('input', function () {
    this.dataset.editado = '1';
  });
  atualizarCamposAtividade();

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();

    var faturamento = parseNumeroBR(document.getElementById('enq-faturamento').value);
    if (faturamento === null || faturamento <= 0) {
      saida.innerHTML = '<div class="aviso aviso-erro">Informe um faturamento anual maior que zero.</div>';
      saida.classList.add('visivel');
      return;
    }

    var atividade = document.querySelector('input[name="enq-atividade"]:checked').value;
    var tipoServico = document.getElementById('enq-tipo-servico').value;

    var entrada = {
      faturamentoAnual: faturamento,
      atividade: atividade,
      tipoServico: tipoServico,
      folhaAnual: parseNumeroBR(document.getElementById('enq-folha').value) || 0,
      issAliquota: (parseNumeroBR(document.getElementById('enq-iss').value) || 0) / 100,
      icmsEfetivo: (parseNumeroBR(document.getElementById('enq-icms').value) || 0) / 100,
      margemLucro: (parseNumeroBR(document.getElementById('enq-margem').value) || 0) / 100,
      creditosPisCofins: (parseNumeroBR(document.getElementById('enq-creditos').value) || 0) / 100
    };

    saida.innerHTML = renderizarResultadoEnquadramento(simularEnquadramento(entrada));
    saida.classList.add('visivel');
    saida.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  form.addEventListener('reset', function () {
    saida.innerHTML = '';
    saida.classList.remove('visivel');
    setTimeout(atualizarCamposAtividade, 0);
  });
}

/* ------------------------------ RODAPÉ / INÍCIO -------------------------- */

/* -----------------------------------------------------------------------------
   LOGO — tenta img/logo.png, depois img/logo.svg, e só então cai no desenho
   de reserva que está embutido no HTML. Assim o Bruno troca o logo apenas
   soltando o arquivo na pasta img, sem editar código nenhum.
   O src é definido aqui (e não no HTML) para garantir que o tratamento de
   erro já esteja ligado quando o navegador tentar carregar a imagem.
----------------------------------------------------------------------------- */
function iniciarLogos() {
  var imagens = document.querySelectorAll('[data-logo]');
  var reservas = document.querySelectorAll('[data-logo-reserva]');
  var pendentes = imagens.length;

  function mostrarReserva() {
    for (var r = 0; r < reservas.length; r++) reservas[r].hidden = false;
  }
  if (pendentes === 0) { mostrarReserva(); return; }

  for (var i = 0; i < imagens.length; i++) {
    (function (img) {
      var base = img.getAttribute('data-logo');
      var tentativas = [base + '.png', base + '.svg'];
      var indice = 0;

      img.addEventListener('load', function () { img.hidden = false; });
      img.addEventListener('error', function () {
        indice++;
        if (indice < tentativas.length) {
          img.src = tentativas[indice];
        } else {
          img.remove();
          mostrarReserva();
        }
      });

      img.src = tentativas[0];
    })(imagens[i]);
  }
}

function preencherDadosDoEscritorio() {
  var e = TABELAS.escritorio;
  var alvos = document.querySelectorAll('[data-escritorio]');
  for (var i = 0; i < alvos.length; i++) {
    var campo = alvos[i].getAttribute('data-escritorio');
    if (e[campo]) alvos[i].textContent = e[campo];
  }
  var whats = document.querySelectorAll('[data-whatsapp]');
  for (var j = 0; j < whats.length; j++) {
    whats[j].setAttribute('href', 'https://wa.me/' + e.whatsapp);
  }
  var versao = document.getElementById('versao-tabelas');
  if (versao) {
    versao.textContent = 'Tabelas versão ' + TABELAS.versao + ' — atualizadas em ' + TABELAS.atualizadoEm;
  }
}

/* Só liga a tela quando estiver rodando dentro do navegador.
   Isso permite reaproveitar as funções de cálculo em testes fora do navegador. */
if (typeof document !== 'undefined' && document.addEventListener) {
  document.addEventListener('DOMContentLoaded', function () {
    /* Cada aba mora num arquivo. A página de conferência (testes.html) carrega
       só os motores de cálculo, sem os arquivos de tela — por isso a chamada é
       condicional. Se um arquivo de tela faltar no index.html, os testes de
       navegador acusam, porque a aba deixa de funcionar. */
    function ligar(nome) {
      if (typeof window[nome] === 'function') window[nome]();
    }
    ligar('iniciarLogos');
    ligar('iniciarAbas');
    ligar('iniciarFormularioIR');
    ligar('iniciarFormularioEnquadramento');
    ligar('iniciarFormularioCorrecao');
    ligar('preencherDadosDoEscritorio');
  });
}
