// src/config/dbConfig.js
const fs = require("fs");
const path = require("path");
const state = require("./state");

const BASE_DIR     = path.join(__dirname, "../../"); 
const CONFIG_FILE  = path.join(BASE_DIR, "config.json");
const LICENSE_FILE = path.join(BASE_DIR, "license.json");
const LOG_DIR      = path.join(BASE_DIR, "logs");

if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });

const CLIENTES_FILE = path.join(LOG_DIR, "clientes.json");
const CUPONS_FILE   = path.join(LOG_DIR, "cupons.json");

function loadConfig() {
  try { if (fs.existsSync(CONFIG_FILE)) return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8")); }
  catch (e) { console.error("[CONFIG]", e.message); }
  return {};
}

function saveConfig(data) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(data, null, 2));
}

function loadClientes() {
  try { 
    if (fs.existsSync(CLIENTES_FILE)) {
      const d = JSON.parse(fs.readFileSync(CLIENTES_FILE,"utf8"));
      for (const [k,v] of Object.entries(d)) state.clientesDB.set(k,v);
    }
  } catch(_) {}
}

function saveClientes() {
  const obj = {}; 
  for (const [k,v] of state.clientesDB) obj[k]=v;
  fs.writeFileSync(CLIENTES_FILE, JSON.stringify(obj,null,2));
}

function loadCupons() {
  try { 
    if (fs.existsSync(CUPONS_FILE)) {
      const d = JSON.parse(fs.readFileSync(CUPONS_FILE,"utf8"));
      for (const [k,v] of Object.entries(d)) state.cuponsDB.set(k,v);
    }
  } catch(_) {}
}

function saveCupons() {
  const obj = {}; 
  for (const [k,v] of state.cuponsDB) obj[k]=v;
  fs.writeFileSync(CUPONS_FILE, JSON.stringify(obj,null,2));
}

module.exports = {
  LOG_DIR,
  CONFIG_FILE,
  LICENSE_FILE,
  loadConfig,
  saveConfig,
  loadClientes,
  saveClientes,
  loadCupons,
  saveCupons
};
