@echo off
echo ==========================================
echo BUILD PORTARIA FACIAL - ANDROID APK
echo ==========================================

echo.
echo [1/4] Verificando WSL...
wsl --list --verbose | findstr "Ubuntu" >nul
if errorlevel 1 (
    echo ERRO: WSL Ubuntu nao encontrado. Instale: wsl --install -d Ubuntu
    pause
    exit /b 1
)

echo.
echo [2/4] Copiando projeto para WSL...
wsl mkdir -p /home/%USERNAME%/portaria_facial
wsl cp -r "%CD%"/* /home/%USERNAME%/portaria_facial/

echo.
echo [3/4] Instalando dependencias no WSL...
wsl bash -c "
    cd /home/%USERNAME%/portaria_facial &&
    sudo apt update &&
    sudo apt install -y python3-pip python3-venv build-essential libssl-dev libffi-dev python3-dev git zip unzip openjdk-17-jdk &&
    python3 -m venv venv &&
    source venv/bin/activate &&
    pip install --upgrade pip &&
    pip install buildozer cython &&
    pip install -r requirements.txt
"

echo.
echo [4/4] Buildando APK...
wsl bash -c "
    cd /home/%USERNAME%/portaria_facial &&
    source venv/bin/activate &&
    buildozer -v android debug
"

echo.
echo ==========================================
echo APK gerado em: bin/*.apk
echo Copiando para Windows...
copy /Y wsl$\Ubuntu\home\%USERNAME%\portaria_facial\bin\*.apk .\ 2>nul
echo.
echo CONCLUIDO! Instale o APK no celular.
echo ==========================================
pause