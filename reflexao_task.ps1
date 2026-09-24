# TRONIX Reflexao automatica - wrapper para Task Scheduler
# Lê HF_TOKEN do .env (Task Scheduler nao herda env do usuario) e roda a reflexao.
$envFile = "C:\xampp\htdocs\agente\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) {
    $cand = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path $cand) { $python = $cand }
}
if (-not $python) {
    Write-Output "[reflexao] ERRO: python nao encontrado"
    exit 1
}

Write-Output "[reflexao] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') iniciando TRONIX MENTE"
& $python "C:\xampp\htdocs\agente\tronix_mente.py" --refletir
Write-Output "[reflexao] fim: $LASTEXITCODE"