@echo off
chcp 65001 >nul
title Delivery Bot - Instalador
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     🚀 DELIVERY BOT - INSTALADOR AUTOMÁTICO               ║
echo ║     Bot WhatsApp para Delivery e Atendimento               ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Verificar se Node.js está instalado
echo [1/6] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Node.js não encontrado!
    echo.
    echo Por favor, instale o Node.js:
    echo 👉 https://nodejs.org/
    echo.
    echo Após instalar, execute este script novamente.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js encontrado: %NODE_VERSION%

:: Verificar se npm está instalado
echo.
echo [2/6] Verificando npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: npm não encontrado!
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo ✅ npm encontrado: %NPM_VERSION%

:: Criar estrutura de diretórios
echo.
echo [3/6] Criando estrutura de diretórios...
if not exist "logs" mkdir logs
if not exist "logs\tts" mkdir logs\tts
if not exist "public" mkdir public
if not exist "public\css" mkdir public\css
if not exist "public\js" mkdir public\js
if not exist "public\img" mkdir public\img
echo ✅ Diretórios criados

:: Instalar dependências
echo.
echo [4/6] Instalando dependências (pode demorar 1-2 minutos)...
call npm install --production
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO ao instalar dependências!
    echo Tente executar: npm install --production
    pause
    exit /b 1
)
echo ✅ Dependências instaladas

:: Criar arquivo .env se não existir
echo.
echo [5/6] Configurando ambiente...
if not exist ".env" (
    copy /y ".env.example" ".env" >nul 2>&1
    if exist ".env.example" (
        echo ✅ Arquivo .env criado a partir do exemplo
    ) else (
        echo # Configuração do Bot - Delivery > .env
        echo GROQ_API_KEY=sua_chave_aqui >> .env
        echo PORT=3000 >> .env
        echo EMPRESA_NOME=Minha Empresa >> .env
        echo EMPRESA_TELEFONE=5511999999999 >> .env
        echo ✅ Arquivo .env criado com valores padrão
    )
) else (
    echo ✅ Arquivo .env já existe
)

:: Criar config.json se não existir
if not exist "config.json" (
    if exist "config.example.json" (
        copy /y "config.example.json" "config.json" >nul 2>&1
        echo ✅ Arquivo config.json criado a partir do exemplo
    ) else (
        echo ✅ config.json será criado no primeiro acesso ao painel
    )
) else (
    echo ✅ Arquivo config.json já existe
)

:: Verificar Chromium para WhatsApp Web
echo.
echo [6/6] Verificando Chromium...
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    where chromium >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  Chromium/Chrome não encontrado no PATH
        echo    O WhatsApp Web pode precisar do Chrome instalado
        echo    Baixe em: https://www.google.com/chrome/
    ) else (
        echo ✅ Chromium encontrado
    )
) else (
    echo ✅ Chrome encontrado
)

:: Finalizar
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║     ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!                  ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 PRÓXIMOS PASSOS:
echo.
echo    1. Edite o arquivo .env com suas configurações:
echo       - GROQ_API_KEY (obtenha em console.groq.com)
echo       - EMPRESA_NOME
echo       - EMPRESA_TELEFONE
echo.
echo    2. Inicie o bot:
echo       INICIAR.bat
echo.
echo    3. Acesse o painel:
echo       http://localhost:3000
echo.
echo    4. Configure o cardápio no painel
echo.
echo    5. Escaneie o QR Code do WhatsApp
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
