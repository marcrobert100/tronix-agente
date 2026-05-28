/**
 * ╔══════════════════════════════════════════════════════╗
 * ║   BOT WHATSAPP — DELIVERY & ATENDIMENTO v6          ║
 * ║   Desenvolvido por Marco Roberto                    ║
 * ╚══════════════════════════════════════════════════════╝
 */

const express  = require("express");
const http     = require("http");
const { Server } = require("socket.io");
const path     = require("path");
const fs       = require("fs");
const QRCode   = require("qrcode");
const { Client, LocalAuth } = require("whatsapp-web.js");
const OpenAI   = require("openai");
const crypto   = require("crypto");
const nodeFetch = (...args) => import("node-fetch").then(({default: f}) => f(...args));

// ═══════════════════════
//  ARQUIVOS
// ═══════════════════════
const PORT         = 3000;
const CONFIG_FILE  = path.join(__dirname, "config.json");
const LICENSE_FILE = path.join(__dirname, "license.json");
const LOG_DIR      = path.join(__dirname, "logs");

if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });
function logFile() { return path.join(LOG_DIR, `conversas-${new Date().toISOString().slice(0,10)}.jsonl`); }

const CLIENTES_FILE = path.join(LOG_DIR, "clientes.json");
const CUPONS_FILE   = path.join(LOG_DIR, "cupons.json");

function loadClientes() {
  try { if (fs.existsSync(CLIENTES_FILE)) {
    const d = JSON.parse(fs.readFileSync(CLIENTES_FILE,"utf8"));
    for (const [k,v] of Object.entries(d)) clientesDB.set(k,v);
  }} catch(_) {}
}
function saveClientes() {
  const obj = {}; for (const [k,v] of clientesDB) obj[k]=v;
  fs.writeFileSync(CLIENTES_FILE, JSON.stringify(obj,null,2));
}
function loadCupons() {
  try { if (fs.existsSync(CUPONS_FILE)) {
    const d = JSON.parse(fs.readFileSync(CUPONS_FILE,"utf8"));
    for (const [k,v] of Object.entries(d)) cuponsDB.set(k,v);
  }} catch(_) {}
}
function saveCupons() {
  const obj = {}; for (const [k,v] of cuponsDB) obj[k]=v;
  fs.writeFileSync(CUPONS_FILE, JSON.stringify(obj,null,2));
}
loadClientes(); loadCupons();

// ═══════════════════════
//  AUTH — login obrigatório para TUDO
// ═══════════════════════
const ADMIN_USER = "cliente";
const ADMIN_PASS = "123456";
const sessoes    = new Map(); // token → expiry

function gerarToken() { return crypto.randomBytes(32).toString("hex"); }

function authOk(req) {
  const token = req.headers["x-token"] || req.query.token;
  if (!token) return false;
  const exp = sessoes.get(token);
  if (!exp || Date.now() > exp) { sessoes.delete(token); return false; }
  return true;
}

function guard(req, res, next) {
  if (authOk(req)) return next();
  res.status(401).json({ ok: false, erro: "Não autorizado" });
}

// ═══════════════════════
//  LICENÇA
// ═══════════════════════
function loadLic() {
  try { if (fs.existsSync(LICENSE_FILE)) return JSON.parse(fs.readFileSync(LICENSE_FILE, "utf8")); }
  catch (_) {}
  return { validade: null, comerciante: "", ativa: false };
}
function saveLic(d) { fs.writeFileSync(LICENSE_FILE, JSON.stringify(d, null, 2)); }
function diasRestantes() {
  const l = loadLic();
  if (!l.validade) return 0;
  return Math.max(0, Math.ceil((new Date(l.validade) - Date.now()) / 86400000));
}
function licOk() {
  const l = loadLic();
  return !!(l.ativa && l.validade && new Date(l.validade) >= new Date());
}

// ═══════════════════════
//  CONFIG — chave Groq nunca se perde
// ═══════════════════════
function loadConfig() {
  try { if (fs.existsSync(CONFIG_FILE)) return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8")); }
  catch (e) { console.error("[CONFIG]", e.message); }
  return {};
}
function saveConfig(data) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(data, null, 2));
}

let config = loadConfig();

// ═══════════════════════
//  GROQ
// ═══════════════════════
let groqClient = null;
function initGroq() {
  const key = (config.groqApiKey || "").trim();
  if (key.startsWith("gsk_")) {
    groqClient = new OpenAI({ apiKey: key, baseURL: "https://api.groq.com/openai/v1" });
    console.log("[IA] Groq OK:", config.model || "llama-3.1-8b-instant");
  } else {
    groqClient = null;
    if (key) console.warn("[IA] Chave inválida — deve começar com gsk_");
  }
}
initGroq();

// ═══════════════════════
//  VOZ: Transcrição de áudio com Groq (Whisper)
// ═══════════════════════
async function transcreverAudioGroq(bufferAudio) {
  const key = (config.groqApiKey || "").trim();
  if (!key.startsWith("gsk_")) {
    console.error("[VOZ]❌ Chave Groq não configurada");
    return null;
  }

  let tmpFile = null;
  let tmpWavFile = null;
  try {
    const FormData = require("form-data");
    const fetch = nodeFetch;
    const form = new FormData();
    
    // Salvar áudio original para debug (descomente se precisar debugar)
    // fs.writeFileSync(path.join(__dirname, "debug_audio_" + Date.now() + ".ogg"), bufferAudio);
    
    // Criar arquivo temporário OGG
    tmpFile = path.join(__dirname, "temp_audio_" + Date.now() + ".ogg");
    fs.writeFileSync(tmpFile, bufferAudio);
    
    console.log("[VOZ]▸ Enviando áudio para Groq... tamanho:", bufferAudio.length, "bytes");
    console.log("[VOZ]▸ Primeiro bytes (hex):", bufferAudio.slice(0, 16).toString("hex"));
    
    // Verificar se é um formato válido
    const magicBytes = bufferAudio.slice(0, 4).toString("hex");
    console.log("[VOZ]▸ Magic bytes:", magicBytes, "(ogg=4f676753, mp4=66747970)");
    
    form.append("file", fs.createReadStream(tmpFile));
    form.append("model", "whisper-large-v3");
    form.append("language", "pt");
    form.append("temperature", "0.2");
    form.append("response_format", "text");

    console.log("[VOZ]▸ Fazendo requisição para API Groq...");
    
    const response = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${key}`,
      },
      body: form
    });

    console.log("[VOZ]▸ Resposta recebida, status:", response.status);

    if (!response.ok) {
      const err = await response.text();
      console.error("[VOZ]❌ Groq erro:", response.status, err);
      return null;
    }

    // Groq retorna texto puro quando response_format=text
    const texto = await response.text();
    console.log("[VOZ]✓ Resultado:", texto);
    return texto.trim() || null;
  } catch (err) {
    console.error("[VOZ]❌ Exceção:", err.message);
    console.error("[VOZ]❌ Stack:", err.stack);
    return null;
  } finally {
    // Limpar arquivos temporários
    if (tmpFile) { try { fs.unlinkSync(tmpFile); } catch (_) {} }
    if (tmpWavFile) { try { fs.unlinkSync(tmpWavFile); } catch (_) {} }
  }
}

// ═══════════════════════
//  ESTADO GLOBAL
// ═══════════════════════
let waClient      = null;
let waConectado   = false;
let io            = null;
let totalMsgs     = 0;
let autoImprimir  = true;
let viasImpressao = 1;
let agenteAtivo   = true;
const inicio      = Date.now();

const historicos     = new Map();
const rateLimiter    = new Map();
const estadosPedido  = new Map();
const pedidosAbertos = new Map();

// ── Novas estruturas ──
const clientesDB        = new Map();
const avaliacoesPend    = new Map();
const cuponsDB          = new Map();
const atendimentoHumano = new Map(); // numero → { inicio, motivo, msgs[] }
let   atendHumanoAtivo  = false;     // liga/desliga pelo painel

// ═══════════════════════
//  EXPRESS
// ═══════════════════════
const app    = express();
const server = http.createServer(app);
io           = new Server(server);

app.use(express.json({ limit: "6mb" }));
app.use(express.urlencoded({ extended: true, limit: "6mb" }));

// Servir arquivos estáticos APENAS para autenticados
// EXCETO o index.html (que tem a tela de login embutida)
app.use("/socket.io", express.static(path.join(__dirname, "node_modules/socket.io/client-dist")));

// Rota raiz → login.html (página pública)
app.get("/", (req, res) => res.sendFile(path.join(__dirname, "public", "login.html")));

// Painel → só com token válido na query string
app.get("/painel", (req, res) => {
  if (!authOk(req)) return res.redirect("/");
  res.sendFile(path.join(__dirname, "public", "painel.html"));
});

// Arquivos estáticos do painel (css, js, etc) — protegidos por referrer ou token
app.use("/public", (req, res, next) => {
  // Permite recursos estáticos quando o token está no header ou na session
  next(); // os arquivos JS/CSS não precisam de auth, mas o HTML sim
});
app.use("/public", express.static(path.join(__dirname, "public")));

// ── AUTH ──
app.post("/api/login", (req, res) => {
  const { usuario, senha } = req.body || {};
  if (usuario === ADMIN_USER && senha === ADMIN_PASS) {
    const token = gerarToken();
    sessoes.set(token, Date.now() + 8 * 3600000); // 8h
    return res.json({ ok: true, token });
  }
  res.status(401).json({ ok: false, erro: "Usuário ou senha incorretos" });
});

app.post("/api/logout", (req, res) => {
  const t = req.headers["x-token"];
  if (t) sessoes.delete(t);
  res.json({ ok: true });
});

app.get("/api/auth/check", (req, res) => res.json({ ok: authOk(req) }));

// ── LICENÇA ──
app.get("/api/licenca", guard, (req, res) => {
  res.json({ ...loadLic(), diasRestantes: diasRestantes(), valida: licOk() });
});
app.post("/api/licenca", guard, (req, res) => {
  const l = { ...loadLic(), ...req.body };
  saveLic(l);
  io.emit("licenca", { ...l, diasRestantes: diasRestantes(), valida: licOk() });
  res.json({ ok: true });
});

// ── STATUS ──
app.get("/api/status", guard, (req, res) => {
  const l = loadLic();
  res.json({
    conectado: waConectado, uptime: Math.floor((Date.now() - inicio) / 1000),
    mensagens: totalMsgs, sessoes: historicos.size, pedidos: pedidosAbertos.size,
    pedindoAgora: estadosPedido.size,
    iaAtiva: !!groqClient && !!config.useAI, groqConfigurada: !!(config.groqApiKey || "").startsWith("gsk_"),
    autoImprimir, viasImpressao, agenteAtivo, voiceEnabled: config.voiceEnabled !== false,
    licenca: { ...l, diasRestantes: diasRestantes(), valida: licOk() },
  });
});

// ── CONFIG (GET — nunca expõe chave) ──
app.get("/api/config", guard, (req, res) => {
  const c = { ...config };
  c.groqApiKey = c.groqApiKey ? "CONFIGURADA" : "";
  res.json(c);
});

// ── CONFIG (POST — nunca sobrescreve chave com dado mascarado) ──
app.post("/api/config", guard, (req, res) => {
  const body = { ...req.body };
  // Nunca aceitar chave via /api/config — use /api/groq-key
  delete body.groqApiKey;
  config = { ...config, ...body };
  saveConfig(config);
  initGroq();
  res.json({ ok: true });
});

// ── SALVAR CHAVE GROQ — rota dedicada e isolada ──
app.post("/api/groq-key", guard, (req, res) => {
  const raw = (req.body || {}).key || "";
  const key = raw.trim();
  if (!key.startsWith("gsk_") || key.length < 20) {
    return res.status(400).json({ ok: false, erro: "Chave inválida. Deve começar com gsk_ e ter pelo menos 20 caracteres." });
  }
  // Lê o config diretamente do disco, altera só a chave, salva
  const cfg = loadConfig();
  cfg.groqApiKey = key;
  saveConfig(cfg);
  config = cfg;
  initGroq();
  console.log("[IA] ✅ Chave Groq salva com sucesso. Tamanho:", key.length);
  res.json({ ok: true, msg: "Chave salva! IA ativada." });
});

// ── VOICE: Toggle atendimento por voz ──
app.post("/api/voice/toggle", guard, (req, res) => {
  config.voiceEnabled = !!req.body.ativo;
  saveConfig(config);
  res.json({ ok: true, ativo: config.voiceEnabled });
});

// ── PRODUTO: adicionar categoria ──
app.post("/api/cardapio/categoria", guard, (req, res) => {
  const { nome, icone } = req.body || {};
  if (!nome) return res.status(400).json({ ok: false, erro: "Nome obrigatório" });
  const cfg = loadConfig();
  cfg.cardapio = cfg.cardapio || [];
  if (cfg.cardapio.find(c => c.categoria === `${icone || ""} ${nome}`.trim())) {
    return res.status(400).json({ ok: false, erro: "Categoria já existe" });
  }
  cfg.cardapio.push({ categoria: `${icone || ""} ${nome}`.trim(), itens: [] });
  saveConfig(cfg); config = cfg;
  io.emit("cardapio_atualizado", cfg.cardapio);
  res.json({ ok: true, cardapio: cfg.cardapio });
});

// ── PRODUTO: adicionar item ──
app.post("/api/cardapio/item", guard, (req, res) => {
  const { categoria, nome, descricao, preco, tamanhos, maxAcomp, imagem } = req.body || {};
  if (!categoria || !nome || !preco) return res.status(400).json({ ok: false, erro: "categoria, nome e preco são obrigatórios" });
  const cfg = loadConfig();
  const cat = (cfg.cardapio || []).find(c => c.categoria === categoria);
  if (!cat) return res.status(404).json({ ok: false, erro: "Categoria não encontrada" });
  const novoItem = { nome, descricao: descricao || "", preco, tamanhos: tamanhos || "", pausado: false };
  if (maxAcomp && parseInt(maxAcomp) > 0) novoItem.maxAcomp = parseInt(maxAcomp);
  // Salvar imagem (base64) — validar tamanho máx ~2MB em base64 (~2.7MB string)
  if (imagem && typeof imagem === "string" && imagem.length > 10 && imagem.length < 3_500_000) {
    novoItem.imagem = imagem;
  }
  cat.itens.push(novoItem);
  saveConfig(cfg); config = cfg;
  io.emit("cardapio_atualizado", cfg.cardapio);
  res.json({ ok: true, cardapio: cfg.cardapio });
});

// ── PRODUTO: editar item ──
app.put("/api/cardapio/item", guard, (req, res) => {
  const { categoria, nomeOriginal, nome, descricao, preco, tamanhos, maxAcomp, imagem } = req.body || {};
  const cfg = loadConfig();
  const cat = (cfg.cardapio || []).find(c => c.categoria === categoria);
  if (!cat) return res.status(404).json({ ok: false });
  const item = cat.itens.find(i => i.nome === nomeOriginal);
  if (!item) return res.status(404).json({ ok: false });
  item.nome = nome || item.nome;
  item.descricao = descricao !== undefined ? descricao : item.descricao;
  item.preco = preco || item.preco;
  item.tamanhos = tamanhos !== undefined ? tamanhos : item.tamanhos;
  if (maxAcomp !== undefined) {
    if (parseInt(maxAcomp) > 0) item.maxAcomp = parseInt(maxAcomp);
    else delete item.maxAcomp;
  }
  // Atualizar imagem: "" = remover, base64 = atualizar, undefined = manter
  if (imagem === "") {
    delete item.imagem;
  } else if (imagem && typeof imagem === "string" && imagem.length > 10 && imagem.length < 3_500_000) {
    item.imagem = imagem;
  }
  saveConfig(cfg); config = cfg;
  io.emit("cardapio_atualizado", cfg.cardapio);
  res.json({ ok: true, cardapio: cfg.cardapio });
});

// ── PRODUTO: excluir item ──
app.delete("/api/cardapio/item", guard, (req, res) => {
  const { categoria, nome } = req.body || {};
  const cfg = loadConfig();
  const cat = (cfg.cardapio || []).find(c => c.categoria === categoria);
  if (!cat) return res.status(404).json({ ok: false });
  cat.itens = cat.itens.filter(i => i.nome !== nome);
  saveConfig(cfg); config = cfg;
  io.emit("cardapio_atualizado", cfg.cardapio);
  res.json({ ok: true });
});

// ── PRODUTO: excluir categoria ──
app.delete("/api/cardapio/categoria", guard, (req, res) => {
  const { categoria } = req.body || {};
  const cfg = loadConfig();
  cfg.cardapio = (cfg.cardapio || []).filter(c => c.categoria !== categoria);
  saveConfig(cfg); config = cfg;
  io.emit("cardapio_atualizado", cfg.cardapio);
  res.json({ ok: true });
});

// ── RELATÓRIOS DE VENDAS ──
function registrarVenda(pedido) {
  const vendasFile = path.join(LOG_DIR, "vendas.json");
  let vendas = [];
  try { if (fs.existsSync(vendasFile)) vendas = JSON.parse(fs.readFileSync(vendasFile,"utf8")); } catch(_) {}
  const hoje = new Date().toISOString().slice(0,10);
  const hora  = new Date().toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
  vendas.push({ ...pedido, data:hoje, hora });
  if (vendas.length > 2000) vendas = vendas.slice(-2000);
  fs.writeFileSync(vendasFile, JSON.stringify(vendas, null, 2));
}

app.get("/api/relatorios", guard, (req, res) => {
  const f = path.join(LOG_DIR,"vendas.json");
  let vendas = [];
  try { if (fs.existsSync(f)) vendas = JSON.parse(fs.readFileSync(f,"utf8")); } catch(_) {}
  const hoje = new Date().toISOString().slice(0,10);
  const vendaHoje = vendas.filter(v=>v.data===hoje);

  // ── Calcular faturamento extraindo valores dos itens ──
  function calcFaturamento(lista) {
    return lista.reduce((acc, v) => {
      const partes = (v.itens||"").split(" | ");
      let sub = 0;
      for (const p of partes) {
        // Extrai R$ valor do item (ex: "2x X-Bacon — R$ 64,00" ou "X-Bacon — R$ 32,00")
        const m = p.match(/R\$\s*([\d,.]+)/);
        if (m) {
          const val = parseFloat(m[1].replace(",","."));
          if (!isNaN(val)) sub += val;
        }
      }
      // Adicionar taxa de entrega se houver
      if (v.taxaEntrega) {
        const taxa = parseFloat((v.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",","."));
        if (!isNaN(taxa)) sub += taxa;
      }
      return acc + sub;
    }, 0);
  }

  const faturamentoHoje = calcFaturamento(vendaHoje);

  const porDia = {};
  for (const v of vendas) {
    if (!porDia[v.data]) porDia[v.data] = {data:v.data,total:0,qtd:0,pagamentos:{}};
    porDia[v.data].qtd++;
    const pag = v.pagamento||"outro";
    porDia[v.data].pagamentos[pag] = (porDia[v.data].pagamentos[pag]||0)+1;
  }
  // Calcular faturamento por dia
  for (const dia of Object.keys(porDia)) {
    const vendasDia = vendas.filter(v=>v.data===dia);
    porDia[dia].faturamento = calcFaturamento(vendasDia);
  }

  const diasOrdenados = Object.values(porDia).sort((a,b)=>b.data.localeCompare(a.data)).slice(0,30);
  const topItens = {};
  for (const v of vendas) {
    const i = (v.itens||"").split(/[,\n]/)[0].replace(/^\d+\s*/,"").trim().toLowerCase();
    if (i.length>2) topItens[i] = (topItens[i]||0)+1;
  }
  const ranking = Object.entries(topItens).sort((a,b)=>b[1]-a[1]).slice(0,8).map(([nome,qtd])=>({nome,qtd}));
  res.json({
    hoje:   { qtd:vendaHoje.length, pedidos:vendaHoje.slice(-30).reverse(), faturamento:faturamentoHoje },
    geral:  { totalPedidos:vendas.length, porDia:diasOrdenados, ranking },
  });
});

// ── PROMOÇÕES ──
app.get("/api/promocoes", guard, (req, res) => res.json(config.promocoes||[]));
app.post("/api/promocoes", guard, (req, res) => {
  const { promocoes } = req.body||{};
  if (!Array.isArray(promocoes)) return res.status(400).json({ok:false});
  config.promocoes = promocoes;
  saveConfig(config);
  res.json({ok:true});
});

// ── PROMOÇÕES COM IMAGEM ──
// Upload de imagem base64 para promoção
app.post("/api/promocoes/imagem", guard, express.json({limit:"10mb"}), (req, res) => {
  const { id, imagem } = req.body||{};
  if (!id || !imagem) return res.status(400).json({ok:false, erro:"id e imagem obrigatórios"});
  const promos = config.promocoes||[];
  const p = promos.find(x=>x.id===id);
  if (!p) return res.status(404).json({ok:false, erro:"Promoção não encontrada"});
  p.imagem = imagem; // base64
  config.promocoes = promos;
  saveConfig(config);
  res.json({ok:true});
});

// Toggle liga/desliga todas as promoções
app.post("/api/promocoes/toggle-geral", guard, (req, res) => {
  config.promoAtiva = !!req.body.ativo;
  saveConfig(config);
  io.emit("promo_status", { ativo: config.promoAtiva });
  res.json({ok:true, ativo: config.promoAtiva});
});
app.get("/api/promocoes/status", guard, (req, res) => {
  res.json({ ativo: !!config.promoAtiva });
});

// ── REGRA MEIO A MEIO ──
// ruleMeioAMeio: "maior" = cobra o maior valor | "media" = faz média dos dois
app.get("/api/meio-a-meio", guard, (req, res) => {
  res.json({ rule: config.ruleMeioAMeio || "maior" });
});
app.post("/api/meio-a-meio", guard, (req, res) => {
  const { rule } = req.body || {};
  if (!["maior","media"].includes(rule)) return res.status(400).json({ ok:false });
  config.ruleMeioAMeio = rule;
  saveConfig(config);
  res.json({ ok:true, rule });
});

// ── PRODUTO: tempo de preparo ──
app.post("/api/produto/tempo", guard, (req, res) => {
  const { categoria, nome, tempoPreparo } = req.body;
  const cfg = loadConfig();
  for (const cat of cfg.cardapio||[]) {
    if (cat.categoria === categoria) {
      for (const item of cat.itens||[]) {
        if (item.nome === nome) { item.tempoPreparo = parseInt(tempoPreparo)||0; }
      }
    }
  }
  saveConfig(cfg); config = cfg;
  res.json({ ok:true });
});

// ── PRODUTO: pausar ──
app.post("/api/produto/pausar", guard, (req, res) => {
  const { categoria, nome, pausado } = req.body;
  const cfg = loadConfig();
  let achou = false;
  for (const cat of cfg.cardapio || []) {
    if (cat.categoria === categoria) {
      for (const item of cat.itens || []) {
        if (item.nome === nome) { item.pausado = !!pausado; achou = true; }
      }
    }
  }
  if (!achou) return res.status(404).json({ ok: false });
  saveConfig(cfg); config = cfg;
  io.emit("cardapio_atualizado", cfg.cardapio);
  res.json({ ok: true });
});

// ── IMPRESSÃO ──
app.post("/api/auto-imprimir", guard, (req, res) => {
  autoImprimir = !!req.body.ativo;
  io.emit("auto_imprimir", { ativo: autoImprimir });
  res.json({ ok: true, ativo: autoImprimir });
});
app.post("/api/vias-impressao", guard, (req, res) => {
  viasImpressao = Math.min(3, Math.max(1, parseInt(req.body.vias) || 1));
  res.json({ ok: true, vias: viasImpressao });
});

// ── STATUS WHATSAPP (Stories/Status) ──

let statusAgendado = null; // timer do próximo status

// Carregar agendamentos de status do config
function initStatusAgendamento() {
  if (statusAgendado) clearInterval(statusAgendado);
  // Verificar a cada minuto se tem status para publicar agora
  statusAgendado = setInterval(verificarEPublicarStatus, 60000);
  // Verificar imediatamente ao iniciar
  setTimeout(verificarEPublicarStatus, 5000);
}

// Controle de publicações já feitas hoje (em memória, evita duplicatas)
const _publicacoesFeitas = new Set();

async function verificarEPublicarStatus() {
  if (!waConectado || !waClient) return;

  // Reler config do disco para pegar mudanças feitas no painel
  const cfg = loadConfig();
  const statusList = cfg.statusWA || [];
  if (!statusList.length) return;

  const agora     = new Date();
  const diaSemana = agora.getDay();
  const horaAtual = String(agora.getHours()).padStart(2,"0") + ":" + String(agora.getMinutes()).padStart(2,"0");
  const dataHoje  = agora.toISOString().slice(0,10);

  for (const item of statusList) {
    if (!item.ativo) continue;
    if (!item.horario) continue;

    // Verificar dia da semana configurado
    const diasAtivos = item.dias && item.dias.length ? item.dias : [0,1,2,3,4,5,6];
    if (!diasAtivos.includes(diaSemana)) continue;

    // Verificar horário — janela exata de 1 minuto
    if (item.horario !== horaAtual) continue;

    // Evitar publicação duplicada no mesmo dia/horário
    const chave = `${item.id||item.horario}_${dataHoje}_${horaAtual}`;
    if (_publicacoesFeitas.has(chave)) continue;
    _publicacoesFeitas.add(chave);

    // Publicar
    try {
      const res = await publicarStatusWA(item);
      const msg = `✅ Status publicado às ${horaAtual}: "${(item.texto||"").slice(0,40)}"`;
      console.log("[STATUS]", msg);
      logC({ tipo:"status_wa", mensagem: msg });
      io.emit("status_wa_publicado", { item, horario: horaAtual, resultados: res });
    } catch(e) {
      console.error("[STATUS] Erro:", e.message);
    }
  }

  // Limpar o controle de publicações de dias anteriores
  for (const chave of _publicacoesFeitas) {
    if (!chave.includes(dataHoje)) _publicacoesFeitas.delete(chave);
  }
}

/**
 * Publica no Status/Stories do WhatsApp (visível por 24h para os contatos).
 *
 * O WhatsApp trata o Status como um chat especial: "status@broadcast".
 * Enviar mensagem para esse chatId posta no Status/Stories do número conectado.
 * Adicionalmente, envia mensagem direta para números extras configurados.
 */
async function publicarStatusWA(item) {
  if (!waClient) throw new Error("WhatsApp não conectado");
  const texto = variaveis((item.texto || "").trim(), config);
  if (!texto) return;

  const resultados = [];

  // ── 1. POSTAR NO STATUS/STORIES (status@broadcast) ──
  // Este é o canal oficial do WhatsApp para Stories/Status.
  // A mensagem ficará visível por 24h para todos os contatos.
  try {
    await waClient.sendMessage("status@broadcast", texto);
    resultados.push("✅ Status/Stories publicado");
    console.log("[STATUS] ✅ Postado no Status/Stories do WhatsApp");
  } catch(e) {
    console.warn("[STATUS] ⚠️  Falha no Status/Stories:", e.message);
    // Fallback: atualizar bio/recado do perfil
    try {
      await waClient.setStatus(texto.slice(0, 139));
      resultados.push("✅ Bio do perfil atualizada");
    } catch(e2) {
      console.warn("[STATUS] setStatus também falhou:", e2.message);
    }
  }

  // ── 2. ENVIAR MENSAGEM DIRETA para números extras configurados ──
  // Opcional: notificar números específicos além do Status.
  const numeros = (item.numeros || []).filter(n => n && n.trim());
  for (const numero of numeros) {
    try {
      const digits = numero.replace(/\D/g, "");
      if (!digits) continue;

      // Resolver o ID correto do número no WhatsApp
      let chatId = digits + "@c.us";
      try {
        const info = await waClient.getNumberId(digits);
        if (info && info._serialized) chatId = info._serialized;
      } catch(_) {}

      await waClient.sendMessage(chatId, texto);
      resultados.push("✅ Msg→" + digits);
      await new Promise(r => setTimeout(r, 1200));
    } catch(e) {
      console.error("[STATUS] Erro ao enviar msg para", numero, "—", e.message);
      resultados.push("❌ Erro→" + numero);
    }
  }

  console.log("[STATUS] Concluído:", resultados.join(" | "));
  return resultados;
}

app.get("/api/status-wa", guard, (req, res) => {
  res.json(config.statusWA || []);
});

app.post("/api/status-wa", guard, (req, res) => {
  const { statusWA } = req.body || {};
  if (!Array.isArray(statusWA)) return res.status(400).json({ ok:false, erro:"Array esperado" });
  config.statusWA = statusWA;
  saveConfig(config);
  initStatusAgendamento();
  io.emit("status_wa_config", config.statusWA);
  res.json({ ok:true });
});

// Publicar status manualmente agora
app.post("/api/status-wa/publicar-agora", guard, async (req, res) => {
  const { id } = req.body || {};
  const item = (config.statusWA || []).find(s => s.id === id);
  if (!item) return res.status(404).json({ ok:false, erro:"Status não encontrado" });
  if (!waConectado) return res.status(503).json({ ok:false, erro:"WhatsApp não conectado" });
  try {
    await publicarStatusWA(item);
    logC({ tipo:"status_wa", mensagem:`Status manual: ${item.texto?.slice(0,50)}` });
    io.emit("status_wa_publicado", { item, horario:"agora" });
    res.json({ ok:true });
  } catch(e) {
    res.status(500).json({ ok:false, erro:e.message });
  }
});

// ── ATENDIMENTO HUMANO ──
// Ligar/desligar
app.post("/api/atendimento-humano/toggle", guard, (req, res) => {
  atendHumanoAtivo = !!req.body.ativo;
  io.emit("atend_humano_status", { ativo: atendHumanoAtivo });
  res.json({ ok:true, ativo: atendHumanoAtivo });
});
app.get("/api/atendimento-humano/status", guard, (req, res) => {
  res.json({ ativo: atendHumanoAtivo, total: atendimentoHumano.size });
});
// Listar conversas abertas
app.get("/api/atendimento-humano", guard, (req, res) => {
  const lista = [];
  for (const [num, a] of atendimentoHumano)
    lista.push({ numero: num.replace("@c.us",""), ...a });
  res.json(lista);
});
// Atendente responde
app.post("/api/atendimento-humano/responder", guard, async (req, res) => {
  const { numero, mensagem } = req.body || {};
  if (!numero || !mensagem) return res.status(400).json({ ok:false });
  const numFull = numero.includes("@c.us") ? numero : numero+"@c.us";
  try {
    if (waConectado && waClient) await waClient.sendMessage(numFull, mensagem);
    const a = atendimentoHumano.get(numFull);
    if (a) a.msgs.push({ de:"atendente", texto:mensagem, ts:Date.now() });
    io.emit("atendimento_msg", { numero:numero.replace("@c.us",""), de:"atendente", texto:mensagem, ts:Date.now() });
    res.json({ ok:true });
  } catch(e) { res.status(500).json({ ok:false, erro:e.message }); }
});
// Encerrar atendimento → devolver ao bot
app.post("/api/atendimento-humano/encerrar", guard, async (req, res) => {
  const { numero } = req.body || {};
  const numExibir = (numero||"").replace("@c.us","");

  // Buscar a chave exata no mapa (pode ter @c.us ou não)
  let chaveReal = null;
  for (const k of atendimentoHumano.keys()) {
    if (k.replace("@c.us","") === numExibir) { chaveReal = k; break; }
  }
  if (chaveReal) atendimentoHumano.delete(chaveReal);

  io.emit("atendimento_encerrado", { numero: numExibir });

  // Enviar mensagem ao cliente usando a chave real encontrada
  const numEnvio = chaveReal || (numExibir + "@c.us");
  if (waConectado && waClient) {
    try {
      await waClient.sendMessage(numEnvio,
        "✅ *Atendimento encerrado!*\n\nEspero ter ajudado! 😊\n_O bot voltou a responder._\n\nDigite *oi* para o menu.");
    } catch(e) {
      console.error("[ENCERRAR]", e.message);
    }
  }
  res.json({ ok:true });
});

// ── AGENTE ──
app.post("/api/agente/fechar", guard, (req, res) => {
  agenteAtivo = !req.body.fechar;
  io.emit("agente_status", { ativo: agenteAtivo });
  res.json({ ok: true, ativo: agenteAtivo });
});

// ── LOJA: fechar/abrir manualmente ──
app.post("/api/loja/fechar", guard, (req, res) => {
  const { fechado, msgCustom } = req.body||{};
  config.lojaFechadaManual = !!fechado;
  if (msgCustom) config.lojaFechadaMensagem = msgCustom;
  saveConfig(config);
  io.emit("loja_status", { fechado: config.lojaFechadaManual });
  res.json({ ok:true, fechado: config.lojaFechadaManual });
});
app.get("/api/loja/status", guard, (req, res) => {
  res.json({ fechado: config.lojaFechadaManual||false, aberta: lojaAberta(config) });
});
app.get("/api/clientes", guard, (req, res) => {
  const lista = [];
  for (const [, cli] of clientesDB) lista.push(cli);
  lista.sort((a,b)=>(b.totalPedidos||0)-(a.totalPedidos||0));
  res.json(lista.slice(0,100));
});

// ── LOGS ──
app.get("/api/logs", guard, (req, res) => {
  try {
    const f = logFile();
    if (!fs.existsSync(f)) return res.json([]);
    const linhas = fs.readFileSync(f, "utf8").split("\n").filter(Boolean)
      .slice(-100).map(l => JSON.parse(l)).reverse();
    res.json(linhas);
  } catch (_) { res.json([]); }
});

// ── PEDIDOS ──
app.get("/api/pedidos", guard, (req, res) => res.json(listaPedidos()));
app.post("/api/pedidos/:num/entregar", guard, async (req, res) => {
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
        const qtdMatch = item.match(/^(\d+)x\s+(.+?)\s+—\s+R\$\s*([\d,.]+)/);
        if (qtdMatch) {
          const qtd   = parseInt(qtdMatch[1]);
          const nome  = qtdMatch[2];
          const prUni = parseFloat(qtdMatch[3].replace(",","."));
          const total = (prUni * qtd).toFixed(2).replace(".",",");
          return `${qtd}x ${nome} — R$ ${total}`;
        }
        return item;
      }).join("\n🍽️ ");
      // Calcular total dos itens para mostrar na entrega
      const subEnt  = calcularTotal(pedido.itens||"", cfg);
      const taxaEnt = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
      const totEnt  = subEnt + taxaEnt;
      const totEntStr = totEnt > 0
        ? `\n💰 *Subtotal:* R$ ${subEnt.toFixed(2).replace(".",",")}\n` +
          `🛵 *Taxa:* ${cfg.taxaEntrega||"—"}\n` +
          `💵 *Total: R$ ${totEnt.toFixed(2).replace(".",",")}*\n`
        : "";

      const msg = (
        `🛵💨 *SEU PEDIDO SAIU PARA ENTREGA!* 💨🛵\n\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
        `📦 *Pedido Nº ${pedido.numPedido}*\n\n` +
        `🍽️ ${itensFormatados}\n` +
        `${totEntStr}\n` +
        `⏱️ *Previsão de chegada:* ${tempo}\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n` +
        `👀 _Fique de olho! Está a caminho!_ 😊🔥`
      );
      await waClient.sendMessage(num, msg);
      // Agendar avaliação pós-entrega (30 min)
      agendarAvaliacao(num, pedido);
    } catch(e) { console.error("[NOTIF]", e.message); }
  }
  res.json({ ok: true });
});

