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

echo [1/6] Criando estrutura de pastas...
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
echo [2/6] Verificando Node.js...
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
echo [3/6] Copiando arquivos do bot...
xcopy /E /Y /I "C:\xampp\htdocs\agente\.opencode\casa\*" "%PASTA_BOT%\"
echo ✓ Arquivos copiados!

echo.
echo [4/6] Instalando dependências...
cd /d "%PASTA_BOT%"
call npm install --production
if %errorlevel% neq 0 (
    echo ✗ Falha ao instalar dependências.
    pause
    exit /b 1
)
echo ✓ Dependências instaladas!

echo.
echo [5/6] Criando atalhos...
:: Criar atalho para iniciar o bot
echo Set WshShell = CreateObject("WScript.Shell") > "%DESTINO%\Iniciar Bot.lnk"
echo strDesktop = WshShell.SpecialFolders("Desktop") >> "%DESTINO%\Iniciar Bot.lnk"
echo Set oShellLink = WshShell.CreateShortcut(strDesktop ^& "\evolucao\Iniciar Bot.lnk") >> "%DESTINO%\Iniciar Bot.lnk"
echo oShellLink.TargetPath = "%PASTA_BOT%\Scripts\INICIAR.bat" >> "%DESTINO%\Iniciar Bot.lnk"
echo oShellLink.WorkingDirectory = "%PASTA_BOT%\Scripts" >> "%DESTINO%\Iniciar Bot.lnk"
echo oShellLink.IconLocation = "%PASTA_BOT%\public\favicon.ico" >> "%DESTINO%\Iniciar Bot.lnk"
echo oShellLink.Save >> "%DESTINO%\Iniciar Bot.lnk"
echo ✓ Atalhos criados!

echo.
echo [6/6] Criando README de instruções...
echo # Delivery Bot WhatsApp - Evolucao > "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ## Instalação Concluída! >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo O bot foi instalado em: `%PASTA_BOT%` >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Como usar: >> "%DESTINO%\README.md"
echo 1. **Iniciar o bot**: Clique no atalho "Iniciar Bot" no desktop >> "%DESTINO%\README.md"
echo 2. **Acessar o painel**: Abra o navegador em `http://localhost:3000` >> "%DESTINO%\README.md"
echo 3. **Login**: Usuário: `cliente` | Senha: `123456` >> "%DESTINO%\README.md"
echo 4. **Conectar WhatsApp**: Escaneie o QR Code que aparecer na tela >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Arquivos importantes: >> "%DESTINO%\README.md"
echo - `%PASTA_BOT%\server.js` - Servidor principal >> "%DESTINO%\README.md"
echo - `%PASTA_BOT%\config.json` - Configurações do bot >> "%DESTINO%\README.md"
echo - `%PASTA_BOT%\logs\` - Logs e dados >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo ### Para atualizar: >> "%DESTINO%\README.md"
echo 1. Pare o bot (feche a janela do CMD) >> "%DESTINO%\README.md"
echo 2. Copie os novos arquivos para `%PASTA_BOT%` >> "%DESTINO%\README.md"
echo 3. Rode `npm install` na pasta do bot >> "%DESTINO%\README.md"
echo 4. Inicie novamente >> "%DESTINO%\README.md"
echo. >> "%DESTINO%\README.md"
echo --- >> "%DESTINO%\README.md"
echo Bot desenvolvido por Marco Roberto >> "%DESTINO%\README.md"

echo ✓ README criado!

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
echo Ou clique no atalho "Iniciar Bot" no desktop.
echo.
pause