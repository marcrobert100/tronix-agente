# Script PowerShell para testar a API da Clod com os modelos Qwen

Write-Host "Testando a API da Clod com os modelos Qwen..." -ForegroundColor Green

$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDZjlBOWRPQ1ZJaDkwQVNqNldIT09SZHh4eWQyIiwidXNlcklkIjoiQ2Y5QTlkT0NWSWg5MEFTajZXSE9PUmR4eHlkMiIsInRlYW1JZCI6IjNhMTAwMjMyLTI4M2ItNDc1My05YWNlLWNkMjI2ZjZhMTFiYiIsInRlYW1Sb2xlIjoib3duZXIiLCJwcm9qZWN0SWQiOiI0N2Q1NDlmMS1lYTAwLTRmNDItYWNkYi1kZGViOWFhZmFjZmQiLCJpYXQiOjE3Nzc5NDIzODksImV4cCI6MTgyNzk0MjM4OX0.r-HVoOLf_J89y4_sauYKAHNp33H9HqMrmraGs3bTf6I"

# Testar modelo Qwen3 235B
Write-Host "`n1. Testando Qwen/Qwen3-235B-A22B-Thinking-2507..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.clod.io/v1/chat/completions" -Method POST -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} -Body '{"model": "Qwen/Qwen3-235B-A22B-Thinking-2507", "messages": [{"role": "user", "content": "Olá, teste da API Clod com o modelo Qwen3 235B"}]}' -TimeoutSec 10 | ConvertFrom-Json
    Write-Host "  Status: OK" -ForegroundColor Green
    Write-Host "  Modelo usado: $($response.model)" -ForegroundColor Cyan
    Write-Host "  Resposta: $($response.choices[0].message.content)" -ForegroundColor Gray
} catch {
    Write-Host "  Status: FALHA ($($_.Exception.Message))" -ForegroundColor Red
}

# Testar modelo Qwen3 Coder
Write-Host "`n2. Testando Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.clod.io/v1/chat/completions" -Method POST -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} -Body '{"model": "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8", "messages": [{"role": "user", "content": "Olá, teste da API Clod com o modelo Qwen3 Coder"}]}' -TimeoutSec 10 | ConvertFrom-Json
    Write-Host "  Status: OK" -ForegroundColor Green
    Write-Host "  Modelo usado: $($response.model)" -ForegroundColor Cyan
    Write-Host "  Resposta: $($response.choices[0].message.content)" -ForegroundColor Gray
} catch {
    Write-Host "  Status: FALHA ($($_.Exception.Message))" -ForegroundColor Red
}

# Testar modelo Qwen2.5
Write-Host "`n3. Testando Qwen/Qwen2.5-7B-Instruct-Turbo..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.clod.io/v1/chat/completions" -Method POST -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} -Body '{"model": "Qwen/Qwen2.5-7B-Instruct-Turbo", "messages": [{"role": "user", "content": "Olá, teste da API Clod com o modelo Qwen2.5"}]}' -TimeoutSec 10 | ConvertFrom-Json
    Write-Host "  Status: OK" -ForegroundColor Green
    Write-Host "  Modelo usado: $($response.model)" -ForegroundColor Cyan
    Write-Host "  Resposta: $($response.choices[0].message.content)" -ForegroundColor Gray
} catch {
    Write-Host "  Status: FALHA ($($_.Exception.Message))" -ForegroundColor Red
}

Write-Host "`nTestes concluídos!" -ForegroundColor Green
