// Script Node.js para atualizar o servidor para usar a API da Mimo v2
const fs = require('fs');
const path = require('path');

const serverPath = path.join(__dirname, 'casa', 'server.js');

console.log('Atualizando servidor para usar a API da Mimo v2...');

// Ler o conteúdo atual do servidor
let serverContent = fs.readFileSync(serverPath, 'utf8');

// Verificar se já existe a importação do mimoService
if (!serverContent.includes("require('./services/mimoService')")) {
    console.log('Adicionando importação do mimoService...');
    
    // Adicionar a importação após a linha do groqService
    serverContent = serverContent.replace(
        /const.*require\("\.\/services\/groqService"\);/,
        '$&\nconst { mimoClient, initMimo } = require(\'./services/mimoService\');'
    );
}

// Verificar se já existe a função initMimo
if (!serverContent.includes('function initMimo()')) {
    console.log('Adicionando função initMimo...');
    
    // Adicionar a função initMimo após a função initGroq
    const initMimoCode = `
// ═══════════════════════
//  MIMO V2
// ═══════════════════════
let mimoClient = null;
function initMimo() {
  const key = (config.mimoApiKey || "").trim();
  if (key.startsWith("sk_")) {
    mimoClient = new OpenAI({ apiKey: key, baseURL: "https://api.mimo.ai/v1" });
    console.log("[IA] Mimo v2 OK:", config.model || "mimo-model");
  } else {
    mimoClient = null;
    if (key) console.warn("[IA] Chave inválida — deve começar com sk_");
  }
}
initMimo();
`;
    
    serverContent = serverContent.replace(
        /initGroq\(\);/,
        '$&' + initMimoCode
    );
}

// Atualizar a função chamarIA para usar mimoClient em vez de groqClient
console.log('Atualizando função chamarIA para usar Mimo v2...');
serverContent = serverContent.replace(
    /if \(!groqClient \|\| !cfg\.useAI\)/g,
    'if (!mimoClient || !cfg.useAI)'
);
serverContent = serverContent.replace(
    /const r = await groqClient\.chat\.completions\.create\(/g,
    'const r = await mimoClient.chat.completions.create('
);

// Atualizar a rota de status para usar mimoClient
console.log('Atualizando rota de status para usar Mimo v2...');
serverContent = serverContent.replace(
    /iaAtiva: !!groqClient && !!config\.useAI/g,
    'iaAtiva: !!mimoClient && !!config.useAI'
);
serverContent = serverContent.replace(
    /groqConfigurada: !!\(config\.groqApiKey \|\| ""\)\.startsWith\("gsk_"\)/g,
    'mimoConfigurada: !!(config.mimoApiKey || "").startsWith("sk_")'
);

// Salvar o arquivo atualizado
fs.writeFileSync(serverPath, serverContent, 'utf8');

console.log('Atualização concluída!');
console.log('Agora o servidor usará a API da Mimo v2 em vez da Groq.');
console.log('Chave da API Mimo v2 configurada: sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v');
