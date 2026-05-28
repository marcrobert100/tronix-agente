// src/services/groqService.js
const { OpenAI } = require("openai");
const db = require("../config/dbConfig");

let groqClient = null;

function initGroq() {
  const config = db.loadConfig();
  const key = (config.groqApiKey || "").trim();
  
  if (key.startsWith("gsk_")) {
    groqClient = new OpenAI({ apiKey: key, baseURL: "https://api.groq.com/openai/v1" });
    console.log("[IA] Groq OK:", config.model || "llama-3.1-8b-instant");
  } else {
    groqClient = null;
    if (key) console.warn("[IA] Chave inválida — deve começar com gsk_");
  }
}

function getClient() {
  return groqClient;
}

// Initial carga no require do service
initGroq();

module.exports = {
  initGroq,
  getClient
};
