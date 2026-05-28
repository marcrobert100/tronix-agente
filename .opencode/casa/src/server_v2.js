// src/server_v2.js
/**
 * ╔══════════════════════════════════════════════════════╗
 * ║   BOT WHATSAPP — DELIVERY & ATENDIMENTO MVC v2.0     ║
 * ║   (Rodando independente sem apagar o legado)          ║
 * ╚══════════════════════════════════════════════════════╝
 */
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const path = require("path");

// Carregamentos do MVC
const state = require("./config/state");
const { initWhatsApp } = require("./services/whatsappService");
const apiRoutes = require("./routes/api");

const PORT = 3001; // Porta divergente da 3000 original para teste conjunto.
const app = express();
const server = http.createServer(app);

// Insere Socket global state
state.io = new Server(server);

// --- Middlewares de App ---
app.use(express.json({ limit: "6mb" }));
app.use(express.urlencoded({ extended: true, limit: "6mb" }));

// --- Servir Front-End original (Temos que subir 1 nivel porque o public ta na raiz da casa) ---
const publicPath = path.join(__dirname, "../public");

app.use("/socket.io", express.static(path.join(__dirname, "../node_modules/socket.io/client-dist")));
app.get("/", (req, res) => res.sendFile(path.join(publicPath, "login.html")));
app.use("/public", express.static(publicPath));
// Painel sem auth check bruto para simplificar mockup, a API quem guardara seus dados
app.get("/painel", (req, res) => res.sendFile(path.join(publicPath, "painel.html")));

// --- Injeção do Roteador MVC ---
app.use("/api", apiRoutes);

// --- Boot Services ---
console.log("Iniciando Core do WhatsApp Web.js...");
initWhatsApp();

server.listen(PORT, () => {
  console.log(`[MVC SERVER] Nova Arquitetura rodando de forma isolada e segura na porta ${PORT}`);
  console.log(`Abra: http://localhost:${PORT}`);
});
