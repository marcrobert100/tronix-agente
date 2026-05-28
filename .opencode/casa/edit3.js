const fs = require('fs');
let c = fs.readFileSync('C:/casa/server.js', 'utf8');

// 1. Update /entregar route - keep pedido with status=saiu, not delete
const oldEntregar = `app.post("/api/pedidos/:num/entregar", guard, async (req, res) => {
  const { num } = req.params;
  if (!pedidosAbertos.has(num)) return res.status(404).json({ ok: false });
  const pedido = pedidosAbertos.get(num);
  pedidosAbertos.delete(num);
  io.emit("pedidos", listaPedidos());
  // Notificar cliente via WhatsApp
  if (waConectado && waClient && pedido) {
    try {
      const cfg = loadConfig();
      const tempo = cfg.tempoEntrega || "30-50 minutos";
      // Formatar itens com valor total (qtd × preço unitário)
      const itensFormatados = (pedido.itens||"").split(" | ").map(item => {
        const qtdMatch = item.match(/^(\\d+)x\\s+(.+?)\\s+—\\s+R\\$\\s*([\\d,.]+)/);
        if (qtdMatch) {
          const qtd   = parseInt(qtdMatch[1]);
          const nome  = qtdMatch[2];
          const prUni = parseFloat(qtdMatch[3].replace(",","."));
          const total = (prUni * qtd).toFixed(2).replace(".",".");
          return \`\${qtd}x \${nome} ............. R$ \${total}\`;
        }
        return \`   \${item}\`;
      }).join("\\n");
      // Calcular total dos itens para mostrar na entrega
      const subEnt  = calcularTotal(pedido.itens||"", cfg);
      const taxaEnt = parseFloat((cfg.taxaEntrega||"0").replace(/[^\\d,\\.]/g,"").replace(",",".")) || 0;
      const totEnt  = subEnt + taxaEnt;
      const totEntStr = totEnt > 0
        ? \`\\n💰 *Subtotal:* R$ \${subEnt.toFixed(2).replace(".",".")}\\n\` +
          \`🛵 *Taxa:* \${cfg.taxaEntrega||"—"}\\n\` +
          \`💵 *Total: R$ \${totEnt.toFixed(2).replace(".",".")}*\\n\`
        : "";

      const msg = (
        \`🛵💨 *SEU PEDIDO SAIU PARA ENTREGA!* 💨🛵\\n\\n\` +
        \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\` +
        \`📦 *Pedido Nº \${pedido.numPedido}*\\n\\n\` +
        \`🍽️ \${itensFormatados}\\n\` +
        \`\${totEntStr}\\n\` +
        \`⏱️ *Previsão de chegada:* \${tempo}\\n\` +
        \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n\` +
        \`👀 _Fique de olho! Está a caminho!_ 😊🔥\`
      );
      await waClient.sendMessage(num, msg);
      // Agendar avaliação pós-entrega (30 min)
      agendarAvaliacao(num, pedido);
    } catch(e) { console.error("[NOTIF]", e.message); }
  }
  res.json({ ok: true });
});`;

const newEntregar = `app.post("/api/pedidos/:num/entregar", guard, async (req, res) => {
  const { num } = req.params;
  if (!pedidosAbertos.has(num)) return res.status(404).json({ ok: false });
  const pedido = pedidosAbertos.get(num);

  // Atualizar status para "saiu"
  pedido.statusPedido = STATUS_PEDIDO.SAIU;
  io.emit("pedidos", listaPedidos());

  // Notificar cliente
  if (waConectado && waClient && pedido) {
    try {
      const cfg = loadConfig();
      const tempo = cfg.tempoEntrega || "30-50 minutos";
      const itensFormatados = (pedido.itens||"").split(" | ").map(item => {
        const qtdMatch = item.match(/^(\\d+)x\\s+(.+?)\\s+—\\s+R\\$\\s*([\\d,.]+)/);
        if (qtdMatch) {
          const qtd   = parseInt(qtdMatch[1]);
          const nome  = qtdMatch[2];
          const prUni = parseFloat(qtdMatch[3].replace(",","."));
          const total = (prUni * qtd).toFixed(2).replace(".",".");
          return \`\${qtd}x \${nome} ............. R$ \${total}\`;
        }
        return \`   \${item}\`;
      }).join("\\n");
      const subEnt  = calcularTotal(pedido.itens||"", cfg);
      const taxaEnt = parseFloat((cfg.taxaEntrega||"0").replace(/[^\\d,\\.]/g,"").replace(",",".")) || 0;
      const totEnt  = subEnt + taxaEnt;
      const totEntStr = totEnt > 0
        ? \`\\n💰 *Subtotal:* R$ \${subEnt.toFixed(2).replace(".",".")}\\n\` +
          \`🛵 *Taxa:* \${cfg.taxaEntrega||"—"}\\n\` +
          \`💵 *Total: R$ \${totEnt.toFixed(2).replace(".",".")}*\\n\`
        : "";

      const msg = (
        \`🛵💨 *SEU PEDIDO SAIU PARA ENTREGA!* 💨🛵\\n\\n\` +
        \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\` +
        \`📦 *Pedido Nº \${pedido.numPedido}*\\n\\n\` +
        \`🍽️ \${itensFormatados}\\n\` +
        \`\${totEntStr}\\n\` +
        \`⏱️ *Previsão de chegada:* \${tempo}\\n\` +
        \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n\` +
        \`👀 _Fique de olho! Está a caminho!_ 😊🔥\`
      );
      await waClient.sendMessage(num, msg);

      // Só agenda avaliação se estiver ativa
      if (config.avaliacaoAtiva !== false) {
        agendarAvaliacao(num, pedido);
      }
    } catch(e) { console.error("[NOTIF]", e.message); }
  }
  res.json({ ok: true });
});`;

const hasOld = c.includes(oldEntregar);
console.log('Has old /entregar:', hasOld);
if (hasOld) {
  c = c.replace(oldEntregar, newEntregar);
}

// 2. Also add "imagem" to the produto/tempo route
const oldTempo = `// ── PRODUTO: tempo de preparo ──`;
const newTempo = `// ── PRODUTO: tempo de preparo ──
// Also supports setting imagem field

`;

if (c.includes(oldTempo) && !c.includes('app.post("/api/produto/tempo"')) {
  // Find the route
  const tempoIdx = c.indexOf(oldTempo);
  console.log('tempo route found at:', tempoIdx);
}

console.log('Script done. Size:', c.length);
fs.writeFileSync('C:/casa/server.js', c, 'utf8');
