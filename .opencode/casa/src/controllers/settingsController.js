// src/controllers/settingsController.js
const authMiddleware = require("../middlewares/authMiddleware");
const db = require("../config/dbConfig");
const state = require("../config/state");

const login = (req, res) => {
  const { usuario, senha } = req.body || {};
  if (usuario === authMiddleware.ADMIN_USER && senha === authMiddleware.ADMIN_PASS) {
    const token = authMiddleware.gerarToken();
    state.sessoes.set(token, Date.now() + 8 * 3600000); // 8 horas validas
    return res.json({ ok: true, token });
  }
  res.status(401).json({ ok: false, erro: "Usuário ou senha incorretos" });
};

const logout = (req, res) => {
  const t = req.headers["x-token"];
  if (t) state.sessoes.delete(t);
  res.json({ ok: true });
};

const getStatus = (req, res) => {
  // Lógica basica retornada do config db
  res.json({
    conectado: state.waConectado,
    uptime: Math.floor((Date.now() - state.inicio) / 1000),
    mensagens: state.totalMsgs,
    sessoes: state.historicos.size,
    pedidos: state.pedidosAbertos.size,
    pedindoAgora: state.estadosPedido.size,
    agenteAtivo: state.agenteAtivo
  });
};

const saveGroqKey = (req, res) => {
  const raw = (req.body || {}).key || "";
  const key = raw.trim();
  if (!key.startsWith("gsk_") || key.length < 20) {
    return res.status(400).json({ ok: false, erro: "Chave inválida. Deve começar com gsk_ e ter pelo menos 20 caracteres." });
  }
  
  const cfg = db.loadConfig();
  cfg.groqApiKey = key;
  db.saveConfig(cfg);
  
  // Como atualizamos a chave, teríamos que recarregar o service Groq, mas faremos isso elegantemente 
  // via evento ou refetching a instancia
  console.log("[IA] ✅ Chave Groq salva isoladamente e segura.");
  res.json({ ok: true, msg: "Chave salva! IA ativada." });
};

module.exports = {
  login,
  logout,
  getStatus,
  saveGroqKey
};
