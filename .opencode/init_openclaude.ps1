# Inicialização do OpenClaude
# Execute este script no seu perfil do PowerShell ou manualmente

# Carregar variáveis de ambiente do registro
$env:NVIDIA_API_KEY = [Environment]::GetEnvironmentVariable("NVIDIA_API_KEY", "User")
$env:OPENAI_API_KEY = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
$env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
$env:WORKSPACE_ROOT = [Environment]::GetEnvironmentVariable("WORKSPACE_ROOT", "User")
$env:OPENCODE_DIR = [Environment]::GetEnvironmentVariable("OPENCODE_DIR", "User")

# Criar aliases
function global:oc { openclaude $args }
function global:openclaude-config { & "C:\xampp\htdocs\agente\.opencode\configure_openclaude.ps1" }
function global:openclaude-verify { & "C:\xampp\htdocs\agente\.opencode\verify_config.ps1" }

# Navegar para o diretório de trabalho ao iniciar
if ($env:WORKSPACE_ROOT -and (Test-Path $env:WORKSPACE_ROOT)) {
    Set-Location $env:WORKSPACE_ROOT
}

Write-Host "OpenClaude inicializado!" -ForegroundColor Green
Write-Host "Use 'oc' para executar o OpenClaude." -ForegroundColor Cyan
