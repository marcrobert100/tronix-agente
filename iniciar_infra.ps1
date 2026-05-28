Write-Host "=== TRONIX - INICIAR INFRAESTRUTURA ===" -ForegroundColor Cyan
Write-Host ""

# 1. Iniciar WSL + Docker + MinIO
Write-Host "[1/3] Iniciando WSL + Docker + MinIO..." -ForegroundColor Yellow
wsl -d Ubuntu -u root -e bash -c "dockerd &>/dev/null & sleep 3" 2>$null
wsl -d Ubuntu -u root -e bash -c "cd /mnt/c/xampp/htdocs/agente/nca-toolkit && docker compose -f docker-compose.minio.yml up -d" 2>$null
Start-Sleep -Seconds 5

# 2. Pegar IP do WSL e configurar porta
Write-Host "[2/3] Configurando rede..." -ForegroundColor Yellow
$wsl_ip = wsl -d Ubuntu -e hostname -I 2>$null
Write-Host "  WSL2 IP: $wsl_ip"

# 3. Iniciar NCA-ToolKit
Write-Host "[3/3] Iniciando NCA-ToolKit..." -ForegroundColor Yellow
$env:API_KEY="tronix_key_2026"
$env:LOCAL_STORAGE_PATH="C:\xampp\htdocs\agente\nca_temp"
$env:S3_ENDPOINT_URL="http://${wsl_ip}:9000"
$env:S3_ACCESS_KEY="tronix"
$env:S3_SECRET_KEY="tronix123!"
$env:S3_BUCKET_NAME="tronix"
$env:S3_REGION="None"

Start-Process -NoNewWindow -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "C:\xampp\htdocs\agente\nca-toolkit"
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "=== PRONTO ===" -ForegroundColor Green
Write-Host "MinIO Console: http://localhost:9001 (tronix / tronix123!)" -ForegroundColor Cyan
Write-Host "NCA Toolkit:   http://localhost:8080" -ForegroundColor Cyan
Write-Host "API Key:       tronix_key_2026" -ForegroundColor Cyan
