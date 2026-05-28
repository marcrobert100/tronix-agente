# Script de teste do OpenClaude
Write-Host "Testando OpenClaude..." -ForegroundColor Green

# Testar se o comando openclaude está acessível
try {
    $openclaudeVersion = openclaude --version 2>&1
    Write-Host "Versão do OpenClaude: $openclaudeVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Erro ao executar openclaude: $_" -ForegroundColor Red
}

# Testar variáveis de ambiente
Write-Host "`nVariáveis de ambiente configuradas:" -ForegroundColor Yellow
Write-Host "NVIDIA_API_KEY: $($env:NVIDIA_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "WORKSPACE_ROOT: $env:WORKSPACE_ROOT" -ForegroundColor Gray

# Testar aliases
Write-Host "`nTestando aliases..." -ForegroundColor Yellow
Write-Host "Use 'oc' para executar o OpenClaude rapidamente." -ForegroundColor Cyan

# Testar diretório de trabalho
if (Test-Path $env:WORKSPACE_ROOT) {
    Write-Host "Diretório de trabalho existe: $env:WORKSPACE_ROOT" -ForegroundColor Green
} else {
    Write-Host "Diretório de trabalho não encontrado!" -ForegroundColor Red
}

Write-Host "`nTeste concluído!" -ForegroundColor Green
