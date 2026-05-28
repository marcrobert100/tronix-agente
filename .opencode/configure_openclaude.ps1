# Script de Configuração do OpenClaude para PowerShell
# Execute este script com: .\configure_openclaude.ps1

Write-Host "Configurando OpenClaude..." -ForegroundColor Green

# 1. Verificar se o OpenClaude está instalado
try {
    $openclaudePath = Get-Command openclaude -ErrorAction Stop | Select-Object -ExpandProperty Source
    Write-Host "OpenClaude encontrado em: $openclaudePath" -ForegroundColor Cyan
} catch {
    Write-Host "OpenClaude não encontrado. Instale com: pip install openclaude" -ForegroundColor Red
    exit 1
}

# 2. Configurar variáveis de ambiente
Write-Host "`nConfigurando variáveis de ambiente..." -ForegroundColor Yellow

# API Keys (substitua com suas chaves reais)
$env:NVIDIA_API_KEY = "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"
$env:OPENAI_API_KEY = "sua-chave-openai-aqui"
$env:ANTHROPIC_API_KEY = "sua-chave-anthropic-aqui"

# Diretórios de trabalho
$env:WORKSPACE_ROOT = "C:\xampp\htdocs\agente"
$env:OPENCODE_DIR = "C:\xampp\htdocs\agente\.opencode"

# 3. Criar alias úteis
Write-Host "`nCriando aliases..." -ForegroundColor Yellow

# Alias para o OpenClaude
function global:oc { openclaude $args }
function global:openclaude-config { & "C:\xampp\htdocs\agente\.opencode\configure_openclaude.ps1" }

# 4. Configurar o perfil do PowerShell
$profileContent = @'
# OpenClaude Configuration
$env:NVIDIA_API_KEY = "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"
$env:WORKSPACE_ROOT = "C:\xampp\htdocs\agente"
$env:OPENCODE_DIR = "C:\xampp\htdocs\agente\.opencode"

# Aliases
function global:oc { openclaude $args }
function global:openclaude-config { & "C:\xampp\htdocs\agente\.opencode\configure_openclaude.ps1" }
'@

# Adicionar ao perfil se não existir
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}

$currentProfile = Get-Content $PROFILE -Raw
if ($currentProfile -notmatch "OpenClaude Configuration") {
    Add-Content -Path $PROFILE -Value "`n$profileContent"
    Write-Host "Perfil do PowerShell atualizado." -ForegroundColor Green
} else {
    Write-Host "Perfil já contém configuração do OpenClaude." -ForegroundColor Cyan
}

# 5. Testar a configuração
Write-Host "`nTestando configuração..." -ForegroundColor Yellow
Write-Host "Variável NVIDIA_API_KEY: $($env:NVIDIA_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "Diretório de trabalho: $env:WORKSPACE_ROOT" -ForegroundColor Gray

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
Write-Host "Use 'oc' para executar o OpenClaude." -ForegroundColor Cyan
Write-Host "Use 'openclaude-config' para reconfigurar." -ForegroundColor Cyan
