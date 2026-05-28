// Test script to simulate "2 suco de uva" order
const fs = require('fs');
const path = require('path');

// Load config
const configPath = path.join(__dirname, 'config.json');
const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Simulate normStr function
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

// Simulate extrairQtd function
function extrairQtd(txt) {
  const s = txt.trim().replace(/[.,!?;:]+$/, "").trim();
  const mN = s.match(/^(\d+)\s+(.+)$/);
  if (mN) {
    const textoDepois = mN[2].trim();
    return { qtd: Math.min(parseInt(mN[1]), 20), texto: textoDepois };
  }
  return { qtd: 1, texto: s };
}

// Simulate validarItem function (simplified)
function validarItem(txt, cfg) {
  const s = normStr(txt);
  const todos = (cfg.cardapio||[]).flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado));

  // 1. Match exato (com e sem normalização)
  for (const item of todos) {
    const n = normStr(item.nome);
    if (n === s) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
  }

  // 1b. Substring — normalizado
  if (s.length >= 4) {
    for (const item of todos) {
      const n = normStr(item.nome);
      if (n.includes(s) || s.includes(n)) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  return { ok:false, sugestoes:"" };
}

// Test the flow
const input = "2 suco de uva";
console.log("Input:", input);

const { qtd, texto } = extrairQtd(input);
console.log("ExtrairQtd result:", { qtd, texto });

const validation = validarItem(texto, cfg);
console.log("ValidarItem result:", validation);

if (validation.ok) {
  console.log("\n✅ Item reconhecido!");
  console.log("Item:", validation.item.nome);
  console.log("Preço:", validation.item.preco);
  console.log("Quantidade:", qtd);
  console.log("Formato final:", `${qtd}x ${validation.item.nome} — ${validation.item.preco}`);
} else {
  console.log("\n❌ Item não reconhecido");
  console.log("Sugestões:", validation.sugestoes);
}
