# Script para iniciar o servidor de estudos
Write-Host "Iniciando Servidor de Estudos..." -ForegroundColor Green

# Navegar para a pasta
Set-Location -Path "C:\xampp\htdocs\agente\estudo"

# Verificar se o Python está instalado
try {
    $pythonVersion = python --version
    Write-Host "Python detectado: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Python não encontrado. Instale o Python ou use o XAMPP." -ForegroundColor Red
    pause
    exit
}

# Iniciar servidor Python
Write-Host "Servidor iniciado em: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

# Abrir o navegador automaticamente
Start-Process "http://localhost:8000"

# Iniciar servidor
python -m http.server 8000