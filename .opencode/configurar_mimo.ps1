# Script PowerShell para configurar a API da Mimo v2
# Execute este script como administrador

Write-Host "Configurando API da Mimo v2..." -ForegroundColor Green

# Caminho para o arquivo de configuração
$configPath = "C:\xampp\htdocs\agente\.opencode\casa\config.json"

# Verificar se o arquivo existe
if (Test-Path $configPath) {
    Write-Host "Arquivo de configuração encontrado: $configPath" -ForegroundColor Yellow
    
    # Ler o conteúdo atual
    $configContent = Get-Content $configPath -Raw | ConvertFrom-Json
    
    # Adicionar a chave da API da Mimo v2
    $configContent | Add-Member -MemberType NoteProperty -Name "mimoApiKey" -Value "sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v" -Force
    
    # Salvar o arquivo
    $configContent | ConvertTo-Json -Depth 10 | Set-Content $configPath
    
    Write-Host "Chave da API da Mimo v2 configurada com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Arquivo de configuração não encontrado em: $configPath" -ForegroundColor Red
}

# Verificar se o serviço da Mimo v2 foi criado
$mimoServicePath = "C:\xampp\htdocs\agente\.opencode\casa\src\services\mimoService.js"
if (Test-Path $mimoServicePath) {
    Write-Host "Serviço da Mimo v2 encontrado: $mimoServicePath" -ForegroundColor Green
} else {
    Write-Host "Serviço da Mimo v2 não encontrado. Criando..." -ForegroundColor Yellow
    
    # Criar o serviço da Mimo v2
    $mimoServiceContent = @'
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
'@
    
    Set-Content -Path $mimoServicePath -Value $mimoServiceContent
    Write-Host "Serviço da Mimo v2 criado com sucesso!" -ForegroundColor Green
}

Write-Host "Configuração concluída!" -ForegroundColor Green
Write-Host "Para usar a API da Mimo v2, você precisará atualizar o código do servidor para usar o mimoService em vez do groqService." -ForegroundColor Yellow
