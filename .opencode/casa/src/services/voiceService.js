// src/services/voiceService.js
const fs = require("fs");
const path = require("path");
const FormData = require("form-data");
// Trata o import dinâmico nativamente do node-fetch v3 (se instalado como módulo ES)
const nodeFetch = (...args) => import("node-fetch").then(({default: f}) => f(...args));
const db = require("../config/dbConfig");

// Utilizaremos uma dependência embarcada chamada google-tts-api gratuita e nativa 
const googleTTS = require("google-tts-api"); 

/**
 * Transcreve áudio enviado pelo cliente no WhatsApp (Áudio -> Texto)
 */
async function transcreverAudioGroq(bufferAudio) {
  const config = db.loadConfig();
  const key = (config.groqApiKey || "").trim();
  
  if (!key.startsWith("gsk_")) {
    console.error("[VOZ]❌ Chave Groq não configurada");
    return null;
  }

  let tmpFile = null;
  try {
    tmpFile = path.join(db.LOG_DIR, "temp_audio_" + Date.now() + ".ogg");
    fs.writeFileSync(tmpFile, bufferAudio);
    
    const form = new FormData();
    form.append("file", fs.createReadStream(tmpFile));
    form.append("model", "whisper-large-v3");
    form.append("language", "pt");
    form.append("temperature", "0.2");
    form.append("response_format", "text");

    const fetch = await nodeFetch;
    
    const response = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
      method: "POST",
      headers: { "Authorization": `Bearer ${key}` },
      body: form
    });

    if (!response.ok) {
      console.error("[VOZ]❌ Groq erro:", response.status, await response.text());
      return null;
    }

    const texto = await response.text();
    return texto.trim() || null;
  } catch (err) {
    console.error("[VOZ]❌ Exceção:", err.message);
    return null;
  } finally {
    if (tmpFile) { try { fs.unlinkSync(tmpFile); } catch (_) {} }
  }
}

/**
 * Sintetiza uma fala de volta para o cliente (Texto -> Áudio Base64)
 * @param {string} texto Mensagem a ser falada
 * @returns {Promise<string|null>} Base64 data do áudio gerado
 */
async function sintetizarFalaBase64(texto) {
  try {
    // Se o texto for muto grande, googleTTS pode reclamar. 
    // É ideal mandar textos diretos (max 200 characteres nativos do TTS gratuito, ou quebrar se preferir).
    // Aqui usaremos getAudioBase64, com fallback
    
    const base64Audio = await googleTTS.getAudioBase64(texto.slice(0, 200), {
      lang: 'pt-BR',
      slow: false,
      host: 'https://translate.google.com',
      timeout: 10000,
    });
    
    return base64Audio;
  } catch(e) {
    console.error("[TTS] Erro ao sintetizar voz embarcada:", e.message);
    return null;
  }
}

module.exports = {
  transcreverAudioGroq,
  sintetizarFalaBase64
};
