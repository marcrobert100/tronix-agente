const fs = require('fs');
let c = fs.readFileSync('C:/casa/public/js/app.js', 'utf8');
console.log('app.js size:', c.length);

// ═══════════════════════════════════════════════════
// 1. Update mkCardPedido to include status buttons
// ═══════════════════════════════════════════════════
const mkCardPedidoStart = c.indexOf('function mkCardPedido');
const mkCardPedidoEnd = c.indexOf('function', mkCardPedidoStart + 50);

// Find the closing of mkCardPedido: the backtick + closing `};`
// It ends with "</div></div></div>";}
const endMarker = '</div></div></div>";\n}';
const endIdx = c.indexOf(endMarker, mkCardPedidoStart);
console.log('mkCardPedido ends at:', endIdx);

// We need to add status display to mkCardPedido
// The function currently returns a div with class "pc"
// Let's find the return statement
const mkContent = c.slice(mkCardPedidoStart, endIdx + endMarker.length);
console.log('MK content (last 300):', JSON.stringify(mkContent.slice(-300)));

// We'll replace the whole mkCardPedido with an enhanced version
const STATUS_ORDER = ['recebido','preparando','saiu','entregue'];
const STATUS_LABELS_JS = `{recebido:"📋 Recebido",preparando:"👨‍🍳 Preparando",saiu:"🛵 Saiu",entregue:"✅ Entregue"}`;
const STATUS_COLORS_JS = `{recebido:"var(--bl)",preparando:"var(--am)",saiu:"var(--pu)",entregue:"var(--gr)"}`;

const newMkCardPedido = `function mkCardPedido(p) {
    const num=(p.numero||"").replace("@c.us","");
    const pid="pc-"+num.replace(/[^a-z0-9]/gi,"_");
    const maps=p.mapsUrl?\`<a href="\${p.mapsUrl}" target="_blank" class="btn btb btsm" style="margin-bottom:3px">🗺️ Mapa</a>\`:"";
    const comp=p.complemento?\`<div>🏠 \${esc(p.complemento)}</div>\`:"";
    const ref=p.referencia?\`<div>📌 \${esc(p.referencia)}</div>\`:"";
    const tel=p.telefone?\`<div>📞 \${esc(p.telefone)}</div>\`:"";
    const troco=p.troco?\`<div>💰 Troco R\$\${esc(p.troco)}</div>\`:"";
    const obs=p.observacao?\`<div>📝 \${esc(p.observacao)}</div>\`:"";
    const end=p.mapsUrl?\`📍 <span style="color:var(--bl)">GPS</span>\`:\`📍 \${esc(p.endereco||"—")}\`;

    // ── Status do Pedido ──
    const statusLabels = ${STATUS_LABELS_JS};
    const statusColors = ${STATUS_COLORS_JS};
    const statusOrder = ${JSON.stringify(STATUS_ORDER)};
    const statusAtual = p.statusPedido || "recebido";
    const statusLabel = statusLabels[statusAtual] || statusAtual;
    const statusColor = statusColors[statusAtual] || "var(--bl)";

    // Next status buttons
    const nextMap = {recebido:{next:"preparando",lbl:"👨‍🍳 Preparar"},preparando:{next:"saiu",lbl:"🛵 Saiu"},saiu:{next:"entregue",lbl:"✅ Entregar"},entregue:{next:null,lbl:null}};
    const next = nextMap[statusAtual];
    const btnNext = next && statusAtual !== "entregue"
      ? \`<button class="btn btp btsm" style="margin-top:6px" onclick="mudarStatusPedido('\${num}','\${next.next}')">\${next.lbl}</button>\`
      : statusAtual === "entregue"
        ? \`<button class="btn btg btsm" style="margin-top:6px" onclick="removerPedidoFinalizado('\${num}')">🗑️ Remover</button>\`
        : "";
    const isFlash = statusAtual !== "entregue";

    return \`<div class="pc\${isFlash ? ' flash' : ''}" id="\${pid}" data-num="\${num}">
      <div class="pc-tag" style="background:\${statusColor}">\${statusLabel}</div>
      <div class="pm">
        <div class="pnum">#\${p.numPedido}</div>
        <div class="pn">\${(p.endereco||"—").slice(0,30)}</div>
        <div class="pt">\${new Date(p.confirmado||p.inicio||Date.now()).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}</div>
      </div>
      <div class="pa">
        <div class="pb">
          <div class="pi">\${(p.itens||"").split(" | ").join("<br/>")}</div>
          <div class="pd">
            \${comp}\${ref}\${tel}\${obs}\${troco}<div>💳 \${esc(p.pagamento||"—")}</div>\${maps?\`<div style="margin-top:4px">\${maps}</div>\`:""}</div>
        </div>
        \${btnNext}
      </div>
    </div>\`;
}

window.mudarStatusPedido = async function(numero, novoStatus) {
    try {
        const r = await fetch("/api/pedidos/"+numero+"/status", {
            method: "POST",
            headers: { "Content-Type":"application/json","x-token":TK },
            body: JSON.stringify({ status: novoStatus })
        });
        if (r.ok) loadPedidos();
    } catch(e) { console.error(e); }
};

window.removerPedidoFinalizado = function(numero) {
    const card = document.getElementById("pc-"+numero.replace(/[^a-z0-9]/gi,"_"));
    if (card) card.remove();
};
`;

