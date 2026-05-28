# Script PowerShell para testar o OpenClaude com a API da Clod

Write-Host "Testando o OpenClaude com a API da Clod..." -ForegroundColor Green

# Testar OpenClaude com o modelo Qwen3 Coder
Write-Host "`n1. Testando OpenClaude com Qwen3 Coder..." -ForegroundColor Yellow
try {
    $response = openclaude --provider openai --model "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8" --print "Olá, teste da API Clod com Qwen3 Coder" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Status: OK" -ForegroundColor Green
        Write-Host "  Resposta: $response" -ForegroundColor Gray
    } else {
        Write-Host "  Status: FALHA" -ForegroundColor Red
        Write-Host "  Erro: $response" -ForegroundColor Red
    }
} catch {
    Write-Host "  Status: FALHA ($($_.Exception.Message))" -ForegroundColor Red
}

Write-Host "`nTeste concluído!" -ForegroundColor Green
