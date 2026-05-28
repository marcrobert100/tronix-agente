# Script PowerShell para atualizar o arquivo de configuração do OpenClaude para usar a API da Clod

Write-Host "Atualizando configuração do OpenClaude para usar a API da Clod..." -ForegroundColor Green

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
        "api_key" = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDZjlBOWRPQ1ZJaDkwQVNqNldIT09SZHh4eWQyIiwidXNlcklkIjoiQ2Y5QTlkT0NWSWg5MEFTajZXSE9PUmR4eHlkMiIsInRlYW1JZCI6IjNhMTAwMjMyLTI4M2ItNDc1My05YWNlLWNkMjI2ZjZhMTFiYiIsInRlYW1Sb2xlIjoib3duZXIiLCJwcm9qZWN0SWQiOiI0N2Q1NDlmMS1lYTAwLTRmNDItYWNkYi1kZGViOWFhZmFjZmQiLCJpYXQiOjE3Nzc5NDIzODksImV4cCI6MTgyNzk0MjM4OX0.r-HVoOLf_J89y4_sauYKAHNp33H9HqMrmraGs3bTf6I"
        "base_url" = "https://api.clod.io/v1"
        "model" = "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"
    }
} | ConvertTo-Json -Depth 10

Set-Content -Path $openClaudeConfigPath -Value $configContent -Encoding UTF8

Write-Host "Arquivo de configuração do OpenClaude atualizado em: $openClaudeConfigPath" -ForegroundColor Green
Write-Host "Conteúdo do arquivo:" -ForegroundColor Yellow
Get-Content $openClaudeConfigPath

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
Write-Host "Agora você pode executar: openclaude" -ForegroundColor Cyan
