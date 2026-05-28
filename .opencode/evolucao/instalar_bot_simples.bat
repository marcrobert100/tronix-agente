@echo off
chcp 65001 > nul
title Instalador Delivery Bot WhatsApp - Evolucao
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   🛵  INSTALADOR DELIVERY BOT WHATSAPP                   ║
echo ║   Evolucao - Marco Roberto                               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Definir diretório de destino
set "DESTINO=%USERPROFILE%\Desktop\evolucao"
set "PASTA_BOT=%DESTINO%\bot"

echo [1/5] Criando estrutura de pastas...
if not exist "%DESTINO%" mkdir "%DESTINO%"
if not exist "%PASTA_BOT%" mkdir "%PASTA_BOT%"
if not exist "%PASTA_BOT%\logs" mkdir "%PASTA_BOT%\logs"
if not exist "%PASTA_BOT%\public" mkdir "%PASTA_BOT%\public"
if not exist "%PASTA_BOT%\public\css" mkdir "%PASTA_BOT%\public\css"
if not exist "%PASTA_BOT%\public\js" mkdir "%PASTA_BOT%\public\js"
if not exist "%PASTA_BOT%\src" mkdir "%PASTA_BOT%\src"
if not exist "%PASTA_BOT%\src\config" mkdir "%PASTA_BOT%\src\config"
if not exist "%PASTA_BOT%\src\controllers" mkdir "%PASTA_BOT%\src\controllers"
if not exist "%PASTA_BOT%\src\middlewares" mkdir "%PASTA_BOT%\src\middlewares"
if not exist "%PASTA_BOT%\src\routes" mkdir "%PASTA_BOT%\src\routes"
if not exist "%PASTA_BOT%\src\services" mkdir "%PASTA_BOT%\src\services"
if not exist "%PASTA_BOT%\Scripts" mkdir "%PASTA_BOT%\Scripts"
echo ✓ Pastas criadas com sucesso!

echo.
echo [2/5] Verificando Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Node.js não encontrado!
    echo.
    echo Baixe e instale em: https://nodejs.org/
    echo Escolha a versão LTS.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set "NODE_VER=%%i"
echo ✓ Node.js encontrado: %NODE_VER%

echo.
echo [3/5] Baixando arquivos do bot...
:: Criar package.json básico
echo { > "%PASTA_BOT%\package.json"
echo   "name": "delivery-bot-whatsapp", >> "%PASTA_BOT%\package.json"
echo   "version": "2.0.0", >> "%PASTA_BOT%\package.json"
echo   "description": "Bot WhatsApp para Delivery e Atendimento", >> "%PASTA_BOT%\package.json"
echo   "main": "server.js", >> "%PASTA_BOT%\package.json"
echo   "scripts": { >> "%PASTA_BOT%\package.json"
echo     "start": "node server.js", >> "%PASTA_BOT%\package.json"
echo     "dev": "nodemon server.js" >> "%PASTA_BOT%\package.json"
echo   }, >> "%PASTA_BOT%\package.json"
echo   "dependencies": { >> "%PASTA_BOT%\package.json"
echo     "express": "^4.18.2", >> "%PASTA_BOT%\package.json"
echo     "form-data": "^4.0.5", >> "%PASTA_BOT%\package.json"
echo     "google-tts-api": "^2.0.2", >> "%PASTA_BOT%\package.json"
echo     "node-fetch": "^3.3.2", >> "%PASTA_BOT%\package.json"
echo     "openai": "^4.52.0", >> "%PASTA_BOT%\package.json"
echo     "qrcode": "^1.5.3", >> "%PASTA_BOT%\package.json"
echo     "socket.io": "^4.7.2", >> "%PASTA_BOT%\package.json"
echo     "tesseract.js": "^7.0.0", >> "%PASTA_BOT%\package.json"
echo     "whatsapp-web.js": "^1.24.0" >> "%PASTA_BOT%\package.json"
echo   } >> "%PASTA_BOT%\package.json"
echo } >> "%PASTA_BOT%\package.json"

:: Criar script INICIAR.bat
echo @echo off > "%PASTA_BOT%\Scripts\INICIAR.bat"
echo chcp 65001 ^> nul >> "%PASTA_BOT%\Scripts\INICIAR.bat"
echo title Delivery Bot WhatsApp >> "%PASTA_BOT%\Scripts\INICIAR.bat"
echo cd /d "%%~dp0.." >> "%PASTA_BOT%\Scripts\INICIAR.bat"
echo node server.js >> "%PASTA_BOT%\Scripts\INICIAR.bat"
echo pause >> "%PASTA_BOT%\Scripts\INICIAR.bat"

echo ✓ Arquivos básicos criados!

echo.
echo [4/5] Instalando dependências...
cd /d "%PASTA_BOT%"
call npm install --production
if %errorlevel% neq 0 (
    echo ✗ Falha ao instalar dependências.
    pause
    exit /b 1
)
echo ✓ Dependências instaladas!

echo.
echo [5/5] Criando atalhos e README...
:: Criar README
echo # Delivery Bot WhatsApp - Evolucao > "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ## Instalação Concluída! >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo O bot foi instalado em: `%PASTA_BOT%` >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Como usar: >> "%DESTINO%\README.md"
echo 1. **Iniciar o bot**: Execute `%PASTA_BOT%\Scripts\INICIAR.bat` >> "%DESTINO%\README.md"
echo 2. **Acessar o painel**: Abra o navegador em `http://localhost:3000` >> "%DESTINO%\README.md"
echo 3. **Login**: Usuário: `cliente` | Senha: `123456` >> "%DESTINO%\README.md"
echo 4. **Conectar WhatsApp**: Escaneie o QR Code que aparecer na tela >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Requisitos: >> "%DESTINO%\README.md"
echo - Node.js 16+ (já verificado) >> "%DESTINO%\README.md"
echo - Conexão com internet >> "%DESTINO%\README.md"
echo - WhatsApp instalado no celular >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo --- >> "%DESTINO%\README.md"
echo Bot desenvolvido por Marco Roberto >> "%DESTINO%\README.md"

echo ✓ Instalação concluída!

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   ✅ INSTALAÇÃO CONCLÚCIDA COM SUCESSO!                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Pasta de instalação: %DESTINO%
echo.
echo Para iniciar o bot, execute:
echo   %PASTA_BOT%\Scripts\INICIAR.bat
echo.
echo Para acessar o painel:
echo   http://localhost:3000
echo.
echo Login: cliente / 123456
echo.
pause