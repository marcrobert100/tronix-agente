# Script de Inicialização Rápida do OpenClaude
# Execute com: .\start_openclaude.ps1

# Carregar variáveis de ambiente
$env:NVIDIA_API_KEY = [Environment]::GetEnvironmentVariable("NVIDIA_API_KEY", "User")
$env:WORKSPACE_ROOT = [Environment]::GetEnvironmentVariable("WORKSPACE_ROOT", "User")
$env:OPENCODE_DIR = [Environment]::GetEnvironmentVariable("OPENCODE_DIR", "User")

Write-Host "OpenClaude Inicializado!" -ForegroundColor Green
Write-Host "Diretório de trabalho: $env:WORKSPACE_ROOT" -ForegroundColor Cyan

# Navegar para o diretório de trabalho
Set-Location $env:WORKSPACE_ROOT

# Mostrar opções
Write-Host "`nOpções disponíveis:" -ForegroundColor Yellow
Write-Host "1. Executar OpenClaude (oc)" -ForegroundColor White
Write-Host "2. Verificar configuração" -ForegroundColor White
Write-Host "3. Sair" -ForegroundColor White

$choice = Read-Host "`nEscolha uma opção (1-3)"

switch ($choice) {
    "1" { 
        Write-Host "Executando OpenClaude..." -ForegroundColor Green
        openclaude
    }
    "2" { 
        Write-Host "Verificando configuração..." -ForegroundColor Green
        . .\verify_config.ps1
    }
    "3" { 
        Write-Host "Saindo..." -ForegroundColor Yellow
        exit
    }
    default { 
        Write-Host "Opção inválida." -ForegroundColor Red
    }
}

Write-Host "`nPressione Enter para continuar..."
Read-Host
