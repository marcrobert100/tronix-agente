@echo off
echo ============================================
echo   NETHUNTER - Atalho Desktop
echo ============================================
echo.
echo Criando atalho no Desktop...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\Kali Linux.lnk'); $s.TargetPath='C:\xampp\htdocs\agente\abrir_kali.bat'; $s.WorkingDirectory='C:\xampp\htdocs\agente'; $s.Description='Kali Linux NetHunter'; $s.Save()"
echo.
echo Atalho criado: %USERPROFILE%\Desktop\Kali Linux.lnk
echo.
pause