// ── ENVIAR MSG ──
app.post("/api/enviar", guard, async (req, res) => {
  const { numero, mensagem } = req.body || {};
  if (!waConectado || !waClient) return res.status(503).json({ ok: false, erro: "WhatsApp não conectado" });
  try {
    await waClient.sendMessage(numero.replace(/\D/g, "") + "@c.us", mensagem);
    logC({ tipo: "saida_manual", para: numero, mensagem });
    res.json({ ok: true });
  } catch (e) { res.status(500).json({ ok: false, erro: e.message }); }
});

// ── WHATSAPP ──
app.post("/api/wa/disconnect", guard, async (req, res) => {
  waConectado = false;
  if (waClient) { try { await waClient.destroy(); } catch (_) {} waClient = null; }
  io.emit("status", { conectado: false, mensagem: "Desconectado." });
  res.json({ ok: true });
});
app.post("/api/wa/restart", guard, async (req, res) => {
  if (waClient) { try { await waClient.destroy(); } catch (_) {} waClient = null; }
  waConectado = false;
  if (req.query.limpar === "1") {
    const ap = path.join(__dirname, ".wwebjs_auth");
    if (fs.existsSync(ap)) fs.rmSync(ap, { recursive: true });
  }
  io.emit("qr", "loading");
  io.emit("status", { conectado: false, mensagem: "Gerando QR Code..." });
  initWA(true);
  res.json({ ok: true });
});

// ═══════════════════════
//  WHATSAPP CLIENT
// ═══════════════════════
function initWA(force = false) {
  if (waClient && !force) return;
  waClient = null;
  waClient = new Client({
    authStrategy: new LocalAuth({ clientId: "delivery-bot" }),
    authTimeoutMs: 180000,
    puppeteer: {
      headless: true, timeout: 120000,
      args: ["--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage",
             "--disable-gpu","--disable-software-rasterizer","--disable-extensions","--no-first-run"],
    },
  });
  waClient.on("qr", async qr => {
    try { io.emit("qr", await QRCode.toDataURL(qr, { width: 300 }));
      io.emit("status", { conectado: false, mensagem: "Escaneie o QR Code com seu WhatsApp" }); } catch (_) {}
  });
  waClient.on("ready", () => {
    waConectado = true; io.emit("qr", null);
    io.emit("status", { conectado: true, mensagem: "WhatsApp conectado!" });
    console.log("[WA] Conectado.");
    initStatusAgendamento();
  });
  waClient.on("disconnected", () => {
    waConectado = false;
    io.emit("status", { conectado: false, mensagem: "Desconectado. Reconectando..." });
    setTimeout(() => { if (!waConectado) initWA(true); }, 10000);
  });
  waClient.on("auth_failure", () => {
    io.emit("status", { conectado: false, mensagem: "Falha auth. Clique em Limpar sessão." });
  });
  waClient.on("message", handleMsg);
  waClient.initialize().catch(err => {
    console.error("[WA]", err.message); waClient = null;
    io.emit("status", { conectado: false, mensagem: "Erro ao iniciar. Clique em Limpar sessão." });
  });
}

// ═══════════════════════
//  HELPERS
// ═══════════════════════
const sleep = ms => new Promise(r => setTimeout(r, ms));

function logC(dados) {
  fs.appendFile(logFile(), JSON.stringify({ ts: new Date().toISOString(), ...dados }) + "\n", () => {});
  io.emit("log", { ts: new Date().toISOString(), ...dados });
}

function listaPedidos() {
  const l = [];
  for (const [n, p] of pedidosAbertos) l.push({ numero: n, ...p });
  return l.reverse();
}

function variaveis(txt, cfg) {
  const cardTxt = (cfg.cardapio || []).map(cat =>
    `${cat.categoria}\n` + (cat.itens || []).filter(i => !i.pausado).map(i =>
      `  • *${i.nome}* — ${i.preco}${i.tamanhos ? ` (${i.tamanhos})` : ""}`
    ).join("\n")
  ).join("\n\n");
  const promoTexto = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto).map(p=>"✨ "+p.texto).join("\n");
  return txt
    .replace(/{promocoes}/g,    promoTexto||"Sem promoções no momento")
    .replace(/{empresaNome}/g,  cfg.empresaNome || "")
    .replace(/{endereco}/g,     cfg.empresaEndereco || "")
    .replace(/{horario}/g,      cfg.horarioFuncionamento || "")
    .replace(/{telefone}/g,     cfg.empresaTelefone || "")
    .replace(/{taxaEntrega}/g,  cfg.taxaEntrega || "")
    .replace(/{tempoEntrega}/g, cfg.tempoEntrega || "")
    .replace(/{pedidoMinimo}/g, cfg.pedidoMinimo || "")
    .replace(/{pagamentos}/g,   cfg.pagamentos || "")
    .replace(/{pixChave}/g,     cfg.pixChave || "")
    .replace(/{cardapio}/g,     cardTxt);
}

function matchFluxo(txt, cfg) {
  const t = txt.trim().toLowerCase();
  for (const f of cfg.fluxos || []) {
    for (const g of f.gatilhos || []) {
      if (t === g.toLowerCase()) return f;
      try { const rx = new RegExp(`\\b${g.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")}\\b`,"i"); if (rx.test(t)) return f; } catch (_) {}
    }
  }
  return null;
}

async function chamarIA(numero, msg, cfg) {
  if (!groqClient || !cfg.useAI) return null;

  // Cardápio completo com descrições para a IA responder com mais detalhes
  const cardTxt = (cfg.cardapio || []).map(cat =>
    `[${cat.categoria}]: ` +
    (cat.itens||[]).filter(i=>!i.pausado).map(i =>
      `${i.nome} - ${i.preco}${i.descricao ? " ("+i.descricao+")" : ""}${i.tamanhos ? " ["+i.tamanhos+"]" : ""}`
    ).join(" | ")
  ).join("\n");

  const sys = `${cfg.promptSistema || "Você é atendente virtual de delivery. Seja simpático, natural e objetivo."}

=== EMPRESA ===
Nome: ${cfg.empresaNome}
Endereço: ${cfg.empresaEndereco}
Horário: ${cfg.horarioFuncionamento}
Telefone: ${cfg.empresaTelefone||""}
Taxa: ${cfg.taxaEntrega} | Tempo: ${cfg.tempoEntrega} | Mínimo: ${cfg.pedidoMinimo}
Pagamentos: ${cfg.pagamentos} | Pix: ${cfg.pixChave}

=== CARDÁPIO ===
${cardTxt}

=== REGRAS ===
1. Use APENAS preços e itens do cardápio acima. NUNCA invente.
2. Para pedidos responda: "Para fazer seu pedido, é só digitar *pedir* 😊"
3. Nunca colete endereço, telefone ou dados pessoais.
4. Para dúvidas sobre ingredientes, tamanhos ou detalhes use as descrições acima.
5. Resposta natural como atendente humano. Emojis com moderação. Máximo 4 linhas.
6. Se não souber algo, diga que vai verificar com a equipe.`;

  const hist = historicos.get(numero) || [];
  try {
    const r = await groqClient.chat.completions.create({
      model: cfg.model || "llama-3.3-70b-versatile",
      messages: [{ role:"system", content:sys }, ...hist, { role:"user", content:msg }],
      max_tokens: 600,
      temperature: 0.5,
    });
    return r.choices?.[0]?.message?.content?.trim() || null;
  } catch (e) { console.error("[IA]", e.message); return null; }
}

