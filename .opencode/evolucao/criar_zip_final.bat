@echo off
chcp 65001 > nul
title Criador de ZIP Final - Delivery Bot WhatsApp
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   📦 CRIADOR DE ZIP FINAL                                ║
echo ║   Delivery Bot WhatsApp - Evolucao                       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set "TEMP_DIR=%TEMP%\delivery_bot_instalador"
set "ZIP_FILE=%USERPROFILE%\Desktop\evolucao\delivery_bot_instalador.zip"

echo [1/4] Criando estrutura temporária...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\bot"
mkdir "%TEMP_DIR%\bot\Scripts"
echo ✓ Pastas criadas!

echo.
echo [2/4] Criando arquivos de instalação...

:: Criar package.json
echo { > "%TEMP_DIR%\bot\package.json"
echo   "name": "delivery-bot-whatsapp", >> "%TEMP_DIR%\bot\package.json"
echo   "version": "2.0.0", >> "%TEMP_DIR%\bot\package.json"
echo   "description": "Bot WhatsApp para Delivery e Atendimento", >> "%TEMP_DIR%\bot\package.json"
echo   "main": "server.js", >> "%TEMP_DIR%\bot\package.json"
echo   "scripts": { >> "%TEMP_DIR%\bot\package.json"
echo     "start": "node server.js" >> "%TEMP_DIR%\bot\package.json"
echo   }, >> "%TEMP_DIR%\bot\package.json"
echo   "dependencies": { >> "%TEMP_DIR%\bot\package.json"
echo     "express": "^4.18.2", >> "%TEMP_DIR%\bot\package.json"
echo     "whatsapp-web.js": "^1.24.0", >> "%TEMP_DIR%\bot\package.json"
echo     "qrcode": "^1.5.3", >> "%TEMP_DIR%\bot\package.json"
echo     "socket.io": "^4.7.2" >> "%TEMP_DIR%\bot\package.json"
echo   } >> "%TEMP_DIR%\bot\package.json"
echo } >> "%TEMP_DIR%\bot\package.json"

:: Criar INICIAR.bat
echo @echo off > "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo chcp 65001 ^> nul >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo title Delivery Bot WhatsApp >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo cd /d "%%~dp0.." >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo node server.js >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo pause >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"

:: Criar instalar_bot.bat
echo @echo off > "%TEMP_DIR%\instalar_bot.bat"
echo chcp 65001 ^> nul >> "%TEMP_DIR%\instalar_bot.bat"
echo title Instalador Delivery Bot WhatsApp >> "%TEMP_DIR%\instalar_bot.bat"
echo echo. >> "%TEMP_DIR%\instalar_bot.bat"
echo set "DESTINO=%%USERPROFILE%%\Desktop\DeliveryBot" >> "%TEMP_DIR%\instalar_bot.bat"
echo if exist "%%DESTINO%%" rmdir /s /q "%%DESTINO%%" >> "%TEMP_DIR%\instalar_bot.bat"
echo mkdir "%%DESTINO%%" >> "%TEMP_DIR%\instalar_bot.bat"
echo xcopy /E /Y /I "bot\*" "%%DESTINO%%\" >> "%TEMP_DIR%\instalar_bot.bat"
echo cd /d "%%DESTINO%%" >> "%TEMP_DIR%\instalar_bot.bat"
echo call npm install --production >> "%TEMP_DIR%\instalar_bot.bat"
echo echo. >> "%TEMP_DIR%\instalar_bot.bat"
echo echo ✅ Instalacao concluida! >> "%TEMP_DIR%\instalar_bot.bat"
echo echo. >> "%TEMP_DIR%\instalar_bot.bat"
echo echo Para iniciar: >> "%TEMP_DIR%\instalar_bot.bat"
echo echo   cd /d "%%DESTINO%%\Scripts" >> "%TEMP_DIR%\instalar_bot.bat"
echo echo   call INICIAR.bat >> "%TEMP_DIR%\instalar_bot.bat"
echo echo. >> "%TEMP_DIR%\instalar_bot.bat"
echo echo Acesse: http://localhost:3000 >> "%TEMP_DIR%\instalar_bot.bat"
echo echo Login: cliente / 123456 >> "%TEMP_DIR%\instalar_bot.bat"
echo echo. >> "%TEMP_DIR%\instalar_bot.bat"
echo pause >> "%TEMP_DIR%\instalar_bot.bat"

:: Criar README
echo # Delivery Bot WhatsApp > "%TEMP_DIR%\README.md"
echo. >> "%TEMP_DIR%\README.md"
echo ## Como Instalar >> "%TEMP_DIR%\README.md"
echo 1. Extraia o ZIP >> "%TEMP_DIR%\README.md"
echo 2. Execute instalar_bot.bat >> "%TEMP_DIR%\README.md"
echo 3. Aguarde conclusão >> "%TEMP_DIR%\README.md"
echo. >> "%TEMP_DIR%\README.md"
echo ## Acesso >> "%TEMP_DIR%\README.md"
echo - URL: http://localhost:3000 >> "%TEMP_DIR%\README.md"
echo - Login: cliente / 123456 >> "%TEMP_DIR%\README.md"

echo ✓ Arquivos criados!

echo.
echo [3/4] Criando arquivo ZIP...
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"
if %errorlevel% neq 0 (
    echo ✗ Falha ao criar ZIP.
    pause
    exit /b 1
)
echo ✓ ZIP criado!

echo.
echo [4/4] Limpando arquivos temporários...
rmdir /s /q "%TEMP_DIR%"
echo ✓ Concluído!

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   ✅ ZIP CRIADO COM SUCESSO!                             ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Arquivo: %ZIP_FILE%
echo.
echo Para usar em outra máquina:
echo   1. Copie o ZIP para a nova máquina
echo   2. Extraia o arquivo
echo   3. Execute instalar_bot.bat
echo.
pause