# Script PowerShell para atualizar o arquivo de configuração do OpenClaude para usar a API da NVIDIA

Write-Host "Atualizando configuração do OpenClaude para usar a API da NVIDIA (Moonshot AI Kimi K2.6)..." -ForegroundColor Green

# Caminho para o arquivo de configuração do OpenClaude
$openClaudeConfigPath = "$env:USERPROFILE\.claude\settings.json"

# Criar diretório se não existir
if (!(Test-Path (Split-Path $openClaudeConfigPath))) {
    New-Item -ItemType Directory -Path (Split-Path $openClaudeConfigPath) -Force
}

# Criar ou atualizar o arquivo de configuração do OpenClaude
$configContent = @{
    "provider" = "openai"
    "openai" = @{
        "api_key" = "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"
        "base_url" = "https://api.nvidia.com/v1"
        "model" = "moonshotai/kimi-k2.6"
    }
} | ConvertTo-Json -Depth 10

Set-Content -Path $openClaudeConfigPath -Value $configContent -Encoding UTF8

Write-Host "Arquivo de configuração do OpenClaude atualizado em: $openClaudeConfigPath" -ForegroundColor Green
Write-Host "Conteúdo do arquivo:" -ForegroundColor Yellow
Get-Content $openClaudeConfigPath

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
Write-Host "Agora você pode executar: openclaude" -ForegroundColor Cyan