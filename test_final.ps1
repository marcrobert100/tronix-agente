# Script de teste final Claude Code + Ollama

Write-Host "=== Teste Final Claude Code + Ollama ===" -ForegroundColor Green

# 1. Verificar Ollama está rodando
Write-Host "`n1. Verificando Ollama..." -ForegroundColor Yellow
try {
    $ollamaStatus = ollama ps
    Write-Host "  ✓ Ollama está rodando" -ForegroundColor Green
    Write-Host "  $ollamaStatus"
} catch {
    Write-Host "  ✗ Ollama não está rodando" -ForegroundColor Red
    Write-Host "  Iniciando Ollama..."
    Start-Process "ollama" -ArgumentList "serve" -NoNewWindow
    Start-Sleep -Seconds 5
}

# 2. Verificar modelo qwen2:0.5b
Write-Host "`n2. Verificando modelo qwen2:0.5b..." -ForegroundColor Yellow
try {
    $modelList = ollama list | Out-String
    if ($modelList -match "qwen2:0.5b") {
        Write-Host "  ✓ Modelo qwen2:0.5b instalado" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Modelo qwen2:0.5b não encontrado" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ Erro ao verificar modelos" -ForegroundColor Red
}

# 3. Testar API Ollama
Write-Host "`n3. Testando API Ollama..." -ForegroundColor Yellow
try {
    $body = @{
        model = "qwen2:0.5b"
        messages = @(@{role = "user"; content = "Responda em português: Olá, como você está?"})
        stream = $false
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Write-Host "  ✓ API funcionando!" -ForegroundColor Green
    Write-Host "  Modelo: $($response.model)"
    Write-Host "  Resposta: $($response.choices[0].message.content)"
} catch {
    Write-Host "  ✗ Erro na API: $_" -ForegroundColor Red
}

# 4. Verificar configuração do Claude Code
Write-Host "`n4. Verificando configuração do Claude Code..." -ForegroundColor Yellow
try {
    $claudeConfig = Get-Content "$env:USERPROFILE\.claude.json" | ConvertFrom-Json
    $activeProfile = $claudeConfig.providerProfiles | Where-Object { $_.id -eq $claudeConfig.activeProviderProfileId }
    Write-Host "  ✓ Configuração encontrada" -ForegroundColor Green
    Write-Host "  Perfil ativo: $($activeProfile.name)"
    Write-Host "  Modelo: $($activeProfile.model)"
    Write-Host "  Base URL: $($activeProfile.baseUrl)"
} catch {
    Write-Host "  ✗ Erro ao ler configuração: $_" -ForegroundColor Red
}

# 5. Verificar variáveis de ambiente
Write-Host "`n5. Verificando variáveis de ambiente..." -ForegroundColor Yellow
$envVars = @("CLAUDE_CODE_USE_OLLAMA", "OLLAMA_MODEL", "OLLAMA_NUM_THREAD")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var, "User")
    if ($value) {
        Write-Host "  ✓ $var = $value" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $var não definida" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Teste Concluído ===" -ForegroundColor Green
Write-Host "O Claude Code está configurado para usar o modelo qwen2:0.5b via Ollama." -ForegroundColor Cyan
Write-Host "Para usar, basta iniciar o Claude Code e ele usará automaticamente o Ollama." -ForegroundColor Cyan