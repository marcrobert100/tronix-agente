# Script PowerShell para configurar variáveis de ambiente do sistema
# Execute este script como administrador

Write-Host "Configurando variáveis de ambiente do sistema para Mimo v2..." -ForegroundColor Green

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
        "api_key" = "sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v"
        "base_url" = "https://api.mimo.ai/v1"
        "model" = "mimo-v2-flash"
    }
} | ConvertTo-Json -Depth 10

Set-Content -Path $openClaudeConfigPath -Value $configContent -Encoding UTF8

Write-Host "Arquivo de configuração do OpenClaude criado em: $openClaudeConfigPath" -ForegroundColor Green
Write-Host "Conteúdo do arquivo:" -ForegroundColor Yellow
Get-Content $openClaudeConfigPath

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
Write-Host "Agora você pode executar: openclaude" -ForegroundColor Cyan
