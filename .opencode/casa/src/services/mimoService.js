// src/services/mimoService.js
const { OpenAI } = require("openai");
const db = require("../config/dbConfig");

let mimoClient = null;

function initMimo() {
  const config = db.loadConfig();
  const key = (config.mimoApiKey || "").trim();
  
  if (key.startsWith("sk_")) {
    // Mimo v2 API é compatível com OpenAI
    mimoClient = new OpenAI({ 
      apiKey: key, 
      baseURL: "https://api.mimo.ai/v1" // URL da API Mimo v2 (ajuste conforme necessário)
    });
    console.log("[IA] Mimo v2 OK:", config.model || "mimo-model");
  } else {
    mimoClient = null;
    if (key) console.warn("[IA] Chave inválida — deve começar com sk_");
  }
}

function getClient() {
  return mimoClient;
}

// Initial carga no require do service
initMimo();

module.exports = {
  initMimo,
  getClient
};
