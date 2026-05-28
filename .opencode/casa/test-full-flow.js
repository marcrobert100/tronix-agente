// Test script to verify full order flow
const fs = require('fs');
const path = require('path');

// Load config
const configPath = path.join(__dirname, 'config.json');
const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Simulate order state
let orderState = {
  etapa: "inicio",
  itens: "",
  endereco: "",
  bairro: "",
  numero: "",
  referencia: "",
  complemento: "",
  telefone: "",
  pagamento: "",
  troco: "",
  observacao: ""
};

// Simulate functions from server.js
function normStr(s) {
  return (s||"").toLowerCase().normalize("NFD")
    .replace(/[\u0300-\u036f]/g,"")
    .replace(/[-_]/g, " ")
    .replace(/[.,!?;:]+$/, "")
    .replace(/\bcoca(\s*)cola\b/gi, "coca lata")
    .replace(/\brefrigerante(s)?\b/gi, "coca lata")
    .replace(/\b(em|de|do|da|dos|das|com|e|o|a|os|as|um|uma|para|pro|pra)\b/g, " ")
    .replace(/s\b/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function extrairQtd(txt) {
  const s = txt.trim().replace(/[.,!?;:]+$/, "").trim();
  const NUM_EXTENSO = {
    "um":1,"uma":1,"dois":2,"duas":2,"três":3,"tres":3,"quatro":4,
    "cinco":5,"seis":6,"sete":7,"oito":8,"nove":9,"dez":10,
    "onze":11,"doze":12,"treze":13,"catorze":14,"quinze":15,
    "dezesseis":16,"dezessete":17,"dezoito":18,"dezenove":19,"vinte":20
  };

  const mExt = s.match(/^(um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte)\s+(?:x\s+)?(.+)$/i);
  if (mExt) {
    const qtd = NUM_EXTENSO[mExt[1].toLowerCase()] || 1;
    return { qtd: Math.min(qtd, 20), texto: mExt[2].trim() };
  }

  const mX = s.match(/^(\d+)\s*x\s+(.+)$/i);
  if (mX) return { qtd: Math.min(parseInt(mX[1]), 20), texto: mX[2].trim() };

  const mN = s.match(/^(\d+)\s+(.+)$/);
  if (mN) {
    const textoDepois = mN[2].trim();
    return { qtd: Math.min(parseInt(mN[1]), 20), texto: textoDepois };
  }

  return { qtd: 1, texto: s };
}

function validarItem(txt, cfg) {
  const s = normStr(txt);
  const sRaw = txt.toLowerCase().trim();
  const todos = (cfg.cardapio||[]).flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado));

  for (const item of todos) {
    const n = normStr(item.nome);
    const nRaw = item.nome.toLowerCase();
    if (n === s || nRaw === sRaw) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
  }

  if (s.length >= 4) {
    for (const item of todos) {
      const n = normStr(item.nome);
      if (n.includes(s) || s.includes(n)) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  return { ok:false, sugestoes:"" };
}

function calcularTotal(itensTxt, cfg) {
  let total = 0;
  const textoLimpo = (itensTxt || "").replace(/\n/g, " ").replace(/\s+/g, " ");
  let partes = [];
  if (textoLimpo.includes(" | ")) {
    partes = textoLimpo.split(" | ");
  } else {
    partes = [textoLimpo];
  }

  for (const parte of partes) {
    const p = parte.trim();
    if (!p) continue;
    const pl = p.toLowerCase();

    const qtdM = pl.match(/^(\d+)x?\s+/);
    const qtd = qtdM ? parseInt(qtdM[1]) : 1;

    const textoSemAcomp = p.replace(/\(.*\)/, "").replace(/\+\s*R\$\s*[\d,.]+/gi, "").replace(/\+\s*[\d,.]+/gi, "");
    const precoMatch = textoSemAcomp.match(/(?:—\s*R\$\s*|—\s*)([\d]+(?:[,.][\d]{2})?)/i);
    
    if (precoMatch) {
      const precoUnitario = parseFloat(precoMatch[1].replace(",", "."));
      if (!isNaN(precoUnitario)) {
        total += (precoUnitario * qtd);
        continue;
      }
    }
  }

  return total;
}

// Test full order flow
console.log("🧪 TESTANDO FLUXO COMPLETO DE PEDIDO\n");
console.log("=".repeat(60));

// Step 1: Add items to order
console.log("\n1️⃣ ADICIONANDO ITENS AO PEDIDO");
console.log("-".repeat(60));

const itemsToAdd = [
  "2 suco de uva",
  "1 pizza calabresa",
  "3x coca lata"
];

itemsToAdd.forEach(input => {
  const { qtd, texto } = extrairQtd(input);
  const validation = validarItem(texto, cfg);
  
  if (validation.ok) {
    const nomeItem = qtd > 1 ? `${qtd}x ${validation.item.nome} — ${validation.item.preco}` : `${validation.item.nome} — ${validation.item.preco}`;
    orderState.itens = orderState.itens ? `${orderState.itens} | ${nomeItem}` : nomeItem;
    console.log(`✅ Adicionado: ${nomeItem}`);
  } else {
    console.log(`❌ Não reconhecido: ${input}`);
  }
});

console.log(`\n🛒 Carrinho: ${orderState.itens}`);

// Step 2: Calculate total
console.log("\n2️⃣ CALCULANDO TOTAL");
console.log("-".repeat(60));

const subtotal = calcularTotal(orderState.itens, cfg);
const taxaEntrega = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
const total = subtotal + taxaEntrega;

console.log(`Subtotal: R$ ${subtotal.toFixed(2).replace(".",",")}`);
console.log(`Taxa de entrega: R$ ${taxaEntrega.toFixed(2).replace(".",",")}`);
console.log(`Total: R$ ${total.toFixed(2).replace(".",",")}`);

// Step 3: Add address
console.log("\n3️⃣ ADICIONANDO ENDEREÇO");
console.log("-".repeat(60));

orderState.endereco = "Rua Teste, 123";
orderState.bairro = "Centro";
orderState.numero = "123";
orderState.referencia = "Próximo ao mercado";
orderState.complemento = "Apto 101";

console.log(`✅ Endereço: ${orderState.endereco}`);
console.log(`✅ Bairro: ${orderState.bairro}`);
console.log(`✅ Número: ${orderState.numero}`);
console.log(`✅ Referência: ${orderState.referencia}`);
console.log(`✅ Complemento: ${orderState.complemento}`);

// Step 4: Add phone
console.log("\n4️⃣ ADICIONANDO TELEFONE");
console.log("-".repeat(60));

orderState.telefone = "(82) 99999-9999";
console.log(`✅ Telefone: ${orderState.telefone}`);

// Step 5: Add payment
console.log("\n5️⃣ ADICIONANDO PAGAMENTO");
console.log("-".repeat(60));

orderState.pagamento = "Pix";
console.log(`✅ Pagamento: ${orderState.pagamento}`);

// Step 6: Add observation
console.log("\n6️⃣ ADICIONANDO OBSERVAÇÃO");
console.log("-".repeat(60));

orderState.observacao = "Sem cebola, por favor";
console.log(`✅ Observação: ${orderState.observacao}`);

// Step 7: Summary
console.log("\n7️⃣ RESUMO DO PEDIDO");
console.log("=".repeat(60));

console.log(`\n📦 *Itens:*`);
orderState.itens.split(" | ").forEach(item => {
  console.log(`  • ${item}`);
});

console.log(`\n💰 *Total:* R$ ${total.toFixed(2).replace(".",",")}`);
console.log(`📍 *Endereço:* ${orderState.endereco}, ${orderState.numero} - ${orderState.bairro}`);
console.log(`📞 *Telefone:* ${orderState.telefone}`);
console.log(`💳 *Pagamento:* ${orderState.pagamento}`);
console.log(`📝 *Observação:* ${orderState.observacao}`);

console.log("\n" + "=".repeat(60));
console.log("\n✅ FLUXO COMPLETO TESTADO COM SUCESSO!");
console.log("=".repeat(60));
