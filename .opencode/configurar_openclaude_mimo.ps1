# Script PowerShell para configurar o OpenClaude com a API da Mimo v2 Flash da Xiaomi
# Execute este script no mesmo terminal onde você executa o openclaude

Write-Host "Configurando OpenClaude com a API da Mimo v2 Flash da Xiaomi..." -ForegroundColor Green

# Configurar variáveis de ambiente para o OpenClaude usar a API da Mimo v2
$env:CLAUDE_CODE_USE_OPENAI = "1"
$env:OPENAI_API_KEY = "sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v"
$env:OPENAI_BASE_URL = "https://api.mimo.ai/v1"
$env:OPENAI_MODEL = "mimo-v2-flash"

Write-Host "Variáveis de ambiente configuradas:" -ForegroundColor Yellow
Write-Host "  CLAUDE_CODE_USE_OPENAI: $env:CLAUDE_CODE_USE_OPENAI" -ForegroundColor Cyan
Write-Host "  OPENAI_API_KEY: $env:OPENAI_API_KEY" -ForegroundColor Cyan
Write-Host "  OPENAI_BASE_URL: $env:OPENAI_BASE_URL" -ForegroundColor Cyan
Write-Host "  OPENAI_MODEL: $env:OPENAI_MODEL" -ForegroundColor Cyan

Write-Host "`nPara usar permanentemente, adicione estas variáveis ao seu perfil do PowerShell:" -ForegroundColor Yellow
Write-Host "  1. Abra o arquivo de perfil: notepad $PROFILE" -ForegroundColor Cyan
Write-Host "  2. Adicione as seguintes linhas:" -ForegroundColor Cyan
Write-Host "     `$env:CLAUDE_CODE_USE_OPENAI = `"1`"" -ForegroundColor Cyan
Write-Host "     `$env:OPENAI_API_KEY = `"sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v`"" -ForegroundColor Cyan
Write-Host "     `$env:OPENAI_BASE_URL = `"https://api.mimo.ai/v1`"" -ForegroundColor Cyan
Write-Host "     `$env:OPENAI_MODEL = `"mimo-v2-flash`"" -ForegroundColor Cyan

Write-Host "`nPara executar o OpenClaude agora, execute:" -ForegroundColor Yellow
Write-Host "  openclaude" -ForegroundColor Cyan

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
