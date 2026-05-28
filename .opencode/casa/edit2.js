// Script para atualizar mostrarCardapio no fluxoPedido
const fs = require('fs');
let c = fs.readFileSync('C:/casa/server.js', 'utf8');

// Substituir a função mostrarCardapio no escopo global (topo do arquivo)
// Esta é a versão apenas texto
const oldMostrarCardapio = `// ─── cardápio formatado ───
function mostrarCardapio(cfg) {
  const proms = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto);
  const promoStr = proms.length
    ? "\\n\\n🔥 *PROMOÇÕES DO DIA:*\\n" + proms.map(p=>\`  ✨ \${p.texto}\`).join("\\n")
    : "";
  return (
    \`🍽️✨ *CARDÁPIO \${cfg.empresaNome||""}* ✨🍽️\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n\` +
    \`\${cardResumido(cfg)}\` +
    \`\${promoStr}\\n\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\` +
    \`🛒 *O que vai querer hoje?*\\n\\n\` +
    \`💬 _Descreva seu pedido. Ex:_\\n\` +
    \`💬 _"1 pizza calabresa G e 2 Coca-Cola"_\\n\\n\` +
    \`❌ _Digite_ *cancelar* _a qualquer momento._\`
  );
}`;

// Nova versão com suporte a fotos
const newMostrarCardapio = `// ─── cardápio: versão texto puro (retrocompatível) ───
function mostrarCardapio(cfg) {
  const proms = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto);
  const promoStr = proms.length
    ? "\\n\\n🔥 *PROMOÇÕES DO DIA:*\\n" + proms.map(p=>\`  ✨ \${p.texto}\`).join("\\n")
    : "";
  return (
    \`🍽️✨ *CARDÁPIO \${cfg.empresaNome||""}* ✨🍽️\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n\` +
    \`\${cardResumido(cfg)}\` +
    \`\${promoStr}\\n\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\` +
    \`🛒 *O que vai querer hoje?*\\n\\n\` +
    \`💬 _Descreva seu pedido. Ex:_\\n\` +
    \`💬 _"1 pizza calabresa G e 2 Coca-Cola"_\\n\\n\` +
    \`❌ _Digite_ *cancelar* _a qualquer momento._\`
  );
}

// ─── cardápio: versão com fotos (envia imagem dos itens) ───
// chat = objeto WhatsApp chat. Esta função é async.
// Retorna string do texto do cardápio.
async function mostrarCardapioComFotos(chat, cfg) {
  const proms = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto);
  const promoStr = proms.length
    ? "\\n\\n🔥 *PROMOÇÕES DO DIA:*\\n" + proms.map(p=>\`  ✨ \${p.texto}\`).join("\\n")
    : "";
  const texto = (
    \`🍽️✨ *CARDÁPIO \${cfg.empresaNome||""}* ✨🍽️\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n\` +
    \`\${cardResumido(cfg)}\` +
    \`\${promoStr}\\n\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\` +
    \`🛒 *O que vai querer hoje?*\\n\\n\` +
    \`💬 _Descreva seu pedido. Ex:_\\n\` +
    \`💬 _"1 pizza calabresa G e 2 Coca-Cola"_\\n\\n\` +
    \`❌ _Digite_ *cancelar* _a qualquer momento._\`
  );

  // Verificar se algum item tem imagem
  const temFotos = (cfg.cardapio||[]).some(cat =>
    (cat.itens||[]).some(item => item.imagem && !item.pausado)
  );

  if (!temFotos) {
    // Sem fotos: retorna texto puro
    return texto;
  }

  // Enviar texto primeiro
  await chat.sendMessage(texto);

  // Enviar foto de cada item que tem imagem
  const { MessageMedia } = require("whatsapp-web.js");
  for (const cat of cfg.cardapio||[]) {
    for (const item of cat.itens||[]) {
      if (item.imagem && !item.pausado) {
        try {
          let b64 = item.imagem;
          if (b64.startsWith("data:")) b64 = b64.split(",")[1] || b64;
          const ext = item.imagem.toLowerCase().includes("png") ? "png" : "jpg";
          const media = new MessageMedia(\`image/\${ext}\`, b64, \`\${item.nome}.\${ext}\`);
          const caption = \`*\${item.nome}* — \${item.preco}\${item.descricao ? \`\\n_\${item.descricao}_\` : ""}\`;
          await chat.sendMessage(media, { caption });
          await sleep(500);
        } catch(e) { console.error("[IMG-CARD]", e.message); }
      }
    }
  }
  return texto; // retorna para compatibilidade (texto já enviado acima)
}`;

const hasOld = c.includes(oldMostrarCardapio);
console.log('Has old mostrarCardapio:', hasOld);

// Also check for the alternate version (with emoji instead of backslash-escaped)
const oldAlt = `// ─── cardápio formatado ───
function mostrarCardapio(cfg) {
  const proms = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto);
  const promoStr = proms.length
    ? "\\n\\n?? *PROMOÇÕES DO DIA:*\\n" + proms.map(p=>\`  ? \${p.texto}\`).join("\\n")
    : "";
  return (
    \`??✨ *CARDÁPIO \${cfg.empresaNome||""}* ✨??\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\\n\` +
    \`\${cardResumido(cfg)}\` +
    \`\${promoStr}\\n\\n\` +
    \`▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\\n\` +
    \`🛒 *O que vai querer hoje?*\\n\\n\` +
    \`💬 _Descreva seu pedido. Ex:_\\n\` +
    \`💬 _"1 pizza calabresa G e 2 Coca-Cola"_\\n\\n\` +
    \`❌ _Digite_ *cancelar* _a qualquer momento._\`
  );
}`;
const hasAlt = c.includes(oldAlt);
console.log('Has alt mostrarCardapio:', hasAlt);

// Find and show context to understand which one is there
const idx1 = c.indexOf('// ─── cardápio formatado ───');
const idx2 = c.indexOf('// ─── exibir cardápio completo ───');
const idx3 = c.indexOf('// ─── cardápio: versão texto puro');
console.log('idx1 (cardápio formatado):', idx1);
console.log('idx2 (exibir cardápio completo):', idx2);
console.log('idx3 (versão texto puro):', idx3);

if (idx1 >= 0) {
  console.log('Content at idx1:', JSON.stringify(c.slice(idx1, idx1+300)));
}
