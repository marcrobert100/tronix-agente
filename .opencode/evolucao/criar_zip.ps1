# Script PowerShell para criar ZIP do Delivery Bot
$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   📦 CRIADOR DE ZIP - DELIVERY BOT WHATSAPP             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configurações
$TempDir = "$env:TEMP\delivery_bot_instalador"
$ZipFile = "$env:USERPROFILE\Desktop\evolucao\delivery_bot_instalador.zip"

# Limpar diretório temporário se existir
if (Test-Path $TempDir) {
    Remove-Item -Path $TempDir -Recurse -Force
}

# Criar estrutura de pastas
Write-Host "[1/4] Criando estrutura temporária..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$TempDir\bot" -Force | Out-Null
New-Item -ItemType Directory -Path "$TempDir\bot\Scripts" -Force | Out-Null
New-Item -ItemType Directory -Path "$TempDir\bot\logs" -Force | Out-Null
Write-Host "✓ Pastas criadas!" -ForegroundColor Green

# Criar package.json
Write-Host "[2/4] Criando arquivos de instalação..." -ForegroundColor Yellow
$packageJson = @'
{
  "name": "delivery-bot-whatsapp",
  "version": "2.0.0",
  "description": "Bot WhatsApp para Delivery e Atendimento - por Marco Roberto",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "form-data": "^4.0.5",
    "google-tts-api": "^2.0.2",
    "node-fetch": "^3.3.2",
    "openai": "^4.52.0",
    "qrcode": "^1.5.3",
    "socket.io": "^4.7.2",
    "tesseract.js": "^7.0.0",
    "whatsapp-web.js": "^1.24.0"
  }
}
'@
$packageJson | Out-File -FilePath "$TempDir\bot\package.json" -Encoding UTF8

# Criar INICIAR.bat
$iniciarBat = @'
@echo off
chcp 65001 > nul
title Delivery Bot WhatsApp - Marco Roberto
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   🛵  DELIVERY BOT WHATSAPP                             ║
echo ║   Desenvolvido por Marco Roberto                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
cd /d "%~dp0.."
echo Iniciando servidor...
echo Acesse: http://localhost:3000
echo.
node server.js
pause
'@
$iniciarBat | Out-File -FilePath "$TempDir\bot\Scripts\INICIAR.bat" -Encoding UTF8

# Criar instalar_bot.bat
$instalarBat = @'
@echo off
chcp 65001 > nul
title Instalador Delivery Bot WhatsApp
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   🛵  INSTALADOR DELIVERY BOT WHATSAPP                   ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
set "DESTINO=%USERPROFILE%\Desktop\DeliveryBot"
echo [1/4] Criando pasta de destino...
if exist "%DESTINO%" rmdir /s /q "%DESTINO%"
mkdir "%DESTINO%"
echo ✓ Pasta criada!
echo.
echo [2/4] Copiando arquivos do bot...
xcopy /E /Y /I "bot\*" "%DESTINO%\"
echo ✓ Arquivos copiados!
echo.
echo [3/4] Verificando Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Node.js não encontrado!
    echo Baixe em: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set "NODE_VER=%%i"
echo ✓ Node.js: %NODE_VER%
echo.
echo [4/4] Instalando dependências...
cd /d "%DESTINO%"
call npm install --production
if %errorlevel% neq 0 (
    echo ✗ Falha ao instalar dependências.
    pause
    exit /b 1
)
echo ✓ Dependências instaladas!
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║   ✅ INSTALAÇÃO CONCLÚCIDA!                              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Para iniciar o bot:
echo   cd /d "%DESTINO%\Scripts"
echo   call INICIAR.bat
echo.
echo Para acessar o painel:
echo   http://localhost:3000
echo.
echo Login: cliente / 123456
echo.
pause
'@
$instalarBat | Out-File -FilePath "$TempDir\instalar_bot.bat" -Encoding UTF8

# Criar README
$readme = @'
# Delivery Bot WhatsApp - Instalador Completo

## 📦 Instalador Standalone

Este instalador contém TODOS os recursos necessários para rodar o bot.

### Como Instalar
1. Extraia o arquivo ZIP
2. Execute `instalar_bot.bat`
3. Aguarde a instalação automática
4. Clique no atalho criado no desktop

### Dados de Acesso
- **Usuário:** cliente
- **Senha:** 123456
- **URL:** http://localhost:3000

### Requisitos
- Windows 10/11
- Node.js 16+ (será verificado automaticamente)
- Conexão com internet
- WhatsApp instalado no celular

---

Bot desenvolvido por Marco Roberto
'@
$readme | Out-File -FilePath "$TempDir\README.md" -Encoding UTF8

Write-Host "✓ Arquivos criados!" -ForegroundColor Green

# Criar ZIP
Write-Host "[3/4] Criando arquivo ZIP..." -ForegroundColor Yellow
Compress-Archive -Path "$TempDir\*" -DestinationPath $ZipFile -Force
Write-Host "✓ ZIP criado!" -ForegroundColor Green

# Limpar temporário
Write-Host "[4/4] Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item -Path $TempDir -Recurse -Force
Write-Host "✓ Concluído!" -ForegroundColor Green

# Mostrar resultado
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ ZIP CRIADO COM SUCESSO!                             ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivo: $ZipFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para usar em outra máquina:" -ForegroundColor White
Write-Host "  1. Copie o ZIP para a nova máquina" -ForegroundColor White
Write-Host "  2. Extraia o arquivo" -ForegroundColor White
Write-Host "  3. Execute instalar_bot.bat" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Enter para continuar..." -ForegroundColor Yellow
Read-Host