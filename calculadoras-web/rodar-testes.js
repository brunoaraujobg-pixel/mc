/* Roda os testes no terminal:  node rodar-testes.js */
var fs = require('fs');
var path = require('path');
var vm = require('vm');

['js/tabelas.js', 'js/calculo-ir.js', 'js/calculo-enquadramento.js', 'js/calculo-correcao.js', 'js/app.js', 'js/aba-correcao.js', 'js/testes.js']
  .forEach(function (arquivo) {
    vm.runInThisContext(fs.readFileSync(path.join(__dirname, arquivo), 'utf8'), { filename: arquivo });
  });

var resultados = rodarTestes();
var falhas = 0;

/* Número no padrão brasileiro: ponto no milhar, vírgula no decimal.
   Quem lê este relatório é contador — 2.751,40 é o que ele reconhece,
   não 2751.40. */
function numeroBR(v) {
  return Number(v).toLocaleString('pt-BR', {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
}

resultados.forEach(function (t) {
  var esperado = t.texto ? t.esperado : numeroBR(t.esperado);
  var obtido = t.texto ? t.obtido : numeroBR(t.obtido);
  if (!t.ok) falhas++;
  console.log((t.ok ? '  OK   ' : '  FALHA') + ' | ' + t.nome +
              '  ->  esperado: ' + esperado + ' | obtido: ' + obtido);
});

console.log('\n' + resultados.length + ' testes | ' + (resultados.length - falhas) +
            ' passaram | ' + falhas + ' falharam');
process.exit(falhas === 0 ? 0 : 1);
