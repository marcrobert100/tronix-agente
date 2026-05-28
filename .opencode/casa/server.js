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
const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const OpenAI   = require("openai");
const googleTTS= require("google-tts-api");
const crypto   = require("crypto");
const nodeFetch = (...args) => import("node-fetch").then(({default: f}) => f(...args));
const Tesseract = require("tesseract.js");
const { TTSService, VOICES } = require("./tts-service");

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


// ═══════════════════════
//  TTS: Text-to-Speech com ElevenLabs
// ═══════════════════════
let ttsService = null;
function initTTS() {
  ttsService = new TTSService({
    ttsApiKey: config.ttsApiKey,
    ttsVoiceId: config.ttsVoiceId,
    ttsModel: config.ttsModel,
    ttsStability: config.ttsStability,
    ttsSimilarityBoost: config.ttsSimilarityBoost,
    ttsStyleExaggeration: config.ttsStyleExaggeration,
    ttsEnabled: config.ttsEnabled || false
  });
  if (config.ttsEnabled) {
    console.log("[TTS] Serviço inicializado com voz:", config.ttsVoiceId || "padrão");
  }
}
initTTS();

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

// ═══════════════════════
//  OCR FUNCTION
// ═══════════════════════
async function extrairDadosComprovante(caminhoImagem) {
  try {
    const { data: { text } } = await Tesseract.recognize(caminhoImagem, 'por', {
      logger: m => console.log(`[OCR] ${m.status} ${m.progress || 0}`)
    });
    
    console.log("[OCR] Texto extraído:", text);
    
    // Expressão regular para encontrar valor monetário (R$ 00,00)
    const valorRegex = /R\$\s*(\d+[\.,]?\d*[\.,]?\d*)/i;
    const valorMatch = text.match(valorRegex);
    
    // Expressão regular para encontrar data (DD/MM/AAAA ou similar)
    const dataRegex = /(\d{1,2}\/\d{1,2}\/\d{2,4})/;
    const dataMatch = text.match(dataRegex);
    
    // Expressão regular para encontrar chave Pix ou CPF/CNPJ
    const chaveRegex = /(Chave:\s*[\w\.\-@]+|CPF:\s*\d{3}\.\d{3}\.\d{3}-\d{2}|CNPJ:\s*\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})/i;
    const chaveMatch = text.match(chaveRegex);
    
    return {
      textoCompleto: text,
      valor: valorMatch ? valorMatch[1].replace(',', '.') : null,
      data: dataMatch ? dataMatch[1] : null,
      chave: chaveMatch ? chaveMatch[0] : null,
      processado: true
    };
  } catch (error) {
    console.error("[OCR] Erro:", error.message);
    return { textoCompleto: "", valor: null, data: null, chave: null, processado: false, erro: error.message };
  }
}

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
app.use("/logs", express.static(path.join(__dirname, "logs")));

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
    iaAtiva: !!mimoClient && !!config.useAI, mimoConfigurada: !!(config.mimoApiKey || "").startsWith("sk_"),
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

// ── TTS: Configuração do Text-to-Speech ──
app.get("/api/tts/config", guard, (req, res) => {
  res.json({
    enabled: config.ttsEnabled || false,
    voiceId: config.ttsVoiceId || '21m00Tcm4TlvDq8ikWAM',
    model: config.ttsModel || 'eleven_multilingual_v2',
    stability: config.ttsStability || 0.5,
    similarityBoost: config.ttsSimilarityBoost || 0.75,
    styleExaggeration: config.ttsStyleExaggeration || 0.0,
    apiKeyConfigured: !!(config.ttsApiKey && config.ttsApiKey.length > 10)
  });
});

app.post("/api/tts/config", guard, (req, res) => {
  const body = req.body || {};
  config.ttsEnabled = !!body.enabled;
  if (body.voiceId) config.ttsVoiceId = body.voiceId;
  if (body.model) config.ttsModel = body.model;
  if (body.stability !== undefined) config.ttsStability = body.stability;
  if (body.similarityBoost !== undefined) config.ttsSimilarityBoost = body.similarityBoost;
  if (body.styleExaggeration !== undefined) config.ttsStyleExaggeration = body.styleExaggeration;
  
  saveConfig(config);
  initTTS();
  res.json({ ok: true, msg: "Configuração TTS salva!" });
});

app.post("/api/tts/key", guard, (req, res) => {
  const raw = (req.body || {}).key || "";
  const key = raw.trim();
  if (!key || key.length < 20) {
    return res.status(400).json({ ok: false, erro: "Chave inválida. Deve ter pelo menos 20 caracteres." });
  }
  const cfg = loadConfig();
  cfg.ttsApiKey = key;
  saveConfig(cfg);
  config = cfg;
  initTTS();
  console.log("[TTS] ✅ Chave ElevenLabs salva com sucesso.");
  res.json({ ok: true, msg: "Chave salva! TTS ativado." });
});

app.get("/api/tts/voices", guard, async (req, res) => {
  try {
    const voices = await ttsService.getVoices();
    res.json({ ok: true, voices });
  } catch (error) {
    res.status(500).json({ ok: false, erro: error.message });
  }
});

