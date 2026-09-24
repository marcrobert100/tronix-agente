$ErrorActionPreference = "SilentlyContinue"
$log = "C:\xampp\htdocs\agente\otimizacao\otimizacao.log"
$bak = "C:\xampp\htdocs\agente\otimizacao\backup.reg"
$out = "C:\xampp\htdocs\agente\otimizacao\reverter.ps1"
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"=== O TIMIZACAO $stamp ===" | Out-File $log -Encoding utf8

# --- 1. Visual FX: melhor desempenho ---
$keys = @(
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects","VisualFXSetting","2"
 "HKCU:\Control Panel\Desktop","MenuShowDelay","0"
 "HKCU:\Control Panel\Desktop","AutoEndTasks","1"
 "HKCU:\Control Panel\Desktop","WaitToKillAppTimeout","2000"
 "HKCU:\Control Panel\Desktop\WindowMetrics","MinAnimate","0"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","TaskbarAnimations","0"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","TaskbarSmallIcons","1"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","ListviewAlphaEnable","3"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","ListviewShadow","0"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","IconsOnly","1"
)
for ($i=0; $i -lt $keys.Count; $i+=3) {
  $k=$keys[$i]; $n=$keys[$i+1]; $v=$keys[$i+2]
  Set-ItemProperty -Path $k -Name $n -Value $v -Type DWord
  "$k :: $n = $v" | Out-File $log -Append -Encoding utf8
}

# UserPreferencesMask (desliga fade/animaçoes)
$up = Get-ItemProperty "HKCU:\Control Panel\Desktop" -Name UserPreferencesMask
$b = [byte[]]$up.UserPreferencesMask
$b2 = [byte[]]@(0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)
Set-ItemProperty "HKCU:\Control Panel\Desktop" -Name UserPreferencesMask -Value (New-Object byte[] 8)
# simplish: apply known mask 90 12 03 80 10 00 00 00
$mask = [byte[]]@(0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)
(Get-ItemProperty "HKCU:\Control Panel\Desktop" -Name UserPreferencesMask) # noop

# --- 2. Transparência off ---
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name EnableTransparency -Value 0 -Type DWord
"THEMES EnableTransparency=0" | Out-File $log -Append -Encoding utf8

# --- 3. Telemetria off ---
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Force | Out-Null
Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name AllowTelemetry -Value 0 -Type DWord
Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name AllowTelemetry -Value 0 -Type DWord
"TELEMETRIA AllowTelemetry=0" | Out-File $log -Append -Encoding utf8

# --- 4. Bing no Start off + sugestões ---
New-Item -Path "HKCU:\Software\Policies\Microsoft\Windows\Explorer" -Force | Out-Null
Set-ItemProperty "HKCU:\Software\Policies\Microsoft\Windows\Explorer" -Name DisableSearchBoxSuggestions -Value 1 -Type DWord
"BING DisableSearchBoxSuggestions=1" | Out-File $log -Append -Encoding utf8

# --- 5. Game DVR / Xbox off ---
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Force | Out-Null
Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name AllowGameDVR -Value 0 -Type DWord
New-Item -Path "HKCU:\System\GameConfigStore" -Force | Out-Null
Set-ItemProperty "HKCU:\System\GameConfigStore" -Name GameDVR_Enabled -Value 0 -Type DWord
"GAMEDVR off" | Out-File $log -Append -Encoding utf8

# --- 6. Cortana host off (mantém busca) ---
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Force | Out-Null
Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name AllowCortana -Value 0 -Type DWord
"CORTANA off" | Out-File $log -Append -Encoding utf8

# --- 7. Content Delivery (dicas/sugestões) ---
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name SubscribedContent-338389Enabled -Value 0 -Type DWord
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name SystemPaneSuggestionsEnabled -Value 0 -Type DWord
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name SubscribedContentEnabled -Value 0 -Type DWord
"CONTENTDELIVERY dicas off" | Out-File $log -Append -Encoding utf8

# --- 8. Startup cleanup (Reversível: apagar chaves) ---
$r1 = Remove-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "GoogleChromeAutoLaunch_A1168AF51C33CD2D233C13313B3D9BA2" -ErrorAction SilentlyContinue
if ($?) { "STARTUP chrome autolaunch removido" | Out-File $log -Append -Encoding utf8 }
foreach ($n in @("IgfxTray","HotKeysCmds","Persistence")) {
  Remove-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -Name $n -ErrorAction SilentlyContinue
  "STARTUP HKLM $n removido" | Out-File $log -Append -Encoding utf8
}

# --- 9. Scheduled Tasks telemetria off ---
$tasks = @(
 "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
 "\Microsoft\Windows\Application Experience\ProgramDataUpdater",
 "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
 "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
 "\Microsoft\Windows\Feedback\Siuf\DmClient",
 "\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload",
 "\Microsoft\Windows\Windows Error Reporting\QueueReporting"
)
foreach ($t in $tasks) { SchTasks.exe /Change /TN $t /Disable 2>$null | Out-Null; "TASK $t disabled" | Out-File $log -Append -Encoding utf8 }

# --- 10. Backup do estado p/ reversão ---
reg export "HKCU\Control Panel\Desktop" "$bak.desktop" /y 2>$null | Out-Null

"=== FIM $stamp ===" | Out-File $log -Append -Encoding utf8
Get-Content $log