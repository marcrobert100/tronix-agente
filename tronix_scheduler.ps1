<#
.TRANSCRIPT
Tronix Scheduler - Instalador de Tarefas Agendadas
Uso: powershell -ExecutionPolicy Bypass -File tronix_scheduler.ps1
#>

$BASE = "C:\xampp\htdocs\agente"
$PYTHON = "python"

Write-Host "=== Tronix Scheduler ===" -ForegroundColor Cyan
Write-Host "Instalando tarefas agendadas no Windows..." -ForegroundColor Yellow

# Tarefa 1: Postar pendentes no Instagram (10h, 14h, 18h)
$ACAO_IG = New-ScheduledTaskAction -Execute $PYTHON -Argument "tronix_instagram.py --pendentes" -WorkingDirectory $BASE
$DISPARO_IG = @(
    New-ScheduledTaskTrigger -Daily -At "10:00",
    New-ScheduledTaskTrigger -Daily -At "14:00",
    New-ScheduledTaskTrigger -Daily -At "18:00"
)
Register-ScheduledTask -TaskName "Tronix-PostarInstagram" -Action $ACAO_IG -Trigger $DISPARO_IG -User "SYSTEM" -RunLevel Highest -Force
Write-Host "  [OK] Tronix-PostarInstagram - 10h, 14h, 18h" -ForegroundColor Green

# Tarefa 2: Gerar mini-novela todo dia as 08h
$ACAO_GERAR = New-ScheduledTaskAction -Execute $PYTHON -Argument "gerar_mini_novela.py" -WorkingDirectory $BASE
$DISPARO_GERAR = New-ScheduledTaskTrigger -Daily -At "08:00"
Register-ScheduledTask -TaskName "Tronix-GerarNovela" -Action $ACAO_GERAR -Trigger $DISPARO_GERAR -User "SYSTEM" -RunLevel Highest -Force
Write-Host "  [OK] Tronix-GerarNovela - 08h" -ForegroundColor Green

# Tarefa 3: Limpeza de arquivos temporarios (domingo as 03h)
$ACAO_LIMPAR = New-ScheduledTaskAction -Execute "powershell" -Argument "Remove-Item '$BASE\temp_*.mp3','$BASE\_concat_list.txt' -Force -ErrorAction SilentlyContinue" -WorkingDirectory $BASE
$DISPARO_LIMPAR = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "03:00"
Register-ScheduledTask -TaskName "Tronix-Limpeza" -Action $ACAO_LIMPAR -Trigger $DISPARO_LIMPAR -User "SYSTEM" -RunLevel Highest -Force
Write-Host "  [OK] Tronix-Limpeza - Domingo 03h" -ForegroundColor Green

Write-Host "`nTarefas instaladas! Verifique em: agendador de tarefas do Windows" -ForegroundColor Cyan
Write-Host "Ou rode: taskschd.msc" -ForegroundColor Gray