function addHist(numero, role, content) {
  const h = historicos.get(numero) || [];
  h.push({ role, content });
  if (h.length > 20) h.splice(0, h.length - 20);
  historicos.set(numero, h);
  clearTimeout(h._t);
  h._t = setTimeout(() => historicos.delete(numero), 2 * 3600000);
}

// ═══════════════════════
//  FLUXO DE PEDIDO PROFISSIONAL
//  boas_vindas → menu → cardapio_escolha → itens → rua_ou_pin → [bairro→num→tipo→complemento] → telefone → pagamento → [troco] → confirmacao
// ═══════════════════════

// ─── gatilhos ───
function querPedir(t) {
  const s = t.trim().toLowerCase();
  // Gatilhos explícitos
  if (["2","pedir","quero pedir","fazer pedido","novo pedido",
       "quero fazer pedido","iniciar pedido","fazer um pedido",
       "pedido","iniciar"].some(g => s === g || s.startsWith(g + " "))) return true;
  // Frases naturais de pedido
  if (/^(quero|queria|me manda|me traz|pode me mandar|gostaria de|vou querer|vou pedir|preciso de)\s+.{3,}/i.test(t.trim())) return true;
  return false;
}
function querCancelar(t) {
  return ["cancelar","cancela","desistir","nao quero","não quero","sair","voltar","menu"].some(g => t.toLowerCase().includes(g));
}

// ─── histórico do cliente ───
function salvarCliente(numero, pedido) {
  const num = numero.replace("@c.us","");
  const cli = clientesDB.get(num) || { numero:num, nome:"", pedidos:[], totalGasto:0 };
  cli.ultimoPedido = { ...pedido, data: new Date().toISOString() };
  cli.pedidos = [cli.ultimoPedido, ...(cli.pedidos||[])].slice(0,10);
  cli.totalPedidos = (cli.totalPedidos||0) + 1;
  clientesDB.set(num, cli);
  saveClientes();
}

function getCliente(numero) {
  const num = numero.replace("@c.us","");
  return clientesDB.get(num) || null;
}

// ─── calcular preço meio a meio ───
function calcularPrecoMeioAMeio(p1, p2, rule) {
  if (rule === "media") return (p1 + p2) / 2;
  return Math.max(p1, p2);
}

// Encontra item do cardápio por nome parcial (busca generosa)
function acharItem(nome, cfg) {
  const n = nome.toLowerCase().trim();
  // busca exata primeiro
  for (const cat of cfg.cardapio||[]) {
    for (const item of cat.itens||[]) {
      if (!item.pausado && item.nome.toLowerCase().includes(n.slice(0,6))) return item;
      if (!item.pausado && n.includes(item.nome.toLowerCase().slice(0,6))) return item;
    }
  }
  // busca por palavras-chave (ex: "marguerita" encontra "Margherita")
  const palavras = n.split(/\s+/).filter(p => p.length > 3);
  for (const cat of cfg.cardapio||[]) {
    for (const item of cat.itens||[]) {
      if (!item.pausado) {
        const nItem = item.nome.toLowerCase();
        if (palavras.some(p => nItem.includes(p) || levenshtein(p, nItem.slice(0,p.length)) <= 2)) return item;
      }
    }
  }
  return null;
}

// Distância de Levenshtein para busca aproximada
function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({length:m+1},(_,i)=>[i,...Array(n).fill(0)]);
  for (let j=0;j<=n;j++) dp[0][j]=j;
  for (let i=1;i<=m;i++) for (let j=1;j<=n;j++)
    dp[i][j] = a[i-1]===b[j-1] ? dp[i-1][j-1] : 1+Math.min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1]);
  return dp[m][n];
}

// Detecta pedido meio a meio separando a mensagem nos marcadores "meio/metade"
// Estratégia: divide o texto nos pontos "meio", pega o que vem ANTES e DEPOIS
// Ex: "pizza margarita MEIO pizza frango catupiry MEIO e 2 refri"
//      parte1="pizza margarita"  parte2="pizza frango catupiry"  resto="e 2 refri"
function detectarMeioAMeio(txt, cfg) {
  const s = txt.toLowerCase().trim();
  const temMeio = s.includes("meio") || s.includes("metade") || s.includes("1/2");
  if (!temMeio || !cfg) return { ehMeio:false };

  // Só processa se o contexto é pizza (contém "pizza" ou categoria pizza)
  const temPizza = s.includes("pizza") || (cfg.cardapio||[]).some(cat =>
    cat.categoria.toLowerCase().includes("pizza") &&
    (cat.itens||[]).some(i => s.includes(i.nome.toLowerCase().slice(0,5)))
  );
  if (!temPizza) return { ehMeio:false };

  // Todos os itens de pizza disponíveis
  const pizzas = (cfg.cardapio||[])
    .filter(cat => cat.categoria.toLowerCase().includes("pizza"))
    .flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado));

  if (pizzas.length === 0) return { ehMeio:false };

  // Função: achar qual pizza está numa substring de texto
  function acharPizzaNaTrecho(trecho) {
    const t = trecho.toLowerCase();
    let melhor = null, melhorScore = 0;
    for (const pizza of pizzas) {
      const palavras = pizza.nome.toLowerCase()
        .split(/\s+/)
        .filter(p => p.length > 3 && !["com","sem","pizza","grande","medio","pequeno"].includes(p));
      let score = 0;
      for (const pw of palavras) {
        if (t.includes(pw)) score += 3;
        else {
          // Busca aproximada (typos): ex "margarita" → "margherita"
          const tokens = t.split(/\s+/);
          for (const tok of tokens) {
            if (tok.length > 3 && levenshtein(tok, pw) <= 2) { score += 2; break; }
          }
        }
      }
      if (score > melhorScore) { melhorScore = score; melhor = pizza; }
    }
    return melhorScore >= 2 ? melhor : null;
  }

  // Separar nos marcadores de meio
  // Remove "pizza", tamanhos e marcadores para isolar os sabores
  const limpar = t => t.replace(/\b(pizza|meio|metade|1\/2|grande|gr|medio|m|pequeno|p|g|e\s)\b/gi,"").trim();

  // Divide: tudo antes do 1º "meio", entre 1º e 2º "meio", depois do 2º "meio"
  const partes = s.split(/\b(?:meio|metade|1\/2)\b/);
  // partes[0] = antes do 1º meio → sabor 1
  // partes[1] = entre 1º e 2º meio → pode ser sabor 2 ou vazio
  // partes[2] = depois do 2º meio → sabor 2 ou itens extras

  if (partes.length < 2) return { ehMeio:false };

  const item1 = acharPizzaNaTrecho(limpar(partes[0]));
  if (!item1) return { ehMeio:false };

  // Tentar achar item2 nos trechos seguintes
  let item2 = null;
  let restoIdx = 2; // índice onde começa o "resto" (itens não-pizza)
  for (let i = 1; i < partes.length; i++) {
    const candidato = acharPizzaNaTrecho(limpar(partes[i]));
    if (candidato && candidato.nome !== item1.nome) {
      item2 = candidato;
      restoIdx = i + 1;
      break;
    }
  }

  if (!item2) return { ehMeio:false };

  // Itens extras = o que sobrou depois do 2º "meio" (ex: "2 refrigerante coca")
  const restoTexto = partes.slice(restoIdx).join(" ").replace(/^\s*e\s*/i,"").trim();

  return { ehMeio:true, item1, item2, sabor1:item1.nome, sabor2:item2.nome, resto:restoTexto };
}

// ─── calcular tempo de preparo estimado ───
function calcularTempoPreparo(itensTxt, cfg) {
  const sep = itensTxt.includes(" | ") ? " | " : ",";
  const partes = (itensTxt||"").split(sep);
  let tempoMax = 0;
  let tempoTotal = 0;
  for (const parte of partes) {
    const p = parte.trim().toLowerCase();
    for (const cat of cfg.cardapio||[]) {
      for (const item of cat.itens||[]) {
        const n = item.nome.toLowerCase();
        if (p.includes(n.slice(0,6)) || n.includes(p.slice(0,6))) {
          const t = parseInt(item.tempoPreparo||0);
          if (t > tempoMax) tempoMax = t;
          tempoTotal += t;
        }
      }
    }
  }
  // Tempo = maior item + 30% dos demais (paralelo parcial)
  if (tempoMax === 0) return null;
  return tempoMax;
}

// ─── emitir contador de pedidos em andamento ───
function emitirContador() {
  io.emit("pedindo_agora", { total: estadosPedido.size });
}

// ── Timeout: cancela pedido abandonado após 30 min ──
const _timeouts = new Map();
function resetarTimeout(numero) {
  if (_timeouts.has(numero)) clearTimeout(_timeouts.get(numero));
  const t = setTimeout(async () => {
    if (!estadosPedido.has(numero)) return;
    const e = estadosPedido.get(numero);
    estadosPedido.delete(numero);
    emitirContador();
    try {
      if (waConectado && waClient && e?.itens) {
        await waClient.sendMessage(numero,
          `⏱️ Seu pedido foi cancelado por inatividade.\n\nDigite *oi* quando quiser recomeçar. 😊`
        );
      }
    } catch(_) {}
  }, 30 * 60 * 1000);
  _timeouts.set(numero, t);
}
function limparTimeout(numero) {
  if (_timeouts.has(numero)) { clearTimeout(_timeouts.get(numero)); _timeouts.delete(numero); }
}

// ─── calcular total dos itens pedidos ───
// IMPORTANTE: itens são separados por " | " para evitar conflito com vírgulas dos preços
function calcularTotal(itensTxt, cfg) {
  let total = 0;
  // Suporta tanto " | " quanto "," como separador (retrocompatibilidade)
  const sep = (itensTxt||"").includes(" | ") ? " | " : ",";
  const partes = (itensTxt||"").split(sep);
  for (const parte of partes) {
    const p = parte.trim();
    if (!p) continue;
    const pl = p.toLowerCase();

    // Se a linha já tem preço embutido (ex: "🍕 Pizza ½ ... — R$ 42,00")
    // extrair o valor diretamente
    const precoEmbutido = p.match(/R\$\s*([\d]+[,.]?[\d]*)/);
    if (p.includes("½") && precoEmbutido) {
      const val = parseFloat(precoEmbutido[1].replace(",","."));
      if (!isNaN(val)) { total += val; continue; }
    }

    const qtdM = pl.match(/^(\d+)x?\s+/);
    const qtd  = qtdM ? parseInt(qtdM[1]) : 1;
    let achou = false;
    for (const cat of cfg.cardapio||[]) {
      for (const item of cat.itens||[]) {
        if (item.pausado) continue;
        if (pl.includes(item.nome.toLowerCase().slice(0,6))) {
          const pr = parseFloat((item.preco||"").replace(/[^\d,.]/g,"").replace(",","."));
          if (!isNaN(pr)) { total += pr * qtd; achou = true; }
          break;
        }
      }
      if (achou) break;
    }
    // Se não achou no cardápio, tentar extrair preço embutido no texto (ex: promoções)
    // Formato: "Nome do item — R$ 30,00" ou "2x Nome — R$ 30,00"
    if (!achou && precoEmbutido) {
      const val = parseFloat(precoEmbutido[1].replace(",","."));
      if (!isNaN(val)) { total += val * qtd; }
    }
  }
  return total;
}

// ─── cardápio formatado ───
function cardResumido(cfg) {
  return (cfg.cardapio||[]).map((cat, ci) => {
    const ativos = (cat.itens||[]).filter(i => !i.pausado);
    if (!ativos.length) return null;
    return `*${cat.categoria}*\n` +
      ativos.map((i, ii) =>
        `  *${ci+1}.${ii+1}* ${i.nome} — *${i.preco}*` +
        (i.descricao ? `\n       _${i.descricao}_` : "") +
        (i.tamanhos  ? ` _(${i.tamanhos})_` : "")
      ).join("\n");
  }).filter(Boolean).join("\n\n");
}

// ─── menu de pagamento ───
function menuPag(cfg) {
  return (cfg.pagamentos||"Dinheiro,Cartão,Pix")
    .split(",").map((f,i) => `  *${i+1}* — ${f.trim()}`).join("\n");
}

// ─── resolver pagamento ───
function resolverPag(txt, cfg) {
  const formas = (cfg.pagamentos||"Dinheiro,Cartão,Pix").split(",").map(f=>f.trim());
  const s = txt.toLowerCase().trim().replace(/\.\s*$/, ""); // remove ponto final do áudio

  // ── Número da opção ──
  const n = parseInt(s);
  if (!isNaN(n) && n>=1 && n<=formas.length) return formas[n-1];

  // ── Match exato nas formas configuradas ──
  const encontrado = formas.find(f => s.includes(f.toLowerCase()));
  if (encontrado) return encontrado;

  // ── PIX — variações de áudio (Whisper transcreve de formas diferentes) ──
  const temPix = formas.some(f => f.toLowerCase().includes("pix"));
  if (temPix) {
    // "pix", "PIX", "Pix", "pics", "peak", "peaks", "pig", "pigs", etc.
    const pixRgx = /^(pix|pics?|peak|peaks?|pig|pigs?|pik|pikes?|piks?|pique|piques?|pit|pits?|pites?|pixes?|pis|fix|feat|feats?|feis|fex|fick|ficks?|pich|pichs?|pig[a-z]|p[iy][xkqg]|peeks?)$/i;
    if (pixRgx.test(s.replace(/[\s\.]/g,""))) return formas.find(f=>f.toLowerCase().includes("pix")) || "Pix";
    // "vou pagar no pix", "quero pix", "no pix", "pelo pix"
    if (/pix|pics?/i.test(s)) return formas.find(f=>f.toLowerCase().includes("pix")) || "Pix";
  }

  // ── DINHEIRO — variações de áudio ──
  const temDinheiro = formas.some(f => /dinheiro|espécie|especie|cash/i.test(f));
  if (temDinheiro) {
    if (/dinheiro|espécie|especie|cash|nota|trocado|em mão|na mão|físico/i.test(s)) {
      return formas.find(f=>/dinheiro|espécie|especie|cash/i.test(f)) || "Dinheiro";
    }
  }

  // ── CARTÃO — variações de áudio ──
  const temCartao = formas.some(f => /cart[aã]o|cartao|débito|debito|crédito|credito/i.test(f));
  if (temCartao) {
    if (/cart[aã]o|cartao|d[eé]bito|debito|cr[eé]dito|credito|maquininha|maquina|visa|master/i.test(s)) {
      return formas.find(f=>/cart[aã]o|cartao|débito|debito|crédito|credito/i.test(f)) || "Cartão";
    }
  }

  return null;
}

// ─── exibir cardápio completo ───
function mostrarCardapio(cfg) {
  const proms = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto);
  const promoStr = proms.length
    ? "\n\n🔥 *PROMOÇÕES DO DIA:*\n" + proms.map(p=>`  ✨ ${p.texto}`).join("\n")
    : "";
  return (
    `🍽️✨ *CARDÁPIO ${cfg.empresaNome||""}* ✨🍽️\n` +
    `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n` +
    `${cardResumido(cfg)}` +
    `${promoStr}\n\n` +
    `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
    `🛒 *O que vai querer hoje?*\n\n` +
    `💬 _Descreva seu pedido. Ex:_\n` +
    `💬 _"1 pizza calabresa G e 2 Coca-Cola"_\n\n` +
    `❌ _Digite_ *cancelar* _a qualquer momento._`
  );
}

// ─── resumo do pedido ───
function resumoPedido(e, cfg) {
  const loc = e.localizacao || {};
  let endFmt;
  if (loc.tipo === "pin") {
    endFmt = `📍 *Localização GPS* ✅\n   🗺️ ${loc.mapsUrl}`;
  } else {
    endFmt = `📍 *${loc.endereco||"—"}*`;
  }
  if (e.complemento) endFmt += `\n   🏢 ${e.complemento}`;
  if (e.referencia)  endFmt += `\n   📌 Ref: ${e.referencia}`;

  const total  = calcularTotal(e.itens, cfg);
  const taxa   = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
  const totG   = total + taxa;
  const valStr = total > 0
    ? `\n💰 *Subtotal:* R$ ${total.toFixed(2).replace(".",",")}\n` +
      `🛵 *Taxa:* ${cfg.taxaEntrega||"—"}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💵 *TOTAL: R$ ${totG.toFixed(2).replace(".",",")}*\n`
    : `\n🛵 *Taxa de entrega:* ${cfg.taxaEntrega||"—"}\n`;

  const trocoStr = e.troco  ? `\n💰 *Troco para:* R$ ${e.troco}` : "";
  const obsStr   = e.observacao ? `\n📝 *Obs:* ${e.observacao}` : "";

  return (
    `\n🧾✨ *RESUMO DO PEDIDO Nº ${e.numPedido}* ✨🧾\n` +
    `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n` +
    `🛒 *Seus itens:*\n_${e.itens}_\n` +
    `${valStr}\n` +
    `${endFmt}\n` +
    `📞 *Telefone:* ${e.telefone||"—"}\n` +
    `💳 *Pagamento:* ${e.pagamento}${trocoStr}${obsStr}\n` +
    `⏱️ *Previsão:* ${cfg.tempoEntrega||"—"}\n\n` +
    `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
    `👇 *Confira e responda:*\n\n` +
    `*1* ✅ Confirmar e enviar\n` +
    `*2* ✏️  Corrigir informações\n` +
    `*3* ➕ Adicionar mais itens\n` +
    `*4* 🗑️ Remover um item\n` +
    `*5* 🔄 Recomeçar do zero`
  );
}

// ── Valida e resolve item digitado pelo cliente ──
// Retorna { ok:true, item, nomeFinal } ou { ok:false, sugestoes }
// Extrai quantidade e nome — "2 X-Bacon Duplo" → { qtd:2, texto:"X-Bacon Duplo" }
function extrairQtd(txt) {
  const m = txt.trim().match(/^(\d+)\s+(.+)$/);
  if (m) return { qtd: Math.min(parseInt(m[1]), 20), texto: m[2].trim() };
  return { qtd: 1, texto: txt.trim() };
}

