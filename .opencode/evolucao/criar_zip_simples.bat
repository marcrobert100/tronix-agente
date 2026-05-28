@echo off
chcp 65001 > nul
title Criador de ZIP Simples
echo Criando ZIP do Delivery Bot...

set "TEMP_DIR=%TEMP%\bot_temp"
set "ZIP_FILE=%USERPROFILE%\Desktop\evolucao\delivery_bot.zip"

:: Criar pastas temporárias
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\bot"
mkdir "%TEMP_DIR%\bot\Scripts"

:: Criar package.json
echo { > "%TEMP_DIR%\bot\package.json"
echo   "name": "delivery-bot-whatsapp", >> "%TEMP_DIR%\bot\package.json"
echo   "version": "2.0.0", >> "%TEMP_DIR%\bot\package.json"
echo   "main": "server.js", >> "%TEMP_DIR%\bot\package.json"
echo   "dependencies": { >> "%TEMP_DIR%\bot\package.json"
echo     "express": "^4.18.2", >> "%TEMP_DIR%\bot\package.json"
echo     "whatsapp-web.js": "^1.24.0" >> "%TEMP_DIR%\bot\package.json"
echo   } >> "%TEMP_DIR%\bot\package.json"
echo } >> "%TEMP_DIR%\bot\package.json"

:: Criar INICIAR.bat
echo @echo off > "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo cd /d "%%~dp0.." >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"
echo node server.js >> "%TEMP_DIR%\bot\Scripts\INICIAR.bat"

:: Criar instalar_bot.bat
echo @echo off > "%TEMP_DIR%\instalar_bot.bat"
echo set "DESTINO=%%USERPROFILE%%\Desktop\DeliveryBot" >> "%TEMP_DIR%\instalar_bot.bat"
echo if exist "%%DESTINO%%" rmdir /s /q "%%DESTINO%%" >> "%TEMP_DIR%\instalar_bot.bat"
echo mkdir "%%DESTINO%%" >> "%TEMP_DIR%\instalar_bot.bat"
echo xcopy /E /Y /I "bot\*" "%%DESTINO%%\" >> "%TEMP_DIR%\instalar_bot.bat"
echo cd /d "%%DESTINO%%" >> "%TEMP_DIR%\instalar_bot.bat"
echo call npm install --production >> "%TEMP_DIR%\instalar_bot.bat"
echo echo Instalacao concluida! >> "%TEMP_DIR%\instalar_bot.bat"
echo pause >> "%TEMP_DIR%\instalar_bot.bat"

:: Criar ZIP usando PowerShell
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"

:: Limpar
rmdir /s /q "%TEMP_DIR%"

echo ZIP criado: %ZIP_FILE%
pause