$ErrorActionPreference = "Continue"
$adb = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools"
$env:PATH = "$adb;$env:PATH"
$env:PYTHONIOENCODING = "utf-8"
arom gui
