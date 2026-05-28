# Teste de integração Claude Code + Ollama

Write-Host "=== Teste de Integração Claude Code + Ollama ===" -ForegroundColor Green

# Verificar variáveis de ambiente
Write-Host "`n1. Variáveis de ambiente Ollama:" -ForegroundColor Yellow
Get-ChildItem Env: | Where-Object { $_.Name -like "*OLLAMA*" } | ForEach-Object { Write-Host "  $($_.Name) = $($_.Value)" }

# Verificar perfil ativo no Claude Code
Write-Host "`n2. Perfil ativo no Claude Code:" -ForegroundColor Yellow
$claudeConfig = Get-Content "$env:USERPROFILE\.claude.json" | ConvertFrom-Json
$activeProfile = $claudeConfig.providerProfiles | Where-Object { $_.id -eq $claudeConfig.activeProviderProfileId }
Write-Host "  Nome: $($activeProfile.name)"
Write-Host "  Modelo: $($activeProfile.model)"
Write-Host "  Base URL: $($activeProfile.baseUrl)"

# Testar API Ollama
Write-Host "`n3. Testando API Ollama..." -ForegroundColor Yellow
$body = @{
    model = "qwen2:0.5b"
    messages = @(@{role = "user"; content = "Olá, teste de integração!"})
    stream = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Write-Host "  ✓ API funcionando!" -ForegroundColor Green
    Write-Host "  Modelo: $($response.model)"
    Write-Host "  Resposta: $($response.choices[0].message.content)"
    Write-Host "  Tokens usados: $($response.usage.total_tokens)"
} catch {
    Write-Host "  ✗ Erro na API: $_" -ForegroundColor Red
}

# Verificar modelos disponíveis
Write-Host "`n4. Modelos Ollama disponíveis:" -ForegroundColor Yellow
ollama list | Select-Object -Skip 1 | ForEach-Object { Write-Host "  $_" }

Write-Host "`n=== Configuração Completa! ===" -ForegroundColor Green
$msg = "O Claude Code está configurado para usar o modelo qwen2:0.5b via Ollama."
Write-Host $msg -ForegroundColor Cyan