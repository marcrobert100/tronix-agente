const fs = require('fs');
let c = fs.readFileSync('C:/casa/public/js/app.js', 'utf8');
console.log('Before cleanup, size:', c.length);

// Remove duplicate mkCardPedido (second occurrence at 27872)
// The second mkCardPedido goes from 27872 to before the next function
// We found it ends somewhere before 29316
// Let's find the exact end
const secondStart = 27872;
const afterSecond = c.indexOf('function', secondStart + 10);
// Find the closing } of the second function by looking for the pattern
// The second function is the OLD version, ends with "</div></div></div>";}
const endMarker = '</div></div></div>";\n}';
let endIdx2 = c.indexOf(endMarker, secondStart);
console.log('End marker at:', endIdx2);

if (endIdx2 > secondStart) {
  const toRemove = c.slice(secondStart - 1, endIdx2 + endMarker.length);
  c = c.replace(toRemove, '');
  console.log('Removed duplicate mkCardPedido, new size:', c.length);
} else {
  // Try alternate end marker
  const altEnd = 'pc-tag\')+">"+"</div>';
  const altIdx = c.indexOf(altEnd, secondStart);
  console.log('Alt end marker at:', altIdx);
  if (altIdx > secondStart) {
    const toRemove = c.slice(secondStart - 1, altIdx + altEnd.length);
    c = c.replace(toRemove, '');
    console.log('Removed using alt marker, new size:', c.length);
  }
}

// ════════════════════════════════════════════
// ADD empresa save new fields
// ════════════════════════════════════════════
const apiPostIdx = c.indexOf('api("POST","/api/config"');
if (apiPostIdx > 0) {
  const oldSave = `pixChave:get("e-pix").value
  });`;
  const newSave = `pixChave:get("e-pix").value,
    horarioInicio:get("e-hor-inicio").value,
    horarioFim:get("e-hor-fim").value,
    avaliacaoAtiva:document.getElementById("tog-avaliacao").checked
  });`;
  if (c.includes(oldSave)) {
    c = c.replace(oldSave, newSave);
    console.log('Added new fields to empresa save');
  } else {
    console.log('Could not find empresa save block');
    // Try to show what comes after pixChave
    const pixIdx = c.indexOf('pixChave:get("e-pix")');
    console.log('pixChave context:', JSON.stringify(c.slice(pixIdx, pixIdx + 200)));
  }
}

// ════════════════════════════════════════════
// ADD loadConfig fills for new empresa fields
// ════════════════════════════════════════════
const empresaPhoneFill = 'fill("e-tel", cfg.empresaTelefone);';
if (c.includes(empresaPhoneFill)) {
  const newFill = `fill("e-tel", cfg.empresaTelefone);
  fill("e-hor-inicio", cfg.horarioInicio || "");
  fill("e-hor-fim", cfg.horarioFim || "");
  const togAval = document.getElementById("tog-avaliacao");
  if (togAval) togAval.checked = cfg.avaliacaoAtiva !== false;`;
  c = c.replace(empresaPhoneFill, newFill);
  console.log('Added config fills for new fields');
}

// ════════════════════════════════════════════
// ADD imagem field to item edit modal
// ════════════════════════════════════════════
// Find the edit item function - it sets mi-nome, mi-cat etc.
const editItemFill = `get("mi-tam").value=item.tamanhos||"";`;
if (c.includes(editItemFill)) {
  const newFill = `get("mi-tam").value=item.tamanhos||"";
  get("mi-img").value=item.imagem||"";`;
  c = c.replace(editItemFill, newFill);
  console.log('Added imagem to item edit');
}

// Find novo item (clean form) - after mi-tam clean
const miTamClean = 'get("mi-tam").value="";\n  get("mi-acomp").value=""';
if (c.includes(miTamClean)) {
  const newClean = `get("mi-tam").value="";
  get("mi-img").value="";
  get("mi-acomp").value=""`;
  c = c.replace(miTamClean, newClean);
  console.log('Added imagem clean in novo item');
}

// Find item save API call and add imagem field
const itemSavePost = `api("POST","/api/cardapio/item",{`;
if (c.includes(itemSavePost)) {
  const afterItemCat = `categoria:get("mi-cat").value,
    nome:get("mi-nome").value,
    descricao:get("mi-desc").value,
    preco:get("mi-preco").value,
    tamanhos:get("mi-tam").value,
    maxAcomp:get("mi-acomp").value`;
  const newItemFields = `categoria:get("mi-cat").value,
    nome:get("mi-nome").value,
    descricao:get("mi-desc").value,
    preco:get("mi-preco").value,
    tamanhos:get("mi-tam").value,
    maxAcomp:get("mi-acomp").value,
    imagem:get("mi-img").value`;
  if (c.includes(afterItemCat)) {
    c = c.replace(afterItemCat, newItemFields);
    console.log('Added imagem to POST /api/cardapio/item');
  }
}

// PUT (edit) item also needs imagem
const itemPutPost = `api("PUT","/api/cardapio/item",{`;
if (c.includes(itemPutPost)) {
  const putFields = `nome:get("mi-nome").value,
    descricao:get("mi-desc").value,
    preco:get("mi-preco").value,
    tamanhos:get("mi-tam").value,
    maxAcomp:get("mi-acomp").value`;
  const newPutFields = `nome:get("mi-nome").value,
    descricao:get("mi-desc").value,
    preco:get("mi-preco").value,
    tamanhos:get("mi-tam").value,
    maxAcomp:get("mi-acomp").value,
    imagem:get("mi-img").value`;
  if (c.includes(putFields)) {
    c = c.replace(putFields, newPutFields);
    console.log('Added imagem to PUT /api/cardapio/item');
  }
}

// ════════════════════════════════════════════
// ADD loadFila to panel tab navigation
// ════════════════════════════════════════════
// Find the tab navigation click handler
const tabClickNav = `if (tab==="logs") loadLogs();`;
if (c.includes(tabClickNav)) {
  const newNav = `if (tab==="logs") loadLogs();
    if (tab==="pedidos") { loadPedidos(); loadFila(); }`;
  c = c.replace(tabClickNav, newNav);
  console.log('Added loadFila to tab navigation');
}

// Add loadFila function definition
const renderPedidosIdx = c.indexOf('function renderPedidos');
if (renderPedidosIdx > 0 && !c.includes('function loadFila')) {
  const loadFilaDef = `
// ── Fila de pedidos ──
function loadFila() {
  fetch("/api/fila", { headers: { "x-token": TK } })
    .then(r => r.json())
    .then(d => {
      const fi = document.getElementById("fila-info");
      if (fi) { fi.style.display = d.fila > 0 ? "flex" : "none"; const fc = document.getElementById("fila-count"); if (fc) fc.textContent = d.fila; }
    }).catch(() => {});
}
`;
  c = c.slice(0, renderPedidosIdx) + loadFilaDef + c.slice(renderPedidosIdx);
  console.log('Added loadFila function');
}

fs.writeFileSync('C:/casa/public/js/app.js', c, 'utf8');
console.log('Final app.js size:', c.length);

// Verify
const c2 = fs.readFileSync('C:/casa/public/js/app.js', 'utf8');
console.log('Verification - mkCardPedido count:', (c2.match(/function mkCardPedido/g)||[]).length);
console.log('Has updateFilaCount:', c2.includes('updateFilaCount'));
console.log('Has loadFila:', c2.includes('function loadFila'));
console.log('Has mi-img fill:', c2.includes('get("mi-img").value'));