app.get("/api/tts/voices/popular", guard, (req, res) => {
  // Retornar lista de vozes populares pré-definidas
  const popularVoices = [
    { id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel v3', gender: 'female', language: 'Portuguese' },
    { id: 'pNInz6vpgTzT1eiaSkG', name: 'Adam', gender: 'male', language: 'English' },
    { id: 'EXAVITQu4vr4xnSDxGS', name: 'Bella', gender: 'female', language: 'English' },
    { id: 'ErXwobaYjN0EzvQzbNU', name: 'Antoni', gender: 'male', language: 'English' },
    { id: 'VR6AewLTigWG4xSuka91', name: 'Arnold', gender: 'male', language: 'English' },
    { id: 'MF3mGyEYCl7XYWbV9Qau', name: 'Elli', gender: 'female', language: 'English' },
    { id: 'TxGEqnHWrfWFTfGW9XjX', name: 'Josh', gender: 'male', language: 'English' },
    { id: 'AZnzlk1XvdvUeBn8csK', name: 'Domi', gender: 'female', language: 'English' },
    { id: 'XB0fDUnXU5powFXDhCwa', name: 'Charlotte', gender: 'female', language: 'English' },
    { id: 'XrExE9yKIg1WjnnlVkGX', name: 'Matilda', gender: 'female', language: 'English' },
    { id: 'Yko7PKHZNXotMUB3Dag', name: 'Matthew', gender: 'male', language: 'English' },
    { id: 'flq6f7yk4E4fJM5XTYuZ', name: 'Michael', gender: 'male', language: 'English' },
    { id: 'LcfcDJNUP1GQjkzn1xUU', name: 'Emily', gender: 'female', language: 'English' },
    { id: '0EE7fFjzDp6W13j3Ly', name: 'Grace', gender: 'female', language: 'English' },
    { id: 'onwK4e9Z3Tg9oabfA6G', name: 'Daniel', gender: 'male', language: 'English' },
    { id: 'pMsXgVXv3BLTtc2OqYe', name: 'Serena', gender: 'female', language: 'English' },
    { id: 'TX3LPaxmHKxFdv7VOQH', name: 'Liam', gender: 'male', language: 'English' },
    { id: 'cgSgvpJhoMroOr11kCF', name: 'Jessica', gender: 'female', language: 'English' },
    { id: 'cjVigY5qzO86Huf0OWal', name: 'Eric', gender: 'male', language: 'English' },
    { id: 'ODQ5ZHVqyTqxPNQbUw', name: 'Patrick', gender: 'male', language: 'English' }
  ];
  res.json({ ok: true, voices: popularVoices });
});

app.post("/api/tts/test", guard, async (req, res) => {
  const { text, engine } = req.body || {};
  if (!text) return res.status(400).json({ ok: false, erro: "Texto obrigatório" });
  
  try {
    let audioBuffer = null;
    
    // Google TTS (gratuito)
    if (engine === "google" || !ttsService.apiKey) {
      const results = await googleTTS.getAllAudioBase64(text, {
        lang: 'pt',
        slow: false,
        host: 'https://translate.google.com',
        timeout: 15000,
      });
      if (results && results.length > 0) {
        const buffers = results.map(r => Buffer.from(r.base64, 'base64'));
        audioBuffer = Buffer.concat(buffers);
      }
    } else {
      // ElevenLabs
      audioBuffer = await ttsService.generateSpeech(text);
    }
    
    if (!audioBuffer) {
      return res.status(500).json({ ok: false, erro: "Falha ao gerar áudio" });
    }
    
    // Salvar áudio temporário
    const filename = `tts-test-${Date.now()}.mp3`;
    const outputDir = path.join(__dirname, 'logs', 'tts');
    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
    fs.writeFileSync(path.join(outputDir, filename), audioBuffer);
    
    // Retornar URL para o áudio
    const audioUrl = `/logs/tts/${filename}`;
    res.json({ ok: true, audioUrl, engine: engine === "google" || !ttsService.apiKey ? "google" : "elevenlabs" });
  } catch (error) {
    console.error('[TTS-TEST] Erro:', error.message);
    res.status(500).json({ ok: false, erro: error.message });
  }
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

  // ── Calcular faturamento usando os campos de total do pedido ──
  function calcFaturamento(lista) {
    return lista.reduce((acc, v) => {
      // Se o pedido já tem o campo 'total' calculado (numérico), usa ele
      if (v.total !== undefined && !isNaN(parseFloat(v.total))) {
        return acc + parseFloat(v.total);
      }
      
      // Caso contrário, recalcula usando a função robusta
      const sub = calcularTotal(v.itens, config);
      const taxa = typeof v.taxaEntrega === "number" ? v.taxaEntrega : parseFloat((v.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",","."));
      return acc + sub + (isNaN(taxa) ? 0 : taxa);
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

// Saiu para entrega (notifica cliente, mantém na lista)
app.post("/api/pedidos/:num/sair", guard, async (req, res) => {
  const { num } = req.params;
  if (!pedidosAbertos.has(num)) return res.status(404).json({ ok: false });
  const pedido = pedidosAbertos.get(num);
  pedido.status = "em_entrega";
  pedidosAbertos.set(num, pedido);
  io.emit("pedidos", listaPedidos());
  if (waConectado && waClient && pedido) {
    try {
      const cfg = loadConfig();
      const tempo = cfg.tempoEntrega || "30-50 minutos";
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
    } catch(e) { console.error("[NOTIF]", e.message); }
  }
  res.json({ ok: true });
});

// Entregue (remove da lista, agenda avaliação)
app.post("/api/pedidos/:num/entregar", guard, async (req, res) => {
  const { num } = req.params;
  if (!pedidosAbertos.has(num)) return res.status(404).json({ ok: false });
  const pedido = pedidosAbertos.get(num);
  pedidosAbertos.delete(num);
  io.emit("pedidos", listaPedidos());
  if (waConectado && waClient && pedido) {
    try {
      const msgEntregue = (
        `✅ *Pedido entregue!*\n\n` +
        `Obrigado pela preferência! 😊🍕\n` +
        `_Esperamos você novamente!_`
      );
      await waClient.sendMessage(num, msgEntregue);
      agendarAvaliacao(num, pedido);
    } catch(e) { console.error("[NOTIF]", e.message); }
  }
  res.json({ ok: true });
});

// ── COMPROVANTES: Verificar/Rejeitar ──
app.post("/api/comprovantes/verificar", guard, async (req, res) => {
  const { numero, filename, status, observacao } = req.body || {};
  if (!numero || !filename || !status) return res.status(400).json({ ok: false, erro: "Dados incompletos" });
  
  const numKey = numero.includes("@c.us") ? numero : numero + "@c.us";
  const pedido = pedidosAbertos.get(numKey) || Array.from(pedidosAbertos.entries()).find(([n]) => n.replace("@c.us","") === numero.replace("@c.us",""));
  
  if (!pedido) return res.status(404).json({ ok: false, erro: "Pedido não encontrado" });
  
  if (!pedido.comprovantes) pedido.comprovantes = [];
  
  const comprovante = pedido.comprovantes.find(c => c.filename === filename);
  if (!comprovante) return res.status(404).json({ ok: false, erro: "Comprovante não encontrado" });
  
  comprovante.status = status;
  comprovante.observacao = observacao;
  comprovante.verificadoEm = new Date().toISOString();
  
  io.emit("pedidos", listaPedidos());
  io.emit("comprovante_verificado", { numero, filename, status, observacao });
  
  // Notificar cliente via WhatsApp
  if (waConectado && waClient) {
    try {
      let msgNotif = "";
      if (status === "verificado") {
        msgNotif = "✅ *Comprovante verificado!*\n\nSeu pagamento foi confirmado. Seu pedido está sendo preparado! 🍕";
      } else if (status === "rejeitado") {
        msgNotif = `⚠️ *Comprovante rejeitado*\n\nMotivo: ${observacao || "Não especificado"}\n\nPor favor, envie um novo comprovante válido.`;
      }
      if (msgNotif) await waClient.sendMessage(numKey, msgNotif);
    } catch(e) { console.error("[NOTIF_COMPROVANTE]", e.message); }
  }
  
  res.json({ ok: true, status, observacao });
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
  if (!mimoClient || !cfg.useAI) return null;

  // Cardápio completo com descrições para a IA responder com mais detalhes
  const cardTxt = (cfg.cardapio || []).map(cat =>
    `[${cat.categoria}]: ` +
    (cat.itens||[]).filter(i=>!i.pausado).map(i =>
      `${i.nome} - ${i.preco}${i.descricao ? " ("+i.descricao+")" : ""}${i.tamanhos ? " ["+i.tamanhos+"]" : ""}`
    ).join(" | ")
  ).join("\n");

  const sys = `${cfg.promptSistema || "Você é um atendente humano de delivery. Fale como uma pessoa real, com jeito natural e caloroso."}

=== QUEM VOCÊ É ===
Você é o(a) atendente do ${cfg.empresaNome}. Trate o cliente como um amigo que está pedindo comida na casa dele. Seja gentil, prestativo e direto — sem parecer robô.

=== EMPRESA ===
Nome: ${cfg.empresaNome}
Endereço: ${cfg.empresaEndereco}
Horário: ${cfg.horarioFuncionamento}
Telefone: ${cfg.empresaTelefone||""}
Taxa: ${cfg.taxaEntrega} | Tempo: ${cfg.tempoEntrega} | Mínimo: ${cfg.pedidoMinimo}
Pagamentos: ${cfg.pagamentos} | Pix: ${cfg.pixChave}

=== CARDÁPIO ===
${cardTxt}

=== COMO FALAR ===
1. Fale como gente: "Oi! Tudo bem?" ou "Opa, bom dia!" — não "Olá, como posso ajudar?"
2. Use o nome do cliente se souber. Ex: "Oi, Maria! 😊"
3. Confirme pedidos com entusiasmo: "Beleza! Anotei tudo certinho ✅"
4. Se atrasar, seja honesto: "Tá demorando um pouco, mas já tá no forno!"
5. Use emojis com moderação (2-3 por msg, no máximo). Não encha de emoji.
6. Máximo 4 linhas por mensagem. Seja objetivo mas carinhoso.
7. Se não souber algo: "Deixa eu verificar com a equipe e já te retorno! 😊"
8. Para pedidos: "Pra fazer seu pedido, é só mandar *pedir* que eu te ajudo! 😊"
9. NUNCA invente preços ou itens. Use SOMENTE o cardápio acima.
10. Nunca colete dados pessoais — o sistema já cuida disso.
11. Varie as respostas. Não repita sempre as mesmas frases.
12. Se o cliente elogiar, agradeça de coração: "Que bom que gostou! Fico muito feliz! ❤️"`;

  const hist = historicos.get(numero) || [];
  try {
    const r = await mimoClient.chat.completions.create({
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
      if (!item.pausado && n.includes(item.nome.toLowerCase())) return item;
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
    (cat.itens||[]).some(i => s.includes(i.nome.toLowerCase()))
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
    const sep = itensTxt.includes(" | ") ? " | " : /,(?![^\(]*\))/;
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
  // Limpa quebras de linha e normaliza espaços
  const textoLimpo = (itensTxt || "").replace(/\n/g, " ").replace(/\s+/g, " ");
  // IMPORTANTE: Itens principais são separados por " | ". 
  // Não podemos usar vírgula como separador global pois acompanhamentos (dentro de parênteses) usam vírgulas.
  // Se não houver " | ", tratamos o texto todo como um único item ou tentamos uma divisão segura.
  let partes = [];
  if (textoLimpo.includes(" | ")) {
    partes = textoLimpo.split(" | ");
  } else {
    // Se não tem " | ", pode ser um item único ou formato antigo com vírgulas.
    // Mas só separamos por vírgula se a vírgula NÃO estiver dentro de parênteses.
    // Regex para split por vírgula fora de parênteses:
    const partesPotenciais = textoLimpo.split(/,(?![^\(]*\))/);
    partes = partesPotenciais.map(p => p.trim()).filter(p => p.length > 0);
  }

  for (const parte of partes) {
    const p = parte.trim();
    if (!p) continue;
    const pl = p.toLowerCase();

    // 1. Extrai a quantidade (ex: "10x")
    const qtdM = pl.match(/^(\d+)x?\s+/);
    const qtd = qtdM ? parseInt(qtdM[1]) : 1;

    // 2. Tenta extrair o preço unitário do item principal
    // Prioriza o formato " — R$ 32,00" ou " — 15"
    // Remove o que está entre parênteses (acompanhamentos) para não confundir o preço do item
    // Também remove qualquer " + R$ ..." ou " + 10" que possa ter sido adicionado erroneamente aos acompanhamentos
    const textoSemAcomp = p.replace(/\(.*\)/, "").replace(/\+\s*R\$\s*[\d,.]+/gi, "").replace(/\+\s*[\d,.]+/gi, "");
    const precoMatch = textoSemAcomp.match(/(?:—\s*R\$\s*|—\s*)([\d]+(?:[,.][\d]{2})?)/i);
    
    if (precoMatch) {
      const precoUnitario = parseFloat(precoMatch[1].replace(",", "."));
      if (!isNaN(precoUnitario)) {
        // Multiplica Quantidade x Preço Unitário (Acompanhamentos são GRATUITOS, valor zero)
        total += (precoUnitario * qtd);
        continue;
      }
    }

    // 3. Fallback: Busca no cardápio se não houver preço no texto
    // IMPORTANTE: Remove acompanhamentos da busca para não cobrar por eles se tiverem nome igual a um item do cardápio
    const nomeBusca = pl.replace(/\(.*\)/, "").trim();
    let achouNoCardapio = false;
    if (cfg && cfg.cardapio) {
      for (const cat of cfg.cardapio) {
        for (const item of cat.itens || []) {
          if (item.pausado) continue;
          // Busca por nome (mínimo 4 caracteres para evitar falsos positivos)
          const nomeItem = item.nome.toLowerCase();
          if (nomeItem.length >= 4 && nomeBusca.includes(nomeItem)) {
            const pr = parseFloat((item.preco || "").replace(/[^\d,.]/g, "").replace(",", "."));
            if (!isNaN(pr)) {
              total += (pr * qtd);
              achouNoCardapio = true;
              break;
            }
          }
        }
        if (achouNoCardapio) break;
      }
    }
  }
  return total;
}

// ─── cardápio formatado ───
// ── Emoji/cor por tipo de categoria ──
function emojiCategoria(nome) {
  const n = nome.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
  if (/pizza/.test(n))                         return "🍕";
  if (/hamburguer|hamburger|burguer|burger|lanche|x-/.test(n)) return "🍔";
  if (/suco|vitamina|smoothie/.test(n))        return "🥤";
  if (/refri|refrigerante|coca|bebida|drink/.test(n)) return "🥤";
  if (/pastel|salgad/.test(n))                 return "🥟";
  if (/frango|galinha|chicken/.test(n))        return "🍗";
  if (/carne|churrasco|espeto|costela/.test(n))return "🥩";
  if (/peixe|frutos|camarao|mariscos/.test(n)) return "🦐";
  if (/salada|verdura|vegano|vegetariano/.test(n)) return "🥗";
  if (/sobremesa|doce|sorvete|bolo|torta/.test(n)) return "🍰";
  if (/tapioca|crepe/.test(n))                 return "🫓";
  if (/acai|açai/.test(n))                     return "🫐";
  if (/sanduiche|hot dog/.test(n))             return "🌭";
  if (/cafe|cafeteria|manha/.test(n))          return "☕";
  if (/combo|promo|especial|destaque/.test(n)) return "🔥";
  if (/adulto|familia|crianca/.test(n))        return "👨‍👩‍👧";
  return "🍽️";
}

// Separadores visuais por índice de categoria (rotação de padrões)
const SEP_CATS = ["━━━━━━━━━━━━━━━━━━", "──────────────────", "▸▸▸▸▸▸▸▸▸▸▸▸▸▸▸▸▸▸", "· · · · · · · · · ·"];

function cardResumido(cfg) {
  return (cfg.cardapio||[]).map((cat, ci) => {
    const ativos = (cat.itens||[]).filter(i => !i.pausado);
    if (!ativos.length) return null;
    const ico = emojiCategoria(cat.categoria);
    const sep = SEP_CATS[ci % SEP_CATS.length];
    return (
      `${sep}\n` +
      `${ico} *${cat.categoria.toUpperCase()}*\n` +
      `${sep}\n` +
      ativos.map((i, ii) =>
        `  *${ci+1}.${ii+1}* ${i.nome} — *${i.preco}*` +
        (i.tamanhos  ? ` _(${i.tamanhos})_` : "") +
        (i.descricao ? `\n       _${i.descricao}_` : "")
      ).join("\n")
    );
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
  const promsAtivas = (cfg.promocoes||[]).filter(p=>p.ativo&&p.nome);
  const promoStr = promsAtivas.length
    ? "\n\n🔥 *PROMOÇÕES:* Digite *7* para ver! (" + promsAtivas.length + " ativas)"
    : "";
  return (
    `🍽️ *CARDÁPIO ${cfg.empresaNome||""}*\n` +
    `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
    `${cardResumido(cfg)}` +
    `${promoStr}\n\n` +
    `━━━━━━━━━━━━━━━━━━━━━━\n` +
    `🛒 *Para pedir, é só dizer!*\n` +
    `_Ex: "2 X-Bacon e 1 suco de uva"_\n` +
    `_Ex de voz: "dois x-bacon duplo com cinco refrigerantes"_\n\n` +
    `*2* 🛒 Fazer pedido agora\n` +
    `*7* 🔥 Ver promoções\n` +
    `*0* ↩️ Voltar ao menu`
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

  // Formatar itens de forma legível
  const itensFormatados = (e.itens||"").split(" | ").map(i => `  • ${i}`).join("\n");

  return (
    `\n━━━━━━━━━━━━━━━━━━━━━━\n` +
    `🧾 *RESUMO DO PEDIDO #${e.numPedido}*\n` +
    `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
    `🛒 *Itens:*\n${itensFormatados}\n` +
    `${valStr}\n` +
    `${endFmt}\n` +
    `📞 *Tel:* ${e.telefone||"—"}\n` +
    `💳 *Pagamento:* ${e.pagamento}${trocoStr}${obsStr}\n` +
    `⏱️ *Entrega:* ${cfg.tempoEntrega||"30-50 min"}\n\n` +
    `━━━━━━━━━━━━━━━━━━━━━━\n` +
    `👆 *Está tudo certo?*\n\n` +
    `*1* ✅ Confirmar e enviar\n` +
    `*2* ✏️  Corrigir algo\n` +
    `*3* ➕ Adicionar item\n` +
    `*4* 🗑️ Remover item\n` +
    `*5* 🔄 Cancelar e recomeçar`
  );
}

// ── Valida e resolve item digitado pelo cliente ──
// Retorna { ok:true, item, nomeFinal } ou { ok:false, sugestoes }
// Extrai quantidade e nome. Suporta todos os padrões de voz:
//   "5 bacon duplo"          → { qtd:5, texto:"bacon duplo" }
//   "bacon duplo 5 unidades" → { qtd:5, texto:"bacon duplo" }
//   "cinco sucos de uva"     → { qtd:5, texto:"sucos de uva" }
//   "suco de uva, 5 unidades"→ { qtd:5, texto:"suco de uva" }
//   "3x bacon"               → { qtd:3, texto:"bacon" }
//   "3 x bacon duplo"        → { qtd:3, texto:"bacon duplo" }
//   "XB com duplo, 3 unid"   → { qtd:3, texto:"XB com duplo" }
function extrairQtd(txt) {
  const s = txt.trim().replace(/[.,!?;:]+$/, "").trim(); // remove pontuação final do Whisper

  const NUM_EXTENSO = {
    "um":1,"uma":1,"dois":2,"duas":2,"três":3,"tres":3,"quatro":4,
    "cinco":5,"seis":6,"sete":7,"oito":8,"nove":9,"dez":10,
    "onze":11,"doze":12,"treze":13,"catorze":14,"quatorze":14,"quinze":15,
    "dezesseis":16,"dezessete":17,"dezoito":18,"dezenove":19,"vinte":20
  };

  // ── 1. Número EXTENSO no início: "cinco sucos de uva" ──
  const mExt = s.match(/^(um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quatorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte)\s+(?:x\s+)?(.+)$/i);
  if (mExt) {
    const qtd = NUM_EXTENSO[mExt[1].toLowerCase()] || 1;
    return { qtd: Math.min(qtd, 20), texto: mExt[2].trim() };
  }

  // ── 2. "3x bacon" ou "3 x bacon" ──
  const mX = s.match(/^(\d+)\s*x\s+(.+)$/i);
  if (mX) return { qtd: Math.min(parseInt(mX[1]), 20), texto: mX[2].trim() };

  // ── 3. Número EXTENSO no FINAL: "bacon duplo cinco unidades" / "suco de uva, cinco" ──
  const mExtFim = s.match(/^(.+?)[,\s]+(?:x\s*)?(um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|catorze|quatorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte)\s*(?:unidades?|und\.?|un\.?|pç|pçs|vezes)?$/i);
  if (mExtFim) {
    const qtd = NUM_EXTENSO[mExtFim[2].toLowerCase()] || 1;
    return { qtd: Math.min(qtd, 20), texto: mExtFim[1].trim().replace(/,\s*$/, "") };
  }

  // ── 4. Número DÍGITO no FINAL: "bacon duplo 5" / "suco de uva, 5 unidades" ──
  const mFim = s.match(/^(.+?)[,\s]+(\d+)\s*(?:unidades?|und\.?|un\.?|pç|pçs|vezes|x)?\s*$/i);
  if (mFim) {
    const qtd = parseInt(mFim[2]);
    const textoAntes = mFim[1].trim().replace(/,\s*$/, "");
    // Não extrair qtd se o texto resultante for muito curto ou genérico (ex: "Número 3" → endereço)
    const PALAVRAS_CONTEXTO = ["número","numero","nº","n°","rua","av","avenida","bloco","apto","apartamento"];
    const ehContextoEnd = PALAVRAS_CONTEXTO.some(p => textoAntes.toLowerCase().includes(p));
    if (qtd >= 1 && qtd <= 20 && textoAntes.length >= 3 && !ehContextoEnd) {
      return { qtd, texto: textoAntes };
    }
  }

  // ── 5. Número DÍGITO no início: "5 bacon duplo" ──
  const mN = s.match(/^(\d+)\s+(.+)$/);
  if (mN) {
    const textoDepois = mN[2].trim();
    // Não tratar como qtd se o que vem depois é palavra de contexto (ex: "3 bairros", raro)
    return { qtd: Math.min(parseInt(mN[1]), 20), texto: textoDepois };
  }

  return { qtd: 1, texto: s };
}

// Normaliza: remove acentos, pontuação final, plural simples
// Normaliza: remove acentos, pontuação final, plural, preposições
function normStr(s) {
  return (s||"").toLowerCase().normalize("NFD")
    .replace(/[\u0300-\u036f]/g,"")    // remove acentos
    .replace(/[-_]/g, " ")               // hifen/underscore → espaço: "x-bacon" → "x bacon"
    .replace(/[.,!?;:]+$/, "")           // pontuação final do Whisper
    .replace(/\bcoca(\s*)cola\b/gi, "coca lata")
    .replace(/\brefrigerante(s)?\b/gi, "coca lata")
    .replace(/\b(em|de|do|da|dos|das|com|e|o|a|os|as|um|uma|para|pro|pra)\b/g, " ")
    .replace(/s\b/g, "")               // plural simples
    .replace(/\s+/g, " ")
    .trim();
}

function validarItem(txt, cfg) {
  const s = normStr(txt);
  const sRaw = txt.toLowerCase().trim();
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

  // 1. Match exato (com e sem normalização)
  for (const item of todos) {
    const n = normStr(item.nome);
    const nRaw = item.nome.toLowerCase();
    if (n === s || nRaw === sRaw) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
  }

  // 1b. Substring — normalizado
  if (s.length >= 4) {
    for (const item of todos) {
      const n = normStr(item.nome);
      if (n.includes(s) || s.includes(n)) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  // 1c. Substring parcial (primeiros 8 chars)
  if (s.length >= 5) {
    for (const item of todos) {
      const n = normStr(item.nome);
      if (n.slice(0,8) === s.slice(0,8)) return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  // 2. Cada palavra principal do item encontrada na msg (normalizado)
  for (const item of todos) {
    const palavras = normStr(item.nome).split(/\s+/).filter(p=>p.length>3);
    const acertos = palavras.filter(p => s.includes(p));
    if (palavras.length > 0 && acertos.length >= 1 && acertos.length >= Math.ceil(palavras.length*0.5)) {
      return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  // 2b. Tokens da busca encontrados no item (ex: "uva" → "suco de uva")
  const tokensB = s.split(/\s+/).filter(t=>t.length>=3);
  for (const item of todos) {
    const nItem = normStr(item.nome);
    const acertosRev = tokensB.filter(t=>nItem.includes(t));
    if (acertosRev.length >= 1 && acertosRev.length >= Math.ceil(tokensB.length*0.6)) {
      return { ok:true, item, nomeFinal:`${item.nome} — ${item.preco}` };
    }
  }

  // 3. Levenshtein - soma da distância mínima para os tokens de busca
  const tokens = s.split(/\s+/).filter(t => t.length > 3);
  let melhor = null, melhorScore = 999;
  if (tokens.length > 0) {
    for (const item of todos) {
      const palavras = item.nome.toLowerCase().split(/\s+/).filter(p=>p.length>3);
      if (!palavras.length) continue;
      let sumScore = 0;
      for (const tk of tokens) {
        let minWordD = 99;
        for (const pw of palavras) {
          const d = levenshtein(tk, pw);
          if (d < minWordD) minWordD = d;
        }
        sumScore += minWordD;
      }
      const avgDist = sumScore / tokens.length;
      if (avgDist < melhorScore) { 
        melhorScore = avgDist; 
        melhor = item; 
      }
    }
  }
  // Aceitar apenas se a distância média for menor ou igual a 2!
  if (melhor && melhorScore <= 2) {
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
  const s = t.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  return [
    "cancelar","cancela","cancelo","vou cancelar","quero cancelar",
    "desistir","desisto","nao quero","não quero","sair","apagar pedido",
    "deletar pedido","excluir pedido"
  ].some(g => s.includes(g));
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

  // Formata acompanhamentos garantindo que o sinal de "+" esteja presente para o cálculo de total
  const acompStr = acomps.length ? ` (+ ${acomps.join(", ")})` : "";
  // Acompanhamentos são gratuitos, não devem alterar o preço do item principal
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
  // Normalizar: remover acentos para comparação robusta
  const s = t.trim().toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // remove acentos
  const sOrig = t.trim().toLowerCase();

  // ── Opção "2" / "dois" isolado = ir para entrega (continuar fluxo) ──
  if (/^(2|dois)$/.test(s)) return "continuar";

  // ── "Continua" ou "continuar" sozinhos = ir para entrega ──
  if (/^(continua|continuar|continuo|continuei|ok|pronto|ta bom|tudo|pode ser|so isso|so|vamos)$/.test(s)) return "continuar";

  // ── Padrões que significam FECHAR/IR PARA ENTREGA ──
  const fecharPadroes = [
    /fechar.*pedido|pedido.*fechar/,
    /finaliz.*pedido|pedido.*finaliz/,
    /confirm.*pedido|pedido.*confirm/,
    /encerr.*pedido|pedido.*encerr/,
    /conclui.*pedido|pedido.*conclui/,  // pega "concluí" normalizado
    /pronto.*pedido|pedido.*pronto/,
    /^(finalizar|fechar|confirmar|encerrar|concluir)$/,
    /ir (para |pro )?(a )?entrega/,
    /continua(r)? (para |pro )?(a )?entrega/,
    /continua o pedido/,
    /continuar o pedido/,
    /seguir (com|para|pro)/,
    /proximo (passo|etapa)/,
    /proxima (etapa|fase)/,
  ];
  if (fecharPadroes.some(p => p.test(s) || p.test(sOrig))) return "fechar";

  // "fechar"/"finaliz"/"conclui" etc + "pedido"
  if (["fechar","finaliz","confirm","encerra","conclui","pronto"]
    .some(p => s.includes(p)) && s.includes("pedido")) return "fechar";

  // ── Padrões que significam ADICIONAR MAIS ITENS ──
  // IMPORTANTE: retorna "adicionar" para ir para itens_extra, NÃO para endereço
  const adicionarPadroes = ["mais item","adicionar","adiciona","outro item","mais algo","quero mais","sim quero","mais coisas","quero adicionar"];
  if (adicionarPadroes.some(p => s.includes(p)) && !s.includes("fechar") && !s.includes("entrega")) {
    return "adicionar";
  }
  // "mais" isolado ou "sim" isolado = adicionar mais
  if (/^(mais|sim|1)$/.test(s)) return "adicionar";

  // "não"/"nao" isolado = não quer mais = ir para entrega
  if (/^(nao|n|nn)$/.test(s)) return "fechar";

  return false;
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

  // ── Ver cardápio / MENU / VOLTAR em qualquer etapa do pedido ──
  if (e) {
    const sLowC = txt.trim().toLowerCase().replace(/\.\s*$/, "");

    // MENU/VOLTAR funciona em QUALQUER etapa — nunca deixa o cliente preso
    const GATILHOS_MENU = ["oi","olá","ola","bom dia","boa tarde","boa noite","bom noite","menu","início","inicio",
      "voltar","home","principal","começo","comeco","tela principal","página inicial","pagina inicial",
      "tela inicial","opções","opcoes","voltar ao menu","voltar o menu","voltar pro menu","ir pro menu","vai pro menu","ver menu",
      "eai","e ai","tudo","tudo bem","tudo bom","hello","ola","olaa"];
    const querMenu = GATILHOS_MENU.some(g => sLowC === g || sLowC === g.trim());

    if (querMenu) {
      if (e.etapa === "itens" && !e.itens) {
        return mostrarCardapio(cfg);
      }
      if (e.itens) {
        const sub  = calcularTotal(e.itens, cfg);
        const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
        const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
        return (
          `📋 *Seu pedido em aberto:*\n_${e.itens}_${subT}\n\n` +
          `O que deseja fazer?\n\n` +
          `*1* ➕ Continuar adicionando\n` +
          `*2* ✅ Ir para entrega\n` +
          `*3* 🗑️ Remover um item\n` +
          `*4* 🔄 Recomeçar do zero\n` +
          `*5* ❌ Cancelar e ver menu principal`
        );
      }
      // Sem itens → cancelar fluxo e ir ao menu
      estadosPedido.delete(numero);
      limparTimeout(numero);
      emitirContador();
      const flBV = matchFluxo("oi", config);
      return flBV ? variaveis(flBV.resposta, config) : mostrarCardapio(cfg);
    }

    // "5" = cancelar pedido e ir ao menu
    if (sLowC === "5" && e.itens) {
      estadosPedido.delete(numero);
      limparTimeout(numero);
      emitirContador();
      const flBV2 = matchFluxo("oi", config);
      return `Pedido cancelado! 😊\n\n` + (flBV2 ? variaveis(flBV2.resposta, config) : mostrarCardapio(cfg));
    }

    // Cardápio durante seleção de itens (etapa itens)
    const querVerCard = ["cardápio","cardapio","ver cardápio","ver cardapio",
      "o que tem","o que vocês têm","o que voces tem","quais são","quais sao",
      "lista","produtos","itens disponíveis","itens disponiveis"
    ].some(g => sLowC === g || sLowC === g.trim());
    if (querVerCard && e.etapa === "itens") {
      return mostrarCardapio(cfg);
    }
  }

  // ── MELHORIA 6: Ver pedido atual ou Acompanhar ──
  if (txt.trim().toLowerCase() === "meu pedido") {
    // Verificar se tem pedido em andamento no fluxo
    if (e && e.itens && e.etapa !== "acompanhar") {
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
    // Verificar se tem pedido "em_entrega" para este número
    const pedidoCliente = pedidosAbertos.get(numero);
    if (pedidoCliente && pedidoCliente.status === "em_entrega") {
      const hora = new Date(pedidoCliente.confirmado).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
      return (
        `🛵 *Seu pedido está a caminho!*\n\n` +
        `📦 *Pedido Nº ${pedidoCliente.numPedido}*\n` +
        `🛒 *Itens:* ${pedidoCliente.itens}\n` +
        `⏱️ *Confirmado às:* ${hora}\n` +
        `📍 *Endereço:* ${pedidoCliente.endereco}\n\n` +
        `🚀 _O entregador está a caminho! Fique de olho!_ 😊`
      );
    }
    // Se não tem pedido em andamento, perguntar o número para acompanhar
    estadosPedido.set(numero, { ...novoEstado("0"), etapa: "acompanhar" });
    return `🔍 *Para acompanhar seu pedido, por favor informe o número dele:*`;
  }

  if (e && e.itens) {
    const sLow6 = txt.trim().toLowerCase();
    if (["ver pedido","meu carrinho","o que pedi","o que eu pedi",
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
    const n = txt.trim().replace(/\D/g, ""); // Limpa pontos e espaços
    let encontrado = null;
    for (const [num, p] of pedidosAbertos) {
      const numPedidoLimpo = String(p.numPedido).replace(/\D/g, "");
      if (numPedidoLimpo === n || num.replace(/\D/g, "").includes(n)) {
        encontrado = { numero: num, ...p }; break;
      }
    }
    estadosPedido.delete(numero);
    if (encontrado) {
      const hora = new Date(encontrado.confirmado).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
      const statusMsg = encontrado.status === "em_entrega"
        ? `🛵 *Status:* Saiu para entrega! Está a caminho! 🚀`
        : `🚦 *Status:* Em preparo / A caminho`;
      return (
        `✅ *Pedido Nº ${encontrado.numPedido} encontrado!*\n\n` +
        `🛒 *Itens:* ${encontrado.itens}\n` +
        `⏱️ *Confirmado às:* ${hora}\n` +
        `📍 *Endereço:* ${encontrado.endereco}\n` +
        `${statusMsg}\n\n` +
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
    e.itens = arr.join(" | ");
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
    let n       = parseInt(op);

    // Tentar encontrar por nome se não for número (melhoria para ÁUDIO)
    if (isNaN(n)) {
      const sBusca = normStr(op);
      const idx = lista.findIndex(a => normStr(a).includes(sBusca) || sBusca.includes(normStr(a)));
      if (idx !== -1) n = idx + 1;
    }

    // 0 = confirmar / pular
    const opLow = op.toLowerCase();
    if (op === "0" || opLow === "confirmar" || opLow === "comfirmar" || opLow === "pular" || opLow === "sim" || opLow.includes("fecha") || opLow.includes("pronto") || opLow.includes("ok") || opLow.includes("confirma") || opLow.includes("comfirma") || opLow.includes("confirmar com estes") || opLow.includes("comfirmar com estes") || opLow.includes("confirmar com este") || opLow.includes("comfirmar com este")) {
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
        
        // Se veio de áudio, enviar áudio de confirmação (opcional, mas aqui garantimos o texto)
        return (
          `✅ *${max} acompanhamento${max>1?"s":""}:* ${acompParaMostrar.join(", ")}\n\n` +
          `🛒 _${e.itens.split(" | ").pop()}_${subT}\n\n` +
          `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
          `👇 *Deseja mais alguma coisa?*\n\n` +
          `*1* ➕ Adicionar mais itens\n` +
          `*2* ✅ Continuar para entrega\n` +
          `*3* 🗑️ Remover item\n` +
          `*4* 🔄 Recomeçar`
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
      
      // "fechar o pedido" ou similar → ir para endereço (fluxo completo)
      if (continuar === "fechar" || opLow.includes("fechar") || opLow.includes("confirm")) {
        e.etapa = "endereco";
        salvar();
        const subEnd = calcularTotal(e.itens, cfg);
        const taxaEnd = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
        const subTEnd = subEnd > 0 ? `\n💰 Subtotal: R$ ${subEnd.toFixed(2).replace(".",",")} + taxa = *R$ ${(subEnd+taxaEnd).toFixed(2).replace(".",",")}*` : "";
        return (
          `📦 *Pedido confirmado:*\n_${e.itens}_\n${subTEnd}\n\n` +
          `📍 Envie sua *localização* ou digite seu *endereço completo*:\n_Rua, número, bairro_`
        );
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
    const achP = paus.find(p => txt.toLowerCase().includes(p.toLowerCase()));
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
        const temItem = naoE.some(i => restoTxt.toLowerCase().includes(i.nome.toLowerCase()));
        const temNum  = /\d/.test(restoTxt);
        if (temItem || temNum) itensExtras = restoTxt;
      }

      e.itens  = itensExtras ? `${pizzaStr} | ${itensExtras}` : pizzaStr;
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
    // MULTI-ITEMS: "2x coca e 3x bacon" / "2 refri, 2 x-bacon"
    // ⚠️  NÃO quebrar "suco de uva, 5 unidades" (qtd no final = 1 item só)
    // ═══════════════════════════════════════════════════════════

    // Primeiro tentar extrair como item único com qtd — pode ser "item, N unidades"
    const { qtd: qtdUnico, texto: txtUnico } = extrairQtd(txt);
    const valUnico = validarItem(txtUnico, cfg);

    // Se já resolveu como item único com qtd, NÃO tentar multi-item
    const ehItemUnicoComQtd = valUnico.ok && qtdUnico > 1;

    // Verificar se realmente parece ter múltiplos itens distintos
    const temMultiE    = txt.includes(" e ") && /\b(e)\b/i.test(txt);
    const temMultiVirg = txt.includes(",") && !txt.includes("meio a meio") && !ehItemUnicoComQtd;
    const temMultiCom  = txt.includes(" com ") && /\d|um|dois|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez/i.test(txt);
    // "5x bacon duplo 5x suco" — padrão numérico repetido sem separador
    const temMultiNumRepetido = /\d+\s*x\s+\S.+\s+\d+\s*x\s+/i.test(txt) ||
      /^(\d+|um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez)\s*x?\s+\S.+\s+(\d+|um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete)\s*x?\s+/i.test(txt);
    const parecePedidoMultiItens = temMultiE || temMultiVirg || temMultiCom || (temMultiNumRepetido && !ehItemUnicoComQtd);

    if (!ehItemUnicoComQtd && parecePedidoMultiItens) {
      let partes = [];
      if (temMultiE) {
        partes = txt.split(/\s+e\s+/i).map(p => p.trim()).filter(p => p.length > 1);
      } else if (temMultiCom) {
        partes = txt.split(/\s+com\s+/i).map(p => p.trim()).filter(p => p.length > 1);
      } else if (temMultiNumRepetido && !temMultiVirg) {
        // Dividir antes de cada número/extenso que inicia novo item
        const splitR = txt
          .replace(/(\s+)(\d+x?\s|(?:um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez)\s)/gi, "|||$2")
          .split("|||")
          .map(p => p.trim())
          .filter(p => p.length > 1);
        if (splitR.length >= 2) partes = splitR;
      } else if (temMultiVirg) {
        // Dividir por vírgula
        const candidatas = txt.split(/,\s*/).map(p => p.trim()).filter(p => p.length > 0);
        // Se a segunda parte for só dígito ou "N unidades" → é qtd do primeiro item
        if (candidatas.length === 2 && /^\d+\s*(?:unidades?|und\.?|un\.?|pç|pçs|x)?$/i.test(candidatas[1])) {
          // Ex: "suco de uva, 5 unidades" → tratar como item único via extrairQtd abaixo
          partes = []; // forçar caminho de item único
        } else {
          partes = candidatas;
        }
      }

      if (partes.length >= 2) {
        const resultados = [];
        const erros = [];

        for (const parte of partes) {
          const { qtd: qtdP, texto: txtP } = extrairQtd(parte);
          const valP = validarItem(txtP, cfg);
          if (!valP.ok) { erros.push(parte); continue; }
          if (valP.item.pausado) { erros.push(`${valP.item.nome} (indisponível)`); continue; }
          if (temAcomp(valP.item, cfg)) {
            // Adicionar os anteriores primeiro
            for (const r of resultados) { e.itens = e.itens ? `${e.itens} | ${r}` : r; }
            e.itemPendente = valP.item; e.qtdPendente = qtdP; e.acompSelecionados = []; e.etapa = "acompanhamentos"; salvar();
            return (resultados.length ? `✅ Adicionados: ${resultados.join(", ")}\n\n` : "") + msgAcomp(valP.item, [], qtdP, cfg);
          }
          resultados.push(qtdP > 1 ? `${qtdP}x ${valP.item.nome} — ${valP.item.preco}` : `${valP.item.nome} — ${valP.item.preco}`);
        }

        if (resultados.length === 0 && erros.length > 0) {
          // Nenhum item reconhecido — cair no caminho de item único
        } else if (resultados.length > 0) {
          // Somar itens iguais
          const mapa = new Map();
          for (const r of resultados) {
            const nomeChave = r.split("—")[0].trim();
            if (mapa.has(nomeChave)) {
              const prev = mapa.get(nomeChave);
              const prevQtd = parseInt(prev.match(/^(\d+)x/)?.[1] || "1");
              const curQtd  = parseInt(r.match(/^(\d+)x/)?.[1] || "1");
              const total   = prevQtd + curQtd;
              const nomeItem = prev.replace(/^\d+x\s+/, "");
              mapa.set(nomeChave, `${total}x ${nomeItem}`);
            } else {
              mapa.set(nomeChave, r);
            }
          }
          for (const r of mapa.values()) { e.itens = e.itens ? `${e.itens} | ${r}` : r; }
          e.etapa = "mais_itens"; salvar();
          const sub  = calcularTotal(e.itens, cfg);
          const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
          const subTxt = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa R$ ${taxa.toFixed(2).replace(".",",")} = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
          let msgR = `🛒✅ *Itens adicionados:*\n` + [...mapa.values()].map(r => `  ✓ ${r}`).join("\n");
          if (erros.length) msgR += `\n⚠️ Não reconhecido: ${erros.join(", ")}`;
          const carrinhoAtual = e.itens.replace(/\s*\|\s*/g, "\n  • ");
          return msgR + subTxt + `\n\n📋 *Carrinho:*\n_${carrinhoAtual}_\n\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n👇 *O que fazer agora?*\n\n*1* ➕ Adicionar mais\n*2* ✅ Ir para entrega\n*3* 🗑️ Remover item\n*4* 🔄 Recomeçar`;
        }
      }
    }
    
    // ── Processar item único (comportamento original) ──
    // Extrair quantidade e validar item
    const { qtd: qtdI, texto: txtI } = extrairQtd(txt);
    const valI = validarItem(txtI, cfg);
    if (!valI.ok) {
      const dicaItem = txt.split(/\s+/).length > 1
        ? `_Dica: fale apenas o nome. Ex: "bacon duplo" ou "suco de uva"_`
        : `_Dica: verifique o nome no cardápio acima_`;
      return (
        `😅 Não encontrei *"${txt.slice(0,30)}"* no cardápio.\n\n` +
        `${cardResumido(cfg)}\n\n` +
        `${dicaItem}\n` +
        `_Ou diga_ *cancelar* _para voltar ao menu_`
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
    e.itens = e.itens ? `${e.itens} | ${nomeItemI}` : nomeItemI;
    e.etapa = "mais_itens";
    salvar();

    // Enviar foto automaticamente se o item tiver imagem cadastrada
    if (valI.item.imagem && waConectado && waClient) {
      try {
        const { MessageMedia } = require("whatsapp-web.js");
        const b64Img = valI.item.imagem.includes(",") ? valI.item.imagem.split(",")[1] : valI.item.imagem;
        const imgMedia = new MessageMedia("image/jpeg", b64Img, valI.item.nome+".jpg");
        await chat.sendMessage(imgMedia, { caption: `📸 *${valI.item.nome}*\n${valI.item.descricao||""}` });
      } catch(eAutoImg) { console.error("[FOTO-AUTO]", eAutoImg.message); }
    }

    const sub  = calcularTotal(e.itens, cfg);
    const taxa = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,\.]/g,"").replace(",",".")) || 0;
    const subTxt = sub > 0
      ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa R$ ${taxa.toFixed(2).replace(".",",")} = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*`
      : "";

    const itensListI = (e.itens||"").split(" | ").map(i=>`  • ${i}`).join("\n");
    return (
      `✅ *${qtdI>1?qtdI+"x ":""}${valI.item.nome}* adicionado!${avisoI}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `🛒 *Carrinho:*\n${itensListI}${subTxt}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `*1* ➕ Adicionar mais\n` +
      `*2* ✅ Finalizar pedido\n` +
      `*3* 🗑️ Remover item\n` +
      `*4* 🔄 Recomeçar`
    );
  }

  // ── ETAPA: mais_itens ──
  // Pergunta se quer adicionar mais ou continuar
  if (e.etapa === "mais_itens") {
    const op = txt.trim().toLowerCase();
    const continuar = querContinuar(txt);

    // "fechar o pedido" ou "confirmar pedido" → vai para endereço (fluxo completo)
    if (continuar === "fechar" || op.includes("fechar") || op.includes("confirm")) {
      // Ir para endereço primeiro (não pular etapas)
      e.etapa = "endereco";
      salvar();
      const subEnd2 = calcularTotal(e.itens, cfg);
      const taxaEnd2 = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const subTEnd2 = subEnd2 > 0 ? `\n💰 Subtotal: R$ ${subEnd2.toFixed(2).replace(".",",")} + taxa = *R$ ${(subEnd2+taxaEnd2).toFixed(2).replace(".",",")}*` : "";
      return (
        `📦 *Pedido confirmado:*\n_${e.itens}_\n${subTEnd2}\n\n` +
        `📍 Envie sua *localização* ou digite seu *endereço completo*:\n_Rua, número, bairro_`
      );
    }

    // "Recomeçar / do zero" → opção 4
    if (/^(4|recome[cç]ar|do zero|tudo de novo|apaga tudo|zerar|e? ?come[cç]ar do zero|e? ?come[çc]ar de novo|limpar pedido)$/i.test(op)) {
      estadosPedido.delete(numero);
      emitirContador();
      salvar();
      const flBV4 = matchFluxo("oi", cfg);
      return `🔄 *Pedido cancelado!*\n\n` + (flBV4 ? variaveis(flBV4.resposta, cfg) : mostrarCardapio(cfg));
    }

    // Quer ADICIONAR MAIS → vai para itens_extra (ANTES de verificar endereço)
    if (continuar === "adicionar" || op === "1"
      || /^(mais itens?|quero mais|adicionar mais?|adiciona(r)?( mais)?( itens?)?|mais coisas?|quero adicionar|sim)$/i.test(op)) {
      e.etapa = "itens_extra";
      salvar();
      const sub1 = calcularTotal(e.itens, cfg);
      const taxa1 = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const subT1 = sub1 > 0 ? `\n💰 Subtotal: R$ ${sub1.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub1+taxa1).toFixed(2).replace(".",",")}*` : "";
      return (
        `👇 *O que mais você gostaria?*${subT1}\n\n` +
        `${cardResumido(cfg)}\n\n` +
        `_Pedido atual: ${e.itens}_\n\n` +
        `_💡 Digite o nome do item ou o número_`
      );
    }

    // Quer continuar → vai para endereço
    if (continuar === "continuar" || op === "2") {
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
      const subEnd = calcularTotal(e.itens, cfg);
      const taxaEnd = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const subTEnd = subEnd > 0 ? `💰 Subtotal: R$ ${subEnd.toFixed(2).replace(".",",")} + taxa = *R$ ${(subEnd+taxaEnd).toFixed(2).replace(".",",")}*` : "";
      return (
        `📦 *Pedido confirmado:*\n_${e.itens}_\n${subTEnd}\n\n` +
        `━━━━━━━━━━━━━━━━━━━━━━\n` +
        `📍 *ETAPA 1 de 4 — Endereço*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
        `📌 *Opção rápida:* envie sua localização\n` +
        `   Toque em 📎 → _Localização_\n\n` +
        `✏️ *Ou diga/digite a rua:*\n` +
        `_Ex: "Rua João Paulo II" ou "Av. Fernandes Lima"_`
      );
    }

    // Quer adicionar mais → vai para etapa de extra
    if (op === "1" || op.includes("sim") || op.includes("quer") || op.includes("adicion") || op.includes("mais")) {
      e.etapa = "itens_extra";
      salvar();
      const subAd = calcularTotal(e.itens, cfg);
      const taxaAd = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const subTAd = subAd > 0 ? `\n💰 Subtotal atual: R$ ${subAd.toFixed(2).replace(".",",")} + taxa = *R$ ${(subAd+taxaAd).toFixed(2).replace(".",",")}*` : "";
      return (
        `➕ *O que mais você quer adicionar?*${subTAd}\n\n` +
        `${cardResumido(cfg)}\n\n` +
        `_Diga o nome do item. Ex: "2 sucos de uva"_\n` +
        `_Carrinho: ${e.itens}_`
      );
    }

    // Texto não reconhecido no mais_itens → mostrar resumo + opções
    if (txt.length >= 2) {
      const valTentativa = validarItem(txt, cfg);
      if (!valTentativa.ok) {
        const subFb = calcularTotal(e.itens, cfg);
        const taxaFb = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
        const subTFb = subFb > 0 ? `\n💰 Subtotal: R$ ${subFb.toFixed(2).replace(".",",")} + taxa = *R$ ${(subFb+taxaFb).toFixed(2).replace(".",",")}*` : "";
        const itensListFb = (e.itens||"").split(" | ").map(i=>`  • ${i}`).join("\n");
        return (
          `❓ Não entendi *"${txt.slice(0,20)}"*\n\n` +
          `──────────────────────\n` +
          `🛒 *Seu carrinho:*\n${itensListFb}${subTFb}\n` +
          `──────────────────────\n\n` +
          `O que deseja fazer?\n\n` +
          `*1* ➕ Adicionar mais itens\n` +
          `*2* ✅ Continuar para entrega\n` +
          `*3* 🗑️ Remover um item\n` +
          `*4* 🔄 Recomecar do zero`
        );
      }
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
    if (txt.length < 2) {
      const subEx = calcularTotal(e.itens, cfg);
      const taxaEx = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      return (
        `➕ *O que deseja adicionar?*\n\n` +
        `${cardResumido(cfg)}\n\n` +
        `_Carrinho atual: ${e.itens}_\n` +
        (subEx > 0 ? `_💰 Subtotal: R$ ${subEx.toFixed(2).replace(".",",")} + taxa = R$ ${(subEx+taxaEx).toFixed(2).replace(".",",")} _` : "")
      );
    }

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
      return (
        `📍 *Localização GPS recebida!* ✅\n\n` +
        `━━━━━━━━━━━━━━━━━━━━━━\n` +
        `📍 *ETAPA 2 de 4 — Bairro*\n` +
        `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
        `🏘️ *Qual o bairro?*\n_Ex: "Centro", "Farol", "Ponta Verde"_`
      );
    }

    // Rejeitar entradas claramente inválidas ou hesitações do áudio
    const txtLimpoEnd = txt.replace(/[.\s…!?,]+$/g, "").trim();
    const PALAVRAS_INVALIDAS_END = ["endereço","endereco","rua","avenida","aqui","ok","sim","não","nao","...","hmm","uh","ah"];
    const ehInvalido = txtLimpoEnd.length < 4
      || PALAVRAS_INVALIDAS_END.includes(txtLimpoEnd.toLowerCase())
      || /^[.\s…!?,]+$/.test(txt); // só pontuação/reticências

    if (ehInvalido) {
      return (
        `📍 *Qual a rua ou avenida?*\n\n` +
        `_Digite ou fale o nome completo da rua._\n` +
        `_Ex: "Rua João Paulo II" ou "Avenida Fernandes Lima"_\n\n` +
        `📌 Ou envie sua *localização GPS* pelo 📎`
      );
    }

    // Remove prefixos de saudação comuns no áudio
    let ruaTxt = txt.replace(/^(oi\s*,?\s*|olá\s*,?\s*|boa\s*,?\s*|bom\s*,?\s*|ei\s*,?\s*|bom dia\s*,?\s*|boa tarde\s*,?\s*|boa noite\s*,?\s*|então\s*,?\s*|então é\s*,?\s*|é a\s+|é o\s+|fica n[ao]\s+)/i, "").trim();
    // Remove "Rua " ou "Avenida " do início se vier precedido de texto extra
    ruaTxt = ruaTxt.replace(/^(minha rua é|meu endereço é|endereço:|rua:|avenida:)\s*/i, "").trim();
    if (ruaTxt.length < 2) {
      return `Informe a *rua ou avenida* 😊\n_Ex: Rua das Flores, Av. Atlântica..._`;
    }
    e.rua   = ruaTxt;
    e.etapa = "bairro";
    salvar();
    return (
      `📍✅ Rua: *${ruaTxt}*\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📍 *ETAPA 2 de 4 — Bairro*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `🏘️ *Qual o bairro?*\n_Diga ou digite. Ex: "Centro", "Farol"_`
    );
  }

  // ── ETAPA: bairro ──
  if (e.etapa === "bairro") {
    if (txt.length < 2) return `Informe o *bairro* 😊`;
    e.bairro = txt;
    e.etapa  = "numero_end";
    salvar();
    return (
      `✅ Bairro: *${txt}*\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📍 *ETAPA 2 de 4 — Número*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `🔢 *Qual o número do imóvel?*\n\n` +
      `_Ex: "123" ou "sem número"_`
    );
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
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📍 *ETAPA 3 de 4 — Referência*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `📌 *Ponto de referência?*\n` +
      `_Ex: "Próximo ao Mercadão", "Em frente à escola"_\n\n` +
      `_Sem referência? Diga_ *não*`
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
      `${semRef ? "✅ Sem referência." : `✅ Ref: _${e.referencia}_`}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📍 *ETAPA 4 de 4 — Tipo do imóvel*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `🏠 *É casa, apartamento ou comércio?*\n\n` +
      `*1* 🏠 Casa\n` +
      `*2* 🏢 Apartamento / Edifício\n` +
      `*3* 🏪 Comércio / Escritório`
    );
  }

  // ── ETAPA: tipo_imovel ──
  if (e.etapa === "tipo_imovel") {
    const op = txt.trim().toLowerCase();
    if (op === "1" || op.includes("casa")) {
      e.tipoComp = "casa"; e.etapa = "telefone"; salvar();
      return `🏠 *Casa* ✅\n\n📞 *Número para contato:*\n_Fale ou digite. Ex: "82 99185-6615"_`;
    }
    if (op === "2" || op.includes("apart") || op.includes("apto") || op.includes("edif")) {
      e.tipoComp = "apto"; e.etapa = "complemento"; salvar();
      return `🏢 *Apartamento* ✅\n\n🔑 *Apto, bloco e nome do edifício:*\n_Ex: "Apto 42, Bloco B, Ed. Solar das Mangueiras"_`;
    }
    if (op === "3" || op.includes("comerc") || op.includes("escrit") || op.includes("outro")) {
      e.tipoComp = "comercio"; e.etapa = "telefone"; salvar();
      return `🏪 *Comércio* ✅\n\n📞 *Número para contato:*\n_Fale ou digite. Ex: "82 99185-6615"_`;
    }
    return (
      `Não entendi 😅 Escolha uma opção:\n\n` +
      `*1* 🏠 Casa\n` +
      `*2* 🏢 Apartamento\n` +
      `*3* 🏪 Comércio`
    );
  }

  // ── ETAPA: complemento ──
  if (e.etapa === "complemento") {
    if (txt.length < 3) return `Informe *apto, bloco e edifício* 😊\n_Ex: Apto 42, Bloco B, Ed. Solar_`;
    e.complemento = txt.trim();
    e.localizacao.endereco += ` — ${e.complemento}`;
    e.etapa = "telefone";
    salvar();
    return `✅ _${e.complemento}_\n\n📞 *Número para contato:*\n_Fale ou digite. Ex: "82 99185-6615"_`;
  }

  // ── ETAPA: telefone ──
  if (e.etapa === "telefone") {
    if (txt.replace(/\D/g,"").length < 8) return `Informe um *telefone válido* 😊\n_Ex: 82 99999-9999_`;
    e.telefone = txt.trim();
    e.etapa    = "pagamento";
    salvar();
    const totalPag = calcularTotal(e.itens, cfg);
    const taxaPag = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
    const totalComTaxaPag = totalPag + taxaPag;
    const totalStrPag = totalComTaxaPag > 0 ? `\n💵 *Total a pagar: R$ ${totalComTaxaPag.toFixed(2).replace(".",",")}*\n` : "";
    return (
      `✅ *Tel:* ${e.telefone}${totalStrPag}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💳 *Como vai pagar?*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      menuPag(cfg) + `\n\n` +
      `_Diga ou digite o número_`
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
      ? `\n\n🔑 *Chave Pix:* \`${cfg.pixChave||""}\`\n_📸 Envie o comprovante após confirmar!_`
      : "";
    e.etapa = "observacao"; salvar();
    return (
      `✅ *${forma}*${pixInfo}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📝 *Alguma observação para o pedido?*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `_Ex: "sem cebola", "bem passado", "capricha no molho"_\n\n` +
      `_Sem observação? Diga_ *não*`
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
      `📝 *Alguma observação para o pedido?*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `_Ex: "sem cebola", "bem passado", "capricha no molho"_\n\n` +
      `_Sem observação? Diga_ *não*`
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
    const reConfirmarVoz = /^(1|sim|s|ok|confirmo?|confirmado|confirma( e envi[ae]?)?|envia(r)?( o pedido)?|manda( o pedido)?|pode|vai|certo|correto|exato|perfeito|isso mesmo|beleza|t[aá] bom|ta bom|pode ser|so isso|só isso|pronto|fechar|fechar o pedido|finalizar( o pedido)?)$/i;
    if (reConfirmarVoz.test(op)) {
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
      const subTotal = calcularTotal(e.itens, cfg);
      const taxaEntrega = parseFloat((cfg.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
      const totalGeral = subTotal + taxaEntrega;

      // Detalhar cada item com valor total e alinhamento
      const itensDetalhados = e.itens.split(" | ").map(item => {
        const m = item.match(/^(\d+)x\s+(.+?)\s+—\s+(?:R\$\s*)?([\d,.]+)/i);
        if (m) {
          const qtd = m[1], nome = m[2].trim();
          const prUni = parseFloat(m[3].replace(",","."));
          const totItem = (prUni * parseInt(qtd)).toFixed(2).replace(".",",");
          // Formato: "3x Nome do Produto" alinhado à esquerda e "R$ 0,00" à direita
          return `${qtd}x ${nome.padEnd(20, " ").slice(0, 20)} R$ ${totItem.padStart(7, " ")}`;
        }
        const m2 = item.match(/^(.+?)\s+—\s+(?:R\$\s*)?([\d,.]+)/i);
        if (m2) {
          const nome = m2[1].trim();
          const prUni = parseFloat(m2[2].replace(",",".")).toFixed(2).replace(".",",");
          return `1x ${nome.padEnd(20, " ").slice(0, 20)} R$ ${prUni.padStart(7, " ")}`;
        }
        return item;
      }).join("\n");

      const totI = subTotal.toFixed(2).replace(".",",");
      const taxaF = taxaEntrega.toFixed(2).replace(".",",");
      const totF  = totalGeral.toFixed(2).replace(".",",");

      // Formatação completa para o cupom (painel e impressão)
      const itensFormatadosParaCupom = `${itensDetalhados}\n` +
                                       `--------------------------------\n` +
                                       `SUBTOTAL:            R$ ${totI.padStart(7, " ")}\n` +
                                       `TAXA ENTREGA:        R$ ${taxaF.padStart(7, " ")}\n` +
                                       `--------------------------------\n` +
                                       `TOTAL:               R$ ${totF.padStart(7, " ")}\n` +
                                       `--------------------------------`;

      // Formatação do cupom de produção (apenas itens e observações)
      const itensProducao = e.itens.split(" | ").map(item => {
        // Regex mais flexível para capturar o nome do item mesmo com observações extras
        const m = item.match(/^(\d+)x\s+(.+?)(?:\s+—|\s+\(|$)/i);
        if (m) return `${m[1]}x ${m[2].trim()}`;
        const m2 = item.match(/^(.+?)(?:\s+—|\s+\(|$)/i);
        if (m2) return `1x ${m2[1].trim()}`;
        return item;
      }).join("\n");

      const horaPedido = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      const cupomProducao = `--------------------------------\n` +
                            `      CUPOM DE PRODUÇÃO         \n` +
                            `--------------------------------\n` +
                            `PEDIDO: #${e.numPedido}\n` +
                            `HORA:   ${horaPedido}\n` +
                            `CLIENTE: ${numero.split("@")[0]}\n` +
                            `--------------------------------\n` +
                            `${itensProducao}\n` +
                            `--------------------------------\n` +
                            `OBSERVAÇÕES:\n` +
                            `${e.observacao || "Nenhuma"}\n` +
                            `--------------------------------`;

      // Cupom de PAGAMENTO (completo com valores)
      const horaConfirmado = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      const dataConfirmado = new Date().toLocaleDateString("pt-BR");
      const cupomPagamento = `================================\n` +
                           `      CUPOM DE PAGAMENTO       \n` +
                           `================================\n` +
                           `PEDIDO: #${e.numPedido}\n` +
                           `DATA:  ${dataConfirmado}\n` +
                           `HORA:  ${horaConfirmado}\n` +
                           `CLIENTE: ${e.telefone || numero.split("@")[0]}\n` +
                           `--------------------------------\n` +
                           `${itensDetalhados}\n` +
                           `--------------------------------\n` +
                           `SUBTOTAL:         R$ ${totI.padStart(7, " ")}\n` +
                           `TAXA ENTREGA:     R$ ${taxaF.padStart(7, " ")}\n` +
                           `--------------------------------\n` +
                           `TOTAL:          R$ ${totF.padStart(7, " ")}\n` +
                           `================================\n` +
                           `PAGAMENTO: ${e.pagamento || "—"}\n` +
                           `${e.troco ? `TROCO PARA:    R$ ${e.troco}\n` : ""}` +
                           `--------------------------------\n` +
                           `ENDEREÇO:\n` +
                           `${loc.tipo === "pin" ? `GPS (${loc.lat?.toFixed(5)},${loc.lng?.toFixed(5)})` : (loc.endereco || "—")}\n` +
                           `${e.complemento ? e.complemento + "\n" : ""}` +
                           `${e.referencia ? "Ref: " + e.referencia : ""}\n` +
                           `================================`;

      const pedido = {
        numPedido:   e.numPedido,
        inicio:      e.inicio,
        confirmado:  new Date().toISOString(),
        itens:       itensFormatadosParaCupom,
        producao:    cupomProducao,
        pagamento:   cupomPagamento,
        itensOriginal: e.itens,
        subtotal:    subTotal,
        taxaEntrega: taxaEntrega,
        total:       totalGeral,
        pagamentoTipo: e.pagamento,
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
      // Envia os cupons separados: producao e pagamento
      io.emit("novo_pedido", { 
        numero, 
        ...pedido, 
        producao: cupomProducao,
        pagamento: cupomPagamento,
        autoImprimir 
      });

      const totStr = totI > 0
        ? `🛒 *Itens do pedido:*\n${itensDetalhados}\n\n` +
          `💰 *Subtotal:* R$ ${totI.toFixed(2).replace(".",",")}\n` +
          `🛵 *Taxa de entrega:* R$ ${taxaF.toFixed(2).replace(".",",")}\n` +
          `━━━━━━━━━━━━━━━━━━━━━\n` +
          `💵 *TOTAL DO PEDIDO: R$ ${totF.toFixed(2).replace(".",",")}*\n`
        : "";


      const tempoEst = (()=>{ const _t=calcularTempoPreparo(e.itens,cfg); return _t?(_t+" min"):cfg.tempoEntrega||"30-50 min"; })();
      let fim = (
        `\n✅ *PEDIDO #${e.numPedido} CONFIRMADO!* 🎉\n\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
        `👨‍🍳 Já estamos preparando!\n` +
        `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n` +
        `${totStr}` +
        `⏱️ *Previsão de entrega:* ${tempoEst}\n`
      );
      if (e.pagamento.toLowerCase().includes("pix")) {
        fim += `\n💸 *Pague via Pix:*\n🔑 Chave: \`${cfg.pixChave||""}\`\n📸 _Envie o comprovante aqui após pagar!_\n`;
      }
      if (e.troco) fim += `\n💵 *Troco:* R$ ${e.troco}\n`;
      fim += (
        `\n━━━━━━━━━━━━━━━━━━━━━━\n` +
        `🛵 _Entregador a caminho em breve!_\n` +
        `❓ _Dúvidas? É só mandar mensagem!_ 😊\n` +
        `\n_Digite_ *meu pedido* _para acompanhar o status_`
      );
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

/** Envia resposta simulando leitura + gravação humana */
async function responderHumano(chat, msg, resposta) {
  // Dividir em blocos se houver separador ━━━ e texto longo
  const blocos = dividirEmBlocos(resposta);

  for (let i = 0; i < blocos.length; i++) {
    const bloco = blocos[i];
    if (!bloco.trim()) continue;

    // Gerar Áudio TTS do bloco 
    let audioMedia = null;
    try {
      // Limpa caracteres especiais, markdown e emojis para a voz TTS
      let textoLimpo = bloco
        .replace(/[*_~`#\-]/g, "")
        .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{2B50}\u{2B55}\u{231A}-\u{231B}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{25AA}-\u{25AB}\u{25B6}\u{25C0}\u{25FB}-\u{25FE}\u{2934}-\u{2935}\u{2B05}-\u{2B07}\u{2B1B}-\u{2B1C}\u{3030}\u{303D}\u{3297}\u{3299}\u{FE0F}\u{200D}]/gu, "")
        .replace(/\s{2,}/g, " ")
        .trim();
      
      if (textoLimpo.length > 0) {
        let textoFala = textoLimpo;
        
        // Usar ElevenLabs se estiver configurado, caso contrário Google TTS
        if (ttsService && ttsService.enabled && ttsService.apiKey) {
          try {
            const audioBuffer = await ttsService.generateSpeech(textoFala);
            if (audioBuffer) {
              const base64Audio = audioBuffer.toString('base64');
              audioMedia = new MessageMedia('audio/mp3', base64Audio, 'audio.mp3');
              console.log("[TTS] Áudio gerado com ElevenLabs:", textoFala.substring(0, 50) + "...");
            }
          } catch (err) {
            console.error("[TTS] Erro ao gerar áudio com ElevenLabs:", err.message);
            // Fallback para Google TTS se ElevenLabs falhar
          }
        }
        
        // Fallback para Google TTS se ElevenLabs não estiver configurado ou falhar
        if (!audioMedia) {
          const results = await googleTTS.getAllAudioBase64(textoFala, {
            lang: 'pt',
            slow: false,
            host: 'https://translate.google.com',
            timeout: 10000,
          });
          
          if (results && results.length > 0) {
            const buffers = results.map(r => Buffer.from(r.base64, 'base64'));
            const finalBuffer = Buffer.concat(buffers);
            const base64Audio = finalBuffer.toString('base64');
          
            if (base64Audio) {
              audioMedia = new MessageMedia('audio/mp3', base64Audio, 'audio.mp3');
            }
          }
        }
      }
    } catch (err) {
      console.error("[TTS] Erro ao gerar áudio:", err.message);
    }

    // Pausa de leitura antes de responder
    await sleep(i === 0 ? 350 : 500);

    if (audioMedia) {
      // Envia o texto primeiro para não perder visualização e dados importantes (como o cardápio)
      await chat.sendStateTyping();
      await sleep(100);
      if (i === 0) await msg.reply(bloco);
      else await chat.sendMessage(bloco);

      // Simula a gravação de áudio em seguida
      await chat.sendStateRecording();
      await sleep(tempoDigitacao(bloco) / 2); // Metade do tempo normal digitando representa gravando
      await chat.sendMessage(audioMedia);
    } else {
      // Fallback de texto caso falhe
      await chat.sendStateTyping();
      await sleep(tempoDigitacao(bloco));
      if (i === 0) await msg.reply(bloco);
      else await chat.sendMessage(bloco);
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
//  PESQUISA DE SATISFAÇÃO PÓS-ENTREGA
// ═══════════════════════
function agendarAvaliacao(numero, pedido) {
  const cfg = loadConfig();
  if (cfg.pesquisaSatisfacao === false) return;

  const pend = avaliacoesPend.get(numero);
  if (pend?.timer) clearTimeout(pend.timer);

  const tempoEspera = (cfg.pesquisaTempoMinutos || 30) * 60 * 1000;

  const timer = setTimeout(async () => {
    avaliacoesPend.delete(numero);
    if (!waConectado || !waClient) return;
    try {
      const perguntas = cfg.pesquisaPerguntas || [
        { emoji: "⭐", texto: "Qualidade da comida" },
        { emoji: "🚀", texto: "Tempo de entrega" },
        { emoji: "💬", texto: "Atendimento" },
        { emoji: "📦", texto: "Embalagem" }
      ];

      let msgPesquisa = `📋 *Pesquisa de Satisfação*\n\n`;
      msgPesquisa += `*Pedido Nº ${pedido.numPedido}*\n`;
      msgPesquisa += `_${pedido.itens}_\n\n`;
      msgPesquisa += `Avalie de 1 a 5 estrelas cada item:\n\n`;

      perguntas.forEach((p, i) => {
        msgPesquisa += `${p.emoji} *${p.texto}*\n`;
        msgPesquisa += `   1⭐ 2⭐ 3⭐ 4⭐ 5⭐\n\n`;
      });

      msgPesquisa += `_Responda com os números separados por espaço._\n`;
      msgPesquisa += `_Ex: "5 4 5 3" (qualidade 5, tempo 4, atendimento 5, embalagem 3)_\n\n`;
      msgPesquisa += `*0* — Pular pesquisa`;

      await waClient.sendMessage(numero, msgPesquisa);
      avaliacoesPend.set(numero, { pedido, aguardando:true, tipo:"multipla" });
    } catch(e) { console.error("[PESQUISA]", e.message); }
  }, tempoEspera);
  avaliacoesPend.set(numero, { pedido, timer, aguardando:false });
}

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

function receberPesquisaMultipla(numero, respostas, pedido) {
  const cfg = loadConfig();
  const perguntas = cfg.pesquisaPerguntas || [
    { emoji: "⭐", texto: "Qualidade da comida" },
    { emoji: "🚀", texto: "Tempo de entrega" },
    { emoji: "💬", texto: "Atendimento" },
    { emoji: "📦", texto: "Embalagem" }
  ];

  const resultado = perguntas.map((p, i) => ({
    pergunta: p.texto,
    emoji: p.emoji,
    nota: parseInt(respostas[i]) || 0
  }));

  const media = resultado.reduce((acc, r) => acc + r.nota, 0) / resultado.length;

  const vendasFile = path.join(LOG_DIR, "vendas.json");
  try {
    let vendas = [];
    if (fs.existsSync(vendasFile)) vendas = JSON.parse(fs.readFileSync(vendasFile,"utf8"));
    const idx = vendas.findIndex(v => v.numPedido === pedido?.numPedido);
    if (idx >= 0) {
      vendas[idx].pesquisaSatisfacao = resultado;
      vendas[idx].avaliacaoMedia = Math.round(media * 10) / 10;
    }
    fs.writeFileSync(vendasFile, JSON.stringify(vendas,null,2));
  } catch(_) {}

  const cli = clientesDB.get(numero.replace("@c.us",""));
  if (cli) {
    cli.ultimaPesquisa = resultado;
    cli.ultimaAvaliacaoMedia = Math.round(media * 10) / 10;
    clientesDB.set(numero.replace("@c.us",""),cli);
    saveClientes();
  }

  io.emit("pesquisa_satisfacao", { numero, resultado, media: Math.round(media * 10) / 10, pedido });
}

// Rota: configuração da pesquisa de satisfação
app.get("/api/pesquisa/config", guard, (req, res) => {
  const cfg = loadConfig();
  res.json({
    ativo: cfg.pesquisaSatisfacao !== false,
    tempoMinutos: cfg.pesquisaTempoMinutos || 30,
    perguntas: cfg.pesquisaPerguntas || [
      { emoji: "⭐", texto: "Qualidade da comida" },
      { emoji: "🚀", texto: "Tempo de entrega" },
      { emoji: "💬", texto: "Atendimento" },
      { emoji: "📦", texto: "Embalagem" }
    ]
  });
});

app.post("/api/pesquisa/config", guard, (req, res) => {
  const { ativo, tempoMinutos, perguntas } = req.body || {};
  const cfg = loadConfig();
  cfg.pesquisaSatisfacao = ativo !== false;
  if (tempoMinutos) cfg.pesquisaTempoMinutos = parseInt(tempoMinutos) || 30;
  if (Array.isArray(perguntas)) cfg.pesquisaPerguntas = perguntas;
  saveConfig(cfg);
  config = cfg;
  res.json({ ok: true });
});

// Rota: resultados da pesquisa
app.get("/api/pesquisa/resultados", guard, (req, res) => {
  const vendasFile = path.join(LOG_DIR, "vendas.json");
  let vendas = [];
  try { if (fs.existsSync(vendasFile)) vendas = JSON.parse(fs.readFileSync(vendasFile,"utf8")); } catch(_) {}

  const pesquisas = vendas.filter(v => v.pesquisaSatisfacao || v.avaliacao);

  const hoje = new Date().toISOString().slice(0,10);
  const pesquisasHoje = pesquisas.filter(v => v.data === hoje);

  const mediaGeral = pesquisas.length > 0
    ? pesquisas.reduce((acc, v) => acc + (v.avaliacaoMedia || v.avaliacao || 0), 0) / pesquisas.length
    : 0;

  const distribuicao = { 1:0, 2:0, 3:0, 4:0, 5:0 };
  pesquisas.forEach(v => {
    const nota = Math.round(v.avaliacaoMedia || v.avaliacao || 0);
    if (nota >= 1 && nota <= 5) distribuicao[nota]++;
  });

  res.json({
    total: pesquisas.length,
    hoje: pesquisasHoje.length,
    mediaGeral: Math.round(mediaGeral * 10) / 10,
    distribuicao,
    ultimas: pesquisas.slice(-20).reverse().map(v => ({
      numPedido: v.numPedido,
      data: v.data,
      hora: v.hora,
      avaliacao: v.avaliacao,
      avaliacaoMedia: v.avaliacaoMedia,
      pesquisa: v.pesquisaSatisfacao
    }))
  });
});

// ── RELATÓRIO GLOBAL COMPLETO ──
app.get("/api/relatorio-global", guard, (req, res) => {
  const { dataInicio, dataFim, periodo } = req.query;

  const vendasFile = path.join(LOG_DIR, "vendas.json");
  let vendas = [];
  try { if (fs.existsSync(vendasFile)) vendas = JSON.parse(fs.readFileSync(vendasFile,"utf8")); } catch(_) {}

  // Filtrar por período
  const hoje = new Date();
  let dataIni = dataInicio || null;
  let dataFi = dataFim || hoje.toISOString().slice(0,10);

  if (periodo && !dataInicio) {
    switch(periodo) {
      case "hoje": dataIni = hoje.toISOString().slice(0,10); break;
      case "7dias":
        const d7 = new Date(hoje); d7.setDate(d7.getDate() - 7);
        dataIni = d7.toISOString().slice(0,10);
        break;
      case "30dias":
        const d30 = new Date(hoje); d30.setDate(d30.getDate() - 30);
        dataIni = d30.toISOString().slice(0,10);
        break;
      case "mes":
        dataIni = hoje.toISOString().slice(0,7) + "-01";
        break;
      case "todos":
        dataIni = "2000-01-01";
        break;
      default:
        const d7d = new Date(hoje); d7d.setDate(d7d.getDate() - 7);
        dataIni = d7d.toISOString().slice(0,10);
    }
  }
  if (!dataIni) {
    const d7 = new Date(hoje); d7.setDate(d7.getDate() - 7);
    dataIni = d7.toISOString().slice(0,10);
  }

  const vendasFiltradas = vendas.filter(v => v.data >= dataIni && v.data <= dataFi);

  // ═══ DADOS FINANCEIROS ═══
  function calcFaturamento(lista) {
    return lista.reduce((acc, v) => {
      if (v.total !== undefined && !isNaN(parseFloat(v.total))) return acc + parseFloat(v.total);
      const sub = calcularTotal(v.itens, config);
      const taxa = typeof v.taxaEntrega === "number" ? v.taxaEntrega : parseFloat((v.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",","."));
      return acc + sub + (isNaN(taxa) ? 0 : taxa);
    }, 0);
  }

  const faturamentoTotal = calcFaturamento(vendasFiltradas);
  const ticketMedio = vendasFiltradas.length > 0 ? faturamentoTotal / vendasFiltradas.length : 0;

  // Faturamento por dia
  const fatPorDia = {};
  for (const v of vendasFiltradas) {
    if (!fatPorDia[v.data]) fatPorDia[v.data] = { data: v.data, total: 0, qtd: 0 };
    fatPorDia[v.data].qtd++;
    fatPorDia[v.data].total += calcFaturamento([v]);
  }
  const diasOrdenados = Object.values(fatPorDia).sort((a,b) => a.data.localeCompare(b.data));

  // Faturamento por hora
  const fatPorHora = {};
  for (let h = 0; h < 24; h++) fatPorHora[h] = 0;
  vendasFiltradas.forEach(v => {
    if (v.hora) {
      const h = parseInt(v.hora.split(":")[0]);
      if (!isNaN(h)) fatPorHora[h] += calcFaturamento([v]);
    }
  });

  // ═══ PRODUTOS ═══
  const itensVendidos = {};
  const categoriasVendidas = {};
  vendasFiltradas.forEach(v => {
    const itensStr = v.itensOriginal || v.itens || "";
    const partes = itensStr.split(" | ");
    partes.forEach(p => {
      const nome = p.replace(/^\d+x?\s*/i, "").split("—")[0].trim().toLowerCase();
      const qtdMatch = p.match(/^(\d+)x?\s+/i);
      const qtd = qtdMatch ? parseInt(qtdMatch[1]) : 1;
      if (nome.length > 2) {
        itensVendidos[nome] = (itensVendidos[nome] || 0) + qtd;
      }
    });
  });
  const rankingProdutos = Object.entries(itensVendidos)
    .sort((a,b) => b[1] - a[1])
    .slice(0, 20)
    .map(([nome, qtd]) => ({ nome, qtd }));

  // ═══ FORMAS DE PAGAMENTO ═══
  const pagamentos = {};
  vendasFiltradas.forEach(v => {
    const pag = v.pagamentoTipo || v.pagamento || "Outro";
    const limpo = pag.split("\n")[0].trim();
    pagamentos[limpo] = (pagamentos[limpo] || 0) + 1;
  });

  // ═══ CLIENTES ═══
  const clientesUnicos = new Set();
  const clientesRecorrentes = new Set();
  const clienteContagem = {};
  vendasFiltradas.forEach(v => {
    const num = (v.numero || "").replace("@c.us", "");
    if (num) {
      clientesUnicos.add(num);
      clienteContagem[num] = (clienteContagem[num] || 0) + 1;
      if (clienteContagem[num] > 1) clientesRecorrentes.add(num);
    }
  });

  // Top clientes
  const topClientes = Object.entries(clienteContagem)
    .sort((a,b) => b[1] - a[1])
    .slice(0, 10)
    .map(([num, qtd]) => ({ numero: num, pedidos: qtd }));

  // ═══ AVALIAÇÕES ═══
  const pesquisas = vendasFiltradas.filter(v => v.pesquisaSatisfacao || v.avaliacao);
  const avaliacoes = vendasFiltradas.filter(v => v.avaliacao);
  const mediaAvaliacao = avaliacoes.length > 0
    ? avaliacoes.reduce((acc, v) => acc + (v.avaliacao || 0), 0) / avaliacoes.length
    : 0;

  const distAvaliacoes = { 1:0, 2:0, 3:0, 4:0, 5:0 };
  avaliacoes.forEach(v => {
    const n = Math.round(v.avaliacao || 0);
    if (n >= 1 && n <= 5) distAvaliacoes[n]++;
  });

  // Pesquisa detalhada
  const pesquisasDetalhadas = vendasFiltradas.filter(v => v.pesquisaSatisfacao);
  const mediaPesquisa = pesquisasDetalhadas.length > 0
    ? pesquisasDetalhadas.reduce((acc, v) => acc + (v.avaliacaoMedia || 0), 0) / pesquisasDetalhadas.length
    : 0;

  // ═══ PEDIDOS ═══
  const pedidosPorStatus = { entregue: 0, aberto: 0 };
  // Pedidos abertos atuais
  for (const [, p] of pedidosAbertos) {
    pedidosPorStatus.aberto++;
  }
  pedidosPorStatus.entregue = vendasFiltradas.length;

  // ═══ HORÁRIOS DE PICO ═══
  const pedidosPorHora = {};
  for (let h = 0; h < 24; h++) pedidosPorHora[h] = 0;
  vendasFiltradas.forEach(v => {
    if (v.hora) {
      const h = parseInt(v.hora.split(":")[0]);
      if (!isNaN(h)) pedidosPorHora[h]++;
    }
  });
  const horaPico = Object.entries(pedidosPorHora).sort((a,b) => b[1] - a[1])[0];

  // ═══ DIAS DA SEMANA ═══
  const pedidosPorDiaSemana = { Dom:0, Seg:0, Ter:0, Qua:0, Qui:0, Sex:0, Sáb:0 };
  const diasLabel = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"];
  vendasFiltradas.forEach(v => {
    if (v.data) {
      const d = new Date(v.data + "T12:00");
      const dia = diasLabel[d.getDay()];
      pedidosPorDiaSemana[dia]++;
    }
  });

  // ═══ TAXA DE CANCELAMENTO ═══
  const totalSessoes = historicos.size + vendasFiltradas.length;
  const taxaConversao = totalSessoes > 0 ? (vendasFiltradas.length / totalSessoes * 100) : 0;

  // ═══ CONFIGURAÇÕES ATUAIS ═══
  const cfgAtual = loadConfig();

  res.json({
    periodo: { inicio: dataIni, fim: dataFi },
    geradoEm: new Date().toISOString(),

    // Resumo executivo
    resumo: {
      totalPedidos: vendasFiltradas.length,
      faturamentoTotal: Math.round(faturamentoTotal * 100) / 100,
      ticketMedio: Math.round(ticketMedio * 100) / 100,
      clientesUnicos: clientesUnicos.size,
      clientesRecorrentes: clientesRecorrentes.size,
      mediaAvaliacao: Math.round(mediaAvaliacao * 10) / 10,
      mediaPesquisa: Math.round(mediaPesquisa * 10) / 10,
      pedidosAbertos: pedidosPorStatus.aberto,
      horaPico: horaPico ? `${horaPico[0]}h (${horaPico[1]} pedidos)` : "—",
    },

    // Financeiro
    financeiro: {
      faturamentoTotal: Math.round(faturamentoTotal * 100) / 100,
      ticketMedio: Math.round(ticketMedio * 100) / 100,
      porDia: diasOrdenados,
      porHora: Object.entries(fatPorHora).map(([h, total]) => ({ hora: `${h}h`, total: Math.round(total * 100) / 100 })),
    },

    // Produtos
    produtos: {
      ranking: rankingProdutos,
      totalItensDiferentes: Object.keys(itensVendidos).length,
    },

    // Pagamentos
    pagamentos: Object.entries(pagamentos).map(([tipo, qtd]) => ({
      tipo,
      qtd,
      percentual: Math.round((qtd / vendasFiltradas.length) * 100)
    })).sort((a,b) => b.qtd - a.qtd),

    // Clientes
    clientes: {
      total: clientesUnicos.size,
      recorrentes: clientesRecorrentes.size,
      taxaRetencao: clientesUnicos.size > 0 ? Math.round((clientesRecorrentes.size / clientesUnicos.size) * 100) : 0,
      top: topClientes,
    },

    // Avaliações
    avaliacoes: {
      total: avaliacoes.length,
      media: Math.round(mediaAvaliacao * 10) / 10,
      distribuicao: distAvaliacoes,
      pesquisasTotal: pesquisasDetalhadas.length,
      mediaPesquisaDetalhada: Math.round(mediaPesquisa * 10) / 10,
    },

    // Operacional
    operacional: {
      pedidosEntregues: pedidosPorStatus.entregue,
      pedidosAbertos: pedidosPorStatus.aberto,
      porDiaSemana: pedidosPorDiaSemana,
      porHora: Object.entries(pedidosPorHora).map(([h, qtd]) => ({ hora: `${h}h`, qtd })),
    },

    // Configurações
    configuracoes: {
      empresa: cfgAtual.empresaNome || "—",
      endereco: cfgAtual.empresaEndereco || "—",
      telefone: cfgAtual.empresaTelefone || "—",
      horario: cfgAtual.horarioFuncionamento || "—",
      taxaEntrega: cfgAtual.taxaEntrega || "—",
      tempoEntrega: cfgAtual.tempoEntrega || "—",
      pedidoMinimo: cfgAtual.pedidoMinimo || "—",
      pagamentos: cfgAtual.pagamentos || "—",
      totalProdutos: (cfgAtual.cardapio||[]).reduce((acc, c) => acc + (c.itens||[]).length, 0),
      totalCategorias: (cfgAtual.cardapio||[]).length,
      iaAtiva: !!cfgAtual.useAI,
      pesquisaAtiva: cfgAtual.pesquisaSatisfacao !== false,
      ttsAtivo: !!cfgAtual.ttsEnabled,
    },

    // Pedidos detalhados
    pedidosDetalhados: vendasFiltradas.slice(-50).reverse().map(v => ({
      numPedido: v.numPedido,
      data: v.data,
      hora: v.hora,
      itens: v.itens,
      total: v.total || calcFaturamento([v]),
      pagamento: v.pagamentoTipo || v.pagamento,
      avaliacao: v.avaliacao || v.avaliacaoMedia || null,
      numero: (v.numero||"").replace("@c.us",""),
    })),
  });
});

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
      if (s.includes(item.nome.toLowerCase())) return true;
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

    // Filtrar tipos de mensagem que não são suportados (stickers, reações, etc.)
    const tiposIgnorar = ["reaction","sticker","revoked","e2e_notification","call_log",
      "notification","notification_template","gp2","broadcast","unknown"];
    if (tiposIgnorar.includes(msg.type)) return;

    if (!msg || !msg.from) return; // guard: mensagem inválida/WA reconectando
    const chat = await msg.getChat().catch(() => null);
    if (!chat || chat.isGroup) return;

    const numero = msg.from;
    const isLoc  = msg.type === "location" || !!msg.location;
    let txt    = isLoc ? "" : (msg.body || "").trim();

    // Mídia sem texto
    if (!txt && !isLoc) {
      if (msg.hasMedia || msg.type === "ptt" || msg.type === "audio" || msg.type === "image") {
        // ══════════════════════════════════════════════════════
        //  NOVO: RECEBER COMPROVANTE PIX (IMAGEM)
        // ══════════════════════════════════════════════════════
        if (msg.type === "image") {
          console.log("[COMPROVANTE] Imagem recebida de", numero);
          try {
            const media = await msg.downloadMedia();
            if (media && media.data) {
              // Salvar no diretório de logs
              const comprovanteDir = path.join(LOG_DIR, "comprovantes");
              if (!fs.existsSync(comprovanteDir)) fs.mkdirSync(comprovanteDir, { recursive: true });
              
              const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
              const filename = `pix_${numero.replace("@c.us","")}_${timestamp}.jpg`;
              const filepath = path.join(comprovanteDir, filename);
              
              fs.writeFileSync(filepath, media.data, "base64");
              console.log("[COMPROVANTE] Salvo em:", filepath);
              
              // Verificar se cliente tem pedido em andamento
              const pedido = pedidosAbertos.get(numero) || Array.from(pedidosAbertos.entries()).find(([n]) => n.replace("@c.us","") === numero.replace("@c.us",""));
              
              if (pedido) {
                // Executar OCR para extrair dados do comprovante
                const dadosOCR = await extrairDadosComprovante(filepath);
                
                // Adicionar comprovante ao pedido
                pedido.comprovantes = pedido.comprovantes || [];
                pedido.comprovantes.push({
                  filename,
                  path: filepath,
                  timestamp: new Date().toISOString(),
                  size: media.data.length,
                  status: "pendente", // pendente, verificado, rejeitado
                  valorOCR: dadosOCR.valor,
                  dataOCR: dadosOCR.data,
                  chaveOCR: dadosOCR.chave,
                  textoOCR: dadosOCR.textoCompleto
                });
                
                // Atualizar no painel
                io.emit("pedidos", listaPedidos());
                
                // Notificar cliente
                let msgResp = "✅ *Comprovante recebido!*\n\nObrigado! Seu comprovante foi salvo e já está visível no painel. 📋";
                if (dadosOCR.valor) {
                  msgResp += `\n\nValor detectado: R$ ${dadosOCR.valor}`;
                }
                await chat.sendMessage(msgResp);
                logC({ tipo:"comprovante_recebido", de:numero, filename, ocr: dadosOCR });
                io.emit("comprovante_recebido", { 
                  numero: numero.replace("@c.us",""), 
                  filename, 
                  timestamp: new Date().toISOString(),
                  ocr: dadosOCR
                });
              } else {
                await chat.sendMessage("✅ *Comprovante recebido!*\n\nNão encontrei um pedido aberto para este número, mas salvei o comprovante. 📋");
                logC({ tipo:"comprovante_recebido_sem_pedido", de:numero, filename });
              }
              
              return; // Processou a imagem, não continua
            }
          } catch(e) {
            console.error("[COMPROVANTE] Erro ao processar imagem:", e.message);
          }
        }
        
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
                
                // ══════════════════════════════════════════════════════
                // ══════════════════════════════════════════════════════
                // ── NORMALIZAÇÕES DE ÁUDIO (Whisper → Bot) v3 ──
                // ══════════════════════════════════════════════════════

                // PASSO 0: Limpar pontuação repetida do Whisper ANTES de tudo
                // "Menu.." / "Atendente..." / "Pagamento.." → remove reticências e pontos duplos
                txt = txt.replace(/[.]{2,}/g, "").replace(/[.,!?]+$/, "").trim();

                // PASSO 0b: Ignorar transcrições muito longas que são claramente ruído
                // (conversas ao fundo, áudio enviado por engano) — mais de 15 palavras sem item do cardápio
                if (txt.split(/\s+/).length > 20) {
                  console.log("[VOZ] Transcrição muito longa, possível ruído — ignorando");
                  return;
                }

                const txtLow = txt.toLowerCase().trim();
                const txtLimpo = txtLow.replace(/[\s.,!?]+/g, "").trim();

                // ── 1. PIX transcrito errado ──
                if (/^(pigues?|fics?|pikes?|piks?|p[iy]ques?|pits?|p[iy]ks?|p[iy]?xe?s?|feats?|fex|feis|fes|f[iy]ts?)$/i.test(txtLimpo) ||
                    ["pigs","piques","fix","pits","pites","pis","feats","feis","fiques","fique"].includes(txtLimpo)) {
                  txt = "PIX"; console.log("[VOZ] Corrigido para PIX");
                }

                // ── 2. Atendente (com reticências já limpas) ──
                if (/^(aprendente|a\s*pendente|apendente|atendimento|atendente|a?\s*p?r?enden?te)$/i.test(txtLow)) {
                  txt = "atendente"; console.log("[VOZ] Corrigido para atendente");
                }

                // ── 2d. ABREVIAÇÕES do Whisper — ex: "5xb com duplo" → "5x bacon duplo" ──
                // "xb" → "x bacon", "xbs" → "x bacon"
                txt = txt.replace(/(\d+)\s*xb\s+(com\s+|e\s+)?/gi, "$1x bacon $2");
                txt = txt.replace(/(\d+)\s*xbs\s+(com\s+|e\s+)?/gi, "$1x bacon $2");

                // ── 2c. RUÍDOS / HESITAÇÕES do Whisper — ignorar silenciosamente ──
                // "Hum", "Mas", "Hmm", "Ah", "Ahn", "Uh", "Eee"
                if (/^(h+u+m+|m+a+s+|h+m+|a+h+|a+h+n+|u+h+|e+|o+|né|ne|é|[Ee] a[íi]|[Ee] [aá]|ta|tá|ahan|aha|aa+)$/i.test(txtLimpo)) {
                  console.log("[VOZ] Ruído/hesitação ignorado:", txt);
                  return; // ignora silenciosamente
                }
                // Frases de recomeço não mapeadas → tratar como "4" (recomeçar)
                if (/^(é? ?começa(r)? do zero|come[cç]ar do zero|tudo de novo|do zero mesmo)$/i.test(txtLow)) {
                  txt = "4"; console.log("[VOZ] Recomeçar → 4");
                }

                // ── 3. MENU / VOLTAR / variações ──
                // Normalizar acentos: "Menú" → "menu"
                const txtLowSemAcento = txtLow.normalize("NFD").replace(/[\u0300-\u036f]/g,"");
                if (/^(menu|ver menu|abre menu|tela principal|pagina inicial|tela inicial|inicio|comeco|vou voltar|vou ao menu|ir ao menu|ir para o menu|volta(r)?( (ao|para o|pro|o) menu)?|voltar|voltar ao menu|voltar o menu|volta pro menu|retornar|ir (ao|para o|pro) menu|quero (voltar|o menu))$/i.test(txtLowSemAcento) ||
                    (/\b(voltar|volta|menu|inicio)\b/.test(txtLowSemAcento) && txtLow.length < 30 && !txtLow.includes("card") && !txtLow.includes("pedido"))) {
                  txt = "oi"; console.log("[VOZ] Corrigido para menu\u2192oi");
                  // Se houver um pedido em andamento, vamos limpá-lo para garantir que vá para a tela principal
                  if (estadosPedido.has(numero)) {
                    estadosPedido.delete(numero);
                    console.log("[VOZ] Estado de pedido removido para forçar menu principal");
                  }
                }

                // ── 4. CARDÁPIO — variações de "ver o cardápio" que o Whisper gera ──
                if (/^(card[aá]pio|ver (o )?card[aá]pio|viu (o )?card[aá]pio|viu,? card[aá]pio|vira (o )?card[aá]pio|(mostra|abre) (o )?card[aá]pio|o que tem|quais (s[aã]o )?os itens|itens dispon[ií]veis)$/i.test(txtLow)) {
                  txt = "cardápio"; console.log("[VOZ] Corrigido para cardápio");
                }

                // ── 5. CONFIRMAR/SIM ──
                if (/^(sim|confirmo|confirmar|comfirmar|pode ser|isso mesmo|t[aá] bom|certo|correto|exato|perfeito|isso|beleza|pode|confirmo o pedido( e envio)?|envio|enviar|confirma( e envi[ae]?)?|comfirma( e envi[ae]?)?|confirma o pedido|comfirma o pedido|envia(r)?( o pedido)?|envia|confirme|comfirme|vai|manda( o pedido)?|confirma e envie?|confirma e envia|comfirma e envie?|comfirma e envia|continua e envia(r)?|continua e enviar|continua e envie?|confirmar com estes|comfirmar com estes|confirmar e enviar|comfirmar e enviar)$/i.test(txtLow)) {
                  txt = "sim"; console.log("[VOZ] Corrigido para sim");
                }

                // ── 6. CANCELAR / NÃO ──
                if (/^(cancelar( o pedido)?|vou cancelar( o pedido)?|cancela( o pedido)?|desistir|n[aã]o|nope|nada)$/i.test(txtLow) && txtLimpo.length <= 25) {
                  // Distinguir: "cancelar" = cancelar pedido; "não" isolado = não quero mais
                  if (/cancelar|cancela|desistir|vou cancelar/i.test(txtLow)) {
                    txt = "cancelar"; console.log("[VOZ] Corrigido para cancelar");
                  } else {
                    txt = "não"; console.log("[VOZ] Corrigido para não");
                  }
                }

                // ── 7. Opções numéricas faladas por extenso ──
                // "Número 1" / "opção 1" / "número dois" / "Três" (isolado) etc. → dígito
                const MAP_NUM = {'um':1,'uma':1,'1':1,'dois':2,'duas':2,'2':2,'tres':3,'3':3,
                  'quatro':4,'4':4,'cinco':5,'5':5,'seis':6,'6':6,'sete':7,'7':7,
                  'oito':8,'8':8,'nove':9,'9':9,'dez':10,'10':10};
                const txtNorm = txtLow.normalize("NFD").replace(/[\u0300-\u036f]/g,"");
                // Com prefixo: "número 1", "opção dois"
                const mNumExt = txtNorm.match(/^(?:numero|opcao|escolho?|quero a?)\s+(um|uma|1|dois|duas|2|tres|3|quatro|4|cinco|5|seis|6|sete|7|oito|8|nove|9|dez|10)$/i);
                if (mNumExt) {
                  const n = MAP_NUM[mNumExt[1].toLowerCase()];
                  if (n) { txt = String(n); console.log("[VOZ] Número por extenso →", txt); }
                }
                // Número ISOLADO: "Três", "Dois", "Um" → só converte se for opção de menu (1–6)
                else if (/^(um|uma|dois|duas|tres|quatro|cinco|seis)$/i.test(txtNorm)) {
                  const n = MAP_NUM[txtNorm.toLowerCase()];
                  if (n && n <= 6) { txt = String(n); console.log("[VOZ] Número isolado por extenso →", txt); }
                }

                // ── 8. Opções de fluxo faladas ──
                const txtLowS = txtLow;
                if (/^(vou adicionar( (item|itens|mais))?|adicionar( mais)? (item|itens|pedido)|continuar adicionando( pedido)?|mais (item|itens)|quero mais|opção (um|1)|vou pedir mais)$/i.test(txtLowS)) {
                  txt = "1"; console.log("[VOZ] Corrigido para 1 (adicionar)");
                } else if (/^(continua(r)?( (para|com|o) (a )?entrega| o? ?pedido| para a entrega)?|ir (para |pro )?(a )?entrega|conclui(r|u)? o? ?pedido|fechar o? ?pedido|finalizar o? ?pedido|seguir( para)?( a)? entrega|vou continuar( para a entrega)?)$/i.test(txtLowS)) {
                  txt = "2"; console.log("[VOZ] Corrigido para 2 (entrega)");
                } else if (/^(remover( item)?|tirar( item)?|excluir( item)?)$/i.test(txtLowS)) {
                  txt = "3"; console.log("[VOZ] Corrigido para 3 (remover)");
                } else if (/^(recome[cç]ar|do zero|tudo de novo|apaga tudo|zerar)$/i.test(txtLowS)) {
                  txt = "4"; console.log("[VOZ] Corrigido para 4 (recomeçar)");
                } else if (/^(cancelar (o )?pedido e ver menu|cancelar e (ir ao|ver o) menu)$/i.test(txtLowS)) {
                  txt = "5"; console.log("[VOZ] Corrigido para 5 (cancelar→menu)");
                }

                // ── 9. VER MEU PEDIDO ──
                if (/^(meu pedido|ver (o )?meu? pedido|ver pedido|meu carrinho|meus itens|o que pedi|resumo( do pedido)?|o que eu pedi|ver o pedido|status do pedido)$/i.test(txtLow)) {
                  txt = "meu pedido"; console.log("[VOZ] Corrigido para ver pedido");
                }

                // ── 10. HORÁRIO / PAGAMENTO / PROMOÇÕES falados ──
                if (/^(hor[aá]rio(s)?( de funcionamento)?)$/i.test(txtLow)) {
                  txt = "horário"; console.log("[VOZ] Corrigido para horário");
                }
                if (/^(pagamento(s)?|formas? de pagamento)$/i.test(txtLow)) {
                  txt = "pagamento"; console.log("[VOZ] Corrigido para pagamento");
                }
                if (/^(promo[cç][aã]o|promo[cç][oõ]es?|promos?)$/i.test(txtLow)) {
                  txt = "promoção"; console.log("[VOZ] Corrigido para promoção");
                }
                if (/^(fazer (o )?pedido|quero pedir|novo pedido|fazer um pedido)$/i.test(txtLow)) {
                  txt = "pedir"; console.log("[VOZ] Corrigido para pedir");
                }

                // ── 10c. PROMOÇÃO falada com ruído: "Do SP1" → "P1", "dois P1" → "2P1" ──
                // Whisper às vezes transcreve "P1" como "SP1", "DP1", "do SP1" etc.
                const mPromoRuido = txt.trim().match(/^(?:do\s+)?s?[Pp](\d+)$/i);
                if (mPromoRuido && !txt.trim().match(/^[Pp]\d+$/)) {
                  txt = `P${mPromoRuido[1]}`; console.log("[VOZ] Promoção ruído →", txt);
                }
                // "dois P1" / "dois vezes P1" → "2P1"
                const mPromoQtd = txt.trim().match(/^(um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|\d+)\s+[Pp](\d+)$/i);
                if (mPromoQtd) {
                  const NUMS = {um:1,uma:1,dois:2,duas:2,três:3,tres:3,quatro:4,cinco:5,seis:6,sete:7,oito:8,nove:9};
                  const q = NUMS[mPromoQtd[1].toLowerCase()] || parseInt(mPromoQtd[1]) || 1;
                  txt = `${q}P${mPromoQtd[2]}`; console.log("[VOZ] Promoção com qtd →", txt);
                }

                // ── 11. Normalizar grandezas por extenso e "X" + plurais ──
                const RE_NUMS = {um:'1',uma:'1',dois:'2',duas:'2',três:'3',tres:'3',quatro:'4',cinco:'5',seis:'6',sete:'7',oito:'8',nove:'9',dez:'10'};
                Object.keys(RE_NUMS).forEach(w => {
                  txt = txt.replace(new RegExp(`(^|\\s)${w}\\s+`, 'gi'), `$1${RE_NUMS[w]}x `);
                });
                txt = txt.replace(/(\d+)\s*[Xx]\s+/g, "$1x ").replace(/[.,!?]\s*$/, "").trim();
                // Remover plurais comuns para dar match no cardápio
                txt = txt.replace(/pizzas/gi, "pizza").replace(/lanches/gi, "lanche").replace(/sucos/gi, "suco");

                // ── 12. Normalizar "e" entre itens ──
                txt = txt.replace(/\s+e\s+/gi, " e ").trim();

                // ── 13. Prefixos de endereço comuns no áudio ──
                // "Boa, João Paulo II" → "João Paulo II" (prefixo de cumprimento antes da rua)
                // NUNCA limpa se txt é um comando reconhecido (oi, menu, cancelar, etc.)
                const CMDS_PROTEGIDOS = ["oi","sim","não","nao","cancelar","atendente","cardápio","pedir","PIX","1","2","3","4","5","6","7"];
                // Limpar prefixos de saudação em etapas de coleta de endereço
                const etapaEndAtual = estadosPedido.get(numero)?.etapa;
                const etapasEndereco = ["endereco","bairro","numero_end","referencia","complemento"];
                if (etapasEndereco.includes(etapaEndAtual) && !CMDS_PROTEGIDOS.includes(txt)) {
                  const txtAntes = txt;
                  txt = txt.replace(/^(boa|bom|oi|olá|ola|ei|ah|ahn|então|e|é),?\s*/i, "").trim();
                  if (!txt) txt = txtAntes; // Segurança: nunca esvaziar
                }

                // ── 10. Telefone falado número a número ──
                const telefonesFalados = txt.match(/(\d[\d\s\-]{8,15}\d)/g);
                if (telefonesFalados) {
                  for (const tel of telefonesFalados) {
                    const telLimpo = tel.replace(/\D/g, "");
                    if (telLimpo.length >= 10 && telLimpo.length <= 11) {
                      const telF = telLimpo.length === 11
                        ? `(${telLimpo.slice(0,2)}) ${telLimpo.slice(2,7)}-${telLimpo.slice(7)}`
                        : `(${telLimpo.slice(0,2)}) ${telLimpo.slice(2,6)}-${telLimpo.slice(6)}`;
                      txt = txt.replace(tel, telF);
                      console.log(`[VOZ] Telefone: ${telF}`);
                    }
                  }
                }
                console.log(`[VOZ] Final: "${txt}"`);
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
          const etapaVoz = eFluxo ? estadosPedido.get(numero)?.etapa : null;
          let dicaVoz = "";
          if (etapaVoz === "endereco")          dicaVoz = "\n_Fale: \"Rua João Paulo II\" ou envie 📍 localização_";
          else if (etapaVoz === "bairro")       dicaVoz = "\n_Fale o bairro. Ex: \"Centro\"_";
          else if (etapaVoz === "numero_end")   dicaVoz = "\n_Fale o número. Ex: \"cento e vinte e três\"_";
          else if (etapaVoz === "referencia")   dicaVoz = "\n_Fale uma referência ou diga \"não\"_";
          else if (["itens","itens_extra"].includes(etapaVoz)) dicaVoz = "\n_Fale o que quer. Ex: \"dois sucos e um bacon\"_";
          else if (etapaVoz === "mais_itens")   dicaVoz = "\n_Diga \"continuar\" ou \"mais itens\"_";
          else if (etapaVoz === "pagamento")    dicaVoz = "\n_Fale a forma. Ex: \"PIX\" ou \"dinheiro\"_";
          else if (etapaVoz === "confirmacao")  dicaVoz = "\n_Diga \"confirmar\" para finalizar_";
          await msg.reply(
            `🎤 Recebi seu áudio, mas não entendi! 😅\n\n` +
            `Fale mais devagar ou mande em *texto* 📝${dicaVoz}` +
            (eFluxo ? `\n\n_Pedido salvo! Pode continuar. 😊_` : "")
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
          `*2* 📸 Catálogo de Fotos\n` +
          `*3* 🛒 Fazer Pedido\n` +
          `*4* 📦 Meu Pedido\n` +
          `*5* 🕐 Horário\n` +
          `*6* 💳 Pagamento\n` +
          `*7* 👤 Atendente\n` +
          `*8* 🔥 Promoções\n\n` +
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
    if (avalPend?.aguardando) {
      const cfgPesq = loadConfig();

      // Pesquisa múltipla (nova)
      if (avalPend.tipo === "multipla") {
        if (txt.trim() === "0") {
          avaliacoesPend.delete(numero);
          resp = `✅ Pesquisa pulada. Obrigado mesmo assim! 😊`;
          await responderHumano(chat, msg, resp);
          logC({ tipo:"saida", para:numero, mensagem:resp });
          io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
          return;
        }

        const respostas = txt.trim().split(/\s+/).map(n => parseInt(n)).filter(n => n >= 1 && n <= 5);
        const perguntas = cfgPesq.pesquisaPerguntas || [
          { emoji: "⭐", texto: "Qualidade da comida" },
          { emoji: "🚀", texto: "Tempo de entrega" },
          { emoji: "💬", texto: "Atendimento" },
          { emoji: "📦", texto: "Embalagem" }
        ];

        if (respostas.length >= perguntas.length) {
          receberPesquisaMultipla(numero, respostas, avalPend.pedido);
          avaliacoesPend.delete(numero);
          const media = respostas.reduce((a,b) => a+b, 0) / respostas.length;
          const estrelas = "⭐".repeat(Math.round(media));

          let msgObrigado = `${estrelas} *Obrigado pela avaliação!*\n\n`;
          perguntas.forEach((p, i) => {
            if (respostas[i]) {
              msgObrigado += `${p.emoji} ${p.texto}: ${"⭐".repeat(respostas[i])}\n`;
            }
          });

          msgObrigado += `\n📊 *Média geral: ${media.toFixed(1)}/5*\n\n`;

          if (media >= 4) {
            msgObrigado += `Fico feliz que tenha gostado! 😊 Volte sempre!`;
          } else if (media >= 3) {
            msgObrigado += `Obrigado pelo feedback! Vamos melhorar sempre. 🙏`;
          } else {
            msgObrigado += `Sentimos muito pela experiência. Vamos melhorar! 🙏\nSe quiser falar com a gente, é só chamar.`;
          }

          resp = msgObrigado;
          await responderHumano(chat, msg, resp);
          logC({ tipo:"saida", para:numero, mensagem:resp });
          io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
          return;
        } else {
          // Resposta inválida - pedir para repetir
          resp = `Por favor, responda com *${perguntas.length} números* de 1 a 5, separados por espaço.\n\n_Ex: "5 4 5 3"_\n\n*0* — Pular pesquisa`;
          await responderHumano(chat, msg, resp);
          logC({ tipo:"saida", para:numero, mensagem:resp });
          io.emit("msg", { numero, mensagem:resp, tipo:"saida" });
          return;
        }
      }

      // Pesquisa simples (legado - 1-5 estrelas)
      if (/^[1-5]$/.test(txt.trim())) {
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
    }

    // ── FEAT 3: Saudação personalizada para cliente conhecido ──
    if (!estadosPedido.has(numero) && !isLoc) {
      const sLow2 = txt.toLowerCase().trim().replace(/\.\s*$/, "");
      const ehOi = ["oi","olá","ola","bom dia","boa tarde","boa noite","bom noite","menu","início","inicio",
        "voltar","home","tela principal","página inicial","pagina inicial","voltar ao menu","voltar o menu","voltar pro menu",
        "eai","e ai","tudo bem","tudo bom","hello"
      ].some(g=>sLow2===g||sLow2.startsWith(g+" ")) ||
      // Nome próprio isolado (cliente fala o nome por engano)
      (/^[A-ZÁÉÍÓÚÀÂÊÔÃÕÇÜÑ][a-záéíóúàâêôãõçüñ]{2,}$/.test(txt.trim()) &&
       !["Cardápio","Cardapio","Promoções","Pedido","Atendente","Cancelar","Confirmar","Voltar","Menu","PIX"].some(w=>txt.toLowerCase().includes(w.toLowerCase())) &&
       !(config.cardapio||[]).flatMap(c=>(c.itens||[])).some(i=>normStr(i.nome).includes(normStr(txt.trim()))));
      if (ehOi) {
        // Se chegou como "menu" (digitado ou por áudio), forçar txt = "oi" para pegar o fluxo boas_vindas
        if (["menu","voltar","home","tela principal","página inicial","pagina inicial","voltar ao menu","início","inicio"].includes(sLow2)) {
          txt = "oi";
        }
        const cli = getCliente(numero);
        if (cli?.ultimoPedido) {
          const itensUlt = (cli.ultimoPedido.itens||"").split(" | ")[0];
          const dataUlt  = new Date(cli.ultimoPedido.data).toLocaleDateString("pt-BR");
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
      // Capturar itens ANTES do fluxo para detectar o que foi adicionado
      const splitItensAntes = (str) => str.split(/\s*\|\s*|,\s*(?!\d)/).map(i => i.trim()).filter(Boolean);
      const itensAntes = splitItensAntes(estadosPedido.get(numero)?.itens || "");

      resp = await fluxoPedido(numero, txt, msg, config);
      if (resp === null) {
        const etapa = estadosPedido.get(numero)?.etapa || "";
        console.warn(`[FLUXO] Etapa "${etapa}" não reconheceu: "${txt}"`);
        resp = "Não entendi 😅\nPor favor, responda conforme a pergunta acima.";
      }

      // ── Enviar imagem APENAS dos itens RECÉM adicionados (1 vez por item) ──
      try {
        const eAtual = estadosPedido.get(numero);
        if (eAtual && eAtual.itens && waConectado && waClient && config.enviarImagemProduto !== false) {
          // Normalizar separador: suporta " | " e ","
          const splitItens = (str) => str.split(/\s*\|\s*|,\s*(?!\d)/).map(i => i.trim()).filter(Boolean);
          const itensDepois = splitItens(eAtual.itens);
          const itensAntesNorm = itensAntes; // já foi dividido com o mesmo método
          // Itens novos = que estão depois mas não estavam antes
          const itensNovos = itensDepois.filter(d => !itensAntesNorm.some(a => a === d));

          for (const itemNovo of itensNovos) {
            // Extrair nome limpo: "3x X-Bacon Duplo — R$ 35,00" → "X-Bacon Duplo"
            const nomeNovo = itemNovo.replace(/^\d+x\s+/, "").split(/\s*—\s*/)[0].trim().toLowerCase();
            if (nomeNovo.length < 2) continue;
            // Procurar no cardápio — match por nome
            let itemComFoto = null;
            for (const cat of config.cardapio || []) {
              for (const item of cat.itens || []) {
                if (!item.imagem) continue;
                const nomeItem = item.nome.toLowerCase();
                // Match se o nome do item contém palavras do pedido ou vice-versa
                const palavrasNovo = nomeNovo.split(/\s+/).filter(p => p.length > 2);
                const acertos = palavrasNovo.filter(p => nomeItem.includes(p));
                if (acertos.length > 0 && acertos.length >= Math.ceil(palavrasNovo.length * 0.5)) {
                  itemComFoto = item; break;
                }
              }
              if (itemComFoto) break;
            }
            if (itemComFoto) {
              try {
                const { MessageMedia } = require("whatsapp-web.js");
                const b64 = itemComFoto.imagem.includes(",") ? itemComFoto.imagem.split(",")[1] : itemComFoto.imagem;
                const media = new MessageMedia("image/jpeg", b64, itemComFoto.nome + ".jpg");
                await chat.sendMessage(media, { caption: `📸 *${itemComFoto.nome}*${itemComFoto.descricao ? "\n_" + itemComFoto.descricao + "_" : ""}` });
                await sleep(400);
              } catch(eImg2) { console.error("[IMG-PRODUTO]", eImg2.message); }
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
    // Permitir ver promoções mesmo durante pedido (cliente pode querer adicionar uma promo)
    if (true) {  // sempre verificar promoções
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
            const pedidoAtivo35 = estadosPedido.get(numero);
            const sufixoPromo = pedidoAtivo35?.itens
              ? `\n\n🛒 _Pedido atual: ${pedidoAtivo35.itens}_\n*2* ✅ Continuar para entrega`
              : "";
            resp = `\n📋 *Resumo das promoções:*\n${lista}\n\nDigite o código (ex: *P1*) para pedir! 🛒${sufixoPromo}\n\n*0* ↩️ Voltar ao menu`;
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
      // Suporta P1, P2 (1 unidade) e 2P1, 3P2 (múltiplas unidades)
      const mP  = txt.trim().match(/^[Pp](\d+)$/);
      const mQP = txt.trim().match(/^(\d+)[Pp](\d+)$/); // ex: 2P1 = 2x promo 1
      if (mP || mQP) {
        const qtdPromo = mQP ? parseInt(mQP[1]) : 1;
        const pIdx = mQP ? parseInt(mQP[2]) - 1 : parseInt(mP[1]) - 1;
        const promCache = historicos.get("__promos__"+numero);
        const promosList = promCache?.promos || (loadConfig().promocoes||[]).filter(p=>p.ativo&&p.nome);
        const escolhida = promosList[pIdx];
        if (escolhida) {
          const precoUsar = escolhida.precoPromo || escolhida.precoOriginal || "—";
          const nomePromoItem = qtdPromo > 1
            ? `${qtdPromo}x ${escolhida.nome} — R$ ${precoUsar}`
            : `${escolhida.nome} — R$ ${precoUsar}`;
          // Se já tem pedido ativo, adicionar a promoção ao pedido existente
          let estado;
          if (estadosPedido.has(numero)) {
            estado = estadosPedido.get(numero);
            estado.itens = estado.itens ? `${estado.itens} | ${nomePromoItem}` : nomePromoItem;
            estado.etapa = "mais_itens";
          } else {
            const numP = String(Date.now()).slice(-5);
            estado = novoEstado(numP);
            estado.itens = nomePromoItem;
            estado.etapa = "mais_itens";
          }
          estadosPedido.set(numero, estado);
          emitirContador();
          resetarTimeout(numero);
          const sub  = calcularTotal(estado.itens, config);
          const taxa = parseFloat((config.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
          const subT = sub > 0 ? `\n💰 Subtotal: R$ ${sub.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub+taxa).toFixed(2).replace(".",",")}*` : "";
          resp = (
            `✅ *${qtdPromo>1?qtdPromo+"x ":""}${escolhida.nome}* adicionado! 🎉${subT}\n\n` +
            `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n` +
            `👇 *Deseja mais alguma coisa?*\n\n` +
            `*1* ➕ Mais itens\n` +
            `*2* ✅ Continuar para entrega\n` +
            `*3* 🗑️ Remover\n` +
            `*4* 🔄 Recomeçar\n` +
            `*0* ↩️ Cancelar e voltar ao menu`
          );
        } else {
          resp = `❓ Promoção *P${pIdx+1}* não encontrada.\n\nDigite *7* para ver as promoções disponíveis.\n\n*0* ↩️ Voltar ao menu`;
        }
      }
    }

    // ════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════
    //  PRIORIDADE 3.5: ITEM(S) DIGITADOS DIRETAMENTE SEM PEDIDO ATIVO
    //  "suco de uva", "5 sucos e 2 bacons" sem ter dito "pedir"
    // ════════════════════════════════════════════════════
    if (resp === null && !estadosPedido.has(numero)) {
      const num35 = String(Date.now()).slice(-5);
      const est35 = novoEstado(num35);
      let achou35 = false;

      // Tentar multi-item
      const temSep35 = txt.includes(" e ") || txt.includes(",") || txt.includes(" com ");
      const reMulti35 = /(\d+|um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez)\s*x?\s+\S.+\s+(e\s+|com\s+|,|\d|um|uma|dois|duas)/i;
      if (temSep35 || reMulti35.test(txt)) {
        let partes35 = [];
        if (txt.includes(" e ")) partes35 = txt.split(/\s+e\s+/i).map(p=>p.trim()).filter(p=>p.length>1);
        else if (txt.includes(" com ")) partes35 = txt.split(/\s+com\s+/i).map(p=>p.trim()).filter(p=>p.length>1);
        else if (txt.includes(",")) partes35 = txt.split(/,\s*/).map(p=>p.trim()).filter(p=>p.length>1);
        if (partes35.length < 2) {
          // "5x bacon 5x suco" — padrão numérico repetido
          const sp35 = txt
            .replace(/(\s+)(\d+x?\s|(?:um|uma|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez)\s)/gi,"|||$2")
            .split("|||")
            .map(p=>p.trim()).filter(p=>p.length>1);
          if (sp35.length >= 2) partes35 = sp35;
        }
        if (partes35.length >= 2) {
          const res35 = [], err35 = [];
          for (const parte of partes35) {
            const { qtd: qP, texto: tP } = extrairQtd(parte.trim());
            const vP = validarItem(tP, config);
            if (!vP.ok) { err35.push(parte.trim()); continue; }
            if (vP.item.pausado) { err35.push(vP.item.nome+" (pausado)"); continue; }
            res35.push({ item: vP.item, qtd: qP });
          }
          if (res35.length > 0) {
            const mapa35 = new Map();
            for (const r of res35) {
              if (mapa35.has(r.item.nome)) mapa35.get(r.item.nome).qtd += r.qtd;
              else mapa35.set(r.item.nome, { item: r.item, qtd: r.qtd });
            }
            let msg35 = "🛒✅ *Pedido recebido:*\n";
            for (const { item, qtd } of mapa35.values()) {
              const ns = qtd > 1 ? `${qtd}x ${item.nome} — ${item.preco}` : `${item.nome} — ${item.preco}`;
              est35.itens = est35.itens ? `${est35.itens} | ${ns}` : ns;
              msg35 += `  ✓ ${ns}
`;
            }
            if (err35.length) msg35 += `
⚠️ Não encontrado: ${err35.join(", ")}
`;
            est35.etapa = "mais_itens";
            estadosPedido.set(numero, est35);
            emitirContador(); resetarTimeout(numero);
            const sub35 = calcularTotal(est35.itens, config);
            const taxa35 = parseFloat((config.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
            const subT35 = sub35 > 0 ? `
💰 Subtotal: R$ ${sub35.toFixed(2).replace(".",",")} + taxa R$ ${taxa35.toFixed(2).replace(".",",")} = *R$ ${(sub35+taxa35).toFixed(2).replace(".",",")}*` : "";
            resp = msg35 + subT35 + `

▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
👇 *Deseja mais alguma coisa?*

*1* ➕ Mais itens
*2* ✅ Continuar para entrega
*3* 🗑️ Remover item
*4* 🔄 Recomeçar`;
            achou35 = true;
          }
        }
      }

      // Item único
      if (!achou35) {
        const valDir = validarItem(txt.trim(), config);
        if (valDir.ok && !valDir.item.pausado) {
          const { qtd: qtdD } = extrairQtd(txt.trim());
          const ns = qtdD > 1 ? `${qtdD}x ${valDir.item.nome} — ${valDir.item.preco}` : `${valDir.item.nome} — ${valDir.item.preco}`;
          est35.itens = ns; est35.etapa = "mais_itens";
          estadosPedido.set(numero, est35);
          emitirContador(); resetarTimeout(numero);
          const sub35 = calcularTotal(est35.itens, config);
          const taxa35 = parseFloat((config.taxaEntrega||"0").replace(/[^\d,.]/g,"").replace(",",".")) || 0;
          const subT35 = sub35 > 0 ? `
💰 Subtotal: R$ ${sub35.toFixed(2).replace(".",",")} + taxa = *R$ ${(sub35+taxa35).toFixed(2).replace(".",",")}*` : "";
          const fotoH = valDir.item.imagem ? `
📷 _Foto disponível — diga "foto do ${valDir.item.nome}"_` : "";
          // Enviar foto automaticamente (usa msg.getChat pois chat não existe nesse escopo)
          if (valDir.item.imagem && waConectado && waClient) {
            try {
              const { MessageMedia } = require("whatsapp-web.js");
              const b64 = valDir.item.imagem.includes(",") ? valDir.item.imagem.split(",")[1] : valDir.item.imagem;
              const mediaImg = new MessageMedia("image/jpeg", b64, valDir.item.nome+".jpg");
              const chat35 = await msg.getChat();
              await chat35.sendMessage(mediaImg, { caption: `📸 *${valDir.item.nome}*\n${valDir.item.descricao||""}` });
            } catch(eImg) { console.error("[FOTO-AUTO]", eImg.message); }
          }
          resp = `✅ *${qtdD>1?qtdD+"x ":""}${valDir.item.nome}* adicionado! 🎉${subT35}

▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
👇 *Deseja mais alguma coisa?*

*1* ➕ Mais itens
*2* ✅ Continuar para entrega
*3* 🗑️ Remover item
*4* 🔄 Recomeçar`;
          achou35 = true;
        }
      }
    }

    //  PRIORIDADE 2.5: CATÁLOGO DE FOTOS (Opção 2)
    // ════════════════════════════════════════════════════
    if (!estadosPedido.has(numero) && (txt.trim() === "2" || normStr(txt).includes("catalogo") || normStr(txt).includes("foto"))) {
      const cats = (config.cardapio || []).filter(c => (c.itens || []).some(i => !i.pausado));
      if (cats.length > 0) {
        await responderHumano(chat, msg, "Aguarde um instante enquanto preparo o nosso catálogo de fotos... 📸");
        
        for (const cat of cats) {
          const itensComFoto = (cat.itens || []).filter(i => !i.pausado);
          if (itensComFoto.length === 0) continue;

          let msgCat = `📂 *GRUPO: ${cat.categoria.toUpperCase()}*\n\n`;
          await chat.sendMessage(msgCat);
          await sleep(500);

          for (const item of itensComFoto) {
            const textoItem = `*${item.nome}*\n💰 Preço: ${item.preco}\n${item.descricao ? `📝 ${item.descricao}\n` : ""}`;
            
            if (item.imagem && waConectado && waClient) {
              try {
                const { MessageMedia } = require("whatsapp-web.js");
                const b64 = item.imagem.includes(",") ? item.imagem.split(",")[1] : item.imagem;
                const mediaImg = new MessageMedia("image/jpeg", b64, item.nome + ".jpg");
                await chat.sendMessage(mediaImg, { caption: textoItem });
              } catch (eImg) {
                console.error("[CATALOGO-FOTO]", eImg.message);
                await chat.sendMessage(textoItem);
              }
            } else {
              await chat.sendMessage(textoItem);
            }
            await sleep(800);
          }
          await sleep(1000);
        }
        
        const msgFinal = "Este é o nosso catálogo completo! 😊\n\n*0* ↩️ Voltar ao menu\n*3* 🛒 Fazer Pedido";
        await chat.sendMessage(msgFinal);
        logC({ tipo: "saida", para: numero, mensagem: "Catálogo de fotos enviado" });
        io.emit("msg", { numero, mensagem: "Catálogo de fotos enviado", tipo: "saida" });
        return;
      }
    }

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
          `*2* 📸 Catálogo de Fotos\n` +
          `*3* 🛒 Fazer Pedido\n` +
          `*4* 📦 Meu Pedido\n` +
          `*5* 🕐 Horário\n` +
          `*6* 💳 Pagamento\n` +
          `*7* 👤 Atendente`
        );
      } else {
        // Texto não reconhecido — oferecer menu + ajuda
        resp = (
          `😅 Não entendi *"${txt.slice(0,30)}"*\n\n` +
          `Tente uma dessas opções:\n\n` +
          `*1* 🍽️ Ver Cardápio\n` +
          `*2* 📸 Catálogo de Fotos\n` +
          `*3* 🛒 Fazer Pedido\n` +
          `*4* 📦 Meu Pedido\n` +
          `*5* 🕐 Horário\n` +
          `*6* 💳 Pagamento\n` +
          `*7* 👤 Atendente\n\n` +
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

// ═══════════════════════
//  ENCERRAMENTO LIMPO
// ═══════════════════════
process.on("SIGINT", async () => {
  console.log("\n[SISTEMA] Encerrando...");
  if (waClient) {
    try { await waClient.destroy(); console.log("[WA] Cliente destruído."); } catch(_) {}
  }
  process.exit(0);
});
process.on("SIGTERM", async () => {
  if (waClient) {
    try { await waClient.destroy(); } catch(_) {}
  }
  process.exit(0);
});
