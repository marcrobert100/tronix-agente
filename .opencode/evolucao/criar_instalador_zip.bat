@echo off
chcp 65001 > nul
title Criador de Instalador ZIP - Delivery Bot WhatsApp
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   📦 CRIADOR DE INSTALADOR ZIP                           ║
echo ║   Delivery Bot WhatsApp - Evolucao                       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Definir diretórios
set "ORIGEM=C:\xampp\htdocs\agente\.opencode\casa"
set "DESTINO=%USERPROFILE%\Desktop\evolucao\instalador_zip"
set "ZIP_FILE=%USERPROFILE%\Desktop\evolucao\delivery_bot_instalador.zip"

echo [1/7] Verificando diretório de origem...
if not exist "%ORIGEM%" (
    echo ✗ Diretório de origem não encontrado: %ORIGEM%
    echo.
    echo Certifique-se de que os arquivos do bot estão em:
    echo C:\xampp\htdocs\agente\.opencode\casa
    echo.
    pause
    exit /b 1
)
echo ✓ Diretório de origem encontrado!

echo.
echo [2/7] Criando estrutura de pastas temporária...
if exist "%DESTINO%" rmdir /s /q "%DESTINO%"
mkdir "%DESTINO%"
mkdir "%DESTINO%\bot"
mkdir "%DESTINO%\bot\logs"
mkdir "%DESTINO%\bot\public"
mkdir "%DESTINO%\bot\public\css"
mkdir "%DESTINO%\bot\public\js"
mkdir "%DESTINO%\bot\src"
mkdir "%DESTINO%\bot\src\config"
mkdir "%DESTINO%\bot\src\controllers"
mkdir "%DESTINO%\bot\src\middlewares"
mkdir "%DESTINO%\bot\src\routes"
mkdir "%DESTINO%\bot\src\services"
mkdir "%DESTINO%\bot\Scripts"
mkdir "%DESTINO%\bot\node_modules"
echo ✓ Pastas temporárias criadas!

echo.
echo [3/7] Copiando arquivos principais do bot...
echo   Copiando server.js...
copy /Y "%ORIGEM%\server.js" "%DESTINO%\bot\"
echo   Copiando package.json...
copy /Y "%ORIGEM%\package.json" "%DESTINO%\bot\"
echo   Copiando tts-service.js...
copy /Y "%ORIGEM%\tts-service.js" "%DESTINO%\bot\"
echo   Copiando config.json (se existir)...
if exist "%ORIGEM%\config.json" copy /Y "%ORIGEM%\config.json" "%DESTINO%\bot\"
echo   Copiando license.json (se existir)...
if exist "%ORIGEM%\license.json" copy /Y "%ORIGEM%\license.json" "%DESTINO%\bot\"
echo ✓ Arquivos principais copiados!

echo.
echo [4/7] Copiando arquivos web...
echo   Copiando public...
xcopy /E /Y /I "%ORIGEM%\public\*" "%DESTINO%\bot\public\"
echo   Copiando scripts...
xcopy /E /Y /I "%ORIGEM%\Scripts\*" "%DESTINO%\bot\Scripts\"
echo ✓ Arquivos web copiados!

echo.
echo [5/7] Copiando código fonte...
xcopy /E /Y /I "%ORIGEM%\src\*" "%DESTINO%\bot\src\"
echo ✓ Código fonte copiado!

