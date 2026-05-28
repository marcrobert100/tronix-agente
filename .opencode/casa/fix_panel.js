const fs = require('fs');
let c = fs.readFileSync('C:/casa/public/painel.html', 'utf8');

console.log('File size:', c.length);

// ════════════════════════════════════════════════════════════════════
// FEAT 2: Cardápio com fotos — add imagem field to modal-item
// ════════════════════════════════════════════════════════════════════
const miTamEnd = c.indexOf('id="mi-tam"') + 300;
const insertImgField = `    <div class="fg"><label>📷 Imagem (URL)</label><input class="inp" id="mi-img" placeholder="https://..."/><div style="font-size:.72rem;color:var(--mu);margin-top:4px">Cole uma URL de imagem ou deixe vazio.</div></div>
    `;
c = c.slice(0, miTamEnd) + insertImgField + c.slice(miTamEnd);
console.log('After imagem field, size:', c.length);

// ════════════════════════════════════════════════════════════════════
// FEAT 3: Horário Automático — add horarioInicio/horarioFim in Empresa tab
// ════════════════════════════════════════════════════════════════════
const ePixEnd = c.indexOf('id="e-pix"') + 200;
const insertHorarios = `            <div class="fg"><label>🕐 Horário de Abertura</label><input class="inp" id="e-hor-inicio" placeholder="08:00" type="time"/></div>
            <div class="fg"><label>🕐 Horário de Fechamento</label><input class="inp" id="e-hor-fim" placeholder="22:00" type="time"/></div>
            <div style="grid-column:1/-1;font-size:.73rem;color:var(--mu);padding:6px 0">
              💡 Se preenchido, o bot só atende dentro desse horário. Deixe vazio para funcionar 24h.
            </div>
            `;
c = c.slice(0, ePixEnd) + insertHorarios + c.slice(ePixEnd);
console.log('After horario fields, size:', c.length);

// ════════════════════════════════════════════════════════════════════
// FEAT 4: Avaliação Toggle — add in empresa tab after e-hor-fim
// ════════════════════════════════════════════════════════════════════
// Find the toast for empresa
const tEmpToast = c.indexOf('id="t-emp"');
// Insert avaliação toggle before t-emp toast (which is inside card)
const avaliacaoToggle = `          <div class="trow"><span>⭐ Avaliação pós-entrega</span><label class="tog"><input type="checkbox" id="tog-avaliacao" checked/><span class="tsl"></span></label></div>
          <div style="font-size:.73rem;color:var(--mu);margin-bottom:12px">
            Quando ativo, o cliente recebe pedido para avaliar após a entrega.
          </div>
          `;
c = c.slice(0, tEmpToast) + avaliacaoToggle + c.slice(tEmpToast);
console.log('After avaliacao toggle, size:', c.length);

// ════════════════════════════════════════════════════════════════════
// FEAT 1+5: Status do Pedido + Fila — update Pedidos tab
// Find the pedidos tab content area
// ════════════════════════════════════════════════════════════════════
const listaPedEnd = c.indexOf('id="lista-ped"') + 50;
const insertPedidosControls = `<div id="fila-info" style="margin-bottom:14px;padding:10px 14px;background:var(--bg3);border:1px solid var(--brd);border-radius:8px;font-size:.82rem;color:var(--mu);display:none">
  📋 <strong style="color:var(--tx)">Fila de pedidos:</strong> <span id="fila-count">0</span> pendente(s)
</div>
<div id="lista-ped"><div class="fe">Nenhum pedido em aberto.</div></div>`;
// Actually, find the lista-ped div more carefully
const listaPedStart = c.indexOf('<div id="lista-ped">');
const listaPedEnd2 = c.indexOf('</div>', listaPedStart + 30);
console.log('lista-ped spans:', listaPedStart, 'to', listaPedEnd2);
// Replace the lista-ped div content
const oldListaPed = c.slice(listaPedStart, listaPedEnd2 + 6);
console.log('oldListaPed:', JSON.stringify(oldListaPed.slice(0, 100)));

const newListaPedSection = `<div id="fila-info" style="margin-bottom:14px;padding:10px 14px;background:var(--bg3);border:1px solid var(--brd);border-radius:8px;font-size:.82rem">
  📋 <strong style="color:var(--tx)">Fila:</strong> <span id="fila-count" style="color:var(--ac);font-weight:700">0</span> pedido(s) pendente(s)
</div>
<div id="lista-ped"><div class="fe">Nenhum pedido em aberto.</div></div>`;
c = c.replace(oldListaPed, newListaPedSection);
console.log('After fila-info, size:', c.length);

