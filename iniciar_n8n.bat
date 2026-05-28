@echo off
cd /d "%~dp0"
echo ============================================
echo  Iniciando n8n - Tronix Workflow Engine
echo ============================================
echo.
echo n8n vai abrir em: http://localhost:5678
echo.
echo Para importar o workflow Tronix:
echo   Settings ^> Workflows ^> Import from File
echo   Selecione: n8n_workflow.json
echo.
echo Configure MySQL em: http://localhost:5678/admin/database
echo   Host: localhost
echo   Database: tronix_n8n (crie no PHPMyAdmin)
echo.
npx n8n start
pause
