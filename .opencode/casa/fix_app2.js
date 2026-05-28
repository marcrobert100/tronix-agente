const fs = require('fs');
let c = fs.readFileSync('C:/casa/public/js/app.js', 'utf8');
console.log('Before cleanup, size:', c.length);

// Remove duplicate mkCardPedido functions
// Find all function mkCardPedido occurrences
let idx = 0;
const positions = [];
while ((idx = c.indexOf('function mkCardPedido', idx)) !== -1) {
  positions.push(idx);
  idx += 'function mkCardPedido'.length;
}
console.log('mkCardPedido positions:', positions);

// Keep only the FIRST occurrence (which should be our enhanced version)
// Find where each function ends
if (positions.length > 1) {
  // Find the end of the SECOND function
  const secondFnStart = positions[1];
  const afterSecond = c.indexOf('function', secondFnStart + 10);
  console.log('Second fn starts at:', secondFnStart, 'next fn at:', afterSecond);
  
  // The second function goes from secondFnStart to 'next function start - some chars back'
  // Actually find the end } of the second function
  // Looking for the pattern: "...</div></div></div>";\n}"
  const endPat = '</div></div></div>";\n}';
  const endIdx2 = c.indexOf(endPat, secondFnStart);
  console.log('End pattern at:', endIdx2);
  
  if (endIdx2 > secondFnStart) {
    const toRemove = c.slice(secondFnStart - 1, endIdx2 + endPat.length);
    c = c.replace(toRemove, '');
    console.log('Removed duplicate mkCardPedido, new size:', c.length);
  }
}

// Now fix the status display - find the original mkCardPedido and update it
const mkStart = c.indexOf('function mkCardPedido');
const mkEnd = c.indexOf('function', mkStart + 50);
const mkContent = c.slice(mkStart, mkEnd);
console.log('mkContent (first 200):', JSON.stringify(mkContent.slice(0, 200)));

// Check what's in mkCardPedido now
console.log('mkContent includes statusPedido:', mkContent.includes('statusPedido'));
console.log('mkContent (last 200):', JSON.stringify(mkContent.slice(-200)));

// ════════════════════════════════════════════
// FIX 1: Ensure socket.on(pedidos) calls updateFilaCount
// ════════════════════════════════════════════
const socketOnPedidos = c.indexOf('socket.on("pedidos"');
console.log('socket.on(pedidos) at:', socketOnPedidos);
if (socketOnPedidos > 0) {
  const context = c.slice(socketOnPedidos, socketOnPedidos + 80);
  console.log('socket context:', JSON.stringify(context));
}

// ════════════════════════════════════════════
// FIX 2: loadConfig - find empresa save and add new fields
// ════════════════════════════════════════════
const svEmpIdx = c.indexOf('btn-sv-emp');
console.log('btn-sv-emp at:', svEmpIdx);
// Find the api POST call near it
const apiPostIdx = c.indexOf('api("POST","/api/config"', svEmpIdx - 100);
console.log('api POST config at:', apiPostIdx);
if (apiPostIdx > 0) {
  // Show the config save block
  const configBlockEnd = c.indexOf('});', apiPostIdx);
  console.log('Config block:', JSON.stringify(c.slice(apiPostIdx, configBlockEnd + 10)));
}

// ════════════════════════════════════════════
// FIX 3: btn-sv-emp handler - add new fields to save
// ════════════════════════════════════════════
const getHorarioIdx = c.indexOf('get("e-hor").value');
console.log('get("e-hor") at:', getHorarioIdx);
if (getHorarioIdx > 0) {
  console.log('Context:', JSON.stringify(c.slice(getHorarioIdx - 100, getHorarioIdx + 200)));
}

fs.writeFileSync('C:/casa/public/js/app.js', c, 'utf8');
console.log('After cleanup, size:', c.length);
