const fs = require('fs');
const c = fs.readFileSync('C:/casa/public/painel.html', 'utf8');

// 1. Find modal-item content area
const modalItem = c.indexOf('id="modal-item"');
console.log('modal-item at:', modalItem);
// Find campos do modal item
const miFields = c.indexOf('id="mi-cat"', modalItem);
console.log('mi-cat at:', miFields);
console.log(c.slice(miFields - 100, miFields + 500));