c = c.slice(0, mkCardPedidoStart) + newMkCardPedido + c.slice(endIdx + endMarker.length);
console.log('After mkCardPedido update, size:', c.length);

// ═══════════════════════════════════════════════════
// 2. Update loadPedidos to also update fila counter
// ═══════════════════════════════════════════════════
const loadPedidosIdx = c.indexOf('async function loadPedidos');
console.log('loadPedidos at:', loadPedidosIdx);
if (loadPedidosIdx > 0) {
  const afterLoadPedidos = c.indexOf('async function', loadPedidosIdx + 20);
  const loadPedidosContent = c.slice(loadPedidosIdx, afterLoadPedidos);
  console.log('loadPedidos content:', JSON.stringify(loadPedidosContent.slice(0, 200)));
}

// ═══════════════════════════════════════════════════
// 3. Add loadFila and update socket.on("pedidos") for fila
// ═══════════════════════════════════════════════════
// Find socket.on("pedidos") - it calls renderPedidos
const socketPedidos = c.indexOf('socket.on("pedidos"');
console.log('socket.on(pedidos) at:', socketPedidos);
if (socketPedidos > 0) {
  // Update it to also update fila
  const old = `socket.on("pedidos", ps => renderPedidos(ps));`;
  const neo = `socket.on("pedidos", ps => { renderPedidos(ps); updateFilaCount(ps); });
function updateFilaCount(ps) {
  const fi = document.getElementById("fila-info");
  if (fi) {
    const filaAtiva = ps.filter(p => (p.statusPedido || "recebido") !== "entregue").length;
    fi.style.display = filaAtiva > 0 ? "flex" : "none";
    const fc = document.getElementById("fila-count");
    if (fc) fc.textContent = filaAtiva;
  }
}`;
  if (c.includes(old)) {
    c = c.replace(old, neo);
    console.log('Updated socket.on(pedidos)');
  } else {
    console.log('Could not find exact socket.on(pedidos) call');
    // Try to find it
    const alt = c.slice(socketPedidos, socketPedidos + 100);
    console.log('Actual:', JSON.stringify(alt));
  }
}

// ═══════════════════════════════════════════════════
// 4. Load config for empresa tab — add horarioInicio/Fim and avaliacaoAtiva
// ═══════════════════════════════════════════════════
const loadConfigIdx = c.indexOf('async function loadConfig');
console.log('loadConfig at:', loadConfigIdx);
if (loadConfigIdx > 0) {
  const nextFn2 = c.indexOf('async function', loadConfigIdx + 20);
  const cfgContent = c.slice(loadConfigIdx, nextFn2);
  // Add fill for new fields
  const oldFillEmp = `fill("e-nome", cfg.empresaNome);
  fill("e-end", cfg.empresaEndereco);
  fill("e-tel", cfg.empresaTelefone);`;
  const newFillEmp = `fill("e-nome", cfg.empresaNome);
  fill("e-end", cfg.empresaEndereco);
  fill("e-tel", cfg.empresaTelefone);
  fill("e-hor-inicio", cfg.horarioInicio || "");
  fill("e-hor-fim", cfg.horarioFim || "");
  const togAval = document.getElementById("tog-avaliacao");
  if (togAval) togAval.checked = cfg.avaliacaoAtiva !== false;`;
  if (c.includes(oldFillEmp)) {
    c = c.replace(oldFillEmp, newFillEmp);
    console.log('Updated config fill for empresa');
  } else {
    console.log('Could not find empresa fill block');
  }
}

// ═══════════════════════════════════════════════════
// 5. Save empresa config — include new fields
// ═══════════════════════════════════════════════════
const svEmpBtn = c.indexOf('btn-sv-emp');
console.log('btn-sv-emp at:', svEmpBtn);
if (svEmpBtn > 0) {
  const nextSvEmp = c.indexOf('btn-sv-emp').toString();
  // Find the save handler
  const svEmpHandler = c.indexOf('btn-sv-emp').toString();
  // Find addEventListener for btn-sv-emp
  const addListener = c.indexOf('addEventListener("click",', svEmpBtn - 200);
  console.log('addEventListener near btn-sv-emp:', addListener);
  console.log(c.slice(addListener, addListener + 300));
}

// ═══════════════════════════════════════════════════
// 6. Load config for cardápio — add imagem field to modal
// ═══════════════════════════════════════════════════
// Find where item is populated for editing
const populateItemIdx = c.indexOf('mi-nome"');
console.log('mi-nome at:', populateItemIdx);
if (populateItemIdx > 0) {
  // Find the function that sets item values in edit modal
  const beforeMi = c.slice(populateItemIdx - 200, populateItemIdx + 50);
  console.log('Context around mi-nome:', JSON.stringify(beforeMi));
}

fs.writeFileSync('C:/casa/public/js/app.js', c, 'utf8');
console.log('app.js updated! Final size:', c.length);
