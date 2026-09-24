# Kali NetHunter - Script de Instalação
# Rodar APÓS habilitar virtualização no BIOS
# PowerShell como Admin

Write-Host "=== KALI NETHUNTER INSTALLER ===" -ForegroundColor Cyan
Write-Host ""

# 1. Habilitar Hyper-V e WSL
Write-Host "[1/6] Habilitando Hyper-V..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart

Write-Host "[2/6] Habilitando Windows Subsystem for Linux..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 2. Atualizar WSL kernel
Write-Host "[3/6] Atualizando WSL..." -ForegroundColor Yellow
wsl --update

# 3. Instalar Kali Linux
Write-Host "[4/6] Instalando Kali Linux Rolling..." -ForegroundColor Yellow
wsl --install -d kali-linux

Write-Host ""
Write-Host "Agora crie seu usuario/senha do Kali quando pedido." -ForegroundColor Green
Write-Host "Depois rode este comando dentro do WSL (bash kali):" -ForegroundColor Green
Write-Host '  curl -s https://raw.githubusercontent.com/WinKex/setup/master/setup.sh | bash' -ForegroundColor White
Write-Host ""
