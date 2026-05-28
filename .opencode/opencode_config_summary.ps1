# Script PowerShell para resumo de configurações do OpenClaude

Write-Host "=== Configurações do OpenClaude Disponíveis ===" -ForegroundColor Green
Write-Host ""

Write-Host "1. Configuração Mimo v2 Flash (Xiaomi):" -ForegroundColor Yellow
Write-Host "   Script: configurar_openclaude_mimo.ps1" -ForegroundColor Cyan
Write-Host "   Modelo: mimo-v2-flash" -ForegroundColor Cyan
Write-Host "   API: https://api.mimo.ai/v1" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Configuração Clod (Qwen3-Coder):" -ForegroundColor Yellow
Write-Host "   Script: atualizar_openclaude_clod.ps1" -ForegroundColor Cyan
Write-Host "   Modelo: Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8" -ForegroundColor Cyan
Write-Host "   API: https://api.clod.io/v1" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Configuração NVIDIA (Moonshot AI Kimi K2.6):" -ForegroundColor Yellow
Write-Host "   Script: configurar_openclaude_nvidia.ps1" -ForegroundColor Cyan
Write-Host "   Modelo: moonshotai/kimi-k2.6" -ForegroundColor Cyan
Write-Host "   API: https://api.nvidia.com/v1" -ForegroundColor Cyan
Write-Host "   Token: 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" -ForegroundColor Cyan
Write-Host ""

Write-Host "4. Configuração Customizada (NVIDIA com parâmetros):" -ForegroundColor Yellow
Write-Host "   Script: configurar_openclaude_custom.ps1" -ForegroundColor Cyan
Write-Host "   Modelo: moonshotai/kimi-k2.6" -ForegroundColor Cyan
Write-Host "   Parâmetros: max_tokens=16384, temperature=1.00, top_p=1.00" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. Testar API NVIDIA:" -ForegroundColor Yellow
Write-Host "   Script: testar_api_nvidia.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Como usar ===" -ForegroundColor Green
Write-Host "Execute o script desejado:" -ForegroundColor Yellow
Write-Host "  .\configurar_openclaude_nvidia.ps1" -ForegroundColor Cyan
Write-Host "  .\configurar_openclaude_custom.ps1" -ForegroundColor Cyan
Write-Host "  .\testar_api_nvidia.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "Para usar permanentemente, adicione ao seu perfil do PowerShell:" -ForegroundColor Yellow
Write-Host "  notepad $PROFILE" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Variáveis de ambiente para NVIDIA ===" -ForegroundColor Green
Write-Host "  `$env:CLAUDE_CODE_USE_OPENAI = `"1`"" -ForegroundColor Cyan
Write-Host "  `$env:OPENAI_API_KEY = `"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`"" -ForegroundColor Cyan
Write-Host "  `$env:OPENAI_BASE_URL = `"https://api.nvidia.com/v1`"" -ForegroundColor Cyan
Write-Host "  `$env:OPENAI_MODEL = `"moonshotai/kimi-k2.6`"" -ForegroundColor Cyan