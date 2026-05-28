const fs = require('fs');
const c = fs.readFileSync('C:/casa/server.js', 'utf8');

// Find the /entregar route
const marker = 'app.post("/api/pedidos/:num/entregar"';
const idx = c.indexOf(marker);
console.log('Route at:', idx);
// Show full route
console.log(c.slice(idx, idx + 1500));
