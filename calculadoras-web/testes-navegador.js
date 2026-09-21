/* =============================================================================
   TESTES-NAVEGADOR.JS — abre a página num navegador de verdade e confere a tela
   -----------------------------------------------------------------------------
   Por que existe, se já temos o rodar-testes.js?

   O rodar-testes.js confere as CONTAS (INSS, IRRF, Simples, presumido, real).
   Ele não abre a página: se o app.js quebrar, se um campo do formulário mudar
   de nome, se o logo sumir ou se a troca de abas parar de funcionar, os 47
   testes continuam passando e a página fica quebrada mesmo assim.

   Este arquivo cobre esse buraco: abre o index.html num Chromium de verdade,
   preenche os formulários como um visitante faria e confere o que aparece
   na tela — além de exigir ZERO erro de JavaScript no console.

   Como rodar:
       npm install playwright
       npx playwright install --with-deps chromium
       node testes-navegador.js

   É usado pelo CI (.github/workflows/testes.yml). Para o uso do dia a dia,
   o Bruno não precisa disto — basta o 2-CONFERIR-CALCULOS.bat.
============================================================================= */

let chromium;
try {
  ({ chromium } = require('playwright'));
} catch (e) {
  ({ chromium } = require('playwright-core')); // usado no ambiente de desenvolvimento
}

const path = require('path');
const BASE = 'file://' + path.resolve(__dirname) + '/';

const resultados = [];

/* O Intl.NumberFormat do pt-BR separa "R$" do numero com um espaco NAO
   SEPARAVEL (U+00A0), que na tela parece um espaco comum mas nao e. Sem
   normalizar, "R$ 6.000,00" nunca casaria com "R$ 6.000,00" aqui. */
function normalizar(valor) {
  return String(valor).replace(/[\u00a0\u202f\u2007]/g, ' ').replace(/\s+/g, ' ').trim();
}

function conferir(nome, obtido, esperado) {
  const a = normalizar(obtido), b = normalizar(esperado);
  const ok = a === b;
  resultados.push({ nome, ok, esperado: b, obtido: a });
  console.log((ok ? '  OK    | ' : '  FALHA | ') + nome +
              (ok ? '' : '\n          esperado: ' + JSON.stringify(b) +
                         '\n          obtido:   ' + JSON.stringify(a)));
}

