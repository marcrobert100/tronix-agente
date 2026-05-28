# Script PowerShell para verificar a configuração da API Mimo v2 Flash

Write-Host "Verificando configuração da API Mimo v2 Flash (Xiaomi)..." -ForegroundColor Green

# Verificar variáveis de ambiente
Write-Host "`n1. Variáveis de ambiente do OpenClaude:" -ForegroundColor Yellow
$envVars = @("CLAUDE_CODE_USE_OPENAI", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var, "Process")
    if ($value) {
        Write-Host "  ${var}: $value" -ForegroundColor Cyan
    } else {
        Write-Host "  ${var}: NÃO CONFIGURADA" -ForegroundColor Red
    }
}

# Verificar perfil do PowerShell
Write-Host "`n2. Perfil do PowerShell:" -ForegroundColor Yellow
if (Test-Path $PROFILE) {
    $profileContent = Get-Content $PROFILE -Raw
    Write-Host "  Arquivo: $PROFILE" -ForegroundColor Cyan
    Write-Host "  Conteúdo:" -ForegroundColor Cyan
    Get-Content $PROFILE | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  Perfil não encontrado" -ForegroundColor Red
}

# Verificar configuração do OpenClaude
Write-Host "`n3. Configuração do OpenClaude:" -ForegroundColor Yellow
$openClaudeConfigPath = "$env:USERPROFILE\.claude\settings.json"
if (Test-Path $openClaudeConfigPath) {
    Write-Host "  Arquivo: $openClaudeConfigPath" -ForegroundColor Cyan
    Write-Host "  Conteúdo:" -ForegroundColor Cyan
    Get-Content $openClaudeConfigPath | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  Arquivo de configuração não encontrado" -ForegroundColor Red
}

# Verificar serviço Mimo v2
Write-Host "`n4. Serviço Mimo v2:" -ForegroundColor Yellow
$mimoServicePath = "C:\xampp\htdocs\agente\.opencode\casa\src\services\mimoService.js"
if (Test-Path $mimoServicePath) {
    Write-Host "  Arquivo: $mimoServicePath" -ForegroundColor Cyan
    Write-Host "  Status: OK" -ForegroundColor Green
} else {
    Write-Host "  Arquivo de serviço não encontrado" -ForegroundColor Red
}

# Verificar configuração do servidor de delivery
Write-Host "`n5. Configuração do servidor de delivery:" -ForegroundColor Yellow
$configPath = "C:\xampp\htdocs\agente\.opencode\casa\config.json"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw | ConvertFrom-Json
    if ($configContent.mimoApiKey) {
        Write-Host "  Chave Mimo API: CONFIGURADA" -ForegroundColor Green
    } else {
        Write-Host "  Chave Mimo API: NÃO CONFIGURADA" -ForegroundColor Red
    }
} else {
    Write-Host "  Arquivo de configuração não encontrado" -ForegroundColor Red
}

# Testar conexão com a OpenRouter
Write-Host "`n6. Teste de conexão com a OpenRouter:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://openrouter.ai/api/v1/models" -Headers @{Authorization="Bearer sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v"; "HTTP-Referer"="https://example.com"; "X-Title"="Test"} -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "  Conexão: OK" -ForegroundColor Green
        Write-Host "  Modelos Xiaomi disponíveis:" -ForegroundColor Cyan
        $models = $response.Content | ConvertFrom-Json | Select-Object -ExpandProperty data | Where-Object { $_.id -like "*xiaomi*" } | Select-Object -First 5
        foreach ($model in $models) {
            Write-Host "    - $($model.name) ($($model.id))" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Conexão: FALHA (Status: $($response.StatusCode))" -ForegroundColor Red
    }
} catch {
    Write-Host "  Conexão: FALHA ($($_.Exception.Message))" -ForegroundColor Red
}

Write-Host "`nVerificação concluída!" -ForegroundColor Green
