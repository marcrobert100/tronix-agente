# Script de Verificação de Configuração do OpenClaude
Write-Host "Verificando configuração do OpenClaude..." -ForegroundColor Green

# Verificar variáveis de ambiente
Write-Host "`nVariáveis de ambiente:" -ForegroundColor Yellow

$envVars = @("NVIDIA_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "WORKSPACE_ROOT", "OPENCODE_DIR")
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var, "User")
    if ($value) {
        Write-Host "${var}: Configurada" -ForegroundColor Green
        if ($var -match "KEY") {
            Write-Host "  Valor: $($value.Substring(0, [Math]::Min(20, $value.Length)))..." -ForegroundColor Gray
        } else {
            Write-Host "  Valor: $value" -ForegroundColor Gray
        }
    } else {
        Write-Host "${var}: NÃO configurada" -ForegroundColor Red
    }
}

# Verificar OpenClaude
Write-Host "`nOpenClaude:" -ForegroundColor Yellow
try {
    $version = openclaude --version 2>&1
    Write-Host "Versão: $version" -ForegroundColor Green
} catch {
    Write-Host "Não encontrado: $_" -ForegroundColor Red
}

# Verificar diretório de trabalho
Write-Host "`nDiretório de trabalho:" -ForegroundColor Yellow
$workspace = [Environment]::GetEnvironmentVariable("WORKSPACE_ROOT", "User")
if (Test-Path $workspace) {
    Write-Host "Existe: $workspace" -ForegroundColor Green
} else {
    Write-Host "Não existe: $workspace" -ForegroundColor Red
}

Write-Host "`nVerificação concluída!" -ForegroundColor Green
