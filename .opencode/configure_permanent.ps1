# Script de Configuração Permanente do OpenClaude
# Configura variáveis de ambiente permanentemente no registro do Windows

Write-Host "Configurando OpenClaude permanentemente..." -ForegroundColor Green

# Função para configurar variável de ambiente permanente
function Set-EnvironmentVariablePermanent {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Scope = "User"  # "User" ou "Machine"
    )
    
    try {
        if ($Scope -eq "User") {
            [Environment]::SetEnvironmentVariable($Name, $Value, "User")
        } else {
            [Environment]::SetEnvironmentVariable($Name, $Value, "Machine")
        }
        Write-Host "Variável $Name configurada permanentemente." -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Erro ao configurar ${Name}: $($_)" -ForegroundColor Red
        return $false
    }
}

# Configurar variáveis de ambiente
Write-Host "`nConfigurando variáveis de ambiente..." -ForegroundColor Yellow

# API Keys (substitua com suas chaves reais)
Set-EnvironmentVariablePermanent -Name "NVIDIA_API_KEY" -Value "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" -Scope "User"
Set-EnvironmentVariablePermanent -Name "OPENAI_API_KEY" -Value "sua-chave-openai-aqui" -Scope "User"
Set-EnvironmentVariablePermanent -Name "ANTHROPIC_API_KEY" -Value "sua-chave-anthropic-aqui" -Scope "User"

# Diretórios de trabalho
Set-EnvironmentVariablePermanent -Name "WORKSPACE_ROOT" -Value "C:\xampp\htdocs\agente" -Scope "User"
Set-EnvironmentVariablePermanent -Name "OPENCODE_DIR" -Value "C:\xampp\htdocs\agente\.opencode" -Scope "User"

# Atualizar variáveis de ambiente atual
$env:NVIDIA_API_KEY = "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"
$env:WORKSPACE_ROOT = "C:\xampp\htdocs\agente"
$env:OPENCODE_DIR = "C:\xampp\htdocs\agente\.opencode"

Write-Host "`nConfiguração permanente concluída!" -ForegroundColor Green
Write-Host "Reinicie o PowerShell para aplicar as mudanças." -ForegroundColor Cyan
