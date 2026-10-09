<#
    ipad_conectar.ps1 - Recupera/conecta iPad via USB usando pymobiledevice3

    Sintoma que corrige:
      O iPad aparece no Gerenciador de Dispositivos (Apple Mobile Device USB Device,
      Apple iPad WPD), mas `pymobiledevice3 usbmux list` devolve [] e
      ConnectionFailedToUsbmuxdError. Causa: o Apple Mobile Device Service foi
      morto pelo Windows durante um eject (evento Kernel-PnP 225) e o device
      plugado antes do servico subir nao se re-anuncia.

    Uso:
      powershell -ExecutionPolicy Bypass -File ipad_conectar.ps1
      powershell -ExecutionPolicy Bypass -File ipad_conectar.ps1 -Force   # cycle agressivo
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Info
)

$ErrorActionPreference = 'Continue'
$SERVICE = 'Apple Mobile Device Service'
$VID     = 'VID_05AC&PID_129A'

function Log($msg, $level = 'INFO') {
    $color = switch ($level) { 'OK' { 'Green' } 'ERR' { 'Red' } 'WARN' { 'Yellow' } default { 'Cyan' } }
    Write-Host ("[{0,-4}] {1}" -f $level, $msg) -ForegroundColor $color
}

function Test-UsbPresent {
    $devs = Get-CimInstance Win32_PnPEntity -Filter "Name LIKE '%Apple Mobile Device USB%'" -ErrorAction SilentlyContinue
    return ($null -ne $devs -and @($devs).Count -gt 0)
}

function Test-UsbmuxSees {
    $out = & python -m pymobiledevice3 usbmux list 2>&1 | Out-String
    return ($out.Trim() -ne '[]' -and $out.Trim().Length -gt 2)
}

if ($Info) {
    Log "Servico $SERVICE : $((Get-Service $SERVICE).Status)"
    Log "Driver iPad      : $((pnputil /enum-devices /instanceid 'USB\$VID&MI_01' /drivers 2>$null | Select-String 'Vers.o do Driver') -join '')"
    Log "USB presente     : $(Test-UsbPresent)"
    Log "usbmux ve device : $(Test-UsbmuxSees)"
    exit 0
}

Log "Iniciando..."

# 1. Garante servico no automatico para nao ocorrer de novo no proximo boot
try {
    Set-Service -Name $SERVICE -StartupType Automatic -ErrorAction Stop
    Log "Startup definido como Automatico" 'OK'
} catch {
    Log "Nao foi possivel mudar startup: $($_.Exception.Message)" 'WARN'
}

# 2. Para o servico para liberar o device node
if ((Get-Service $SERVICE).Status -ne 'Stopped') {
    Stop-Service $SERVICE -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    Log "Servico parado" 'OK'
}

# 3. Remove os device nodes do iPad do PnP (equivalente digital do replug)
$ids = Get-PnpDevice -ErrorAction SilentlyContinue |
       Where-Object { $_.InstanceId -like "*$VID*" -and $_.Class -ne 'WPD' } |
       Select-Object -ExpandProperty InstanceId

foreach ($id in $ids) {
    pnputil /remove-device "$id" *> $null
    Log "Node removido: $id" 'OK'
    Start-Sleep -Milliseconds 800
}

# 4. Rescan global do hardware
pnputil /scan-devices *> $null
Log "Rescan de hardware executado" 'OK'
Start-Sleep -Seconds 8

# 5. Sobe o servico
Start-Service $SERVICE
Start-Sleep -Seconds 5
Log "Servico iniciado: $((Get-Service $SERVICE).Status)" 'OK'

# 6. Verifica
if (Test-UsbmuxSees) {
    Log "iPad ANUNCADO pelo usbmuxd" 'OK'
    & python -m pymobiledevice3 lockdown info 2>&1 | Out-String | Write-Host
    exit 0
}

Log "usbmuxd ainda devolve lista vazia" 'WARN'

if ($Force) {
    Log "Modo -Force: reiniciando o servico de forma agressiva" 'WARN'
    for ($i = 1; $i -le 3; $i++) {
        Stop-Service $SERVICE -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        pnputil /scan-devices *> $null
        Start-Sleep -Seconds 5
        Start-Service $SERVICE
        Start-Sleep -Seconds 6
        if (Test-UsbmuxSees) {
            Log "Conectado na tentativa $i" 'OK'
            exit 0
        }
        Log "Tentativa $i falhou" 'WARN'
    }
}

Log ""
Log "O software esta correto. Falta o iPad se anunciar:" 'WARN'
Log "  1. Desbloqueie a tela do iPad (device bloqueado nao anuncia)" 'WARN'
Log "  2. Tire o cabo USB e espere 5 segundos" 'WARN'
Log "  3. Se aparecer 'Confiar neste computador' -> Confia" 'WARN'
Log "  4. Replugue o cabo" 'WARN'
Log ""
Log "Com o servico agora em Automatico, o proximo boot ja comeca certo."
exit 1