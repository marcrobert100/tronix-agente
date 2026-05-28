@echo off
chcp 65001 > nul
title Criador de Instalador Standalone - Delivery Bot WhatsApp
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   📦 CRIADOR DE INSTALADOR STANDALONE                    ║
echo ║   Delivery Bot WhatsApp - Evolucao                       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Definir diretórios
set "DESTINO=%USERPROFILE%\Desktop\evolucao\instalador_standalone"
set "ZIP_FILE=%USERPROFILE%\Desktop\evolucao\delivery_bot_standalone.zip"

echo [1/6] Criando estrutura de pastas...
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
echo ✓ Pastas criadas!

echo.
echo [2/6] Criando package.json...
echo { > "%DESTINO%\bot\package.json"
echo   "name": "delivery-bot-whatsapp", >> "%DESTINO%\bot\package.json"
echo   "version": "2.0.0", >> "%DESTINO%\bot\package.json"
echo   "description": "Bot WhatsApp para Delivery e Atendimento - por Marco Roberto", >> "%DESTINO%\bot\package.json"
echo   "main": "server.js", >> "%DESTINO%\bot\package.json"
echo   "scripts": { >> "%DESTINO%\bot\package.json"
echo     "start": "node server.js", >> "%DESTINO%\bot\package.json"
echo     "dev": "nodemon server.js" >> "%DESTINO%\bot\package.json"
echo   }, >> "%DESTINO%\bot\package.json"
echo   "dependencies": { >> "%DESTINO%\bot\package.json"
echo     "express": "^4.18.2", >> "%DESTINO%\bot\package.json"
echo     "form-data": "^4.0.5", >> "%DESTINO%\bot\package.json"
echo     "google-tts-api": "^2.0.2", >> "%DESTINO%\bot\package.json"
echo     "node-fetch": "^3.3.2", >> "%DESTINO%\bot\package.json"
echo     "openai": "^4.52.0", >> "%DESTINO%\bot\package.json"
echo     "qrcode": "^1.5.3", >> "%DESTINO%\bot\package.json"
echo     "socket.io": "^4.7.2", >> "%DESTINO%\bot\package.json"
echo     "tesseract.js": "^7.0.0", >> "%DESTINO%\bot\package.json"
echo     "whatsapp-web.js": "^1.24.0" >> "%DESTINO%\bot\package.json"
echo   } >> "%DESTINO%\bot\package.json"
echo } >> "%DESTINO%\bot\package.json"
echo ✓ package.json criado!

echo.
echo [3/6] Criando scripts de instalação...
:: Script INICIAR.bat
echo @echo off > "%DESTINO%\bot\Scripts\INICIAR.bat"
echo chcp 65001 ^> nul >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo title Delivery Bot WhatsApp - Marco Roberto >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo. >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo ╔══════════════════════════════════════════════════════════╗ >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo ║   🛵  DELIVERY BOT WHATSAPP                             ║ >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo ║   Desenvolvido por Marco Roberto                        ║ >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo ╚══════════════════════════════════════════════════════════╝ >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo. >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo cd /d "%%~dp0.." >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo Iniciando servidor... >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo Acesse: http://localhost:3000 >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo echo. >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo node server.js >> "%DESTINO%\bot\Scripts\INICIAR.bat"
echo pause >> "%DESTINO%\bot\Scripts\INICIAR.bat"

:: Script instalar_bot.bat
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

echo ✓ Scripts criados!

echo.
echo [4/6] Criando README e documentação...
:: README principal
echo # Delivery Bot WhatsApp - Instalador Completo > "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ## 📦 Instalador Standalone >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo Este instalador contém TODOS os recursos necessários para rodar o bot. >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Como Instalar >> "%DESTINO%\README.md"
echo 1. Extraia o arquivo ZIP >> "%DESTINO%\README.md"
echo 2. Execute `instalar_bot.bat` >> "%DESTINO%\README.md"
echo 3. Aguarde a instalação automática >> "%DESTINO%\README.md"
echo 4. Clique no atalho criado no desktop >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Dados de Acesso >> "%DESTINO%\README.md"
echo - **Usuário:** cliente >> "%DESTINO%\README.md"
echo - **Senha:** 123456 >> "%DESTINO%\README.md"
echo - **URL:** http://localhost:3000 >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Requisitos >> "%DESTINO%\README.md"
echo - Windows 10/11 >> "%DESTINO%\README.md"
echo - Node.js 16+ (será verificado automaticamente) >> "%DESTINO%\README.md"
echo - Conexão com internet >> "%DESTINO%\README.md"
echo - WhatsApp instalado no celular >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo --- >> "%DESTINO%\README.md"
echo Bot desenvolvido por Marco Roberto >> "%DESTINO%\README.md"

