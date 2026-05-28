<# 
.SYNOPSIS
    Configura o repositório GitHub do Tronix e prepara o ambiente de evolução.
.DESCRIPTION
    Este script automatiza a configuração do repositório GitHub para o
    sistema Tronix, incluindo init, commit inicial, remote e push.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$RepoName = "tronix",

    [Parameter(Mandatory = $false)]
    [string]$GithubUser = "",

    [Parameter(Mandatory = $false)]
    [switch]$Private = $true
)

$ROOT = Resolve-Path "$PSScriptRoot/.."
Set-Location $ROOT

Write-Host "🚀 Configurando Tronix para GitHub..." -ForegroundColor Cyan

# 1. Inicializar git se necessário
$gitDir = "$ROOT/.git"
if (-not (Test-Path $gitDir)) {
    Write-Host "📦 Inicializando git..." -ForegroundColor Yellow
    git init
    git checkout -b main
    Write-Host "   ✅ Git inicializado" -ForegroundColor Green
} else {
    Write-Host "   ✅ Git já inicializado" -ForegroundColor Green
}

# 2. Verificar .gitignore
if (Test-Path "$ROOT/.gitignore") {
    Write-Host "   ✅ .gitignore encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠️  .gitignore não encontrado. Criando..." -ForegroundColor Yellow
    # O .gitignore já foi criado pelo assistente
}

# 3. Primeiro commit
$status = git status --porcelain
if ($status) {
    Write-Host "📝 Criando commit inicial..." -ForegroundColor Yellow
    git add -A
    git commit -m "🎬 Tronix — Sistema Multi-Agente de Geração de Mídia

    🤖 CrewAI com 11 agentes
    🎨 Geração de imagens via Cloudflare SDXL
    🎥 Ken Burns + Edge-TTS + vídeos automáticos
    🌐 API Gateway FastAPI (porta 8081)
    ⚡ Workflows n8n automatizados
    📊 Dashboard interativo com monitoramento
    🚀 Auto-evolução via GitHub Actions"
    Write-Host "   ✅ Commit criado" -ForegroundColor Green
} else {
    Write-Host "   ✅ Nada a commitar (limpo)" -ForegroundColor Green
}

# 4. Configurar remote
Write-Host ""
Write-Host "📌 Para conectar ao GitHub, siga os passos abaixo:" -ForegroundColor Cyan
Write-Host ""

if ($GithubUser) {
    $remoteUrl = "https://github.com/$GithubUser/$RepoName.git"
    Write-Host "   git remote add origin $remoteUrl" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor White
} else {
    Write-Host "   1. Crie um repositório no GitHub:" -ForegroundColor White
    Write-Host "       https://github.com/new" -ForegroundColor Gray
    Write-Host "       Nome: $RepoName" -ForegroundColor White
    if ($Private) { Write-Host "       Visibilidade: Private" -ForegroundColor White }
    Write-Host ""
    Write-Host "   2. Conecte e faça push:" -ForegroundColor White
    Write-Host "       git remote add origin https://github.com/SEU_USUARIO/$RepoName.git" -ForegroundColor White
    Write-Host "       git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "3. Configure os Secrets no GitHub:" -ForegroundColor Yellow
Write-Host "   Settings → Secrets and variables → Actions" -ForegroundColor Gray
Write-Host "   Adicione:" -ForegroundColor Gray
Write-Host "   - CF_API_TOKEN" -ForegroundColor White
Write-Host "   - CF_ACCOUNT_ID" -ForegroundColor White
Write-Host "   - DEEPSEEK_API_KEY" -ForegroundColor White
Write-Host "   - NVIDIA_API_KEY" -ForegroundColor White
Write-Host "   - OPENROUTER_API_KEY" -ForegroundColor White
Write-Host "   - INSTAGRAM_USER / INSTAGRAM_PASS (opcional)" -ForegroundColor White

Write-Host ""
Write-Host "4. Ative as GitHub Actions:" -ForegroundColor Yellow
Write-Host "   Actions → Automatically approve workflows" -ForegroundColor Gray
Write-Host ""
Write-Host "✨ Pronto! O Tronix está pronto para evoluir no GitHub!" -ForegroundColor Green
