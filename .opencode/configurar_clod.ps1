# Script PowerShell para configurar o OpenClaude com a API da Clod
# Execute este script no mesmo terminal onde você executa o openclaude

Write-Host "Configurando OpenClaude com a API da Clod..." -ForegroundColor Green

# Configurar variáveis de ambiente para o OpenClaude usar a API da Clod
$env:CLAUDE_CODE_USE_OPENAI = "1"
$env:OPENAI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDZjlBOWRPQ1ZJaDkwQVNqNldIT09SZHh4eWQyIiwidXNlcklkIjoiQ2Y5QTlkT0NWSWg5MEFTajZXSE9PUmR4eHlkMiIsInRlYW1JZCI6IjNhMTAwMjMyLTI4M2ItNDc1My05YWNlLWNkMjI2ZjZhMTFiYiIsInRlYW1Sb2xlIjoib3duZXIiLCJwcm9qZWN0SWQiOiI0N2Q1NDlmMS1lYTAwLTRmNDItYWNkYi1kZGViOWFhZmFjZmQiLCJpYXQiOjE3Nzc5NDIzODksImV4cCI6MTgyNzk0MjM4OX0.r-HVoOLf_J89y4_sauYKAHNp33H9HqMrmraGs3bTf6I"
$env:OPENAI_BASE_URL = "https://api.clod.io/v1"
$env:OPENAI_MODEL = "Qwen/Qwen3-235B-A22B-Thinking-2507"

Write-Host "Variáveis de ambiente configuradas:" -ForegroundColor Yellow
Write-Host "  CLAUDE_CODE_USE_OPENAI: $env:CLAUDE_CODE_USE_OPENAI" -ForegroundColor Cyan
Write-Host "  OPENAI_API_KEY: (token JWT)" -ForegroundColor Cyan
Write-Host "  OPENAI_BASE_URL: $env:OPENAI_BASE_URL" -ForegroundColor Cyan
Write-Host "  OPENAI_MODEL: $env:OPENAI_MODEL" -ForegroundColor Cyan

Write-Host "`nModelos Qwen disponíveis na Clod:" -ForegroundColor Yellow
Write-Host "  1. Qwen/Qwen3-235B-A22B-Thinking-2507" -ForegroundColor Cyan
Write-Host "  2. Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8" -ForegroundColor Cyan
Write-Host "  3. Qwen/Qwen2.5-7B-Instruct-Turbo" -ForegroundColor Cyan

Write-Host "`nPara usar permanentemente, adicione estas variáveis ao seu perfil do PowerShell:" -ForegroundColor Yellow
Write-Host "  1. Abra o arquivo de perfil: notepad $PROFILE" -ForegroundColor Cyan
Write-Host "  2. Adicione as seguintes linhas:" -ForegroundColor Cyan
Write-Host "     `$env:CLAUDE_CODE_USE_OPENAI = `"1`"" -ForegroundColor Cyan
Write-Host "     `$env:OPENAI_API_KEY = `"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`"" -ForegroundColor Cyan
Write-Host "     `$env:OPENAI_BASE_URL = `"https://api.clod.io/v1`"" -ForegroundColor Cyan
Write-Host "     `$env:OPENAI_MODEL = `"Qwen/Qwen3-235B-A22B-Thinking-2507`"" -ForegroundColor Cyan

Write-Host "`nPara executar o OpenClaude agora, execute:" -ForegroundColor Yellow
Write-Host "  openclaude" -ForegroundColor Cyan

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
