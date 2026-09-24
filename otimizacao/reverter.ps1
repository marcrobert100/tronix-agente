$ErrorActionPreference = "SilentlyContinue"
"=== REVERTENDO OTIMIZACAO ==="

$keys = @(
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects","VisualFXSetting","3"
 "HKCU:\Control Panel\Desktop","MenuShowDelay","400"
 "HKCU:\Control Panel\Desktop","AutoEndTasks","0"
 "HKCU:\Control Panel\Desktop","WaitToKillAppTimeout","20000"
 "HKCU:\Control Panel\Desktop\WindowMetrics","MinAnimate","1"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","TaskbarAnimations","1"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","TaskbarSmallIcons","0"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","ListviewAlphaEnable","1"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","ListviewShadow","1"
 "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","IconsOnly","0"
)
for ($i=0; $i -lt $keys.Count; $i+=3) {
  Set-ItemProperty -Path $keys[$i] -Name $keys[$i+1] -Value $keys[$i+2] -Type DWord
  "$($keys[$i]) :: $($keys[$i+1]) = $($keys[$i+2])"
}

$maskDefault = [byte[]]@(0x9E,0x3E,0x07,0x80,0x12,0x00,0x00,0x00)
Set-ItemProperty "HKCU:\Control Panel\Desktop" -Name UserPreferencesMask -Value $maskDefault
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name EnableTransparency -Value 1 -Type DWord
Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name AllowTelemetry -Value 1 -Type DWord
Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name AllowTelemetry -Value 1 -Type DWord
Set-ItemProperty "HKCU:\Software\Policies\Microsoft\Windows\Explorer" -Name DisableSearchBoxSuggestions -Value 0 -Type DWord
Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name AllowGameDVR -Value 1 -Type DWord
Set-ItemProperty "HKCU:\System\GameConfigStore" -Name GameDVR_Enabled -Value 1 -Type DWord
Set-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name AllowCortana -Value 1 -Type DWord
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name SubscribedContent-338389Enabled -Value 1 -Type DWord
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name SystemPaneSuggestionsEnabled -Value 1 -Type DWord
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name SubscribedContentEnabled -Value 1 -Type DWord

New-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "GoogleChromeAutoLaunch_A1168AF51C33CD2D233C13313B3D9BA2" -Value `"C:\Program Files\Google\Chrome\Application\chrome.exe` --no-startup-window /prefetch:5" -PropertyType String -Force
New-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "IgfxTray" -Value "C:\WINDOWS\system32\igfxtray.exe" -PropertyType String -Force
New-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "HotKeysCmds" -Value "C:\WINDOWS\system32\hkcmd.exe" -PropertyType String -Force
New-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "Persistence" -Value "C:\WINDOWS\system32\igfxpers.exe" -PropertyType String -Force

$tasks = @(
 "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
 "\Microsoft\Windows\Application Experience\ProgramDataUpdater",
 "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
 "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
 "\Microsoft\Windows\Feedback\Siuf\DmClient",
 "\Microsoft\Windows\Feedback\Siuf\DmClientOnScenarioDownload",
 "\Microsoft\Windows\Windows Error Reporting\QueueReporting"
)
foreach ($t in $tasks) { SchTasks.exe /Change /TN $t /Enable 2>$null | Out-Null; "TASK $t re-enabled" }

"REVERT OK - reinicie o explorer (taskkill /f /im explorer.exe) para aplicar"