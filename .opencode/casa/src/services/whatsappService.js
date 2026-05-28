// src/services/whatsappService.js
const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const qrcode = require("qrcode");
const state = require("../config/state");
const db = require("../config/dbConfig");
const voiceService = require("./voiceService");

/**
 * Envia uma mensagem em áudio gerada pelo Chatbot (PNS - Plug'N'Speak).
 * Simula um áudio gravado no microfone usando 'sendAudioAsVoice'
 */
async function enviarMensagemComoAudio(chatId, textoResposta) {
  if (!state.waClient || !state.waConectado) return false;
  
  try {
    // Passo 1: Sintetizar o texto em Base64
    const audioBase64 = await voiceService.sintetizarFalaBase64(textoResposta);
    
    if (!audioBase64) {
      // Fallback para texto se falhar o TTS
      await state.waClient.sendMessage(chatId, textoResposta);
      return false;
    }

    // Passo 2: Construir Mídia para WhatsApp Web
    // google-tts-api padroniza base64 no formato audio/mp3 
    const media = new MessageMedia('audio/mp3', audioBase64, 'audio.mp3');

    // Passo 3: Enviar como "Gravação de Voz"
    await state.waClient.sendMessage(chatId, media, { sendAudioAsVoice: true });
    return true;
  } catch (error) {
    console.error("[WA] Erro ao enviar áudio do Bot:", error.message);
    // Tenta fallback enviando apenas texto se engasgar
    await state.waClient.sendMessage(chatId, textoResposta).catch(()=>{});
    return false;
  }
}

/**
 * Inicializa a instância do WhatsApp Client e os eventos essenciais
 * @param {import('socket.io').Server} io Para comunicação de interface web
 */
function initWhatsApp() {
  const io = state.io; // garante que pegaremos o IO do estado global
  
  const client = new Client({
    authStrategy: new LocalAuth({ dataPath: ".wwebjs_auth" }),
    puppeteer: {
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-extensions", "--disable-gpu"]
    }
  });

  state.waClient = client;

  // -- Eventos de Conexão --
  client.on("qr", async (qr) => {
    state.waConectado = false;
    console.log("[WA] Novo QR Code Gerado");
    try {
      const url = await qrcode.toDataURL(qr);
      if (io) io.emit("qr", url);
    } catch (e) {
      console.error("[WA] Erro QR:", e.message);
    }
  });

  client.on("ready", () => {
    state.waConectado = true;
    console.log("[WA] WhatsApp Pronto e Conectado!");
    if (io) io.emit("ready");
  });

  client.on("authenticated", () => {
    console.log("[WA] Autenticado na sessão salvada.");
    if (io) io.emit("authenticated");
  });

  client.on("disconnected", (motivo) => {
    state.waConectado = false;
    console.warn("[WA] Desconectado!", motivo);
    if (io) io.emit("disconnected", motivo);
  });

  return client;
}

/**
 * Wrapper limpo para publicar status do WhatsApp (Stories/Bio).
 */
async function publicarStatusWA(item) {
  if (!state.waClient || !state.waConectado) throw new Error("WhatsApp não conectado");
  
  // Tratamento basico da string (variaveis precisarao estar mapeadas)
  const texto = item.texto || ""; 
  if (!texto) return;

  const resultados = [];
  try {
    await state.waClient.sendMessage("status@broadcast", texto);
    resultados.push("✅ Status/Stories publicado");
  } catch(e) {
    console.warn("[STATUS] ⚠️  Falha no Status:", e.message);
    try {
      await state.waClient.setStatus(texto.slice(0, 139));
      resultados.push("✅ Bio do perfil atualizada");
    } catch(e2) {
      console.warn("[STATUS] setStatus também falhou:", e2.message);
    }
  }
  return resultados;
}

module.exports = {
  initWhatsApp,
  enviarMensagemComoAudio,
  publicarStatusWA
};
