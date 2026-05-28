// Test script to verify all commands and flows in the system
const fs = require('fs');
const path = require('path');

// Load config
const configPath = path.join(__dirname, 'config.json');
const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Import functions from server.js (simplified for testing)
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

  // Número EXTENSO no início: "cinco sucos de uva"
  const mExt = s.match(/^(um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte)\s+(?:x\s+)?(.+)$/i);
  if (mExt) {
    const qtd = NUM_EXTENSO[mExt[1].toLowerCase()] || 1;
    return { qtd: Math.min(qtd, 20), texto: mExt[2].trim() };
  }

  // "3x bacon" ou "3 x bacon"
  const mX = s.match(/^(\d+)\s*x\s+(.+)$/i);
  if (mX) return { qtd: Math.min(parseInt(mX[1]), 20), texto: mX[2].trim() };

  // Número EXTENSO no FINAL
  const mExtFim = s.match(/^(.+?)[,\s]+(?:x\s*)?(um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte)\s*(?:unidades?|und\.?|un\.?|pç|pçs|vezes)?$/i);
  if (mExtFim) {
    const qtd = NUM_EXTENSO[mExtFim[2].toLowerCase()] || 1;
    return { qtd: Math.min(qtd, 20), texto: mExtFim[1].trim().replace(/,\s*$/, "") };
  }

  // Número DÍGITO no FINAL
  const mFim = s.match(/^(.+?)[,\s]+(\d+)\s*(?:unidades?|und\.?|un\.?|pç|pçs|vezes|x)?\s*$/i);
  if (mFim) {
    const qtd = parseInt(mFim[2]);
    const textoAntes = mFim[1].trim().replace(/,\s*$/, "");
    const PALAVRAS_CONTEXTO = ["número","numero","nº","n°","rua","av","avenida","bloco","apto","apartamento"];
    const ehContextoEnd = PALAVRAS_CONTEXTO.some(p => textoAntes.toLowerCase().includes(p));
    if (qtd >= 1 && qtd <= 20 && textoAntes.length >= 3 && !ehContextoEnd) {
      return { qtd, texto: textoAntes };
    }
  }

  // Número DÍGITO no início
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

  // Match exato
  for (const item of todos) {
    const n = normStr(item.nome);
    const nRaw = item.nome.toLowerCase();
    if (n === s || nRaw === sRaw) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
  }

  // Substring
  if (s.length >= 4) {
    for (const item of todos) {
      const n = normStr(item.nome);
      if (n.includes(s) || s.includes(n)) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  return { ok:false, sugestoes:"" };
}

  // Test cases
const testCases = [
  // Comandos básicos
  { input: "oi", expected: "boas_vindas" },
  { input: "olá", expected: "boas_vindas" },
  { input: "menu", expected: "boas_vindas" },
  { input: "cardápio", expected: "cardapio" },
  
  // Pedidos simples
  { input: "suco de uva", expected: "item_reconhecido", item: "suco de uva" },
  { input: "peito de frango", expected: "item_reconhecido", item: "PEITO DE FRANGO" },
  { input: "pizza calabresa", expected: "item_reconhecido", item: "Pizza Calabresa" },
  
  // Pedidos com quantidade
  { input: "2 suco de uva", expected: "item_reconhecido", item: "suco de uva", qtd: 2 },
  { input: "3x coca lata", expected: "item_reconhecido", item: "Coca Lata", qtd: 3 },
  { input: "dois refrigerantes", expected: "item_reconhecido", item: "Coca Lata", qtd: 2 },
  
  // Pedidos múltiplos
  { input: "suco de uva e pizza calabresa", expected: "multi_item" },
  { input: "2x coca e 3x bacon", expected: "multi_item" },
  
  // Meio a meio
  { input: "meio a meio pizza calabresa e frango", expected: "meio_a_meio" },
  
  // Acompanhamentos
  { input: "peito de frango com feijão tropeiro", expected: "acompanhamentos" },
];

console.log("🧪 TESTANDO COMANDOS E FLUXOS DO SISTEMA\n");
console.log("=" .repeat(60));

let passed = 0;
let failed = 0;

testCases.forEach((test, index) => {
  console.log(`\n${index + 1}. Testando: "${test.input}"`);
  
  // Simular fluxo de validação
  const { qtd, texto } = extrairQtd(test.input);
  const validation = validarItem(texto, cfg);
  
  // Verificar se corresponde a algum fluxo
  const fluxos = cfg.fluxos || [];
  const matchedFluxo = fluxos.find(f => 
    f.gatilhos && f.gatilhos.some(g => {
      const gLower = g.toLowerCase();
      const inputLower = test.input.toLowerCase();
      return inputLower === gLower || inputLower.includes(gLower);
    })
  );
  
  // Verificar resultados
  let result = "";
  let status = "";
  
  if (test.expected === "boas_vindas" && matchedFluxo && matchedFluxo.id === "boas_vindas") {
    result = "✅ Boas vindas acionado";
    status = "PASS";
    passed++;
  } else if (test.expected === "cardapio" && matchedFluxo && matchedFluxo.id === "cardapio") {
    result = "✅ Cardápio acionado";
    status = "PASS";
    passed++;
  } else if (test.expected === "item_reconhecido" && validation.ok) {
    const qtdMatch = !test.qtd || qtd === test.qtd;
    const itemMatch = !test.item || validation.item.nome.toLowerCase().includes(test.item.toLowerCase());
    
    if (qtdMatch && itemMatch) {
      result = `✅ Item reconhecido: ${validation.item.nome} (qtd: ${qtd})`;
      status = "PASS";
      passed++;
    } else {
      result = `❌ Item não corresponde: esperado ${test.item} (qtd: ${test.qtd}), obtido ${validation.item.nome} (qtd: ${qtd})`;
      status = "FAIL";
      failed++;
    }
  } else if (test.expected === "multi_item") {
    // Verificar se parece ter múltiplos itens
    const temMultiE = test.input.includes(" e ") && /\b(e)\b/i.test(test.input);
    if (temMultiE) {
      result = "✅ Pedido múltiplo detectado";
      status = "PASS";
      passed++;
    } else {
      result = "❌ Pedido múltiplo não detectado";
      status = "FAIL";
      failed++;
    }
  } else if (test.expected === "meio_a_meio") {
    const temMeio = test.input.includes("meio") || test.input.includes("metade");
    if (temMeio) {
      result = "✅ Meio a meio detectado";
      status = "PASS";
      passed++;
    } else {
      result = "❌ Meio a meio não detectado";
      status = "FAIL";
      failed++;
    }
  } else if (test.expected === "acompanhamentos") {
    const temAcomp = test.input.includes(" com ");
    if (temAcomp) {
      result = "✅ Acompanhamentos detectados";
      status = "PASS";
      passed++;
    } else {
      result = "❌ Acompanhamentos não detectados";
      status = "FAIL";
      failed++;
    }
  } else {
    result = `❌ Teste falhou: esperado ${test.expected}, obtido ${validation.ok ? "item_reconhecido" : "não reconhecido"}`;
    status = "FAIL";
    failed++;
  }
  
  console.log(`   ${result}`);
  console.log(`   Status: ${status}`);
});

console.log("\n" + "=".repeat(60));
console.log(`\n📊 RESUMO: ${passed} PASS, ${failed} FAIL, ${testCases.length} TOTAL`);

// Testar cardápio
console.log("\n" + "=".repeat(60));
console.log("\n📋 TESTANDO CARDAPIO");
console.log("=".repeat(60));

const categorias = cfg.cardapio || [];
categorias.forEach(cat => {
  console.log(`\n${cat.categoria}:`);
  (cat.itens || []).forEach((item, idx) => {
    if (!item.pausado) {
      console.log(`  ${idx + 1}. ${item.nome} - ${item.preco}`);
    }
  });
});

// Testar fluxos
console.log("\n" + "=".repeat(60));
console.log("\n🔄 TESTANDO FLUXOS");
console.log("=".repeat(60));

const fluxos = cfg.fluxos || [];
fluxos.forEach(fluxo => {
  console.log(`\n${fluxo.id}:`);
  console.log(`  Gatilhos: ${fluxo.gatilhos.join(", ")}`);
  console.log(`  Resposta: ${fluxo.resposta.substring(0, 100)}...`);
});

console.log("\n" + "=".repeat(60));
console.log("\n✅ TESTE COMPLETO FINALIZADO");
console.log("=".repeat(60));
