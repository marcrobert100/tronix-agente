@echo off
chcp 65001 >nul
title Hermes Agent Desktop - Instalação Completa

echo ========================================================
echo    Hermes Agent Desktop - Instalação Completa
echo    Senha padrão: 123
echo ========================================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCESSO] Executando como administrador
) else (
    echo [AVISO] Execute este script como Administrador
    echo Clique com o botão direito > "Executar como administrador"
    pause
    exit /b 1
)

echo.
echo [INFO] Instalando dependências necessárias...
echo.

REM 1. Instalar Node.js
echo [INFO] Verificando Node.js...
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Node.js não encontrado. Instalando...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile '%TEMP%\node-lts.msi'"
    msiexec /i "%TEMP%\node-lts.msi" /quiet /norestart
    echo [SUCESSO] Node.js instalado
) else (
    echo [SUCESSO] Node.js já está instalado
)

REM 2. Instalar Python
echo.
echo [INFO] Verificando Python...
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Python não encontrado. Instalando...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
    start /wait "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1
    echo [SUCESSO] Python instalado
) else (
    echo [SUCESSO] Python já está instalado
)

REM 3. Instalar Git
echo.
echo [INFO] Verificando Git...
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Git não encontrado. Instalando...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe' -OutFile '%TEMP%\git-installer.exe'"
    start /wait "%TEMP%\git-installer.exe" /VERYSILENT /NORESTART
    echo [SUCESSO] Git instalado
) else (
    echo [SUCESSO] Git já está instalado
)

REM 4. Instalar Hermes Agent Desktop
echo.
echo [INFO] Verificando Hermes Agent Desktop...
if not exist "%LOCALAPPDATA%\Programs\hermes-desktop\hermes-agent.exe" (
    echo [INFO] Hermes Agent Desktop não encontrado. Instalando...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/fathah/hermes-desktop/releases/download/v0.3.5/hermes-desktop-0.3.5-setup.exe' -OutFile '%TEMP%\hermes-desktop-setup.exe'"
    start /wait "%TEMP%\hermes-desktop-setup.exe"
    echo [SUCESSO] Hermes Agent Desktop instalado
) else (
    echo [SUCESSO] Hermes Agent Desktop já está instalado
)

REM 5. Criar diretório de configuração
echo.
echo [INFO] Configurando Hermes...
if not exist "%USERPROFILE%\.hermes" mkdir "%USERPROFILE%\.hermes"

REM Criar config.yaml
echo # Hermes Agent Configuration > "%USERPROFILE%\.hermes\config.yaml"
echo # Senha padrão: 123 >> "%USERPROFILE%\.hermes\config.yaml"
echo provider: openrouter >> "%USERPROFILE%\.hermes\config.yaml"
echo model: openrouter/auto >> "%USERPROFILE%\.hermes\config.yaml"
echo. >> "%USERPROFILE%\.hermes\config.yaml"
echo # API Keys >> "%USERPROFILE%\.hermes\config.yaml"
echo OPENROUTER_API_KEY: "" >> "%USERPROFILE%\.hermes\config.yaml"
echo ANTHROPIC_API_KEY: "" >> "%USERPROFILE%\.hermes\config.yaml"
echo OPENAI_API_KEY: "" >> "%USERPROFILE%\.hermes\config.yaml"
echo. >> "%USERPROFILE%\.hermes\config.yaml"
echo # Security >> "%USERPROFILE%\.hermes\config.yaml"
echo password: "123" >> "%USERPROFILE%\.hermes\config.yaml"

REM Criar .env
echo # Hermes Environment Variables > "%USERPROFILE%\.hermes\.env"
echo # Senha padrão: 123 >> "%USERPROFILE%\.hermes\.env"
echo HERMES_PASSWORD=123 >> "%USERPROFILE%\.hermes\.env"

echo [SUCESSO] Configurações criadas

REM 6. Criar atalhos
echo.
echo [INFO] Criando atalhos...

REM Atalho no Desktop
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Hermes Agent.lnk'); $shortcut.TargetPath = '%LOCALAPPDATA%\Programs\hermes-desktop\hermes-agent.exe'; $shortcut.WorkingDirectory = '%LOCALAPPDATA%\Programs\hermes-desktop'; $shortcut.Save()"

echo [SUCESSO] Atalhos criados

REM 7. Instalar Hermes Agent CLI
echo.
echo [INFO] Instalando Hermes Agent CLI...
pip install hermes-agent --upgrade
echo [SUCESSO] Hermes Agent CLI instalado

REM 8. Finalização
echo.
echo ========================================================
echo    INSTALAÇÃO COMPLETA!
echo ========================================================
echo.
echo Hermes Agent Desktop instalado com sucesso!
echo.
echo Como usar:
echo 1. Clique no atalho "Hermes Agent" no Desktop
echo 2. Na primeira execução, siga o assistente de configuração
echo 3. Use a senha "123" quando solicitado
echo.
echo Configurações:
echo - Arquivos: %USERPROFILE%\.hermes
echo - Senha: 123
echo.
echo Pressione Enter para abrir o Hermes Agent...
pause >nul

REM Abrir Hermes Agent
start "" "%LOCALAPPDATA%\Programs\hermes-desktop\hermes-agent.exe"