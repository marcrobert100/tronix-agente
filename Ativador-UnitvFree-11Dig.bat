@echo off
chcp 65001 > nul
color 0A
cd /d C:\xampp\htdocs\agente

echo.
echo ===========================================
echo   TRONIX - SISTEMA DE LICENCIAMENTO 11 DÍGITOS
echo ===========================================
echo.
echo  [1] GERADOR - Criar chaves de 11 dígitos
echo  [2] VALIDADOR - Verificar chaves
echo  [3] SAIR
echo.
echo ===========================================
echo.

set /p opt=Escolha uma opção: 

if "%opt%"=="1" (
    start "" "C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\Python\Python312\python.exe" gerador_11dig_gui.py
    exit
)

if "%opt%"=="2" (
    start "" "C:\Users\CHCONTE RECPÇÃO\AppData\Local\Programs\Python\Python312\python.exe" validador_11dig.py
    exit
)

if "%opt%"=="3" (
    exit
)

echo Opção inválida!
pause
exit