// ════════════════════════════════════════════════════════════════════
// Add JS for status buttons in pedido cards
// Find the app.js script area (before </body>) to add new JS
// ════════════════════════════════════════════════════════════════════
const bodyEnd = c.lastIndexOf('</body>');
const jsInjection = `

// ═══════════════════════════════════════════════════
//  FEAT 1: STATUS DO PEDIDO — botões no painel
// ═══════════════════════════════════════════════════
const STATUS_LABELS = {
  recebido:   "📋 Recebido",
  preparando: "👨‍🍳 Preparando",
  saiu:      "🛵 Saiu",
  entregue:  "✅ Entregue"
};
const STATUS_COLORS = {
  recebido:   "var(--bl)",
  preparando: "var(--am)",
  saiu:      "var(--pu)",
  entregue:  "var(--gr)"
};
const STATUS_ORDER = ["recebido","preparando","saiu","entregue"];

function renderPedidoCard(p) {
  const status = p.statusPedido || "recebido";
  const statusColor = STATUS_COLORS[status] || "var(--bl)";
  const statusLabel = STATUS_LABELS[status] || status;

  const nextStatuses = {
    recebido:   { next: "preparando", label: "👨‍🍳 Preparar" },
    preparando: { next: "saiu",       label: "🛵 Saiu" },
    saiu:       { next: "entregue",   label: "✅ Entregar" },
    entregue:   { next: null,         label: null }
  };
  const next = nextStatuses[status];

  const items = (p.itens||"").split(" | ").join("<br/>");

  const isEntregue = status === "entregue";

  return \`<div class="pc\${isEntregue ? '' : ' flash'}" id="pc-\${p.numero}" data-num="\${p.numero}">
    <div class="pc-tag">\${statusLabel}</div>
    <div class="pm">
      <div class="pnum">#\${p.numPedido}</div>
      <div class="pn">\${(p.endereco||"—").slice(0,30)}</div>
      <div class="pt">\${new Date(p.confirmado||p.inicio||Date.now()).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}</div>
    </div>
    <div class="pa">
      <div class="pb">
        <div class="pi">\${items}</div>
        <div class="pd">
          <div>💳 \${p.pagamento||"—"} \${p.troco ? '| Troco: R$ '+p.troco : ''}</div>
          <div>📍 \${(p.endereco||"—").slice(0,40)}</div>
          \${p.telefone ? '<div>📞 '+p.telefone+'</div>' : ''}
        </div>
      </div>
      \${next && !isEntregue ? \`<button class="btn btp btsm" style="margin-top:6px" onclick="mudarStatusPedido('\${p.numero}','\${next.next}')">\${next.label}</button>\` : ''}
      \${isEntregue ? \`<button class="btn btg btsm" style="margin-top:6px" onclick="removerPedidoFinalizado('\${p.numero}')">🗑️ Remover</button>\` : ''}
    </div>
  </div>\`;
}

async function mudarStatusPedido(numero, novoStatus) {
  try {
    const r = await fetch("/api/pedidos/"+numero+"/status", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-token": token },
      body: JSON.stringify({ status: novoStatus })
    });
    if (r.ok) {
      loadPedidos();
      const card = document.getElementById("pc-"+numero);
      if (card) {
        const label = STATUS_LABELS[novoStatus] || novoStatus;
        const tag = card.querySelector(".pc-tag");
        if (tag) { tag.textContent = label; tag.style.background = STATUS_COLORS[novoStatus] || "var(--bl)"; }
        // Hide the button that was just clicked
        const btn = card.querySelector("button");
        if (btn) btn.remove();
      }
    }
  } catch(e) { console.error(e); }
}

async function removerPedidoFinalizado(numero) {
  // Simply remove from UI (the pedido stays in vendas.json)
  const card = document.getElementById("pc-"+numero);
  if (card) card.remove();
  loadPedidos();
}

// ═══════════════════════════════════════════════════
//  FEAT 5: FILA — atualizar info de fila
// ═══════════════════════════════════════════════════
async function loadFila() {
  try {
    const r = await fetch("/api/fila", { headers: { "x-token": token } });
    if (r.ok) {
      const d = await r.json();
      const fi = document.getElementById("fila-info");
      if (fi) {
        fi.style.display = d.fila > 0 ? "flex" : "none";
        const fc = document.getElementById("fila-count");
        if (fc) fc.textContent = d.fila;
      }
    }
  } catch(e) {}
}

`;

c = c.slice(0, bodyEnd) + jsInjection + c.slice(bodyEnd);
console.log('After JS injection, size:', c.length);

// ════════════════════════════════════════════════════════════════════
// Update loadPedidos() in app.js to use new card renderer
// ════════════════════════════════════════════════════════════════════
// Find the socket.on for "pedidos" in the HTML
const pedidosOnIdx = c.indexOf('socket.on("pedidos"');
console.log('socket.on(pedidos) at:', pedidosOnIdx);
if (pedidosOnIdx > 0) {
  // Show context
  console.log('Context:', JSON.stringify(c.slice(pedidosOnIdx, pedidosOnIdx + 300)));
}

fs.writeFileSync('C:/casa/public/painel.html', c, 'utf8');
console.log('Panel updated! Final size:', c.length);
