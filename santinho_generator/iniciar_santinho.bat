@echo off
chcp 65001 >nul
echo ========================================
echo  TRONIX SANTINHO GENERATOR
echo  Equipe: DEV + MEDIA + SUPER + DB
echo ========================================
echo.

REM Detectar Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado no PATH
    pause
    exit /b 1
)

REM Instalar dependencias se necessario
python -c "import PIL" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Instalando Pillow...
    python -m pip install pillow reportlab --quiet
)

REM Inicializar banco
python santinho.py --init-db

REM Abrir interface no navegador
echo.
echo [OK] Abrindo interface...
echo [OK] URL: http://localhost/agente/santinho_generator/
start http://localhost/agente/santinho_generator/
start "" index.html

echo.
echo ========================================
echo  INTERFACE ABERTA NO NAVEGADOR
echo  Para gerar via CLI: python santinho.py --help
echo  Para lote: python gerar_lote.py --input exemplos_candidatos.json --quantidade 100
echo ========================================
pause
