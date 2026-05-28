@echo off
cd /d "%~dp0"
echo ============================================
echo  Iniciando Dify e RAGFlow via Docker (WSL2)
echo ============================================
echo.
echo  Isso pode levar varios minutos na primeira vez
echo  (download das imagens Docker).
echo.

echo [1/4] Iniciando Dify...
wsl sudo bash -c "cd /mnt/c/xampp/htdocs/agente/dify/docker && docker compose up -d"

echo [2/4] Iniciando RAGFlow...
wsl sudo bash -c "cd /mnt/c/xampp/htdocs/agente/ragflow/docker && docker compose up -d"

echo.
echo ============================================
echo  Servicos disponiveis em:
echo.
echo  Langflow:   http://localhost:7860
echo  Dify:       http://localhost:3000
echo  RAGFlow:    http://localhost:9380
echo  n8n:        http://localhost:5678
echo ============================================
echo.
echo  Para iniciar o Langflow:
echo    python -m langflow run --port 7860
echo.
pause
