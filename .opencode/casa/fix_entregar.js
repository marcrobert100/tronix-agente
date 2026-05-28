const fs = require('fs');
let c = fs.readFileSync('C:/casa/server.js', 'utf8');

// The /entregar route - find its full extent
const marker = 'app.post("/api/pedidos/:num/entregar"';
const idx = c.indexOf(marker);
const endMarker = 'res.json({ ok: true });\n});';
const endIdx = c.indexOf(endMarker, idx + 1000);
const routeEnd = endIdx + endMarker.length;
console.log('Route spans:', idx, 'to', routeEnd);

const oldRoute = c.slice(idx, routeEnd);
console.log('Old route length:', oldRoute.length);

// New route: keep pedido with status=saiu, respect avaliacaoAtiva
const newRoute = `app.post("/api/pedidos/:num/entregar", guard, async (req, res) => {
  const { num } = req.params;
  if (!pedidosAbertos.has(num)) return res.status(404).json({ ok: false });
  const pedido = pedidosAbertos.get(num);

  // Atualizar status para saida (não remove da lista)
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
          return qtd+"x "+nome+" — R$ "+total;
        }
        return item;
      }).join("\\n🍽️ ");
      const subEnt  = calcularTotal(pedido.itens||"", cfg);
      const taxaEnt = parseFloat((cfg.taxaEntrega||"0").replace(/[^\\d,\\.]/g,"").replace(",",".")) || 0;
      const totEnt  = subEnt + taxaEnt;
      const totEntStr = totEnt > 0
        ? "\\n💰 *Subtotal:* R$ "+subEnt.toFixed(2).replace(".",".")+"\\n" +
          "\\n🛵 *Taxa:* "+(cfg.taxaEntrega||"—")+"\\n" +
          "\\n💵 *Total: R$ "+totEnt.toFixed(2).replace(".",".")+"*\\n"
        : "";

      const msg = (
        "\\n🛵💨 *SEU PEDIDO SAIU PARA ENTREGA!* 💨🛵\\n\\n" +
        "\\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n" +
        "\\n📦 *Pedido Nº "+pedido.numPedido+"*\\n\\n" +
        "\\n🍽️ "+itensFormatados+"\\n" +
        totEntStr+
        "\\n⏱️ *Previsão de chegada:* "+tempo+"\\n" +
        "\\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n" +
        "\\n👀 _Fique de olho! Está a caminho!_ 😊🔥"
      );
      await waClient.sendMessage(num, msg);

      // Agendar avaliação apenas se estiver ativa
      if (config.avaliacaoAtiva !== false) {
        agendarAvaliacao(num, pedido);
      }
    } catch(e) { console.error("[NOTIF]", e.message); }
  }
  res.json({ ok: true });
});
`;

c = c.slice(0, idx) + newRoute + c.slice(routeEnd);
fs.writeFileSync('C:/casa/server.js', c, 'utf8');
console.log('Done! New size:', c.length);
