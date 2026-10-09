@echo off
REM SAMSUNG FRP via navegador - sem instalacao. Patch de seguranca antes de Ago/2022.
REM Requer driver USB Samsung instalado.
setlocal
set BASE=%~dp0
start "" "%BASE%frp\samsung-frp-web\index.html"
echo.
echo  Samsung FRP (web) aberto no navegador padrao.
echo  Passos: discador - Emergency Dialer - #0# - Conectar - WebSerial - botoes em ordem - WebUSB - botoes - Reboot
echo.
pause
