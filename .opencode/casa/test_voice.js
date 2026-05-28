/**
 * Teste de transcrição de áudio com Groq
 */
const fs = require("fs");
const path = require("path");
const FormData = require("form-data");

// Carregar config
const config = JSON.parse(fs.readFileSync(path.join(__dirname, "config.json"), "utf8"));
const key = config.groqApiKey;

console.log("=== TESTE DE VOZ ===");
console.log("Chave Groq:", key ? "OK (" + key.length + " chars)" : "FALTANDO");

// Testar transcrição com um arquivo de áudio existente (se houver)
const logsDir = path.join(__dirname, "logs");
const arquivos = fs.readdirSync(logsDir).filter(f => f.endsWith(".ogg") || f.endsWith(".mp3") || f.endsWith(".m4a"));

if (arquivos.length > 0) {
  console.log("\nArquivos de áudio encontrados:", arquivos);
} else {
  console.log("\nNenhum arquivo de áudio de teste encontrado.");
  console.log("Para testar: cole o base64 de um áudio no arquivo test_audio.txt");
}

// Testar API Groq - criar um texto simples
async function testarAPI() {
  console.log("\n=== TESTE DA API GROQ ===");
  
  try {
    const form = new FormData();
    // Criar arquivo de teste vazio só para ver se a API responde
    const testFile = path.join(__dirname, "test_tts.txt");
    fs.writeFileSync(testFile, "test");
    form.append("file", fs.createReadStream(testFile));
    form.append("model", "whisper-large-v3");
    form.append("language", "pt");
    
    const response = await fetch("https://api.groq.com/openai/v1/audio/transcriptions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${key}`,
      },
      body: form
    });
    
    fs.unlinkSync(testFile);
    
    console.log("Status:", response.status);
    console.log("Headers:", response.headers.raw());
    
    if (!response.ok) {
      const err = await response.text();
      console.log("Erro:", err);
    } else {
      const data = await response.json();
      console.log("Resposta:", data);
    }
  } catch (err) {
    console.log("Exceção:", err.message);
  }
}

testarAPI();

console.log("\n=== FIM DO TESTE ===");
