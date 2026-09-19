/* Roda os testes no terminal:  node rodar-testes.js */
var fs = require('fs');
var path = require('path');
var vm = require('vm');

['js/tabelas.js', 'js/calculo-ir.js', 'js/calculo-enquadramento.js', 'js/app.js', 'js/testes.js']
  .forEach(function (arquivo) {
    vm.runInThisContext(fs.readFileSync(path.join(__dirname, arquivo), 'utf8'), { filename: arquivo });
  });

var resultados = rodarTestes();
var falhas = 0;

resultados.forEach(function (t) {
  var esperado = t.texto ? t.esperado : Number(t.esperado).toFixed(2);
  var obtido = t.texto ? t.obtido : Number(t.obtido).toFixed(2);
  if (!t.ok) falhas++;
  console.log((t.ok ? '  OK   ' : '  FALHA') + ' | ' + t.nome +
              '  ->  esperado: ' + esperado + ' | obtido: ' + obtido);
});

console.log('\n' + resultados.length + ' testes | ' + (resultados.length - falhas) +
            ' passaram | ' + falhas + ' falharam');
process.exit(falhas === 0 ? 0 : 1);
