// Script para editar server.js
const fs = require('fs');
let c = fs.readFileSync('C:/casa/server.js', 'utf8');

const marker = '// ── Acompanhar pedido ──';
const idx = c.indexOf(marker);
console.log('Marker at:', idx);

// Inserir ANTES do marker
const inject = `  // ════════════════════════════════════════════════════
  //  FEAT 1: STATUS DO PEDIDO
  // ════════════════════════════════════════════════════
  if (!estadosPedido.has(numero)) {
    const sLowSt = txt.trim().toLowerCase();
    const querStatus = ["meu pedido","ver status","status","status do pedido",
      "como está meu pedido","onde está meu pedido","situação","situacao"
    ].some(g => sLowSt.includes(g));

    if (querStatus) {
      let encontrado = null;
      for (const [num, p] of pedidosAbertos) {
        if (num === numero || num.replace(/[^0-9]/g,"").includes(numero.replace(/[^0-9]/g,"").slice(-8))) {
          encontrado = { numero: num, ...p }; break;
        }
      }
      if (encontrado) {
        const statusAtual = encontrado.statusPedido || STATUS_PEDIDO.RECEBIDO;
        const statusLabel = labelStatus(statusAtual);
        const hora = new Date(encontrado.confirmado || encontrado.inicio)
          .toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
        const posicao = posicaoNaFila(encontrado.numero);
        const posStr = (posicao !== null && posicao > 0)
          ? "\n📋 *Posição na fila:* "+posicao+" pedido(s) antes" : "";
        resp = (
          "📦 *Pedido Nº "+encontrado.numPedido+"*\n" +
          "🚦 *Status:* "+statusLabel+"\n" +
          "🛒 *Itens:* "+encontrado.itens+"\n" +
          "📍 *Endereço:* "+(encontrado.endereco || "—")+"\n" +
          "💳 *Pagamento:* "+(encontrado.pagamento || "—")+"\n" +
          "⏱️ *Confirmado às:* "+hora+posStr+"\n\n" +
          "_Dúvida? Chame um atendente!_ 😊"
        );
        await responderHumano(chat, msg, resp);
        logC({ tipo:"saida", para:numero, mensagem:resp });
        io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
        return;
      }
    }

    // FEAT 5: FILA
    const querFila = ["fila","quantos pedidos","posição","posicao na fila",
      "pedidos na frente","quantos na frente","na fila"
    ].some(g => sLowSt.includes(g));

    if (querFila) {
      const fila = listaPedidos().filter(p =>
        (p.statusPedido || STATUS_PEDIDO.RECEBIDO) !== STATUS_PEDIDO.ENTREGUE
      );
      if (fila.length === 0) {
        resp = "🎉 *Não há pedidos na fila!*\n\nTodos entregues.\nSeja o primeiro! 😊";
      } else {
        resp = "📋 *Fila de pedidos:*\n\n🛒 *"+fila.length+" pedido(s) pendente(s)*\n\n";
        fila.slice(0, 5).forEach((p, i) => {
          resp += (i+1)+". #"+p.numPedido+" — "+labelStatus(p.statusPedido || STATUS_PEDIDO.RECEBIDO)+"\n";
        });
        if (fila.length > 5) resp += "\n...e mais "+(fila.length - 5)+" pedido(s)";
        resp += "\n\n_Seu pedido pode ser o próximo!_ 😊";
      }
      await responderHumano(chat, msg, resp);
      logC({ tipo:"saida", para:numero, mensagem:resp });
      io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
      return;
    }
  }

`;

// Injetar ANTES do marker
c = c.slice(0, idx) + inject + c.slice(idx);

fs.writeFileSync('C:/casa/server.js', c, 'utf8');
console.log('Edit done! File written.');
console.log('New size:', c.length);