function validarItem(txt, cfg) {
  const s = txt.toLowerCase().trim();
  const todos = (cfg.cardapio||[]).flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado));

  // ── Reconhecer número de item ex: "3.1", "2.2" ──
  const mNum = s.match(/^(\d+)\.(\d+)$/);
  if (mNum) {
    const catIdx = parseInt(mNum[1]) - 1;
    const itemIdx = parseInt(mNum[2]) - 1;
    const cats = (cfg.cardapio||[]).filter(c => (c.itens||[]).some(i=>!i.pausado));
    const cat = cats[catIdx];
    if (cat) {
      const itensAtivos = (cat.itens||[]).filter(i=>!i.pausado);
      const item = itensAtivos[itemIdx];
      if (item) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
    return { ok:false, sugestoes:"" };
  }

  // 1. Match exato ou substring direto
  for (const item of todos) {
    const n = item.nome.toLowerCase();
    if (n === s || s.includes(n.slice(0,8)) || n.includes(s.slice(0,8))) {
      return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  // 2. Cada palavra principal do item encontrada na msg
  for (const item of todos) {
    const palavras = item.nome.toLowerCase().split(/\s+/).filter(p=>p.length>3);
    const acertos = palavras.filter(p => s.includes(p));
    if (acertos.length >= 1 && acertos.length >= Math.ceil(palavras.length*0.5)) {
      return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  // 3. Levenshtein — cada token da mensagem contra cada palavra do item
  const tokens = s.split(/\s+/).filter(t => t.length > 3);
  let melhor = null, melhorScore = 99;
  for (const item of todos) {
    const palavras = item.nome.toLowerCase().split(/\s+/).filter(p=>p.length>3);
    for (const tk of tokens) {
      for (const pw of palavras) {
        const d = levenshtein(tk, pw);
        if (d < melhorScore) { melhorScore = d; melhor = item; }
      }
    }
  }
  // Aceitar apenas se muito próximo (1 erro)
  if (melhor && melhorScore <= 1) {
    return { ok:true, item:melhor, nomeFinal:`${melhor.nome} — ${melhor.preco}` };
  }

  // Não encontrou — sugerir os mais parecidos
  const sugestoes = todos.slice(0,5).map((p,ii)=>`  *${ii+1}* — ${p.nome} (${p.preco})`).join("\n");
  return { ok:false, sugestoes };
}

// ═══════════════════════════════════════════════════
//  FLUXO DO PEDIDO — Linear, sem ambiguidade
//  itens → [mais_itens loop] → endereco → bairro
//  → numero → referencia → tipo → [complemento]
//  → telefone → pagamento → [troco] → observacao → confirmacao
// ═══════════════════════════════════════════════════

function querPedir(t) {
  const s = t.trim().toLowerCase();
  if (["2","pedir","quero pedir","fazer pedido","novo pedido",
       "quero fazer pedido","iniciar pedido","fazer um pedido",
       "pedido","iniciar"].some(g => s === g || s.startsWith(g+" "))) return true;
  if (/^(quero|queria|me manda|manda|pode me mandar|gostaria de|vou querer|vou pedir)\s+.{3,}/i.test(t.trim())) return true;
  return false;
}

function querPizzaMeio(t) {
  const s = t.trim().toLowerCase();
  return (s.includes("meio") || s.includes("metade") || s.includes("1/2"))
    && (s.includes("pizza") || s === "meio a meio" || s.startsWith("meio"));
}

function querCancelar(t) {
  const s = t.trim().toLowerCase();
  return ["cancelar","cancela","desistir","nao quero","não quero","sair"].some(g => s.includes(g));
}

function novoEstado(numPedido) {
  return {
    etapa:"itens", numPedido,
    itens:"", pagamento:"", troco:"", observacao:"",
    localizacao:null, rua:"", bairro:"", numEnd:"",
    tipoComp:"", complemento:"", referencia:"", telefone:"",
    itemPendente:null,    // item aguardando acompanhamentos
    acompSelecionados:[], // acompanhamentos já escolhidos
    qtdPendente:1,        // quantidade do item pendente
    inicio: new Date().toISOString()
  };
}

// ── Helper: verificar se item tem direito a acompanhamentos ──
// Item precisa ter maxAcomp > 0
// Lista de acompanhamentos vem do próprio item OU de config.acompanhamentos (lista global)
function temAcomp(item, cfg) {
  const max = parseInt(item.maxAcomp) || 0;
  if (max <= 0) return false;
  // Verifica se existe lista no item OU lista global no config
  const lista = item.acompanhamentos || cfg.acompanhamentos || [];
  return lista.length > 0;
}

// ── Helper: obter lista de acompanhamentos do item ──
function listaAcomp(item, cfg) {
  return item.acompanhamentos || cfg.acompanhamentos || [];
}

// ── Helper: montar mensagem de seleção de acompanhamentos ──
function msgAcomp(item, selecionados, qtd, cfg) {
  const lista  = listaAcomp(item, cfg);
  const max    = parseInt(item.maxAcomp) || lista.length;
  const restam = max - selecionados.length;

  // Mostrar em blocos de 10 para não ficar gigante
  const opcoes = lista.map((a, i) => {
    const marcado = selecionados.includes(a);
    return `*${i+1}* ${marcado ? "✅" : "⬜"} ${a}`;
  }).join("\n");

  const selStr = selecionados.length
    ? `\n✅ *Escolhidos (${selecionados.length}/${max}):* ${selecionados.join(", ")}`
    : "";

  return (
    `🍽️ *${qtd > 1 ? qtd+"x " : ""}${item.nome}* — ${item.preco}\n` +
    `🧩 *Escolha ${max} acompanhamento${max>1?"s":""}:*${selStr}\n\n` +
    `${opcoes}\n\n` +
    `_Faltam ${restam} escolha${restam!==1?"s":""}. Digite o número._\n` +
    (selecionados.length > 0
      ? `\n*0* ✅ Confirmar com estes`
      : `\n*0* ⏭️ Pular (sem acompanhamento)`)
  );
}

// ── Helper: finalizar item com acompanhamentos ──
function finalizarItemComAcomp(e, cfg, isExtra) {
  const item   = e.itemPendente;
  const qtd    = e.qtdPendente || 1;
  const acomps = e.acompSelecionados || [];

  const acompStr = acomps.length ? ` (+ ${acomps.join(", ")})` : "";
  const nomeItem = (qtd > 1 ? `${qtd}x ` : "") + `${item.nome}${acompStr} — ${item.preco}`;

  if (e.itens && !isExtra) {
    e.itens += " | " + nomeItem;
  } else if (isExtra) {
    e.itens += " | " + nomeItem;
  } else {
    e.itens = nomeItem;
  }

  e.itemPendente     = null;
  e.acompSelecionados = [];
  e.qtdPendente      = 1;
  e.etapa            = "mais_itens";
}

// Detecta intenção de remover um item
function querRemover(t) {
  const s = t.trim().toLowerCase();
  return ["tirar","remov","retir","cancela o","sem o","sem a","nao quero o",
          "não quero o","tira o","tira a","exclu"].some(g => s.includes(g));
}

// Extrai qual item remover comparando com o pedido atual
function extrairItemRemover(txt, itensStr) {
  const s = txt.toLowerCase();
  const itens = itensStr.split(",").map(i => i.trim()).filter(Boolean);
  for (const item of itens) {
    const nome = item.replace(/^[0-9]+\s+/,"").split("—")[0].trim().toLowerCase();
    if (nome.length > 2 && s.includes(nome.slice(0,6))) return item.trim();
    const palavras = nome.split(/\s+/).filter(p => p.length > 3);
    if (palavras.some(p => s.includes(p))) return item.trim();
  }
  return null;
}

// Detecta intenção de recomeçar
function querRecomecar(t) {
  const s = t.trim().toLowerCase();
  return ["recome","começar de novo","comecar de novo","tudo de novo",
          "apaga tudo","zerar","do zero","refazer","limpa"].some(g => s.includes(g));
}

// Palavras que significam "não quero mais / continuar"
// ⚠️ "não" e "n" são interpretados como CONTINUAR no contexto "mais alguma coisa?"
// Mas se vierem ISOLADOS após "mais alguma coisa?", devem ser interpretados como "não quero mais"
function querContinuar(t) {
  const s = t.trim().toLowerCase();
  // Extensões: continuar pedido, fechar pedido, confirmar pedido, etc.
  const extFechar = ["fechar","finaliz","confirm","encerra","conclui","pronto"];
  const extContinuar = ["continu","mais","adiciona","outro","outro item","mais algo"];
  
  // "fechar o pedido" ou "confirmar pedido" → vai para confirmação
  if (extFechar.some(p => s.includes(p)) && s.includes("pedido")) return "fechar";
  
  // "continuar" ou "continua" sozinho → continuar fluxo
  if (extContinuar.some(p => s.includes(p)) && !s.includes("fechar")) return "continuar";
  
  // ── CORREÇÃO: "não" / "n" isolado = NÃO QUERO MAIS → NÃO é "continuar" ──
  // Apenas quando a mensagem É exata "não" ou "n" (comuns em áudios que confirmam)
  // Mas se vier depois de "mais alguma coisa?" e o cliente disser "não" → deve PARAR de adicionar
  // A lógica correta: "não" como resposta única = parar de adicionar = NÃO continuar
  // NOVO: verificar se o cliente está respondendo "não" à pergunta de adicionar mais
  // Contexto: etapa = "mais_itens" e pergunta foi "deseja mais algo?"
  // Se o cliente disser "não" → deve ir para endereço, não continuar adicionando
  // 
  // OLD: return s === "não" || s === "nao" || s === "n" || s === "nn" → CONTINUAR (BUG!)
  // NEW: "não"/"nao" isolado = continuar para próxima etapa (endereço)
  // Mas na dúvida, "não" significa "não quero mais" → seguir em frente (fechar pedido)
  if (s === "não" || s === "nao" || s === "n" || s === "nn") return "fechar";
  
  return s === "2" || s === "ok" || s === "pronto" || s === "s\u00f3" || s === "so"
    || s.includes("continu") || s.includes("pronto") || s.includes("s\u00f3 isso")
    || s.includes("so isso") || s.includes("pode ser") || s.includes("t\u00e1 bom")
    || s.includes("ta bom") || s.includes("tudo") || s.includes("finaliz") ? "continuar" : false;
}

async function fluxoPedido(numero, txt, msg, cfg) {
  let e = estadosPedido.get(numero);

  // Cancelar em QUALQUER etapa (incluindo pizza)
  if (e && querCancelar(txt)) {
    estadosPedido.delete(numero);
    limparTimeout(numero);
    emitirContador();
    return `Pedido cancelado! 😊\nDigite *oi* para o menu ou *pedir* para um novo pedido.`;
  }

  // Recomeçar em QUALQUER etapa
  if (e && querRecomecar(txt)) {
    estadosPedido.set(numero, novoEstado(e.numPedido));
    return `✅ Recomeçando do zero! 😊\n\n` + mostrarCardapio(cfg);
  }

  // ── Ver cardápio durante o pedido ──
  if (e) {
    const sLowC = txt.trim().toLowerCase();
    const querVerCard = [
      "cardápio","cardapio","ver cardápio","ver cardapio","1","menu",
      "o que tem","o que vocês têm","o que voces tem","quais são","quais sao",
      "lista","produtos","itens disponíveis","itens disponiveis"
    ].some(g => sLowC === g || sLowC === g.trim());
    if (querVerCard && e.etapa === "itens") {
      return mostrarCardapio(cfg);
    }
  }

  // ── MELHORIA 6: Ver pedido atual ──
  if (e && e.itens) {
    const sLow6 = txt.trim().toLowerCase();
    if (["meu pedido","ver pedido","meu carrinho","o que pedi","o que eu pedi",
         "resumo","meus itens"].some(g => sLow6.includes(g))) {
      const sub  = calcularTotal(e.itens, cfg);
      const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
      return (
        `🛒 *Seu pedido até agora:*\n\n` +
        `_${e.itens}_${subT}\n\n` +
        `_Continue de onde parou ou escolha:_\n` +
        `*1* ➕ Adicionar  |  *2* ✅ Continuar  |  *4* 🔄 Recomeçar`
      );
    }
  }

  // ── Acompanhar pedido ──
  if (e && e.etapa === "acompanhar") {
    const n = txt.trim();
    let encontrado = null;
    for (const [num, p] of pedidosAbertos) {
      if (p.numPedido === n || num.replace(/[^0-9]/g,"").includes(n.replace(/[^0-9]/g,""))) {
        encontrado = { numero: num, ...p }; break;
      }
    }
    estadosPedido.delete(numero);
    if (encontrado) {
      const hora = new Date(encontrado.confirmado).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
      return (
        `✅ *Pedido Nº ${encontrado.numPedido} encontrado!*

` +
        `🛒 *Itens:* ${encontrado.itens}
` +
        `⏱️ *Confirmado às:* ${hora}
` +
        `📍 *Endereço:* ${encontrado.endereco}
` +
        `🚦 *Status:* Em preparo / A caminho

` +
        `_Qualquer dúvida chame um atendente!_ 😊`
      );
    }
    return (
      `🔍 Não encontrei o pedido *${n}*.

` +
      `Verifique o número ou aguarde — um atendente verificará pra você! 😊`
    );
  }

  // Remover item (funciona em qualquer etapa que tenha itens)
  if (e && e.itens && querRemover(txt)) {
    const itemRemover = extrairItemRemover(txt, e.itens);
    if (!itemRemover) {
      const lista = (e.itens.includes(" | ")?e.itens.split(" | "):e.itens.split(",")).map((it,i)=>`  *${i+1}* — ${it.trim()}`).join("\n");
      e.etapa = "remover_item"; estadosPedido.set(numero, e);
      return `🗑️ *Qual item deseja remover?*\n\n${lista}\n\n_Digite o número ou o nome_`;
    }
    const arr = (e.itens.includes(" | ")?e.itens.split(" | "):e.itens.split(",")).map(i=>i.trim()).filter(i=>i!==itemRemover);
    if (arr.length === 0) {
      estadosPedido.set(numero, novoEstado(e.numPedido));
      return `🗑️ *${itemRemover}* removido.\n\nSeu pedido ficou vazio! Vamos recomeçar:\n\n` + mostrarCardapio(cfg);
    }
    e.itens = arr.join(", ");
    e.etapa = "mais_itens";
    estadosPedido.set(numero, e);
    const sub  = calcularTotal(e.itens, cfg);
    const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
    const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
    return (
      `✅ *${itemRemover}* removido!\n\n` +
      `*Pedido:* _${e.itens}_${subT}\n\n` +
      `*1* ➕ Adicionar mais  |  *2* ✅ Continuar  |  *3* 🗑️ Remover mais`
    );
  }


  // FEAT 3: repetir último pedido
  if (!e && /^(repetir|repetir pedido|quero repetir)$/i.test(txt.trim())) {
    const cli = getCliente(numero);
    if (cli?.ultimoPedido?.itens) {
      const numP3 = String(Date.now()).slice(-5);
      const est3  = novoEstado(numP3);
      est3.itens  = cli.ultimoPedido.itens;
      est3.etapa  = "mais_itens";
      estadosPedido.set(numero, est3);
      return (
        `✅ *Último pedido carregado:*\n_${est3.itens}_\n\n` +
        `*1* ➕ Adicionar mais  |  *2* ✅ Continuar  |  *4* 🔄 Recomeçar`
      );
    }
    return `Não encontrei pedidos anteriores 😊\nDigite *pedir* para fazer um novo pedido!`;
  }

  // Iniciar
  if (!e && querPedir(txt)) {
    const numP = String(Date.now()).slice(-5);
    const estado = novoEstado(numP);
    estadosPedido.set(numero, estado);
    e = estadosPedido.get(numero);
    emitirContador();

    // Detectar intenção de pizza meio a meio já no gatilho (ex: "pedir meio a meio")
    const sMeio = txt.toLowerCase();
    const querMeio = (sMeio.includes("meio") || sMeio.includes("metade"))
      && (sMeio.includes("pizza") || (cfg.cardapio||[]).some(c=>c.categoria.toLowerCase().includes("pizza")));
    if (querMeio) {
      e.etapa = "pizza_sabor1";
      estadosPedido.set(numero, e);
      const pizzas = (cfg.cardapio||[])
        .filter(cat=>cat.categoria.toLowerCase().includes("pizza"))
        .flatMap(cat=>(cat.itens||[]).filter(i=>!i.pausado));
      const lista = pizzas.map((p,i)=>`  *${i+1}* — ${p.nome} — *${p.preco}*`).join("\n");
      return (
        `🍕 *Pizza Meio a Meio*\n\n` +
        `Qual o *1º sabor?*\n\n` +
        `${lista}\n\n` +
        `_Digite o número ou o nome_`
      );
    }
    return mostrarCardapio(cfg);
  }

  if (!e) return null;

  const salvar = () => { estadosPedido.set(numero, e); resetarTimeout(numero); };

  // ══════════════════════════════════════════════════════
  //  PIZZA MEIO A MEIO — 3 etapas: sabor1 → sabor2 → tamanho
  // ══════════════════════════════════════════════════════

  // Helper: buscar pizza por número ou texto
  function buscarPizza(input, lista) {
    const n = parseInt(input.trim());
    if (!isNaN(n) && n >= 1 && n <= lista.length) return lista[n-1];
    const sl = input.toLowerCase();
    // Busca direta por nome
    for (const pz of lista) {
      const nomes = pz.nome.toLowerCase().split(/\s+/).filter(p=>p.length>3);
      if (nomes.some(nm => sl.includes(nm))) return pz;
    }
    // Busca aproximada (typos)
    for (const pz of lista) {
      const nomes = pz.nome.toLowerCase().split(/\s+/).filter(p=>p.length>3);
      const tokens = sl.split(/\s+/);
      for (const tk of tokens) {
        if (tk.length > 3 && nomes.some(nm => levenshtein(tk, nm) <= 2)) return pz;
      }
    }
    return null;
  }

  // Helper: montar lista numerada de pizzas
  function listaPizzas(lista) {
    return lista.map((p,i)=>`  *${i+1}* — ${p.nome} — *${p.preco}*`).join("\n");
  }

  // Helper: extrair preço por tamanho
  function precoPizzaTam(item, tamKey) {
    if (!item) return 0;
    if (item.precos && item.precos[tamKey]) {
      return parseFloat((item.precos[tamKey]||"").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
    }
    // Fallback: tentar extrair do campo preco ("R$ 25,00 / 35,00 / 42,00")
    const idx = tamKey==="P"?0:tamKey==="M"?1:2;
    const partes = (item.preco||"").split("/");
    if (partes[idx]) {
      const v = parseFloat(partes[idx].replace(/[^\d,.]/g,"").replace(",","."));
      if (!isNaN(v) && v > 0) return v;
    }
    return parseFloat((item.preco||"").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
  }

  // ── ETAPA: pizza_sabor1 ──
  if (e.etapa === "pizza_sabor1") {
    const todasPizzas = (cfg.cardapio||[])
      .filter(cat => cat.categoria.toLowerCase().includes("pizza"))
      .flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado));

    // ── Sempre tentar número primeiro (1, 2, 3...) ──
    let achado = null;
    const nTxt = parseInt(txt.trim());
    if (!isNaN(nTxt) && nTxt >= 1 && nTxt <= todasPizzas.length) {
      achado = todasPizzas[nTxt - 1];
    } else {
      // Filtrar palavras genéricas para buscar por nome
      const palavrasGenericas = ["pizza","meio","metade","a","1/2","half","e","de","ao","com","sem","quero","pedir"];
      const tokensMsg = txt.trim().toLowerCase().split(/\s+/);
      const tokensSabor = tokensMsg.filter(t => !palavrasGenericas.includes(t) && t.length > 2);
      if (tokensSabor.length > 0) {
        achado = buscarPizza(tokensSabor.join(" "), todasPizzas);
      }
    }

    if (!achado) {
      return (
        `🍕 *Pizza Meio a Meio*\n\n` +
        `Qual o *1º sabor?*\n\n` +
        `${listaPizzas(todasPizzas)}\n\n` +
        `_Digite o número_ ☝️`
      );
    }
    e.pizzaSabor1 = achado;
    e.etapa = "pizza_sabor2";
    salvar();
    const resto = todasPizzas.filter(p=>p.nome!==achado.nome);
    return (
      `✅ *1º sabor:* ${achado.nome}\n\n` +
      `🍕 *Qual o 2º sabor?*\n\n` +
      `${listaPizzas(resto)}\n\n` +
      `_Digite o número_ ☝️`
    );
  }

  // ── ETAPA: pizza_sabor2 ──
  if (e.etapa === "pizza_sabor2") {
    const todasPizzas = (cfg.cardapio||[])
      .filter(cat => cat.categoria.toLowerCase().includes("pizza"))
      .flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado))
      .filter(p=>p.nome !== e.pizzaSabor1?.nome);

    // Tentar por número primeiro, depois por nome
    const n2 = parseInt(txt.trim());
    let achado = (!isNaN(n2) && n2 >= 1 && n2 <= todasPizzas.length)
      ? todasPizzas[n2-1]
      : buscarPizza(txt, todasPizzas);

    if (!achado) {
      return (
        `🍕 *Qual o 2º sabor?*\n\n` +
        `${listaPizzas(todasPizzas)}\n\n` +
        `_Digite o número_ ☝️`
      );
    }
    e.pizzaSabor2 = achado;
    e.etapa = "pizza_tamanho";
    salvar();
    const item1 = e.pizzaSabor1;
    return (
      `✅ *2º sabor:* ${achado.nome}\n\n` +
      `🍕 *½ ${item1.nome}*\n` +
      `🍕 *½ ${achado.nome}*\n\n` +
      `📏 *Tamanho da pizza?*\n\n` +
      `*1* — 🍕 Pequena\n` +
      `*2* — 🍕 Média\n` +
      `*3* — 🍕 Grande`
    );
  }

  // ── ETAPA: pizza_tamanho ──
  if (e.etapa === "pizza_tamanho") {
    const op = txt.trim().toLowerCase();
    const tamKey = (op==="1"||op.includes("pequ")||op==="p") ? "P"
      : (op==="2"||op.includes("medi")||op==="m") ? "M"
      : (op==="3"||op.includes("gran")||op==="g") ? "G"
      : null;
    if (!tamKey) {
      // Cancelar ou recomeçar dentro da etapa tamanho
      if (querCancelar(txt)) {
        estadosPedido.delete(numero);
        return `Pedido cancelado! 😊\nDigite *oi* para o menu.`;
      }
      if (querRecomecar(txt)) {
        estadosPedido.set(numero, novoEstado(e.numPedido));
        return `✅ Recomeçando!\n\n` + mostrarCardapio(cfg);
      }
      return (
        `📏 *Qual o tamanho da pizza?*\n\n` +
        `*1* — 🍕 Pequena\n` +
        `*2* — 🍕 Média\n` +
        `*3* — 🍕 Grande\n\n` +
        `_Digite 1, 2 ou 3_`
      );
    }
    const tamNome = tamKey==="P"?"Pequena":tamKey==="M"?"Média":"Grande";
    const item1   = e.pizzaSabor1;
    const item2   = e.pizzaSabor2;
    const rule    = cfg.ruleMeioAMeio || "maior";
    const pr1     = precoPizzaTam(item1, tamKey);
    const pr2     = precoPizzaTam(item2, tamKey);
    const prF     = calcularPrecoMeioAMeio(pr1, pr2, rule);
    const ruleStr = rule==="maior"
      ? `_(maior: ${pr1>=pr2?item1.nome:item2.nome})_`
      : `_(média dos dois)_`;

    const pizzaStr = `🍕 Pizza ${tamNome} ½ ${item1.nome} + ½ ${item2.nome} — R$ ${prF.toFixed(2).replace(".",",")}`;

    // Substituir a linha provisória — aceita "R$ ?" ou qualquer valor
    if (e.itens && e.itens.includes("R$ ?")) {
      e.itens = e.itens.replace(/🍕 Pizza ½ .+ — R\\$ \?/, pizzaStr);
    } else if (e.itens && e.itens.includes("½")) {
      e.itens = e.itens.replace(/🍕 Pizza ½ .+ — R\\$ [\d,.]+/, pizzaStr);
    } else {
      e.itens = e.itens ? e.itens + " | " + pizzaStr : pizzaStr;
    }

    e.etapa = "mais_itens";
    salvar();

    const sub  = calcularTotal(e.itens, cfg);
    const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
    const totG = sub + taxa;
    return (
      `✅ *Pizza ${tamNome} — R$ ${prF.toFixed(2).replace(".",",")}* ${ruleStr}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `🛒 *Pedido:*\n_${e.itens}_\n\n` +
      (sub>0?`💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa R$ ${taxa.toFixed(2).replace(".",",")} = *R$ ${totG.toFixed(2).replace(".",",")}*\n\n`:"") +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `*1* ➕ Adicionar mais itens\n` +
      `*2* ✅ Continuar para entrega\n` +
      `*3* 🗑️ Remover um item\n` +
      `*4* 🔄 Recomeçar`
    );
  }

  // ── ETAPA: acompanhamentos ──
  // Cliente está escolhendo acompanhamentos de um item
  if (e.etapa === "acompanhamentos") {
    const item  = e.itemPendente;
    if (!item) { e.etapa = "itens"; salvar(); return mostrarCardapio(cfg); }

    const lista = listaAcomp(item, cfg);
    const max   = parseInt(item.maxAcomp) || lista.length;
    const op    = txt.trim();
    const n     = parseInt(op);

    // 0 = confirmar / pular
    if (op === "0" || op.toLowerCase() === "confirmar" || op.toLowerCase() === "pular") {
      const isExtra = !!e.itens;
      finalizarItemComAcomp(e, cfg, isExtra);
      salvar();
      const sub  = calcularTotal(e.itens, cfg);
      const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
      const acompStr = (e.acompSelecionados||[]).length
        ? `\n🧩 *Acompanhamentos:* ${(e.acompSelecionados||[]).join(", ")}`
        : "";
      // Recalcular após finalizar (e.acompSelecionados já foi zerado)
      const itemFinal = e.itens.split(" | ").pop();
      return (
        `🛒✅ *Adicionado!*\n_${itemFinal}_${subT}\n\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
        `👇 *Deseja mais alguma coisa?*\n\n` +
        `*1* ➕ Adicionar mais itens\n` +
        `*2* ✅ Continuar para entrega\n` +
        `*3* 🗑️ Remover item\n` +
        `*4* 🔄 Recomeçar`
      );
    }

    // Número de opção
    if (!isNaN(n) && n >= 1 && n <= lista.length) {
      const escolha = lista[n - 1];
      const selecionados = e.acompSelecionados || [];

      if (selecionados.includes(escolha)) {
        // Desmarcar
        e.acompSelecionados = selecionados.filter(a => a !== escolha);
      } else if (selecionados.length < max) {
        // Marcar
        e.acompSelecionados = [...selecionados, escolha];
      } else {
        // Já atingiu o máximo
        salvar();
        return (
          `⚠️ Você já escolheu o máximo de *${max}* acompanhamento${max>1?"s":""}!\n\n` +
          msgAcomp(item, e.acompSelecionados, e.qtdPendente, cfg) +
          `\n\nDigite *0* para confirmar ou desmarque um antes de adicionar.`
        );
      }
      salvar();

      // Se atingiu o máximo, confirmar automaticamente
      if (e.acompSelecionados.length === max) {
        const isExtra = !!e.itens;
        const acompParaMostrar = [...e.acompSelecionados];
        finalizarItemComAcomp(e, cfg, isExtra);
        salvar();
        const sub  = calcularTotal(e.itens, cfg);
        const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
        const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
        return (
          `✅ *${max} acompanhamento${max>1?"s":""}:* ${acompParaMostrar.join(", ")}\n\n` +
          `🛒 _${e.itens.split(" | ").pop()}_${subT}\n\n` +
          `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
          `👇 *Deseja mais alguma coisa?*\n\n` +
          `*1* ➕ Mais itens  |  *2* ✅ Continuar  |  *3* 🗑️ Remover  |  *4* 🔄 Recomeçar`
        );
      }

      return msgAcomp(item, e.acompSelecionados, e.qtdPendente, cfg);
    }

    // Entrada inválida
    return msgAcomp(item, e.acompSelecionados || [], e.qtdPendente||1, cfg);
  }

  // ── ETAPA: itens ──
  // Cliente viu o cardápio e digita o que quer
  if (e.etapa === "itens") {
    // Se já tem itens e cliente diz "continua" ou "fechar pedido"
    if (e.itens) {
      const continuar = querContinuar(txt);
      const opLow = txt.trim().toLowerCase();
      
      // "fechar o pedido" ou similar → ir para confirmação
      if (continuar === "fechar" || opLow.includes("fechar") || opLow.includes("confirm")) {
        e.etapa = "confirmacao";
        salvar();
        return resumoPedido(e, cfg);
      }
      
      // "continua" ou "mais" → ir para mais_itens (perguntar se quer mais)
      if (continuar === "continuar" || opLow.includes("continu") || opLow.includes("mais") || opLow.includes("adiciona")) {
        e.etapa = "mais_itens";
        salvar();
        const sub  = calcularTotal(e.itens, cfg);
        const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(","," .")) || 0;
        return (
          `🛒 *Itens no seu pedido:*\n_${e.itens}_\n\n` +
          `💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")}\n\n` +
          `➕ Deseja adicionar mais algo?\n` +
          `*1* Sim, adicionar mais\n` +
          `*2* ✅ Não, continuar para entrega`
        );
      }
    }
    
    if (txt.length < 3) return `Por favor, descreva o que deseja pedir 😊`;

    // Detectar pizza meio a meio dentro da etapa itens → redirecionar para fluxo guiado
    if (querPizzaMeio(txt)) {
      e.etapa = "pizza_sabor1";
      salvar();
      const todasPizzas = (cfg.cardapio||[])
        .filter(cat=>cat.categoria.toLowerCase().includes("pizza"))
        .flatMap(cat=>(cat.itens||[]).filter(i=>!i.pausado));
      return (
        `🍕 *Pizza Meio a Meio — 1º Sabor*\n\n` +
        `${listaPizzas(todasPizzas)}\n\n` +
        `_Digite o número da opção_ ☝️`
      );
    }
    const paus = (cfg.cardapio||[]).flatMap(c=>(c.itens||[]).filter(i=>i.pausado).map(i=>i.nome));
    const achP = paus.find(p => txt.toLowerCase().includes(p.toLowerCase().slice(0,5)));
    if (achP) return `⚠️ *${achP}* está indisponível hoje.\nEscolha outro item 😊`;

    // Verificar meio a meio
    const mam = detectarMeioAMeio(txt, cfg);
    if (mam.ehMeio) {
      const item1 = acharItem(mam.sabor1, cfg);
      const item2 = acharItem(mam.sabor2, cfg);
      if (!item1 || !item2) {
        // Não achou um dos sabores, pedir confirmação
        const nf = !item1 ? mam.sabor1 : mam.sabor2;
        return (
          `🍕 Não encontrei *"${nf}"* no cardápio.

` +
          `Confira os sabores disponíveis:

` +
          `${cardResumido(cfg)}

` +
          `_Digite novamente o pedido meio a meio:_
` +
          `_Ex: "meio calabresa meio frango G"_`
        );
      }
      const pr1  = parseFloat((item1.preco||"").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const pr2  = parseFloat((item2.preco||"").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const rule = cfg.ruleMeioAMeio || "maior";
      const prFinal = calcularPrecoMeioAMeio(pr1, pr2, rule);
      const ruleStr = rule === "maior"
        ? `_Cobrado pelo maior valor (${pr1>pr2?item1.nome:item2.nome})_`
        : `_Cobrado pela média dos dois sabores_`;

      const pizzaStr = `🍕 Pizza ½ ${item1.nome} + ½ ${item2.nome} — R$ ${prFinal.toFixed(2).replace(".",",")}`;

      // Itens extras: o que o detectarMeioAMeio separou como "resto"
      // Ex: "2 refrigerante coca" ou "suco laranja"
      let itensExtras = "";
      const restoTxt = (mam.resto||"").trim();
      if (restoTxt.length > 2) {
        // Verificar se o resto contém algum item do cardápio (exceto pizzas)
        const naoE = (cfg.cardapio||[])
          .filter(cat => !cat.categoria.toLowerCase().includes("pizza"))
          .flatMap(cat => (cat.itens||[]).filter(i=>!i.pausado));
        const temItem = naoE.some(i => restoTxt.toLowerCase().includes(i.nome.toLowerCase().slice(0,5)));
        const temNum  = /\d/.test(restoTxt);
        if (temItem || temNum) itensExtras = restoTxt;
      }

      e.itens  = itensExtras ? `${pizzaStr}, ${itensExtras}` : pizzaStr;
      e.etapa  = "mais_itens";
      salvar();

      const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
      const totalComExtras = calcularTotal(e.itens, cfg);
      const totalFmt = totalComExtras + taxa;
      return (
        `✅ *Pizza meio a meio anotada!*

` +
        `🍕 ½ *${item1.nome}* + ½ *${item2.nome}*
` +
        `💰 *Valor da pizza:* R$ ${prFinal.toFixed(2).replace(".",",")} ${ruleStr}
` +
        (itensExtras ? `➕ *Mais itens:* ${itensExtras}
` : "") +
        `🛵 Taxa: ${cfg.taxaEntrega||"—"} = *Total: R$ ${totalFmt.toFixed(2).replace(".",",")}*

` +
        `━━━━━━━━━━━━━━━━━━━━━━
` +
        `Deseja adicionar mais alguma coisa?

` +
        `*1* — ➕ Adicionar mais
` +
        `*2* — ✅ Continuar
` +
        `*3* — 🗑️ Remover item
` +
        `*4* — 🔄 Recomeçar`
      );
    }

    // ═══════════════════════════════════════════════════════════
    // MULTI-ITEMS: detectar "2x item e 3x item2" ou "2 refri, 2 x-bacon"
    // ═══════════════════════════════════════════════════════════
    // Quebrar por " e " ou ", " para processar múltiplos itens de uma vez
    const multiMatch = txt.match(/(\d+)\s*(?:x\s*)?(.+?)(?:\s+e\s+|\s*,\s*|\s+e\s+)(\d+)\s*(?:x\s*)?(.+?)$/i);
    if (multiMatch || txt.includes(" e ") || (txt.includes(",") && !txt.includes("meio a meio"))) {
      // Tentar dividir por " e " ou ", " 
      let partes = [];
      if (txt.includes(" e ")) {
        partes = txt.split(/\s+e\s+/i);
      } else if (txt.includes(",")) {
        partes = txt.split(/,\s*/);
      }
      
      if (partes.length >= 2) {
        // Processar cada parte individualmente
        const resultados = [];
        const erros = [];
        
        for (const parte of partes) {
          const parteTrim = parte.trim();
          if (parteTrim.length < 2) continue;
          
          const { qtd: qtdP, texto: txtP } = extrairQtd(parteTrim);
          const valP = validarItem(txtP, cfg);
          
          if (!valP.ok) {
            erros.push(parteTrim);
            continue;
          }
          if (valP.item.pausado) {
            erros.push(`${valP.item.nome} (indisponível)`);
            continue;
          }
          
          // Verificar se tem acompanhamentos
          if (temAcomp(valP.item, cfg)) {
            e.itemPendente = valP.item;
            e.qtdPendente = qtdP;
            e.acompSelecionados = [];
            e.etapa = "acompanhamentos";
            salvar();
            return (
              `✅ *${qtdP > 1 ? qtdP+"x " : ""}${valP.item.nome}* adicionado!\n
` +
              msgAcomp(valP.item, [], qtdP, cfg)
            );
          }
          
          const nomeItemP = qtdP > 1
            ? `${qtdP}x ${valP.item.nome} — ${valP.item.preco}`
            : `${valP.item.nome} — ${valP.item.preco}`;
          resultados.push(nomeItemP);
        }
        
        if (erros.length > 0 && resultados.length === 0) {
          return (
            `😅 Não encontrei nenhum item válido no seu pedido.\n` +
            `Itens não reconhecidos: *${erros.join(", ")}*\n
` +
            `${cardResumido(cfg)}`
          );
        }
        
        if (resultados.length > 0) {
          // Adicionar todos os itens ao pedido
          for (const itemStr of resultados) {
            e.itens = e.itens ? `${e.itens}, ${itemStr}` : itemStr;
          }
          e.etapa = "mais_itens";
          salvar();
          
          const sub = calcularTotal(e.itens, cfg);
          const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(","," .")) || 0;
          const subTxt = sub > 0
            ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa R$ ${taxa.toFixed(2).replace(".",",")} = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*`
            : "";
          
          let msgResp = `🛒✅ *Itens adicionados:*\n`;
          for (const itemStr of resultados) {
            msgResp += `  ✓ ${itemStr}\n`;
          }
          if (erros.length > 0) {
            msgResp += `\n⚠️ *Não reconhecido:* ${erros.join(", ")}\n`;
          }
          msgResp += `${subTxt}\n
`;
          msgResp += `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n`;
          msgResp += `👇 *Deseja mais alguma coisa?*\n\n`;
          msgResp += `*1* ➕ Adicionar mais itens\n`;
          msgResp += `*2* ✅ Continuar para entrega\n`;
          msgResp += `*3* 🗑️ Remover item\n`;
          msgResp += `*4* 🔄 Recomeçar`;
          
          return msgResp;
        }
      }
    }
    
    // ── Processar item único (comportamento original) ──
    // Extrair quantidade e validar item
    const { qtd: qtdI, texto: txtI } = extrairQtd(txt);
    const valI = validarItem(txtI, cfg);
    if (!valI.ok) {
      return (
        `😅 Não encontrei *"${txt}"* no cardápio.\n\n` +
        `Confira os itens disponíveis e peça pelo nome ou número:\n\n` +
        `${cardResumido(cfg)}`
      );
    }
    if (valI.item.pausado) return `⚠️ *${valI.item.nome}* está indisponível hoje. Escolha outro 😊`;

    const corrigiuI = valI.item.nome.toLowerCase() !== txtI.toLowerCase();
    const avisoI = corrigiuI ? `\n_✏️ Entendi como: *${valI.item.nome}*_` : "";

    // ── Verificar se tem acompanhamentos para escolher ──
    if (temAcomp(valI.item, cfg)) {
      e.itemPendente      = valI.item;
      e.qtdPendente       = qtdI;
      e.acompSelecionados = [];
      e.etapa             = "acompanhamentos";
      salvar();
      return (
        `✅ *${qtdI > 1 ? qtdI+"x " : ""}${valI.item.nome}* adicionado!${avisoI}\n\n` +
        msgAcomp(valI.item, [], qtdI, cfg)
      );
    }

    // Adicionar ao pedido (preserva itens anteriores)
    const nomeItemI = qtdI > 1
      ? `${qtdI}x ${valI.item.nome} — ${valI.item.preco}`
      : `${valI.item.nome} — ${valI.item.preco}`;
    e.itens = e.itens ? `${e.itens}, ${nomeItemI}` : nomeItemI;
    e.etapa = "mais_itens";
    salvar();

    const sub  = calcularTotal(e.itens, cfg);
    const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
    const subTxt = sub > 0
      ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa R$ ${taxa.toFixed(2).replace(".",",")} = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*`
      : "";

    return (
      `🛒✅ *Anotei:* ${valI.item.nome}${avisoI}${subTxt}\n\n` +
      `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
      `👇 *Deseja mais alguma coisa?*\n\n` +
      `*1* ➕ Adicionar mais itens\n` +
      `*2* ✅ Continuar para entrega\n` +
      `*3* 🗑️ Remover item\n` +
      `*4* 🔄 Recomeçar`
    );
  }

  // ── ETAPA: mais_itens ──
  // Pergunta se quer adicionar mais ou continuar
  if (e.etapa === "mais_itens") {
    const op = txt.trim().toLowerCase();
    const continuar = querContinuar(txt);

    // "fechar o pedido" ou "confirmar pedido" → vai direto para resumo/confirmacao
    if (continuar === "fechar" || op.includes("fechar") || op.includes("confirm")) {
      // Ir para confirmação (resumo do pedido)
      e.etapa = "confirmacao";
      salvar();
      return resumoPedido(e, cfg);
    }

    // Quer continuar → vai para endereço
    if (continuar || op === "2") {
      // ── Validar pedido mínimo antes de ir para endereço ──
      const minStr2 = (cfg.pedidoMinimo||"0").replace(/[^\d,.]/g,"").replace(",",".");
      const minVal2 = parseFloat(minStr2) || 0;
      const subAtual2 = calcularTotal(e.itens, cfg);
      if (minVal2 > 0 && subAtual2 < minVal2) {
        const falta2 = (minVal2 - subAtual2).toFixed(2).replace(".",",");
        return (
          `⚠️ *Pedido mínimo: R$ ${minVal2.toFixed(2).replace(".",",")}*\n\n` +
          `Seu pedido está em *R$ ${subAtual2.toFixed(2).replace(".",",")}* — faltam *R$ ${falta2}*.\n\n` +
          `➕ Adicione mais itens para continuar!\n\n` +
          `*1* ➕ Adicionar itens\n*4* 🔄 Recomeçar`
        );
      }
      e.etapa = "endereco";
      salvar();
      return (
        `✅ *Pedido:* _${e.itens}_\n\n` +
        `━━━━━━━━━━━━━━━━━━━━━━\n` +
        `📍 *Endereço de entrega*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
        `Envie de duas formas:\n\n` +
        `📌 *GPS — mais rápido!*\n` +
        `Toque em 📎 → Localização → Enviar localização\n\n` +
        `✏️ *Ou digitar:*\n` +
        `Qual a *rua ou avenida?*`
      );
    }

    // Quer adicionar mais → vai para etapa de extra
    if (op === "1" || op.includes("sim") || op.includes("quer") || op.includes("adicion") || op.includes("mais")) {
      e.etapa = "itens_extra";
      salvar();
      return (
        `Ok! O que mais você gostaria?\n\n` +
        `${cardResumido(cfg)}\n\n` +
        `_Pedido atual: ${e.itens}_`
      );
    }

    // Digitou direto um item → validar no cardápio antes de adicionar
    if (txt.length >= 3) {
      // Pizza meio a meio dentro do loop
      if (querPizzaMeio(txt)) {
        e.etapa = "pizza_sabor1"; salvar();
        const pzs = (cfg.cardapio||[]).filter(c=>c.categoria.toLowerCase().includes("pizza")).flatMap(c=>(c.itens||[]).filter(i=>!i.pausado));
        return `🍕 *Pizza Meio a Meio — 1º Sabor:*\n\n${listaPizzas(pzs)}\n\n_Digite o número_ ☝️`;
      }

      const { qtd: qtdM, texto: txtM } = extrairQtd(txt);
      const val = validarItem(txtM, cfg);
      if (!val.ok) {
        return (
          `😅 Não encontrei *"${txt}"* no cardápio.\n\n` +
          `Confira o cardápio e tente novamente:\n\n` +
          `${cardResumido(cfg)}\n\n` +
          `_Pedido atual: ${e.itens}_`
        );
      }
      if (val.item.pausado) return `⚠️ *${val.item.nome}* está indisponível hoje. Escolha outro 😊`;

      const corrigiu = val.item.nome.toLowerCase() !== txtM.toLowerCase();
      const aviso = corrigiu ? `\n_✏️ Entendi como: *${val.item.nome}*_` : "";

      // Verificar acompanhamentos
      if (temAcomp(val.item, cfg)) {
        e.itemPendente      = val.item;
        e.qtdPendente       = qtdM;
        e.acompSelecionados = [];
        e.etapa             = "acompanhamentos";
        salvar();
        return (
          `✅ *${qtdM > 1 ? qtdM+"x " : ""}${val.item.nome}*${aviso}\n\n` +
          msgAcomp(val.item, [], qtdM, cfg)
        );
      }

      const nomeItem = qtdM > 1
        ? `${qtdM}x ${val.item.nome} — ${val.item.preco}`
        : `${val.item.nome} — ${val.item.preco}`;
      e.itens += " | " + nomeItem;
      salvar();

      const sub2  = calcularTotal(e.itens, cfg);
      const taxa2 = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const sub2Txt = sub2 > 0
        ? `\n💰 Subtotal: R$ ${sub2.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub2+taxa2).toFixed(2).replace(".",",")}*`
        : "";

      return (
        `✅ *Adicionado:* ${val.item.nome}${aviso}\n\n` +
        `*Pedido:* _${e.itens}_${sub2Txt}\n\n` +
        `*1* ➕ Mais  |  *2* ✅ Continuar  |  *3* 🗑️ Remover  |  *4* 🔄 Recomeçar`
      );
    }

    // Pedir pizza meio a meio via menu ou texto
    if (querPizzaMeio(txt) || op === "pizza meio a meio") {
      e.etapa = "pizza_sabor1"; salvar();
      const pizzas = (cfg.cardapio||[])
        .filter(cat=>cat.categoria.toLowerCase().includes("pizza"))
        .flatMap(cat=>(cat.itens||[]).filter(i=>!i.pausado));
      const lista = pizzas.map((p,i)=>`  *${i+1}* — ${p.nome} — *${p.preco}*`).join("\n");
      return `🍕 *Pizza Meio a Meio — 1º sabor:*\n\n${lista}\n\n_Digite o número ou nome_`;
    }

    // Opção 3 — remover item
    if (op === "3" || querRemover(txt)) {
      const lista = (e.itens.includes(" | ")?e.itens.split(" | "):e.itens.split(",")).map((it,i)=>`  *${i+1}* — ${it.trim()}`).join("\n");
      e.etapa = "remover_item"; salvar();
      return `🗑️ *Qual item remover?*\n\n${lista}\n\n_Digite o número ou nome_`;
    }

    // Opção 4 — recomeçar
    if (op === "4" || querRecomecar(txt)) {
      estadosPedido.set(numero, novoEstado(e.numPedido));
      return `✅ Tudo limpo! Vamos recomeçar 😊\n\n` + mostrarCardapio(cfg);
    }

    return `👇 *O que deseja fazer?*\n\n*1* ➕ Adicionar mais\n*2* ✅ Continuar\n*3* 🗑️ Remover item\n*4* 🔄 Recomeçar`;
  }

  // ── ETAPA: remover_item ──
  if (e.etapa === "remover_item") {
    const sep2 = e.itens.includes(" | ") ? " | " : ",";
    const arr = e.itens.split(sep2).map(i=>i.trim()).filter(Boolean);
    const num = parseInt(txt.trim());
    let removido = null;
    if (!isNaN(num) && num >= 1 && num <= arr.length) {
      removido = arr[num - 1];
    } else {
      removido = extrairItemRemover(txt, e.itens);
    }
    if (!removido) {
      const lista = arr.map((it,i)=>`  *${i+1}* — ${it}`).join("\n");
      return `Não encontrei 😅 Escolha pelo número:\n\n${lista}`;
    }
    const novos = arr.filter(i=>i.trim()!==removido.trim());
    if (novos.length === 0) {
      estadosPedido.set(numero, novoEstado(e.numPedido));
      return `🗑️ *${removido}* removido.\n\nPedido vazio! Vamos recomeçar:\n\n` + mostrarCardapio(cfg);
    }
    e.itens = novos.join(" | ");
    e.etapa = "mais_itens";
    salvar();
    const sub  = calcularTotal(e.itens, cfg);
    const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
    const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
    return (
      `✅ *${removido}* removido!\n\n` +
      `*Pedido:* _${e.itens}_${subT}\n\n` +
      `*1* ➕ Mais  |  *2* ✅ Continuar  |  *3* 🗑️ Remover mais  |  *4* 🔄 Recomeçar`
    );
  }

  // ── ETAPA: itens_extra ──
  if (e.etapa === "itens_extra") {
    if (txt.length < 2) return `O que você gostaria de adicionar? 😊`;

    // Pizza meio a meio dentro da adição extra
    if (querPizzaMeio(txt)) {
      e.etapa = "pizza_sabor1"; salvar();
      const pzs = (cfg.cardapio||[]).filter(c=>c.categoria.toLowerCase().includes("pizza")).flatMap(c=>(c.itens||[]).filter(i=>!i.pausado));
      return `🍕 *Pizza Meio a Meio — 1º Sabor:*\n\n${listaPizzas(pzs)}\n\n_Digite o número_ ☝️`;
    }

    const { qtd: qtdE, texto: txtE } = extrairQtd(txt);
    const val = validarItem(txtE, cfg);
    if (!val.ok) {
      return (
        `😅 Não encontrei *"${txt}"* no cardápio.\n\n` +
        `Confira os itens disponíveis:\n\n` +
        `${cardResumido(cfg)}\n\n` +
        `_Pedido atual: ${e.itens}_`
      );
    }
    if (val.item.pausado) return `⚠️ *${val.item.nome}* está indisponível hoje 😊`;

    const nomeItem = qtdE > 1
      ? `${qtdE}x ${val.item.nome} — ${val.item.preco}`
      : `${val.item.nome} — ${val.item.preco}`;
    e.itens += " | " + nomeItem;
    e.etapa  = "mais_itens";
    salvar();

    const sub3  = calcularTotal(e.itens, cfg);
    const taxa3 = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
    const sub3Txt = sub3 > 0
      ? `\n💰 Subtotal: R$ ${sub3.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub3+taxa3).toFixed(2).replace(".",",")}*`
      : "";

    const corrigiu = val.item.nome.toLowerCase() !== txtE.toLowerCase();
    const aviso = corrigiu ? `\n_✏️ Entendi como: *${val.item.nome}*_` : "";

    return (
      `✅ *Adicionado:* ${val.item.nome}${aviso}\n\n` +
      `*Pedido:* _${e.itens}_${sub3Txt}\n\n` +
      `*1* ➕ Mais  |  *2* ✅ Continuar  |  *3* 🗑️ Remover  |  *4* 🔄 Recomeçar`
    );
  }

  // ── ETAPA: endereco ──
  if (e.etapa === "endereco") {
    const isPin = msg.type === "location" || !!msg.location;
    if (isPin) {
      const lat = msg.location?.latitude;
      const lng = msg.location?.longitude;
      e.localizacao = { tipo:"pin", lat, lng, mapsUrl:`https://maps.google.com/?q=${lat},${lng}`, endereco:"GPS" };
      e.rua = `GPS`;
      e.etapa = "bairro";
      salvar();
      return `📍 *GPS recebido!* ✅\n\nQual o *bairro?*`;
    }
    if (txt.length < 3) return `Informe a *rua ou avenida* 😊`;
    // Remove prefixos de saudação comuns no áudio: "Oi", "Olá", "Bom dia", " Boa tarde"
    let ruaTxt = txt.replace(/^(oi\s*,?\s*|olá\s*,?\s*|bom dia\s*,?\s*|boa tarde\s*,?\s*|boa noite\s*,?\s*)/i, "").trim();
    if (ruaTxt.length < 2) return `Informe a *rua ou avenida* 😊`;
    e.rua   = ruaTxt;
    e.etapa = "bairro";
    salvar();
    return `📍✅ *${ruaTxt}*\n\n🏘️ *Qual o bairro?*\n_Ex: Centro, Farol, Ponta Verde..._`;
  }

  // ── ETAPA: bairro ──
  if (e.etapa === "bairro") {
    if (txt.length < 2) return `Informe o *bairro* 😊`;
    e.bairro = txt;
    e.etapa  = "numero_end";
    salvar();
    return `✅ *${txt}*\n\n🔢 *Número do imóvel?*\n_Sem número? Responda_ *sem número*`;
  }

  // ── ETAPA: numero_end ──
  if (e.etapa === "numero_end") {
    const semNum = /sem\s*n[úu]mero|s\/n|^sn$|^nn$|nao tem|não tem/i.test(txt.trim());
    e.numEnd = semNum ? "S/N" : txt.trim();
    const endBase = `${e.rua}, Nº ${e.numEnd} — ${e.bairro}`;
    if (e.localizacao) {
      e.localizacao.endereco = endBase;
    } else {
      e.localizacao = { tipo:"texto", endereco:endBase, mapsUrl:null };
    }
    e.etapa = "referencia";
    salvar();
    return (
      `✅ ${semNum ? "Sem número." : `Nº *${e.numEnd}*`}\n\n` +
      `📌 *Ponto de referência:*\n` +
      `_Ex: "próximo ao Mercadão", "em frente à escola"_\n\n` +
      `_Sem referência? Responda_ *não*`
    );
  }

  // ── ETAPA: referencia ──
  if (e.etapa === "referencia") {
    const semRef = /^(n[ãa]o|n|nn|nada|nenhum|pular|skip)$/i.test(txt.trim());
    e.referencia = semRef ? "" : txt.trim();
    if (e.referencia && e.localizacao) e.localizacao.endereco += ` (Ref: ${e.referencia})`;
    e.etapa = "tipo_imovel";
    salvar();
    return (
      `${semRef ? "✅ Sem referência." : `✅ _${e.referencia}_`}\n\n` +
      `🏠 *Tipo de imóvel:*\n\n` +
      `*1* — Casa\n` +
      `*2* — Apartamento / Edifício\n` +
      `*3* — Comércio / Escritório`
    );
  }

  // ── ETAPA: tipo_imovel ──
  if (e.etapa === "tipo_imovel") {
    const op = txt.trim().toLowerCase();
    if (op === "1" || op.includes("casa")) {
      e.tipoComp = "casa"; e.etapa = "telefone"; salvar();
      return `🏠 *Casa* ✅\n\n📞 *Seu telefone para contato:*\n_Ex: 82 99999-9999_`;
    }
    if (op === "2" || op.includes("apart") || op.includes("apto") || op.includes("edif")) {
      e.tipoComp = "apto"; e.etapa = "complemento"; salvar();
      return `🏢 *Apartamento* ✅\n\n🔑 *Apto, bloco e nome do edifício:*\n_Ex: Apto 42, Bloco B, Ed. Solar_`;
    }
    if (op === "3" || op.includes("comerc") || op.includes("escrit") || op.includes("outro")) {
      e.tipoComp = "comercio"; e.etapa = "telefone"; salvar();
      return `🏪 *Comércio* ✅\n\n📞 *Seu telefone para contato:*\n_Ex: 82 99999-9999_`;
    }
    return `Por favor, escolha:\n*1* — Casa | *2* — Apartamento | *3* — Comércio`;
  }

  // ── ETAPA: complemento ──
  if (e.etapa === "complemento") {
    if (txt.length < 3) return `Informe *apto, bloco e edifício* 😊\n_Ex: Apto 42, Bloco B, Ed. Solar_`;
    e.complemento = txt.trim();
    e.localizacao.endereco += ` — ${e.complemento}`;
    e.etapa = "telefone";
    salvar();
    return `✅ _${e.complemento}_\n\n📞 *Seu telefone para contato:*\n_Ex: 82 99999-9999_`;
  }

  // ── ETAPA: telefone ──
  if (e.etapa === "telefone") {
    if (txt.replace(/\D/g,"").length < 8) return `Informe um *telefone válido* 😊\n_Ex: 82 99999-9999_`;
    e.telefone = txt.trim();
    e.etapa    = "pagamento";
    salvar();
    return (
      `✅ *${e.telefone}*\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💳 *Forma de pagamento:*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      menuPag(cfg) + `\n\n` +
      `_Digite o número da opção_`
    );
  }

  // ── ETAPA: pagamento ──
  if (e.etapa === "pagamento") {
    const forma = resolverPag(txt, cfg);
    if (!forma) return `Não reconheci 😅\n\nEscolha pelo número:\n\n${menuPag(cfg)}`;
    e.pagamento = forma;
    if (forma.toLowerCase().includes("dinheiro")) {
      e.etapa = "troco"; salvar();
      return (
        `💵 *Dinheiro* ✅\n\n` +
        `💰 *Vai precisar de troco?*\n` +
        `Informe o valor: _Ex: 50, 100_\n\n` +
        `Sem troco? Responda *não*`
      );
    }
    const pixInfo = forma.toLowerCase().includes("pix")
      ? `\n\n🔑 *Chave Pix:* \`${cfg.pixChave||""}\`\n_Envie o comprovante após confirmar!_`
      : "";
    e.etapa = "observacao"; salvar();
    return (
      `✅ *${forma}*${pixInfo}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📝 *Alguma observação?*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `_Ex: sem cebola, bem passado..._\n\n` +
      `Sem observação? Responda *não*`
    );
  }

  // ── ETAPA: troco ──
  if (e.etapa === "troco") {
    const semTroco = /^(n[ãa]o|n|nn|nao precisa|não precisa|sem troco)$/i.test(txt.trim());
    if (!semTroco) {
      // Extrair APENAS o primeiro valor numérico da mensagem (evita duplicação como "200 200")
      const match = txt.replace(/[^0-9,.]/g, "").match(/([\d,.]+)/);
      if (!match) return `Informe o valor da nota _Ex: 200_ ou responda *não*`;
      // Pegar só o primeiro grupo capturador para evitar "200200" de "Troco para 200 200"
      const valStr = match[1];
      const val = parseFloat(valStr.replace(",", "."));
      if (isNaN(val) || val <= 0) return `Informe o valor da nota _Ex: 200_ ou responda *não*`;
      // Troco precisa ser maior que o total do pedido
      const totalPedido = calcularTotal(e.itens, cfg);
      const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const totalComTaxa = totalPedido + taxa;
      if (totalComTaxa > 0 && val < totalComTaxa) {
        return (
          `⚠️ O valor informado (R$ ${val.toFixed(2).replace(".",",")}) é menor que o total do pedido (R$ ${totalComTaxa.toFixed(2).replace(".",",")})!\n\n` +
          `Informe um valor maior, ex: *${Math.ceil(totalComTaxa / 10) * 10}*\n` +
          `Ou responda *não* se não precisar de troco.`
        );
      }
      e.troco = String(val.toFixed(2).replace(".",","));
    } else {
      e.troco = "";
    }
    const pixInfo = e.pagamento.toLowerCase().includes("pix")
      ? `\n\n🔑 *Pix:* \`${cfg.pixChave||""}\`` : "";
    e.etapa = "observacao"; salvar();
    return (
      `✅ ${e.troco ? `Troco para *R$ ${e.troco}*` : "Sem troco."}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📝 *Alguma observação?*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `_Ex: sem cebola, bem passado..._\n\n` +
      `Sem observação? Responda *não*`
    );
  }

  // ── ETAPA: observacao ──
  if (e.etapa === "observacao") {
    const semObs = /^(n[ãa]o|n|nn|nada|nenhuma|pular|nao tem|sem obs)$/i.test(txt.trim());
    e.observacao = semObs ? "" : txt.trim();
    e.etapa = "confirmacao";
    salvar();
    const pixExtra = e.pagamento.toLowerCase().includes("pix")
      ? `\n\n🔑 *Chave Pix:* \`${cfg.pixChave||""}\`` : "";
    return resumoPedido(e, cfg) + pixExtra;
  }

  // ── ETAPA: confirmacao ──
  if (e.etapa === "confirmacao") {
    const op = txt.trim().toLowerCase();

    // CONFIRMAR
    if (op === "1" || op === "sim" || op === "s" || op === "ok" || op.startsWith("confirm")) {
      // ── Validar pedido mínimo ──
      const minStr = (cfg.pedidoMinimo||"0").replace(/[^\d,.]/g,"").replace(",",".");
      const minVal = parseFloat(minStr) || 0;
      const subAtual = calcularTotal(e.itens, cfg);
      if (minVal > 0 && subAtual < minVal) {
        const falta = (minVal - subAtual).toFixed(2).replace(".",",");
        return (
          `⚠️ *Pedido mínimo não atingido!*\n\n` +
          `Mínimo: *R$ ${minVal.toFixed(2).replace(".",",")}*\n` +
          `Seu pedido: *R$ ${subAtual.toFixed(2).replace(".",",")}*\n` +
          `Faltam: *R$ ${falta}*\n\n` +
          `➕ Adicione mais itens para continuar:\n\n` +
          `*3* ➕ Adicionar itens  |  *5* 🔄 Recomeçar`
        );
      }
      const loc = e.localizacao || {};
      const pedido = {
        numPedido:   e.numPedido,
        inicio:      e.inicio,
        confirmado:  new Date().toISOString(),
        itens:       e.itens,
        pagamento:   e.pagamento,
        troco:       e.troco || "",
        observacao:  e.observacao || "",
        endereco:    loc.tipo === "pin"
          ? `GPS (${loc.lat?.toFixed(5)},${loc.lng?.toFixed(5)})`
          : (loc.endereco || "—"),
        complemento: e.complemento || "",
        referencia:  e.referencia  || "",
        telefone:    e.telefone    || "",
        mapsUrl:     loc.mapsUrl   || null,
      };

      pedidosAbertos.set(numero, pedido);
      estadosPedido.delete(numero);
      limparTimeout(numero);
      emitirContador();
      registrarVenda(pedido);
      // Salvar histórico do cliente
      salvarCliente(numero, pedido);
      io.emit("pedidos", listaPedidos());
      io.emit("novo_pedido", { numero, ...pedido, autoImprimir });

      const totI = calcularTotal(e.itens, cfg);
      const taxaF = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
      const totF  = totI + taxaF;

      // Detalhar cada item com valor total
      const itensDetalhados = e.itens.split(" | ").map(item => {
        const m = item.match(/^(\d+)x\s+(.+?)\s+—\s+R\$\s*([\d,.]+)/);
        if (m) {
          const qtd = parseInt(m[1]), nome = m[2];
          const prUni = parseFloat(m[3].replace(",","."));
          const totItem = (prUni * qtd).toFixed(2).replace(".",",");
          return `   ${qtd}x ${nome} ............. R$ ${totItem}`;
        }
        return `   ${item}`;
      }).join("\n");

      const totStr = totI > 0
        ? `🛒 *Itens do pedido:*\n${itensDetalhados}\n\n` +
          `🛵 *Taxa de entrega:* ${cfg.taxaEntrega||"—"}\n` +
          `━━━━━━━━━━━━━━━━━━━━━\n` +
          `💵 *TOTAL: R$ ${totF.toFixed(2).replace(".",",")}*\n`
        : "";

      let fim = (
        `\n🎉🎊 *PEDIDO Nº ${e.numPedido} CONFIRMADO!* 🎊🎉\n\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
        `✅ *Recebemos seu pedido!*\n` +
        `👨‍🍳 *Já estamos preparando!*\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n` +
        `${totStr}` +
        `⏱️ *Previsão de entrega:* ${(()=>{ const _t=calcularTempoPreparo(e.itens,cfg); return _t?(_t+" min"):cfg.tempoEntrega||"30-50 min"; })()}\n`
      );
      if (e.pagamento.toLowerCase().includes("pix")) {
        fim += `\n💸 *Pagamento via Pix:*\n🔑 Chave: \`${cfg.pixChave||""}\`\n📸 _Envie o comprovante aqui!_\n`;
      }
      if (e.troco) fim += `\n💵 *Troco para R$ ${e.troco}*\n`;
      fim += `\n🛵 _A caminho em breve!_\n❓ _Qualquer dúvida é só chamar!_ 😊`;
      return fim;
    }

    // CORRIGIR
    if (op === "2" || op.includes("corrig") || op.includes("alterar")) {
      estadosPedido.set(numero, novoEstado(e.numPedido));
      return `Vamos refazer! ✏️\n\n` + mostrarCardapio(cfg);
    }

    // ADICIONAR
    if (op === "3" || op.includes("adicion") || op.includes("mais")) {
      e.etapa = "itens_extra"; salvar();
      return `${cardResumido(cfg)}\n\n✍️ *O que mais deseja?*\n_Pedido atual: ${e.itens}_`;
    }

    // REMOVER ITEM
    if (op === "4" || querRemover(txt)) {
      const lista = (e.itens.includes(" | ")?e.itens.split(" | "):e.itens.split(",")).map((it,i)=>`  *${i+1}* — ${it.trim()}`).join("\n");
      e.etapa = "remover_item"; salvar();
      return `🗑️ *Qual item deseja remover?*\n\n${lista}\n\n_Digite o número ou nome_`;
    }

    // RECOMEÇAR
    if (op === "5" || querRecomecar(txt)) {
      estadosPedido.set(numero, novoEstado(e.numPedido));
      return `✅ Tudo limpo! Vamos recomeçar 😊\n\n` + mostrarCardapio(cfg);
    }

    return resumoPedido(e, cfg);
  }

  return null;
}

function mostrarCardapio(cfg) {
  const proms = (cfg.promocoes||[]).filter(p=>p.ativo&&p.texto);
  const promoStr = proms.length
    ? "\n\n🔥 *PROMOÇÕES DO DIA:*\n" + proms.map(p=>`  ✨ ${p.texto}`).join("\n")
    : "";
  return (
    `🛒 *Cardápio ${cfg.empresaNome||""}*\n` +
    `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
    `${cardResumido(cfg)}` +
    `${promoStr}\n\n` +
    `━━━━━━━━━━━━━━━━━━━━━━\n` +
    `💰 *Pedido mínimo:* ${cfg.pedidoMinimo||"—"}\n` +
    `🛵 *Taxa de entrega:* ${cfg.taxaEntrega||"—"}\n` +
    `⏱️ *Tempo médio:* ${cfg.tempoEntrega||"—"}\n\n` +
    `✍️ *O que vai querer hoje?*\n` +
    `_Digite o nome, número do item ou:_\n\n` +
    `*0* ↩️ Voltar ao menu`
  );
}

function msgEndereco() {
  return "placeholder";
}


// ═══════════════════════
//  SIMULAÇÃO HUMANA
// ═══════════════════════

/** Calcula tempo de digitação realista baseado no tamanho da mensagem */
function tempoDigitacao(texto) {
  const chars = texto.replace(/[^\w\s]/g,"").length;
  // 40–90 chars/seg simulando digitação humana, mais pausa para pensar
  return Math.min(Math.max(chars * 22, 700), 4000);
}

/** Envia resposta simulando leitura + digitação humana */
async function responderHumano(chat, msg, resposta) {
  // Dividir em blocos se houver separador ━━━ e texto longo
  const blocos = dividirEmBlocos(resposta);

  for (let i = 0; i < blocos.length; i++) {
    const bloco = blocos[i];
    if (!bloco.trim()) continue;
    // Pausa de "leitura/pensamento" antes de digitar
    await sleep(i === 0 ? 350 : 500);
    await chat.sendStateTyping();
    await sleep(tempoDigitacao(bloco));

    if (i === 0) {
      await msg.reply(bloco);
    } else {
      await chat.sendMessage(bloco);
    }
    if (i < blocos.length - 1) await sleep(400);
  }
}

function dividirEmBlocos(texto) {
  if (!texto || texto.length < 700) return [texto];
  // Dividir em separador ━━━
  const partes = texto.split(/(?=\n━━━)/);
  if (partes.length > 1) return partes.filter(p => p.trim());
  return [texto];
}

// ═══════════════════════
// ═══════════════════════
//  AVALIAÇÃO PÓS-ENTREGA
// ═══════════════════════
function agendarAvaliacao(numero, pedido) {
  // Cancelar timer anterior se houver
  const pend = avaliacoesPend.get(numero);
  if (pend?.timer) clearTimeout(pend.timer);
  const timer = setTimeout(async () => {
    avaliacoesPend.delete(numero);
    if (!waConectado || !waClient) return;
    try {
      await waClient.sendMessage(numero,
        `⭐ *Como foi seu pedido?*\n\n` +
        `*Pedido Nº ${pedido.numPedido}*\n` +
        `_${pedido.itens}_\n\n` +
        `Responda com uma nota de *1 a 5*:\n` +
        `1 ⭐ Ruim  |  3 ⭐⭐⭐ Ok  |  5 ⭐⭐⭐⭐⭐ Excelente!\n\n` +
        `_Sua opinião nos ajuda a melhorar! 🙏_`
      );
      avaliacoesPend.set(numero, { pedido, aguardando:true });
    } catch(e) { console.error("[AVAL]", e.message); }
  }, 30 * 60 * 1000); // 30 minutos
  avaliacoesPend.set(numero, { pedido, timer, aguardando:false });
}

// Salvar avaliação recebida
function receberAvaliacao(numero, nota, pedido) {
  const vendasFile = path.join(LOG_DIR, "vendas.json");
  try {
    let vendas = [];
    if (fs.existsSync(vendasFile)) vendas = JSON.parse(fs.readFileSync(vendasFile,"utf8"));
    const idx = vendas.findIndex(v => v.numPedido === pedido?.numPedido);
    if (idx >= 0) vendas[idx].avaliacao = nota;
    fs.writeFileSync(vendasFile, JSON.stringify(vendas,null,2));
  } catch(_) {}
  const cli = clientesDB.get(numero.replace("@c.us",""));
  if (cli) { cli.ultimaAvaliacao = nota; clientesDB.set(numero.replace("@c.us",""),cli); saveClientes(); }
  io.emit("avaliacao", { numero, nota, pedido });
}

// ═══════════════════════
//  MODO LOJA FECHADA
// ═══════════════════════
// ── Verifica se hora está dentro de um intervalo (suporta cruzar meia-noite) ──
function dentroDoHorario(hMin, abre, fecha) {
  if (fecha === 0) fecha = 1440; // 00:00 = meia-noite
  if (fecha > abre) {
    // Normal: 11:00 → 23:00
    return hMin >= abre && hMin < fecha;
  } else {
    // Cruza meia-noite: ex 22:00 → 04:00
    return hMin >= abre || hMin < fecha;
  }
}

function lojaAberta(cfg) {
  if (cfg.lojaFechadaManual) return false;

  const agora = new Date();
  const dia   = agora.getDay(); // 0=dom...6=sab
  const hMin  = agora.getHours() * 60 + agora.getMinutes();

  // ── Horários estruturados (configurados via painel) ──
  if (Array.isArray(cfg.horarios) && cfg.horarios.length > 0) {
    // 1. Verificar horário do dia atual
    for (const h of cfg.horarios) {
      if (!h.ativo) continue;
      if (!(h.dias||[]).includes(dia)) continue;
      const [ah, am] = (h.abre||"11:00").split(":").map(Number);
      const [fh, fm] = (h.fecha||"23:00").split(":").map(Number);
      const abre  = ah * 60 + (am||0);
      const fecha = fh * 60 + (fm||0);
      if (dentroDoHorario(hMin, abre, fecha)) return true;
    }
    // 2. Verificar se ainda estamos no período noturno de ontem
    // Ex: Sáb abre 11:00 fecha 04:00 → domingo às 02:00 ainda está aberto
    const diaOntem = (dia + 6) % 7;
    for (const h of cfg.horarios) {
      if (!h.ativo) continue;
      if (!(h.dias||[]).includes(diaOntem)) continue;
      const [ah, am] = (h.abre||"11:00").split(":").map(Number);
      const [fh, fm] = (h.fecha||"23:00").split(":").map(Number);
      const abre  = ah * 60 + (am||0);
      const fecha = fh * 60 + (fm||0);
      // Só interessa cruzamento de meia-noite (fecha < abre)
      if (fecha < abre && hMin < fecha) return true;
    }
    return false;
  }

  // ── Sem horários configurados → não bloqueia ──
  return true;
}

function msgLojaFechada(cfg) {
  const prox = cfg.horarioFuncionamento || "nosso horário de funcionamento";
  return (
    `😴 *Estamos fechados no momento.*\n\n` +
    `⏰ *Horário:* ${prox}\n\n` +
    `Quando abrirmos, é só mandar *oi* que te atendemos! 😊\n` +
    `_Deixe sua mensagem e retornaremos assim que possível._`
  );
}

// ═══════════════════════
//  HANDLER PRINCIPAL
// ═══════════════════════

// Detecta se a mensagem parece ser um item do cardápio ou intenção de pedido
function parecePedido(txt, cfg) {
  const s = txt.trim().toLowerCase();
  // Já pega pelos gatilhos diretos
  if (querPedir(txt)) return true;
  // Verifica se menciona algum item do cardápio
  for (const cat of cfg.cardapio || []) {
    for (const item of cat.itens || []) {
      if (s.includes(item.nome.toLowerCase().slice(0, 5))) return true;
    }
  }
  // Frases que indicam pedido informal
  const frasesP = ["quero","queria","me manda","me traz","pode trazer","um lanche",
    "uma pizza","um x-","hamburguer","hambúrguer","lanche","pizza","refrigerante",
    "pedido","pedir","meu pedido"];
  return frasesP.some(f => s.includes(f));
}

async function handleMsg(msg) {
  try {
    if (!msg.from || msg.from.endsWith("@g.us")) return;
    const chat = await msg.getChat();
    if (chat.isGroup) return;

    const numero = msg.from;
    const isLoc  = msg.type === "location" || !!msg.location;
    let txt    = isLoc ? "" : (msg.body || "").trim();

    // Mídia sem texto
    if (!txt && !isLoc) {
      if (msg.hasMedia || msg.type === "ptt" || msg.type === "audio") {
        // ATENDIMENTO POR VOZ: transcrever áudio com Groq (Whisper)
        if ((msg.type === "ptt" || msg.type === "audio") && config.voiceEnabled !== false) {
          console.log("[VOZ] Áudio recebido, tipo:", msg.type, "voiceEnabled:", config.voiceEnabled);
          try {
            const media = await msg.downloadMedia();
            console.log("[VOZ] Media baixada, tamanho:", media?.data?.length);
            if (media && media.data) {
              const buf = Buffer.from(media.data, "base64");
              console.log("[VOZ] Buffer criado:", buf.length, "bytes");
              const transcrito = await transcreverAudioGroq(buf);
              console.log("[VOZ] Transcrição retornou:", transcrito);
              if (transcrito && transcrito.trim().length > 0) {
                console.log(`[VOZ] Transcrito: "${transcrito}"`);
                await chat.sendStateTyping();
                await sleep(600);
                txt = transcrito.trim();
                
                // ── NORMALIZAÇÕES DE ÁUDIO ──
                // Corrigir "PIX" transcrito errado (Pigues, Piques, FIX, PITS, PITES, PIS, etc.)
                const txtLow = txt.toLowerCase();
                // Remove pontuação e espaços extras para análise
                const txtLimpo = txtLow.replace(/[\s\.,]+/g, "").trim();
                if (/^(pigues?|fics?|pikes?|piks?|p[iy]ques?|pits?|p[iy]ks?|p[iy]?xe?s?|feats?|fex|feis|fes|fics?|f[iy]ts?)$/i.test(txtLimpo) || 
                    /^p[iy][kq]u?e?s$/i.test(txtLimpo) || 
                    txtLow === "pigs" || txtLow === "piques" || txtLow === "fix" || 
                    txtLow === "pits" || txtLow === "pites" || txtLow === "pis" || 
                    txtLow === "feats" || txtLow === "feis") {
                  txt = "PIX";
                  console.log("[VOZ] Corrigido para PIX");
                }
                // Corrigir "Aprendente" ou "a pendente" ou "apendente" → "atendente"
                if (/^(aprendente|a\s*pendente|apendente|a?\s*p?r?enden?te|a\s*pr?en?de?n?te)$/i.test(txtLow.replace(/\.{3,}$/, ""))) {
                  txt = "atendente";
                  console.log("[VOZ] Corrigido para atendente");
                }
                // Telefone falado número por número: "82991856656" ou "82 99 18 56 66 56" → formato brasileiro
                const telefonesFalados = txt.match(/(\d[\d\s]{8,15}\d)/g);
                if (telefonesFalados) {
                  for (const tel of telefonesFalados) {
                    const telLimpo = tel.replace(/\D/g, "");
                    // Se tem 10-11 dígitos, é um telefone brasileiro
                    if (telLimpo.length >= 10 && telLimpo.length <= 11) {
                      const telFormatado = telLimpo.length === 11 
                        ? `(${telLimpo.slice(0,2)}) ${telLimpo.slice(2,7)}-${telLimpo.slice(7)}`
                        : `(${telLimpo.slice(0,2)}) ${telLimpo.slice(2,6)}-${telLimpo.slice(6)}`;
                      txt = txt.replace(tel, telFormatado);
                      console.log(`[VOZ] Telefone corrigido para: ${telFormatado}`);
                    }
                  }
                }
              } else {
                // Áudio não reconhecido - ignora silenciosamente para não travar o fluxo
                console.log("[VOZ] Áudio não entendido, ignorando");
                return;
              }
            } else {
              console.log("[VOZ] Media sem dados, ignorando");
              return;
            }
          } catch (errAudio) {
            console.error("[VOZ] Erro:", errAudio.message);
            return; // Ignora silenciosamente
          }
        } else {
          await sleep(800);
          await chat.sendStateTyping();
          await sleep(1200);
          const eFluxo = estadosPedido.has(numero);
          await msg.reply(
            `\u{1F3A4} Recebi seu \u00e1udio, mas n\u00e3o consigo ouvir! \ud83d\ude05\n\n` +
            `Me manda em *texto* que atendo na hora! \u270d\ufe0f` +
            (eFluxo ? `\n\n_Seu pedido est\u00e1 salvo, pode continuar de onde parou._` : "")
          );
          return;
        }
      } else {
        await msg.reply("Recebi! \ud83d\udce4\nPara eu te ajudar, descreva o que precisa em texto 😊");
        return;
      }
    }

    if (!agenteAtivo) return;

    // Rate limit
    const now = Date.now(), last = rateLimiter.get(numero) || 0;
    if (now - last < 1500) return;
    rateLimiter.set(numero, now);

    // ── Se em atendimento humano: só encaminhar para painel, bot silenciado ──
    // Checar em ambos os formatos por segurança
    const numChave = atendimentoHumano.has(numero) ? numero
      : atendimentoHumano.has(numero.replace("@c.us","")) ? numero.replace("@c.us","")
      : null;
    if (numChave) {
      const a = atendimentoHumano.get(numChave);
      a.msgs.push({ de:"cliente", texto:txt, ts:Date.now() });
      io.emit("atendimento_msg", { numero:numero.replace("@c.us",""), de:"cliente", texto:txt, ts:Date.now() });
      logC({ tipo:"entrada", de:numero, mensagem:txt });
      io.emit("msg", { numero, mensagem:txt, tipo:"entrada" });
      return; // bot não responde — atendente humano ativo
    }

    // Reclamação detectada na Prioridade 0 acima

    totalMsgs++;
    const logTxt = isLoc ? "📍 Localização" : txt;
    logC({ tipo: "entrada", de: numero, mensagem: logTxt });
    io.emit("msg", { numero, mensagem: logTxt, tipo: "entrada" });

    const leitura = isLoc ? 800 : Math.min(400 + txt.length * 15, 2200);
    await sleep(leitura);

    let resp = null;

    // ── FEAT 13: Loja fechada — bloquear atendimento fora do horário ──
    const cfg = config;

    // ── Capturar nome do cliente se aguardando ──
    if (historicos.get("__aguardando_nome__"+numero) && !isLoc) {
      historicos.delete("__aguardando_nome__"+numero);
      const nomeCap = txt.trim().replace(/[^a-zA-ZÀ-ÿ\s]/g,"").trim();
      if (nomeCap.length >= 2) {
        const numLimpo = numero.replace("@c.us","");
        const cliSalvo = clientesDB.get(numLimpo) || { numero:numLimpo, nome:"", pedidos:[], totalGasto:0 };
        cliSalvo.nome = nomeCap;
        clientesDB.set(numLimpo, cliSalvo);
        try { saveClientes(); } catch(_) {}
        resp = (
          `Olá, *${nomeCap}*! 😊\n\n` +
          `Que bom ter você aqui! Escolha uma opção:\n\n` +
          `*1* 🍽️ Ver Cardápio\n` +
          `*2* 🛒 Fazer Pedido\n` +
          `*3* 📦 Meu Pedido\n` +
          `*4* 🕐 Horário\n` +
          `*5* 💳 Pagamento\n` +
          `*6* 👤 Atendente\n` +
          `*7* 🔥 Promoções\n\n` +
          `_Ou é só digitar o que quer!_ 😊`
        );
        await responderHumano(chat, msg, resp);
        logC({ tipo:"saida", para:numero, mensagem:resp });
        io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
        return;
      } else {
        // Nome inválido — pedir de novo
        historicos.set("__aguardando_nome__"+numero, true);
        resp = `Por favor, me diga seu *nome* para continuar 😊`;
        await responderHumano(chat, msg, resp);
        return;
      }
    }
    if (!estadosPedido.has(numero) && !lojaAberta(cfg)) {
      // Permitir apenas palavras-chave de agendamento ou avaliação
      const sLow = txt.toLowerCase();
      const ehAvaliacao = avaliacoesPend.get(numero)?.aguardando && /^[1-5]$/.test(txt.trim());
      if (!ehAvaliacao) {
        resp = msgLojaFechada(cfg);
        await responderHumano(chat, msg, resp);
        logC({ tipo:"saida", para:numero, mensagem:resp });
        io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
        return;
      }
    }

    // ── FEAT 4: Receber avaliação pós-entrega ──
    const avalPend = avaliacoesPend.get(numero);
    if (avalPend?.aguardando && /^[1-5]$/.test(txt.trim())) {
      const nota = parseInt(txt.trim());
      receberAvaliacao(numero, nota, avalPend.pedido);
      avaliacoesPend.delete(numero);
      const estrelas = "⭐".repeat(nota);
      resp = (
        `${estrelas} *Obrigado pela avaliação!*\n\n` +
        (nota >= 4
          ? `Fico feliz que tenha gostado! 😊 Volte sempre!`
          : nota >= 3
            ? `Obrigado pelo feedback! Vamos melhorar sempre. 🙏`
            : `Sentimos muito pela experiência. Vamos melhorar! 🙏\nSe quiser falar com a gente, é só chamar.`)
      );
      await responderHumano(chat, msg, resp);
      logC({ tipo:"saida", para:numero, mensagem:resp });
      io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
      return;
    }

    // ── FEAT 3: Saudação personalizada para cliente conhecido ──
    if (!estadosPedido.has(numero) && !isLoc) {
      const sLow2 = txt.toLowerCase().trim();
      const ehOi = ["oi","olá","ola","bom dia","boa tarde","boa noite","menu","início","inicio"].some(g=>sLow2===g||sLow2.startsWith(g+" "));
      if (ehOi) {
        const cli = getCliente(numero);
        if (cli?.ultimoPedido) {
          const itensUlt = (cli.ultimoPedido.itens||"").split(" | ")[0];
          const dataUlt  = new Date(cli.ultimoPedido.data).toLocaleDateString("pt-BR");
          // Adicionar saudação personalizada ao histórico para ser usada abaixo
          // A resposta virá do matchFluxo normalmente, mas adicionamos um prefixo
          historicos.set("__saudacao__"+numero, { itensUlt, dataUlt, totalPedidos: cli.totalPedidos||1 });
        }
      }
    }

    // ── "0" = voltar ao menu em qualquer tela informativa ──
    if (!estadosPedido.has(numero) && txt.trim() === "0" && !isLoc) {
      const flBV = matchFluxo("oi", config);
      const cliV = getCliente(numero);
      let respMenu = flBV ? variaveis(flBV.resposta, config) : `Digite *oi* para o menu 😊`;
      if (cliV?.nome) respMenu = respMenu.replace(/^Olá! 👋/, `Olá, *${cliV.nome}*! 👋`);
      await responderHumano(chat, msg, respMenu);
      logC({ tipo:"saida", para:numero, mensagem:respMenu });
      io.emit("msg", { numero, mensagem:respMenu, tipo:"saida" });
      return;
    }

    // ── Responder "qual meu nome" / "me chamo" ──
    if (!estadosPedido.has(numero) && !isLoc) {
      const sLowNome = txt.trim().toLowerCase();
      if (["qual meu nome","qual é meu nome","qual e meu nome","como me chamo",
           "você sabe meu nome","voce sabe meu nome","meu nome"].some(g=>sLowNome.includes(g))) {
        const cliN = getCliente(numero);
        const nomeResp = cliN?.nome || null;
        const r2 = nomeResp
          ? `Seu nome é *${nomeResp}*! 😊`
          : `Ainda não sei seu nome! Me conta como você se chama? 😊`;
        await responderHumano(chat, msg, r2);
        logC({ tipo:"saida", para:numero, mensagem:r2 });
        io.emit("msg", { numero, mensagem:r2, tipo:"saida" });
        return;
      }
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 0: ATENDENTE HUMANO — intercepta TUDO
    // ════════════════════════════════════════════════════
    const sLow0 = txt.trim().toLowerCase();
    // Declarar no escopo do handleMsg para uso posterior
    const palavrasReclam0 = ["errado","faltou","faltando","problema","reclamação","reclamacao",
      "não chegou","nao chegou","frio","ruim","horrível","horrivel","péssimo","pessimo",
      "absurdo","cadê","cade","onde está meu","onde esta meu","tudo errado","deu errado",
      "não veio","nao veio","diferente do","veio errado"];
    const ehReclam = palavrasReclam0.some(p => sLow0.includes(p));
    // Detectar pedido de atendente — qualquer variação
    const querAtendente = (
      sLow0.includes("atendente") ||
      sLow0.includes("atend") ||
      sLow0.includes("humano") ||
      sLow0.includes("pessoa real") ||
      sLow0.includes("falar com alguem") ||
      sLow0.includes("falar com alguém") ||
      sLow0.includes("fala com") ||
      sLow0.includes("quero falar") ||
      sLow0.includes("preciso falar") ||
      sLow0.includes("me passa") ||
      sLow0.includes("responsavel") ||
      sLow0.includes("responsável") ||
      sLow0.includes("gerente") ||
      sLow0.includes("dono") ||
      sLow0.includes("falar com o") ||
      sLow0.includes("aprendente") ||  // "Aprendente" (transcrição errada de "atendente")
      sLow0.includes("a pendente") ||    // "A pendente..." (transcrição errada de "atendente")
      sLow0.includes("apendente") ||     // "apendente" (transcrição errada)
      sLow0 === "ajuda" ||
      sLow0.includes("erro") ||
      sLow0.includes("errado") ||
      sLow0.includes("problema") ||
      sLow0.includes("reclam")
    );

    // ehReclam já declarado acima no escopo do handleMsg

    if (ehReclam) {
      io.emit("alerta_reclamacao", {
        numero: numero.replace("@c.us",""),
        mensagem: txt.slice(0,100),
        ts: Date.now()
      });
      console.log("[⚠️ RECLAMAÇÃO]", numero.replace("@c.us",""), txt.slice(0,60));
    }

    if (querAtendente || ehReclam) {
      // SEMPRE pausar bot e direcionar para painel quando cliente solicitar atendente ou reclamar
      if (!atendimentoHumano.has(numero)) {
        // Pausar bot e abrir atendimento humano — SEMPRE funciona, mesmo se toggle está OFF
        atendimentoHumano.set(numero, {
          inicio: new Date().toISOString(),
          motivo: querAtendente ? "solicitação do cliente" : "reclamação",
          msgs: [{ de:"cliente", texto:txt, ts:Date.now() }]
        });
        estadosPedido.delete(numero); // pausar fluxo de pedido
        limparTimeout(numero);
        emitirContador();
        io.emit("novo_atendimento", {
          numero: numero.replace("@c.us",""),
          motivo: querAtendente ? "solicitação do cliente" : "reclamação: "+txt.slice(0,60),
          ts: Date.now()
        });
        console.log("[ATENDENTE] Cliente solicitou atendimento humano, fluxo pausado");
      }
      // Notificar cliente que atendente foi chamado — mesmo se toggle está OFF
      const numAtend = (cfg.numeroAtendente||"").replace(/\D/g,"");
      const linkWpp  = numAtend ? `\n\n📲 Ou fale direto: https://wa.me/55${numAtend}` : "";
      resp = (
        `👤 *Atendente chamado!* ✅\n\n` +
        `Um atendente já foi notificado e vai te responder aqui em breve. 😊\n` +
        `_O bot está pausado até o atendimento ser encerrado._${linkWpp}`
      );
      await responderHumano(chat, msg, resp);
      logC({ tipo:"saida", para:numero, mensagem:resp });
      io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
      return;
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 1: FLUXO ESTRUTURADO
    //  Se o cliente está em alguma etapa, APENAS o fluxo responde.
    //  Nenhuma IA, nenhum fluxo de config interfere.
    // ════════════════════════════════════════════════════
    if (estadosPedido.has(numero)) {
      resp = await fluxoPedido(numero, txt, msg, config);
      // null = etapa não reconheceu → pedir para repetir
      if (resp === null) {
        const etapa = estadosPedido.get(numero)?.etapa || "";
        console.warn(`[FLUXO] Etapa "${etapa}" não reconheceu: "${txt}"`);
        resp = "Não entendi 😅\nPor favor, responda conforme a pergunta acima.";
      }

      // ── Enviar imagem do produto se acabou de ser adicionado ──
      // Detecta itens recém-adicionados e envia a foto antes da resposta de texto
      try {
        const eAtual = estadosPedido.get(numero);
        if (eAtual && eAtual.itens && waConectado && waClient && config.enviarImagemProduto !== false) {
          const itensAdicionados = (eAtual.itens || "").split("|").map(i => i.trim()).filter(Boolean);
          const ultimoItem = itensAdicionados[itensAdicionados.length - 1] || "";
          const nomeUltimo = ultimoItem.replace(/^\d+x\s+/, "").split("—")[0].trim().toLowerCase();
          // Procurar item no cardápio com imagem
          for (const cat of config.cardapio || []) {
            for (const item of cat.itens || []) {
              if (item.imagem && item.nome.toLowerCase().includes(nomeUltimo.slice(0, 6))) {
                const { MessageMedia } = require("whatsapp-web.js");
                const b64 = item.imagem.includes(",") ? item.imagem.split(",")[1] : item.imagem;
                const media = new MessageMedia("image/jpeg", b64, item.nome + ".jpg");
                await chat.sendMessage(media, { caption: `📸 *${item.nome}*${item.descricao ? "\n_" + item.descricao + "_" : ""}` });
                await sleep(500);
                break;
              }
            }
          }
        }
      } catch(eImg) {
        console.error("[IMG-PRODUTO]", eImg.message);
      }

      await responderHumano(chat, msg, resp);
      logC({ tipo: "saida", para: numero, mensagem: resp });
      io.emit("msg", { numero, mensagem: resp, tipo: "saida" });
      return; // ← RETORNO ANTECIPADO: nada mais processa
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 2a: PIZZA MEIO A MEIO — fluxo guiado
    // ════════════════════════════════════════════════════
    if (!estadosPedido.has(numero) && querPizzaMeio(txt)) {
      const _np = String(Date.now()).slice(-5);
      const _est = novoEstado(_np);
      _est.etapa = "pizza_sabor1";
      estadosPedido.set(numero, _est);
      resp = await fluxoPedido(numero, txt, msg, config);
      if (resp !== null) {
        await responderHumano(chat, msg, resp);
        logC({ tipo:"saida", para:numero, mensagem:resp });
        io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
        return;
      }
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 2: INICIAR PEDIDO NORMAL
    // ════════════════════════════════════════════════════
    if (parecePedido(txt, config)) {
      // Garantir que o fluxo seja iniciado mesmo que a mensagem
      // não tenha o gatilho exato "pedir"
      if (!estadosPedido.has(numero)) {
        const numPedido = String(Date.now()).slice(-5);
        estadosPedido.set(numero, {
          etapa: "itens", numPedido,
          itens: "", pagamento: "", troco: "", observacao: "",
          localizacao: null, rua: "", bairro: "", numEnd: "",
          tipoComp: "", complemento: "", referencia: "", telefone: "",
          inicio: new Date().toISOString()
        });
      }
      resp = await fluxoPedido(numero, txt, msg, config);
      if (resp !== null) {
        await responderHumano(chat, msg, resp);
        logC({ tipo: "saida", para: numero, mensagem: resp });
        io.emit("msg", { numero, mensagem: resp, tipo: "saida" });
        return;
      }
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 2.5: PROMOÇÕES ESPECIAIS
    // ════════════════════════════════════════════════════
    if (!estadosPedido.has(numero)) {
      const sLowP = txt.trim().toLowerCase().replace(/\.\s*$/, "");
      // Gatilhos ampliados — inclui variações de áudio como "promoções especiais", "ver promoções", etc.
      const querPromo = (
        sLowP === "7" ||
        /^(promo[cç][aã]o|promo[cç][oõ]es?|promo|promos?|ofertas?|descontos?|especiais?|novidades?|ver promo[cç][oõ]es?|quais (s[aã]o )?as promo[cç][oõ]es?|tem promo[cç][aã]o|promos especiais|promo[cç][oõ]es especiais|o que est[aá] em promo[cç][aã]o)$/i.test(sLowP)
      );
      if (querPromo) {
        const cfgFresh = loadConfig();
        if (cfgFresh.promoAtiva !== false) {
          const promos = (cfgFresh.promocoes||[]).filter(p=>p.ativo && p.nome);
          if (promos.length) {
            // Enviar cada promoção com número para pedir
            for (let pi = 0; pi < promos.length; pi++) {
              const p = promos[pi];
              try {
                const txt2 = (
                  `🔥 *${pi+1}. ${p.nome}*\n` +
                  (p.descricao ? `_${p.descricao}_\n` : "") +
                  (p.precoOriginal ? `~~R$ ${p.precoOriginal}~~  ` : "") +
                  (p.precoPromo ? `*R$ ${p.precoPromo}* 🏷️\n` : "") +
                  (p.desconto ? `✅ *${p.desconto}*\n` : "") +
                  `\n👉 Digite *P${pi+1}* para pedir esta promoção`
                );
                if (p.imagem && waConectado && waClient) {
                  const { MessageMedia } = require("whatsapp-web.js");
                  const b64 = p.imagem.includes(",") ? p.imagem.split(",")[1] : p.imagem;
                  const media = new MessageMedia("image/jpeg", b64, p.nome+".jpg");
                  await chat.sendMessage(media, { caption: txt2 });
                } else {
                  await chat.sendMessage(txt2);
                }
                await sleep(700);
              } catch(eP) { console.error("[PROMO]", eP.message); }
            }
            // Salvar lista de promos no estado para reconhecer P1, P2...
            historicos.set("__promos__"+numero, { promos, ts: Date.now() });
            const lista = promos.map((p,i)=>`*P${i+1}* — ${p.nome} ${p.precoPromo?"(R$ "+p.precoPromo+")":""}`).join("\n");
            resp = `\n📋 *Resumo das promoções:*\n${lista}\n\nDigite o código (ex: *P1*) para pedir! 🛒\n\n*0* ↩️ Voltar ao menu`;
          } else {
            resp = `😊 No momento não temos promoções ativas.\n\nConsulte nosso cardápio: *cardápio*!`;
          }
        } else {
          resp = `😊 No momento não temos promoções ativas.\n\nConsulte nosso cardápio: *cardápio*!`;
        }
        if (resp !== null) {
          await responderHumano(chat, msg, resp);
          logC({ tipo:"saida", para:numero, mensagem:resp });
          io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
          return;
        }
      }
    }


    // ════════════════════════════════════════════════════
    //  PRIORIDADE 2.7: ESCOLHER PROMOÇÃO POR CÓDIGO (P1, P2...)
    // ════════════════════════════════════════════════════
    if (!estadosPedido.has(numero) && resp === null) {
      // "0" = voltar ao menu
      if (txt.trim() === "0" && historicos.get("__promos__"+numero)) {
        historicos.delete("__promos__"+numero);
        const flBV = matchFluxo("oi", config);
        resp = flBV ? variaveis(flBV.resposta, config) : `Digite *oi* para o menu 😊`;
        await responderHumano(chat, msg, resp);
        logC({ tipo:"saida", para:numero, mensagem:resp });
        io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
        return;
      }
      const mP = txt.trim().match(/^[Pp](\d+)$/);
      if (mP) {
        const pIdx = parseInt(mP[1]) - 1;
        const promCache = historicos.get("__promos__"+numero);
        const promosList = promCache?.promos || (loadConfig().promocoes||[]).filter(p=>p.ativo&&p.nome);
        const escolhida = promosList[pIdx];
        if (escolhida) {
          // Iniciar pedido com esta promoção
          const numP = String(Date.now()).slice(-5);
          const estado = novoEstado(numP);
          // Usar preço promocional se disponível
          const precoUsar = escolhida.precoPromo || escolhida.precoOriginal || "—";
          estado.itens = `${escolhida.nome} — R$ ${precoUsar}`;
          estado.etapa = "mais_itens";
          estadosPedido.set(numero, estado);
          emitirContador();
          resetarTimeout(numero);
          const sub  = calcularTotal(estado.itens, config);
          const taxa = parseFloat((config.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
          const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
          resp = (
            `✅ *${escolhida.nome}* adicionado ao pedido! 🎉${subT}\n\n` +
            `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
            `👇 *Deseja mais alguma coisa?*\n\n` +
            `*1* ➕ Mais itens\n*2* ✅ Continuar para entrega\n*4* 🔄 Recomeçar`
          );
        } else {
          resp = `❓ Promoção *P${pIdx+1}* não encontrada.\n\nDigite *7* para ver as promoções disponíveis. 😊`;
        }
      }
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 3: FLUXOS CONFIGURADOS (menu, cardápio, etc.)
    // ════════════════════════════════════════════════════
    const fl = matchFluxo(txt, config);
    if (fl) {
      if (fl.id === "acompanhar") {
        estadosPedido.set(numero, { etapa:"acompanhar", inicio:new Date().toISOString() });
      }
      resp = variaveis(fl.resposta, config);
      // Fluxos informativos — sempre oferecer voltar ao menu
      const fluxosInfo = ["cardapio","horario_endereco","pagamento","tempo_entrega","taxa_entrega","ajuda","demora","agradecimento"];
      if (fluxosInfo.includes(fl.id)) {
        resp += "\n\n*0* ↩️ Voltar ao menu";
      }
      // Se fluxo de atendente → pausar bot SEMPRE (com ou sem toggle)
      if (fl.id === "atendente") {
        // Registrar atendimento humano
        atendimentoHumano.set(numero, {
          inicio: new Date().toISOString(),
          motivo: "solicitação do cliente",
          msgs: [{ de:"cliente", texto:txt, ts:Date.now() }]
        });
        estadosPedido.delete(numero); // garantir que fluxo de pedido seja pausado
        limparTimeout(numero);
        emitirContador();
        io.emit("novo_atendimento", {
          numero: numero.replace("@c.us",""),
          motivo: "solicitação do cliente",
          ts: Date.now()
        });
        const numAtend = (config.numeroAtendente||"").replace(/\D/g,"");
        const linkWpp  = numAtend
          ? `\n\n📲 Ou fale direto: https://wa.me/55${numAtend}`
          : "";
        resp = (
          `👤 *Atendente chamado!* ✅\n\n` +
          `Um de nossos atendentes foi notificado e vai te responder aqui em breve. 😊\n` +
          `_O bot está pausado. Quando resolver, o atendente encerra e o bot volta._${linkWpp}`
        );
      }
      // Se reclamação detectada → oferecer atendente (SEMPRE funciona)
      if (ehReclam && !atendimentoHumano.has(numero)) {
        atendimentoHumano.set(numero, {
          inicio: new Date().toISOString(),
          motivo: "reclamação",
          msgs: [{ de:"cliente", texto:txt, ts:Date.now() }]
        });
        estadosPedido.delete(numero);
        limparTimeout(numero);
        emitirContador();
        io.emit("novo_atendimento", {
          numero: numero.replace("@c.us",""),
          motivo: "reclamação: "+txt.slice(0,60),
          ts: Date.now()
        });
        resp += (
          `\n\n👤 *Atendente chamado!* ✅\n` +
          `O bot está pausado. Um de nós vai te atender aqui em breve.\n` +
          `_Quando resolver, o atendimento é encerrado e o bot volta._`
        );
      }
      // FEAT 3: personalizar boas-vindas se cliente retornou
      if (fl.id === "boas_vindas") {
        // Verificar se já tem nome — se não tiver, pedir
        const cliNome = getCliente(numero);
        if (!cliNome?.nome) {
          // Guardar que está aguardando nome
          historicos.set("__aguardando_nome__"+numero, true);
          resp = (
            `👋 Olá! Bem-vindo ao *${cfg.empresaNome||"Delivery"}*!\n\n` +
            `Antes de começar, qual é o seu *nome*? 😊`
          );
          await responderHumano(chat, msg, resp);
          logC({ tipo:"saida", para:numero, mensagem:resp });
          io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
          return;
        } else {
          // Já tem nome — personalizar resposta do fluxo boas_vindas
          resp = resp.replace(/^Olá! 👋/,"Olá, *"+cliNome.nome+"*! 👋");
        }
        try {
          const cli2 = getCliente(numero);
          if (cli2?.ultimoPedido?.itens) {
            const itensUlt = (cli2.ultimoPedido.itens||"").split(" | ")[0];
            // Data pode estar em formatos diferentes — tentar parse seguro
            const dataBruta = cli2.ultimoPedido.data || cli2.ultimoPedido.inicio || "";
            const dataObj   = dataBruta ? new Date(dataBruta) : null;
            const dataValida = dataObj && !isNaN(dataObj.getTime());
            const dataUlt    = dataValida ? dataObj.toLocaleDateString("pt-BR") : "recentemente";
            const diasPassados = dataValida
              ? Math.floor((Date.now() - dataObj.getTime()) / 86400000)
              : 999;
            const saudacao = diasPassados <= 1
              ? `Olá de novo! 😊 Bem-vindo de volta!\n`
              : diasPassados <= 7
                ? `Que saudade! 😊 Bem-vindo de volta!\n`
                : `Olá! Faz tempo que não te vejo! 😊 Bem-vindo de volta!\n`;
            const prefixo = (
              `${saudacao}` +
              `_Último pedido (${dataUlt}): ${itensUlt}_\n\n` +
              `👉 Digite *repetir* para pedir o mesmo ou escolha abaixo:\n\n`
            );
            resp = prefixo + resp.replace(/^Olá! 😊 /,"");
          }
        } catch(eSaud) {
          console.error("[SAUDAÇÃO]", eSaud.message);
          // Continua com resp normal sem saudação
        }
      }
    }

    // ════════════════════════════════════════════════════
    //  PRIORIDADE 4: IA (apenas para dúvidas gerais)
    //  NUNCA coleta dados de pedido.
    // ════════════════════════════════════════════════════
    if (resp === null && config.useAI) {
      addHist(numero, "user", txt);
      const iaResp = await chamarIA(numero, txt, config);
      if (iaResp) {
        // Bloquear se IA tentou conduzir pedido
        const low = iaResp.toLowerCase();
        const bloqueado = [
          "qual o endereço", "informe o endereço", "endereço de entrega",
          "número do imóvel", "qual o bairro", "seu telefone",
          "forma de pagamento", "confirmar pedido", "para continuar o pedido",
          "seu pedido foi"
        ].some(p => low.includes(p));

        if (bloqueado) {
          resp = "Para fazer seu pedido, é só digitar *pedir* 😊\nCuido de tudo no passo a passo! 🛵";
        } else {
          resp = iaResp;
          addHist(numero, "assistant", iaResp);
        }
      }
    }



    // ════════════════════════════════════════════════════
    //  FALLBACK — redireciona com menu completo
    // ════════════════════════════════════════════════════
    if (resp === null) {
      const sLowFb = txt.trim().toLowerCase();
      const ehNumero = /^\d+$/.test(txt.trim());
      const opcoes = (config.fluxos||[])
        .find(f=>f.id==="boas_vindas")?.resposta || "";

      if (ehNumero) {
        // Cliente digitou número inválido — mostrar menu de volta
        resp = (
          `❓ A opção *${txt.trim()}* não existe.\n\n` +
          `Escolha uma das opções abaixo:\n\n` +
          `*1* 🍽️ Ver Cardápio\n` +
          `*2* 🛒 Fazer Pedido\n` +
          `*3* 📦 Meu Pedido\n` +
          `*4* 🕐 Horário\n` +
          `*5* 💳 Pagamento\n` +
          `*6* 👤 Atendente`
        );
      } else {
        // Texto não reconhecido — oferecer menu + ajuda
        resp = (
          `😅 Não entendi *"${txt.slice(0,30)}"*\n\n` +
          `Tente uma dessas opções:\n\n` +
          `*1* 🍽️ Ver Cardápio\n` +
          `*2* 🛒 Fazer Pedido\n` +
          `*3* 📦 Meu Pedido\n` +
          `*4* 🕐 Horário\n` +
          `*5* 💳 Pagamento\n` +
          `*6* 👤 Atendente\n\n` +
          `_Ou descreva o que precisa!_ 😊`
        );
      }
    }

    await responderHumano(chat, msg, resp);
    logC({ tipo: "saida", para: numero, mensagem: resp });
    io.emit("msg", { numero, mensagem: resp, tipo: "saida" });

  } catch (err) {
    console.error("[MSG]", err.message);
    try { await msg.reply("Ops! Ocorreu um erro. Tente novamente em instantes 🙏"); } catch(_) {}
  }
}

// ═══════════════════════
//  SOCKET
// ═══════════════════════
io.on("connection", socket => {
  if (!authOk({ headers: { "x-token": socket.handshake.auth?.token }, query: socket.handshake.query })) {
    socket.disconnect(); return;
  }
  socket.emit("status", { conectado:waConectado, mensagem:waConectado?"WhatsApp conectado!":"Conecte o QR Code" });
  if (!waConectado) socket.emit("qr","loading");
  socket.emit("pedidos", listaPedidos());
  socket.emit("pedindo_agora", { total: estadosPedido.size });
  socket.emit("atend_humano_status", { ativo: atendHumanoAtivo, total: atendimentoHumano.size });
  socket.emit("auto_imprimir", { ativo:autoImprimir });
  socket.emit("vias_impressao", { vias:viasImpressao });
  socket.emit("agente_status", { ativo:agenteAtivo });
  socket.emit("cardapio_atualizado", config.cardapio||[]);
  socket.emit("status_wa_config", config.statusWA||[]);
  const l = loadLic();
  socket.emit("licenca", { ...l, diasRestantes:diasRestantes(), valida:licOk() });
});

// ═══════════════════════
//  LIMPEZA
// ═══════════════════════
setInterval(() => {
  const now = Date.now();
  for (const [k,v] of rateLimiter)  if(now-v>3*3600000)  rateLimiter.delete(k);
  for (const [k,v] of estadosPedido) if(now-new Date(v.inicio).getTime()>24*3600000) estadosPedido.delete(k);
  for (const [k,v] of sessoes)       if(now>v) sessoes.delete(k);
}, 3600000);

// ═══════════════════════
//  START
// ═══════════════════════
server.listen(PORT, () => {
  console.log(`\n╔══════════════════════════════════════════╗\n║  🛵 DELIVERY BOT v6 — Marco Roberto     ║\n║  http://localhost:${PORT}                  ║\n╚══════════════════════════════════════════╝\n`);
  initWA();
});
