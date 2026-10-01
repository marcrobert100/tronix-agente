@echo off
REM AppDrop Bridge — instala no iPad o que o AppDrop nao consegue instalar
title AppDrop Bridge
cd /d "%~dp0"

echo.
echo   === AppDrop Bridge ===
echo.
echo    1) Instalar o que ja falhou no AppDrop
echo    2) Ver os erros do AppDrop
echo    3) Buscar app no catalogo
echo    4) Buscar e instalar pelo nome
echo    5) Instalar uma URL de IPA direto
echo    6) Historico do que foi instalado
echo    7) Monitorar em background (Ctrl+C sai)
echo    8) Baixar catalogo do iPad
echo    0) Sair
echo.
set /p op="  Opcao: "

if "%op%"=="1" python appdrop_bridge.py --pendentes
if "%op%"=="2" python appdrop_bridge.py --listar
if "%op%"=="3" set /p t="Nome do app: " & python appdrop_bridge.py --buscar "%t%"
if "%op%"=="4" set /p t="Nome do app: " & python appdrop_bridge.py --instalar-nome "%t%"
if "%op%"=="5" set /p u="URL do IPA: " & python appdrop_bridge.py --instalar "%u%"
if "%op%"=="6" python appdrop_bridge.py --historico
if "%op%"=="7" python appdrop_bridge.py --monitorar
if "%op%"=="8" python appdrop_bridge.py --puxar-catalogo

echo.
pause