@echo off
setlocal enabledelayedexpansion

title = Instalador - Delivery Bot
color 0a

echo ========================================
echo   INSTALADOR - DELIVERY BOT v6
echo ========================================
echo.

:: ========================================
:: 1. Verificar Node.js
:: ========================================
echo [1/5] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERRO: Node.js nao encontrado!
    echo.
    echo   Instale o Node.js primeiro:
    echo   https://nodejs.org (versao LTS)
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
echo   OK - Node.js !NODE_VER! instalado
echo.

:: ========================================
:: 2. Verificar npm
:: ========================================
echo [2/5] Verificando npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERRO: npm nao encontrado!
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VER=%%i
echo   OK - npm !NPM_VER! instalado
echo.

:: ========================================
:: 3. Instalar dependências
:: ========================================
echo [3/5] Instalando dependências...
echo   Isso pode levar alguns minutos...
echo.

if not exist "package.json" (
    echo   ERRO: package.json nao encontrado!
    echo   Execute este script na pasta do projeto.
    pause
    exit /b 1
)

call npm install
if %errorlevel% neq 0 (
    echo   ERRO ao instalar dependências!
    pause
    exit /b 1
)

echo.
echo   OK - Dependências instaladas
echo.

:: ========================================
:: 4. Verificar configuração
:: ========================================
echo [4/5] Verificando configuração...

if not exist "config.json" (
    echo   ATENCAO: config.json nao encontrado!
    echo   Criando config.json padrão...
    (
        echo {
        echo   "useAI": true,
        echo   "model": "llama-3.1-8b-instant",
        echo   "empresaNome": "Minha Delivery",
        echo   "empresaEndereco": "Rua, Número - Bairro",
        echo   "empresaTelefone": "8199999-9999",
        echo   "horarioFuncionamento": "Seg a Dom: 18h as 23h",
        echo   "taxaEntrega": "R$ 5,00",
        echo   "tempoEntrega": "30 a 50 minutos",
        echo   "pedidoMinimo": "R$ 20,00",
        echo   "pagamentos": "Dinheiro, Cartão, Pix",
        echo   "pixChave": "sua-chave-pix@email.com",
        echo   "groqApiKey": "SUA_CHAVE_AQUI"
        echo }
    ) > config.json
    echo   config.json criado!
)

echo.
echo   OK - Configuração verificada
echo.

:: ========================================
:: 5. Instruções finais
:: ========================================
echo [5/5] Preparando inicialização...
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo   PROXIMOS PASSOS:
echo   1. Edite o arquivo config.json
echo   2. Adicione sua chave Groq (gsk_...)
echo   3. Configure nome, endereço, telefone
echo   4. Execute: npm start
echo.
echo   Para conectar o WhatsApp:
echo   - Execute npm start
echo   - Escaneie o QR Code
echo.
echo ========================================
echo.
set /p INICIAR="Deseja iniciar o bot agora? (S/N): "
if /i "%INICIAR%"=="S" (
    echo.
    echo   Iniciando bot...
    echo   Para WhatsApp: escaneie o QR Code
    echo.
    call npm start
) else (
    echo.
    echo   OK! Execute "npm start" quando quiser.
    pause
)
