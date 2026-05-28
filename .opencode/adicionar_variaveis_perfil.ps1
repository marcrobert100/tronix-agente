# Script PowerShell para adicionar variáveis de ambiente ao perfil do PowerShell
# Execute este script como administrador

Write-Host "Adicionando variáveis de ambiente ao perfil do PowerShell..." -ForegroundColor Green

# Verificar se o perfil existe, se não, criar
if (!(Test-Path $PROFILE)) {
    Write-Host "Criando perfil do PowerShell..." -ForegroundColor Yellow
    New-Item -ItemType File -Path $PROFILE -Force
}

# Ler o conteúdo atual do perfil
$profileContent = Get-Content $PROFILE -Raw

# Verificar se as variáveis já existem no perfil
$variablesToAdd = @(
    '$env:CLAUDE_CODE_USE_OPENAI = "1"',
    '$env:OPENAI_API_KEY = "sk-s8qqh1bphw41tx7sdpgb2cg8nsrcrf2b6ie6ziqa2ivloi3v"',
    '$env:OPENAI_BASE_URL = "https://api.mimo.ai/v1"',
    '$env:OPENAI_MODEL = "mimo-v2-flash"'
)

foreach ($var in $variablesToAdd) {
    if ($profileContent -notmatch [regex]::Escape($var)) {
        Write-Host "Adicionando: $var" -ForegroundColor Yellow
        Add-Content -Path $PROFILE -Value $var
    } else {
        Write-Host "Já existe no perfil: $var" -ForegroundColor Green
    }
}

Write-Host "`nVariáveis de ambiente adicionadas ao perfil do PowerShell!" -ForegroundColor Green
Write-Host "Arquivo de perfil: $PROFILE" -ForegroundColor Cyan
Write-Host "`nPara aplicar as mudanças, execute:" -ForegroundColor Yellow
Write-Host "  . `$PROFILE" -ForegroundColor Cyan
Write-Host "Ou abra um novo terminal do PowerShell." -ForegroundColor Cyan
