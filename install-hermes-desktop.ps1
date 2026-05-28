# Hermes Agent Desktop - Instalação Completa com Dependências
# Script para Windows PowerShell
# Senha padrão: 123 (quando solicitado)

# Configurações
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Funções auxiliares
function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $colors = @{
        "Info"    = "Cyan"
        "Success" = "Green"
        "Warning" = "Yellow"
        "Error"   = "Red"
    }
    Write-Host "[$Type] $Message" -ForegroundColor $colors[$Type]
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Início da instalação
Write-Status "Iniciando instalação do Hermes Agent Desktop..." "Info"
Write-Status "Senha padrão: 123 (quando solicitado)" "Warning"

# 1. Verificar e instalar Node.js
Write-Status "Verificando Node.js..." "Info"
if (-not (Test-Command "node")) {
    Write-Status "Node.js não encontrado. Instalando..." "Warning"
    
    # Download do Node.js LTS
    $nodeInstaller = "$env:TEMP\node-lts.msi"
    Invoke-WebRequest -Uri "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi" -OutFile $nodeInstaller
    
    # Instalar Node.js silenciosamente
    Start-Process msiexec.exe -ArgumentList "/i `"$nodeInstaller`" /quiet /norestart" -Wait
    
    # Atualizar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Status "Node.js instalado com sucesso!" "Success"
} else {
    Write-Status "Node.js já está instalado: $(node --version)" "Success"
}

# 2. Verificar e instalar Python
Write-Status "Verificando Python..." "Info"
if (-not (Test-Command "python")) {
    Write-Status "Python não encontrado. Instalando..." "Warning"
    
    # Download do Python
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe" -OutFile $pythonInstaller
    
    # Instalar Python silenciosamente
    Start-Process $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    
    # Atualizar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Status "Python instalado com sucesso!" "Success"
} else {
    Write-Status "Python já está instalado: $(python --version)" "Success"
}

# 3. Verificar e instalar Git
Write-Status "Verificando Git..." "Info"
if (-not (Test-Command "git")) {
    Write-Status "Git não encontrado. Instalando..." "Warning"
    
    # Download do Git
    $gitInstaller = "$env:TEMP\git-installer.exe"
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" -OutFile $gitInstaller
    
    # Instalar Git silenciosamente
    Start-Process $gitInstaller -ArgumentList "/VERYSILENT /NORESTART" -Wait
    
    # Atualizar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Status "Git instalado com sucesso!" "Success"
} else {
    Write-Status "Git já está instalado: $(git --version)" "Success"
}

# 4. Verificar e instalar Hermes Agent Desktop
Write-Status "Verificando Hermes Agent Desktop..." "Info"
$hermesPath = "$env:LOCALAPPDATA\Programs\hermes-desktop\hermes-agent.exe"
if (-not (Test-Path $hermesPath)) {
    Write-Status "Hermes Agent Desktop não encontrado. Instalando..." "Warning"
    
    # Download do instalador
    $hermesInstaller = "$env:TEMP\hermes-desktop-setup.exe"
    Invoke-WebRequest -Uri "https://github.com/fathah/hermes-desktop/releases/download/v0.3.5/hermes-desktop-0.3.5-setup.exe" -OutFile $hermesInstaller
    
    # Executar instalador
    Write-Status "Executando instalador do Hermes Desktop..." "Info"
    Start-Process $hermesInstaller -Wait
    
    # Aguardar instalação
    Start-Sleep -Seconds 5
    
    Write-Status "Hermes Agent Desktop instalado com sucesso!" "Success"
} else {
    Write-Status "Hermes Agent Desktop já está instalado!" "Success"
}

# 5. Configurar dependências do Hermes
Write-Status "Configurando dependências do Hermes..." "Info"

# Criar diretório de configuração
$hermesConfigDir = "$env:USERPROFILE\.hermes"
if (-not (Test-Path $hermesConfigDir)) {
    New-Item -ItemType Directory -Path $hermesConfigDir -Force | Out-Null
}

# Criar arquivo de configuração básico
$configContent = @"
# Hermes Agent Configuration
# Senha padrão: 123

provider: openrouter
model: openrouter/auto

# API Keys (preencha com suas chaves)
OPENROUTER_API_KEY: ""
ANTHROPIC_API_KEY: ""
OPENAI_API_KEY: ""
GOOGLE_API_KEY: ""
XAI_API_KEY: ""

# Local providers
OLLAMA_BASE_URL: "http://localhost:11434"
LM_STUDIO_BASE_URL: "http://localhost:1234"

# Features
enable_tools: true
enable_memory: true
enable_scheduling: true
enable_gateways: true

# Security
password: "123"
"@

Set-Content -Path "$hermesConfigDir\config.yaml" -Value $configContent

# Criar arquivo .env
$envContent = @"
# Hermes Environment Variables
# Senha padrão: 123

# Provider API Keys
OPENROUTER_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
XAI_API_KEY=

# Local Provider URLs
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234

# Security
HERMES_PASSWORD=123

# Features
ENABLE_TOOLS=true
ENABLE_MEMORY=true
ENABLE_SCHEDULING=true
ENABLE_GATEWAYS=true
"@

Set-Content -Path "$hermesConfigDir\.env" -Value $envContent

Write-Status "Configurações criadas em: $hermesConfigDir" "Success"

# 6. Criar atalhos
Write-Status "Criando atalhos..." "Info"

# Atalho no Desktop
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Hermes Agent.lnk"
$targetPath = "$env:LOCALAPPDATA\Programs\hermes-desktop\hermes-agent.exe"

$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = Split-Path $targetPath
$shortcut.IconLocation = "$targetPath,0"
$shortcut.Save()

Write-Status "Atalho criado no Desktop" "Success"

# 7. Instalar dependências do Hermes Agent CLI
Write-Status "Instalando dependências do Hermes Agent CLI..." "Info"

# Instalar Hermes Agent via pip
try {
    pip install hermes-agent --upgrade
    Write-Status "Hermes Agent CLI instalado com sucesso!" "Success"
}
catch {
    Write-Status "Erro ao instalar Hermes Agent CLI: $_" "Error"
}

# 8. Verificar instalação final
Write-Status "Verificando instalação..." "Info"

$checks = @(
    @{Name = "Node.js"; Command = "node --version"},
    @{Name = "Python"; Command = "python --version"},
    @{Name = "Git"; Command = "git --version"},
    @{Name = "Hermes Desktop"; Path = $hermesPath}
)

foreach ($check in $checks) {
    if ($check.ContainsKey("Command")) {
        if (Test-Command $check.Command.Split(" ")[0]) {
            Write-Status "$($check.Name): OK" "Success"
        } else {
            Write-Status "$($check.Name): FALHOU" "Error"
        }
    } else {
        if (Test-Path $check.Path) {
            Write-Status "$($check.Name): OK" "Success"
        } else {
            Write-Status "$($check.Name): FALHOU" "Error"
        }
    }
}

# 9. Instruções finais
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "INSTALAÇÃO COMPLETA!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Hermes Agent Desktop instalado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Como usar:" -ForegroundColor Yellow
Write-Host "1. Clique no atalho 'Hermes Agent' no Desktop" -ForegroundColor White
Write-Host "2. Na primeira execução, siga o assistente de configuração" -ForegroundColor White
Write-Host "3. Use a senha '123' quando solicitado" -ForegroundColor White
Write-Host ""
Write-Host "Configurações:" -ForegroundColor Yellow
Write-Host "- Arquivos de configuração: $hermesConfigDir" -ForegroundColor White
Write-Host "- Senha padrão: 123" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar manualmente:" -ForegroundColor Yellow
Write-Host "Start-Process '$targetPath'" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Enter para abrir o Hermes Agent..." -ForegroundColor Cyan
Read-Host

# Abrir o Hermes Agent
Start-Process $targetPath