async function principal() {
  const opcoes = { args: ['--no-sandbox'] };
  if (process.env.CHROMIUM_PATH) opcoes.executablePath = process.env.CHROMIUM_PATH;
  const navegador = await chromium.launch(opcoes);

  const problemas = [];
  async function novaPagina(viewport) {
    const pagina = await navegador.newPage({ viewport });
    pagina.on('pageerror', e => problemas.push('erro de JS: ' + e.message));
    pagina.on('console', function (m) {
      if (m.type() !== 'error') return;
      if (/ERR_FAILED|api\.bcb\.gov\.br/.test(m.text())) return; // idem: abortado de propósito
      problemas.push('console: ' + m.text());
    });
    /* A chamada ao Banco Central é abortada de propósito num dos testes, para
       conferir a mensagem de erro e o modo manual. Falha dela não é bug da página
       — o que importa é a página tratar isso bem, e isso é testado logo abaixo. */
    pagina.on('requestfailed', function (r) {
      if (/api\.bcb\.gov\.br/.test(r.url())) return;
      problemas.push('nao carregou: ' + r.url().split('/').pop());
    });
    return pagina;
  }

  // ======================= PÁGINA PRINCIPAL =======================
  const pagina = await novaPagina({ width: 1280, height: 900 });
  await pagina.goto(BASE + 'index.html');
  await pagina.waitForTimeout(600);

  // --- o logo carregou? (a corrente png -> svg -> desenho embutido) ---
  const logo = await pagina.evaluate(() => {
    const img = document.querySelector('.cabecalho [data-logo]');
    return {
      existe: !!img,
      visivel: img ? !img.hidden : false,
      arquivo: img ? (img.getAttribute('src') || '') : '',
      largura: img ? img.naturalWidth : 0
    };
  });
  conferir('logo: a imagem do cabecalho carregou', logo.visivel, true);
  conferir('logo: veio do arquivo esperado', logo.arquivo, 'img/logo.png');
  conferir('logo: a imagem tem largura de verdade', logo.largura > 0, true);

  // --- a política de segurança continua no lugar? ---
  // Nada além deste teste impede que alguém afrouxe o CSP sem perceber.
  // O erro do 'frame-ancestors' só foi pego por acaso, pelo detector de
  // erro de console; isto aqui é a trava de verdade.
  const csp = await pagina.evaluate(() => {
    const m = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
    return m ? m.getAttribute('content').replace(/\s+/g, ' ').trim() : null;
  });
  conferir('CSP: a politica esta presente na pagina', csp !== null, true);
  conferir('CSP: script so do proprio site', /script-src [^;]*'self'/.test(csp || ''), true);
  conferir('CSP: script NAO aceita codigo embutido (unsafe-inline)',
    /script-src [^;]*unsafe-inline/.test(csp || ''), false);
  conferir('CSP: script NAO aceita eval (unsafe-eval)',
    /script-src [^;]*unsafe-eval/.test(csp || ''), false);
  conferir('CSP: so fala com a API do Banco Central',
    /connect-src https:\/\/api\.bcb\.gov\.br/.test(csp || ''), true);
  conferir('CSP: default-src fechado', /default-src 'none'/.test(csp || ''), true);
  // frame-ancestors e ignorado em <meta>; se alguem reintroduzir, o navegador
  // volta a reclamar no console e o teste de "nenhum erro de JS" quebra
  conferir('CSP: nao usa diretiva que <meta> ignora (frame-ancestors)',
    /frame-ancestors/.test(csp || ''), false);

  // --- dados do escritório preenchidos pelo JS ---
  conferir('rodape: telefone preenchido pelo tabelas.js',
    (await pagina.textContent('[data-escritorio="telefoneFixo"]')).trim(), '(81) 3224-3472');
  conferir('rodape: link do WhatsApp montado',
    await pagina.getAttribute('.rodape [data-whatsapp]', 'href'),
    'https://wa.me/5581987747434');

  // --- ABA 1: validação de campo vazio ---
  await pagina.click('#form-ir button[type=submit]');
  await pagina.waitForTimeout(250);
  conferir('aba 1: salario vazio mostra aviso de erro',
    await pagina.isVisible('#resultado-ir .aviso-erro'), true);

  // --- ABA 1: cálculo com valor conhecido ---
  // 6.000,00 com 1 dependente -> INSS 641,51 | IRRF 332,97 | liquido 5.025,52
  await pagina.fill('#ir-salario', '6.000,00');
  await pagina.fill('#ir-dependentes', '1');
  await pagina.click('#form-ir button[type=submit]');
  await pagina.waitForTimeout(400);

  const cartoes = await pagina.$$eval('#resultado-ir .cartao .cartao-valor',
    ns => ns.map(n => n.textContent.trim()));
  conferir('aba 1: salario bruto na tela', cartoes[0], 'R$ 6.000,00');
  conferir('aba 1: INSS na tela', cartoes[1], '− R$ 641,51');
  conferir('aba 1: IRRF na tela', cartoes[2], '− R$ 332,97');
  conferir('aba 1: salario liquido na tela', cartoes[3], 'R$ 5.025,52');

  const memoria = await pagina.textContent('#resultado-ir');
  conferir('aba 1: mostra a memoria de calculo do INSS',
    memoria.includes('INSS — contribuição do segurado'), true);
  conferir('aba 1: mostra o redutor da Lei 15.270/2025',
    memoria.includes('Lei nº 15.270/2025'), true);
  conferir('aba 1: mostra o botao de WhatsApp no fim do calculo',
    await pagina.isVisible('#resultado-ir .botao-whats'), true);

  // --- INSS digitado errado tem de ser recusado, não gerar líquido negativo ---
  await pagina.fill('#ir-salario', '3.000,00');
  await pagina.fill('#ir-inss', '5.000,00');
  await pagina.click('#form-ir button[type=submit]');
  await pagina.waitForTimeout(300);
  conferir('aba 1: recusa INSS maior que o salario bruto',
    (await pagina.textContent('#resultado-ir')).includes('maior que o salário bruto'), true);
  await pagina.fill('#ir-inss', '');

  // --- isenção: 3.036,00 (dois salários mínimos) tem de dar IRRF zero ---
  await pagina.fill('#ir-salario', '3036');
  await pagina.fill('#ir-dependentes', '0');
  await pagina.click('#form-ir button[type=submit]');
  await pagina.waitForTimeout(400);
  const cartoesIsento = await pagina.$$eval('#resultado-ir .cartao .cartao-valor',
    ns => ns.map(n => n.textContent.trim()));
  conferir('aba 1: salario de 3.036,00 fica isento de IRRF', cartoesIsento[2], '− R$ 0,00');

  // --- troca de abas ---
  await pagina.click('[data-aba="painel-enq"]');
  await pagina.waitForTimeout(300);
  conferir('abas: a aba 2 abriu', await pagina.isVisible('#painel-enq'), true);
  conferir('abas: a aba 1 fechou', await pagina.isVisible('#painel-ir'), false);

  // --- ABA 2: campos aparecem conforme a atividade ---
  conferir('aba 2: comercio mostra o campo de ICMS',
    await pagina.isVisible('#bloco-icms'), true);
  conferir('aba 2: comercio esconde o campo de ISS',
    await pagina.isVisible('#bloco-iss'), false);

  await pagina.check('input[name="enq-atividade"][value="servico"]');
  await pagina.waitForTimeout(250);
  conferir('aba 2: servico mostra o campo de ISS',
    await pagina.isVisible('#bloco-iss'), true);
  conferir('aba 2: servico mostra o tipo de servico (Fator R)',
    await pagina.isVisible('#bloco-tipo-servico'), true);

  // --- ABA 2: simulação com valores conhecidos ---
  // servico, 600.000 de faturamento, folha 120.000 -> Fator R 20% -> Anexo V
  // DAS = (600.000 x 19,5% - 9.900) = 107.100,00
  await pagina.fill('#enq-faturamento', '600.000,00');
  await pagina.fill('#enq-folha', '120.000,00');
  await pagina.click('#form-enq button[type=submit]');
  await pagina.waitForTimeout(400);

  const regimes = await pagina.$$eval('#resultado-enq .resultado-destaques .cartao',
    ns => ns.map(n => ({
      titulo: n.querySelector('.cartao-rotulo').textContent.trim(),
      valor: n.querySelector('.cartao-valor').textContent.trim()
    })));
  conferir('aba 2: Simples Nacional calculado', regimes[0].valor, 'R$ 107.100,00');
  conferir('aba 2: aponta o Simples como menor carga',
    /menor carga/i.test(regimes[0].titulo), true);
  conferir('aba 2: Lucro Presumido calculado', regimes[1].valor, 'R$ 131.340,00');
  conferir('aba 2: Lucro Real calculado', regimes[2].valor, 'R$ 127.710,00');

  const textoEnq = await pagina.textContent('#resultado-enq');
  conferir('aba 2: identificou o Anexo V pelo Fator R',
    textoEnq.includes('Anexo V'), true);
  conferir('aba 2: mostra o aviso de que e estimativa',
    textoEnq.includes('Simulação simplificada'), true);
  conferir('aba 2: avisa sobre a mudanca de 2027 (IBS/CBS)',
    textoEnq.includes('2027'), true);

  // --- teto do Simples ---
  await pagina.fill('#enq-faturamento', '5.000.000,00');
  await pagina.click('#form-enq button[type=submit]');
  await pagina.waitForTimeout(400);
  conferir('aba 2: acima de 4,8 mi o Simples aparece como nao permitido',
    (await pagina.textContent('#resultado-enq')).includes('Não permitido'), true);

  // ======================= ABA 3 — ATUALIZAÇÃO MONETÁRIA =======================
  // Duas situações: o Banco Central fora de alcance (cai no modo manual) e o
  // Banco Central respondendo (resposta simulada, para o teste não depender de rede).

  await pagina.click('[data-aba="painel-cor"]');
  await pagina.waitForTimeout(300);
  conferir('aba 3: abriu', await pagina.isVisible('#painel-cor'), true);
  conferir('aba 3: a lista de indices veio do tabelas.js',
    (await pagina.$$eval('#cor-indice option', ns => ns.length)), 6);
  conferir('aba 3: mes final ja vem preenchido',
    (await pagina.inputValue('#cor-fim')).length, 7);
  conferir('aba 3: campo do acumulado comeca escondido',
    await pagina.isVisible('#bloco-manual'), false);

  await pagina.selectOption('#cor-indice', 'selic');
  await pagina.waitForTimeout(200);
  conferir('aba 3: SELIC oferece o 1% do mes do pagamento',
    await pagina.isVisible('#bloco-selic1'), true);
  await pagina.selectOption('#cor-indice', 'ipca');
  await pagina.waitForTimeout(200);
  conferir('aba 3: IPCA nao oferece o 1%', await pagina.isVisible('#bloco-selic1'), false);

  // índice com código de série ainda não conferido tem de avisar na tela
  await pagina.selectOption('#cor-indice', 'ipcae');
  await pagina.waitForTimeout(200);
  conferir('aba 3: IPCA-E avisa que a serie nao foi conferida',
    await pagina.isVisible('#cor-aviso-serie'), true);
  await pagina.selectOption('#cor-indice', 'ipca');
  await pagina.waitForTimeout(200);
  conferir('aba 3: IPCA nao mostra esse aviso',
    await pagina.isVisible('#cor-aviso-serie'), false);

  await pagina.fill('#cor-valor', '1.500,00');
  await pagina.fill('#cor-inicio', '2026-05');
  await pagina.fill('#cor-fim', '2026-01');
  await pagina.click('#form-cor button[type=submit]');
  await pagina.waitForTimeout(250);
  conferir('aba 3: recusa periodo invertido',
    (await pagina.textContent('#resultado-cor')).includes('não pode ser anterior'), true);

  // --- Banco Central respondendo (simulado): IPCA 0,5% + 0,3% + 0,2% ---
  await pagina.route('**/api.bcb.gov.br/**', function (rota) {
    rota.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([
      { data: '01/01/2026', valor: '0.50' },
      { data: '01/02/2026', valor: '0.30' },
      { data: '01/03/2026', valor: '0.20' }
    ]) });
  });
  await pagina.fill('#cor-inicio', '2026-01');
  await pagina.fill('#cor-fim', '2026-03');
  await pagina.fill('#cor-juros', '1');
  await pagina.click('#form-cor button[type=submit]');
  await pagina.waitForTimeout(700);

  const cor = await pagina.$$eval('#resultado-cor .cartao .cartao-valor',
    ns => ns.map(n => n.textContent.trim()));
  conferir('aba 3: valor original na tela', cor[0], 'R$ 1.500,00');
  conferir('aba 3: correcao de 1,0031% sobre 1.500,00', cor[1], '+ R$ 15,05');
  conferir('aba 3: juros simples de 1% x 3 meses', cor[2], '+ R$ 45,45');
  conferir('aba 3: valor atualizado', cor[3], 'R$ 1.560,50');

  const textoCor = await pagina.textContent('#resultado-cor');
  conferir('aba 3: mostra a tabela mes a mes', textoCor.includes('Índices usados, mês a mês'), true);
  conferir('aba 3: cita a serie oficial usada', textoCor.includes('série 433'), true);

  // --- pediu mais meses do que o BCB tem divulgado ---
  await pagina.fill('#cor-fim', '2026-06');
  await pagina.click('#form-cor button[type=submit]');
  await pagina.waitForTimeout(600);
  conferir('aba 3: avisa quando faltam meses divulgados',
    (await pagina.textContent('#resultado-cor')).includes('só tem 3 divulgados'), true);

  // --- Banco Central fora do ar: tem de cair no modo manual ---
  await pagina.unroute('**/api.bcb.gov.br/**');
  await pagina.route('**/api.bcb.gov.br/**', function (rota) { rota.abort('failed'); });
  await pagina.fill('#cor-fim', '2026-03');
  await pagina.click('#form-cor button[type=submit]');
  await pagina.waitForTimeout(800);
  conferir('aba 3: explica que nao falou com o Banco Central',
    (await pagina.textContent('#resultado-cor')).includes('Não consegui falar com o Banco Central'), true);
  conferir('aba 3: abre o campo do acumulado manual',
    await pagina.isVisible('#bloco-manual'), true);

  await pagina.fill('#cor-acumulado', '12,5');
  await pagina.fill('#cor-juros', '0');
  await pagina.click('#form-cor button[type=submit]');
  await pagina.waitForTimeout(400);
  const corManual = await pagina.$$eval('#resultado-cor .cartao .cartao-valor',
    ns => ns.map(n => n.textContent.trim()));
  conferir('aba 3 manual: 12,5% sobre 1.500,00 = 187,50', corManual[1], '+ R$ 187,50');
  conferir('aba 3 manual: total', corManual[2], 'R$ 1.687,50');
  conferir('aba 3 manual: avisa que usou o percentual informado',
    (await pagina.textContent('#resultado-cor')).includes('que você informou'), true);
  await pagina.unroute('**/api.bcb.gov.br/**');

  // ======================= CELULAR =======================
  const celular = await novaPagina({ width: 360, height: 780 });
  await celular.goto(BASE + 'index.html');
  await celular.waitForTimeout(500);
  const rolaDeLado = await celular.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  conferir('celular: a pagina nao rola de lado', rolaDeLado, false);

  await celular.fill('#ir-salario', '4200');
  await celular.click('#form-ir button[type=submit]');
  await celular.waitForTimeout(400);
  conferir('celular: o calculo funciona na tela pequena',
    await celular.isVisible('#resultado-ir .cartao-principal'), true);

  // ======================= PÁGINA DE TESTES =======================
  const testes = await novaPagina({ width: 1280, height: 900 });
  await testes.goto(BASE + 'testes.html');
  await testes.waitForTimeout(600);
  const resumo = (await testes.textContent('#resumo')).trim();
  console.log('\n  testes.html diz: ' + resumo + '\n');
  conferir('testes.html: nenhuma conferencia de calculo falhou',
    resumo.includes('0 falharam'), true);

  // ======================= ERROS DE JS =======================
  conferir('nenhum erro de JavaScript em nenhuma pagina',
    problemas.length === 0 ? 'nenhum' : problemas.join(' | '), 'nenhum');

  await navegador.close();

  const falhas = resultados.filter(r => !r.ok).length;
  console.log('\n' + resultados.length + ' testes de navegador | ' +
              (resultados.length - falhas) + ' passaram | ' + falhas + ' falharam');
  process.exit(falhas === 0 ? 0 : 1);
}

principal().catch(e => { console.error('\nERRO ao rodar os testes de navegador:\n', e); process.exit(1); });