:: Instruções rápidas
echo # Instruções Rápidas > "%DESTINO%\INSTRUCOES.txt"
echo. >> "%DESTINO%\INSTRUCOES.txt"
echo ╔══════════════════════════════════════════════════════════╗ >> "%DESTINO%\INSTRUCOES.txt"
echo ║   INSTALADOR DELIVERY BOT WHATSAPP - EVOLUCAO            ║ >> "%DESTINO%\INSTRUCOES.txt"
echo ╚══════════════════════════════════════════════════════════╝ >> "%DESTINO%\INSTRUCOES.txt"
echo. >> "%DESTINO%\INSTRUCOES.txt"
echo PASSO A PASSO: >> "%DESTINO%\INSTRUCOES.txt"
echo 1. Extraia o ZIP >> "%DESTINO%\INSTRUCOES.txt"
echo 2. Execute instalar_bot.bat >> "%DESTINO%\INSTRUCOES.txt"
echo 3. Aguarde conclusão >> "%DESTINO%\INSTRUCOES.txt"
echo 4. Acesse http://localhost:3000 >> "%DESTINO%\INSTRUCOES.txt"
echo. >> "%DESTINO%\INSTRUCOES.txt"
echo LOGIN: cliente / 123456 >> "%DESTINO%\INSTRUCOES.txt"
echo. >> "%DESTINO%\INSTRUCOES.txt"
echo Bot: %USERPROFILE%\Desktop\DeliveryBot >> "%DESTINO%\INSTRUCOES.txt"

echo ✓ Documentação criada!

echo.
echo [5/6] Criando atalhos...
:: Criar atalho para iniciar o bot
echo Set WshShell = CreateObject("WScript.Shell") > "%DESTINO%\bot\Scripts\criar_atalho.vbs"
echo strDesktop = WshShell.SpecialFolders("Desktop") >> "%DESTINO%\bot\Scripts\criar_atalho.vbs"
echo Set oShellLink = WshShell.CreateShortcut(strDesktop ^& "\Iniciar Delivery Bot.lnk") >> "%DESTINO%\bot\Scripts\criar_atalho.vbs"
echo oShellLink.TargetPath = "%USERPROFILE%\Desktop\DeliveryBot\Scripts\INICIAR.bat" >> "%DESTINO%\bot\Scripts\criar_atalho.vbs"
echo oShellLink.WorkingDirectory = "%USERPROFILE%\Desktop\DeliveryBot\Scripts" >> "%DESTINO%\bot\Scripts\criar_atalho.vbs"
echo oShellLink.Save >> "%DESTINO%\bot\Scripts\criar_atalho.vbs"
echo ✓ Atalhos criados!

echo.
echo [6/6] Criando arquivo ZIP...
powershell -Command "Compress-Archive -Path '%DESTINO%\*' -DestinationPath '%ZIP_FILE%' -Force"
if %errorlevel% neq 0 (
    echo ✗ Falha ao criar ZIP com PowerShell.
    echo Tentando método alternativo...
    where 7z >nul 2>&1
    if %errorlevel% equ 0 (
        7z a -tzip "%ZIP_FILE%" "%DESTINO%\*" -r
    ) else (
        echo ✗ Não foi possível criar o ZIP.
        pause
        exit /b 1
    )
)
echo ✓ Arquivo ZIP criado!

:: Limpar pasta temporária
rmdir /s /q "%DESTINO%"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   ✅ INSTALADOR STANDALONE CRIADO COM SUCESSO!           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Arquivo ZIP: %ZIP_FILE%
echo.
echo Este instalador contém:
echo   ✓ Estrutura de pastas completa
echo   ✓ Scripts de instalação automáticos
echo   ✓ Documentação completa
echo   ✓ Configuração pré-definida
echo.
echo Para usar em outra máquina:
echo   1. Copie o ZIP para a nova máquina
echo   2. Extraia o arquivo
echo   3. Execute instalar_bot.bat
echo.
echo O bot será instalado em: %USERPROFILE%\Desktop\DeliveryBot
echo.
pause