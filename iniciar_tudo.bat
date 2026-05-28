@echo off
title Tronix - Iniciando Infraestrutura
echo ========================================
echo      TRONIX - INICIAR SERVICOS
echo ========================================
echo.

echo [1/4] Iniciando Moto S3 (mock)...
start /B python -m moto.server -p 9090
timeout /t 3 /nobreak >nul

echo [2/4] Configurando bucket...
python -c "import boto3; c=boto3.client('s3', endpoint_url='http://localhost:9090', aws_access_key_id='x', aws_secret_access_key='x', region_name='us-east-1'); c.create_bucket(Bucket='tronix'); print('Bucket OK')"

echo [3/4] Iniciando NCA-ToolKit...
set API_KEY=tronix_key_2026
set LOCAL_STORAGE_PATH=C:\xampp\htdocs\agente\nca_temp
set S3_ENDPOINT_URL=http://localhost:9090
set S3_ACCESS_KEY=x
set S3_SECRET_KEY=x
set S3_BUCKET_NAME=tronix
set S3_REGION=us-east-1
start /B python C:\xampp\htdocs\agente\nca-toolkit\app.py
timeout /t 5 /nobreak >nul

echo [4/4] Verificando...
python -c "import requests; r=requests.get('http://localhost:8080/v1/toolkit/test', headers={'X-API-Key':'tronix_key_2026'}, timeout=10); print('NCA:', r.status_code)"

echo.
echo ========================================
echo      PRONTO!
echo ========================================
echo.
echo MinIO:  http://localhost:9090
echo NCA:    http://localhost:8080
echo Galeria: http://localhost/agente/
echo.
echo Para parar: taskkill /f /im python.exe
echo ========================================
pause