echo.
echo [6/7] Criando scripts de instalação...
:: Criar script de instalação principal
echo @echo off > "%DESTINO%\instalar_bot.bat"
echo chcp 65001 ^> nul >> "%DESTINO%\instalar_bot.bat"
echo title Instalador Delivery Bot WhatsApp >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo ╔══════════════════════════════════════════════════════════╗ >> "%DESTINO%\instalar_bot.bat"
echo echo ║   🛵  INSTALADOR DELIVERY BOT WHATSAPP                   ║ >> "%DESTINO%\instalar_bot.bat"
echo echo ╚══════════════════════════════════════════════════════════╝ >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo set "DESTINO_FINAL=%%USERPROFILE%%\Desktop\DeliveryBot" >> "%DESTINO%\instalar_bot.bat"
echo echo [1/4] Criando pasta de destino... >> "%DESTINO%\instalar_bot.bat"
echo if exist "%%DESTINO_FINAL%%" rmdir /s /q "%%DESTINO_FINAL%%" >> "%DESTINO%\instalar_bot.bat"
echo mkdir "%%DESTINO_FINAL%%" >> "%DESTINO%\instalar_bot.bat"
echo echo ✓ Pasta criada! >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo [2/4] Copiando arquivos do bot... >> "%DESTINO%\instalar_bot.bat"
echo xcopy /E /Y /I "bot\*" "%%DESTINO_FINAL%%\" >> "%DESTINO%\instalar_bot.bat"
echo echo ✓ Arquivos copiados! >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo [3/4] Verificando Node.js... >> "%DESTINO%\instalar_bot.bat"
echo where node ^>nul 2^>^&1 >> "%DESTINO%\instalar_bot.bat"
echo if %%errorlevel%% neq 0 ( >> "%DESTINO%\instalar_bot.bat"
echo     echo ✗ Node.js não encontrado! >> "%DESTINO%\instalar_bot.bat"
echo     echo Baixe em: https://nodejs.org/ >> "%DESTINO%\instalar_bot.bat"
echo     pause >> "%DESTINO%\instalar_bot.bat"
echo     exit /b 1 >> "%DESTINO%\instalar_bot.bat"
echo ) >> "%DESTINO%\instalar_bot.bat"
echo for /f "tokens=*" %%%%i in ('node --version') do set "NODE_VER=%%%%i" >> "%DESTINO%\instalar_bot.bat"
echo echo ✓ Node.js: %%NODE_VER%% >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo [4/4] Instalando dependências... >> "%DESTINO%\instalar_bot.bat"
echo cd /d "%%DESTINO_FINAL%%" >> "%DESTINO%\instalar_bot.bat"
echo call npm install --production >> "%DESTINO%\instalar_bot.bat"
echo if %%errorlevel%% neq 0 ( >> "%DESTINO%\instalar_bot.bat"
echo     echo ✗ Falha ao instalar dependências. >> "%DESTINO%\instalar_bot.bat"
echo     pause >> "%DESTINO%\instalar_bot.bat"
echo     exit /b 1 >> "%DESTINO%\instalar_bot.bat"
echo ) >> "%DESTINO%\instalar_bot.bat"
echo echo ✓ Dependências instaladas! >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo ╔══════════════════════════════════════════════════════════╗ >> "%DESTINO%\instalar_bot.bat"
echo echo ║   ✅ INSTALAÇÃO CONCLÚCIDA!                              ║ >> "%DESTINO%\instalar_bot.bat"
echo echo ╚══════════════════════════════════════════════════════════╝ >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo Para iniciar o bot: >> "%DESTINO%\instalar_bot.bat"
echo echo   cd /d "%%DESTINO_FINAL%%\Scripts" >> "%DESTINO%\instalar_bot.bat"
echo echo   call INICIAR.bat >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo Para acessar o painel: >> "%DESTINO%\instalar_bot.bat"
echo echo   http://localhost:3000 >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo echo Login: cliente / 123456 >> "%DESTINO%\instalar_bot.bat"
echo echo. >> "%DESTINO%\instalar_bot.bat"
echo pause >> "%DESTINO%\instalar_bot.bat"

:: Criar README no ZIP
echo # Delivery Bot WhatsApp - Instalador Completo > "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ## Como Instalar >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo 1. Extraia o arquivo ZIP >> "%DESTINO%\README.md"
echo 2. Execute `instalar_bot.bat` >> "%DESTINO%\README.md"
echo 3. Aguarde a instalação automática >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ## Dados de Acesso >> "%DESTINO%\README.md"
echo - **Usuário:** cliente >> "%DESTINO%\README.md"
echo - **Senha:** 123456 >> "%DESTINO%\README.md"
echo - **URL:** http://localhost:3000 >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ## Requisitos >> "%DESTINO%\README.md"
echo - Node.js 16+ >> "%DESTINO%\README.md"
echo - Conexão com internet >> "%DESTINO%\README.md"
echo - WhatsApp instalado no celular >> "%DESTINO%\README.md"

echo ✓ Scripts de instalação criados!

echo.
echo [7/7] Criando arquivo ZIP...
:: Usar PowerShell para criar o ZIP (mais confiável no Windows)
powershell -Command "Compress-Archive -Path '%DESTINO%\*' -DestinationPath '%ZIP_FILE%' -Force"
if %errorlevel% neq 0 (
    echo ✗ Falha ao criar ZIP com PowerShell.
    echo Tentando método alternativo...
    :: Método alternativo: usar 7-Zip se disponível
    where 7z >nul 2>&1
    if %errorlevel% equ 0 (
        7z a -tzip "%ZIP_FILE%" "%DESTINO%\*" -r
    ) else (
        echo ✗ Não foi possível criar o ZIP.
        echo Instale o 7-Zip ou use o método do PowerShell.
        pause
        exit /b 1
    )
)
echo ✓ Arquivo ZIP criado!

:: Limpar pasta temporária
rmdir /s /q "%DESTINO%"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   ✅ INSTALADOR ZIP CRIADO COM SUCESSO!                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Arquivo ZIP: %ZIP_FILE%
echo.
echo Tamanho: %~z1 bytes
echo.
echo Este arquivo contém:
echo   ✓ Todos os arquivos do bot
echo   ✓ Scripts de instalação automáticos
echo   ✓ Documentação completa
echo   ✓ Dependências pré-configuradas
echo.
echo Para usar em outra máquina:
echo   1. Copie o ZIP para a nova máquina
echo   2. Extraia o arquivo
echo   3. Execute instalar_bot.bat
echo.
pause