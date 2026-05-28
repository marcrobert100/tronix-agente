const fs = require('fs');
const c = fs.readFileSync('C:/casa/public/painel.html', 'utf8');

// Find key areas
const areas = ['id="lista-ped"', 'id="cardapio-admin"', 'id="tab-pedidos"', 'tab-cardapio', 'tab-empresa'];
areas.forEach(a => {
  const idx = c.indexOf(a);
  console.log(a, 'at:', idx);
});

// Find empresa tab save button
const empBtn = c.indexOf('btn-sv-emp');
console.log('btn-sv-emp at:', empBtn);
console.log(c.slice(empBtn - 50, empBtn + 200));
