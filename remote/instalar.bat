@echo off
title Tronix Remote - Instalador
color 0a
echo.
echo  ========================================
echo   INSTALANDO TRONIX REMOTE
echo  ========================================
echo.

set ADB=C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\adb.exe
set SCRCPY=C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\scrcpy.exe

echo [1/3] Verificando dispositivo...
"%ADB%" devices
echo.

echo [2/3] Criando atalhos...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\Tronix Remote.lnk'); $s.TargetPath='C:\xampp\htdocs\agente\remote\iniciar.bat'; $s.WorkingDirectory='C:\xampp\htdocs\agente\remote'; $s.Save()"
echo Atalho criado na Area de Trabalho!
echo.

echo [3/3] Criando batch rapidos...
echo @echo off > "C:\xampp\htdocs\agente\tela.bat"
echo "%SCRCPY%" --stay-awake >> "C:\xampp\htdocs\agente\tela.bat"

echo @echo off > "C:\xampp\htdocs\agente\tela_hd.bat"
echo "%SCRCPY%" --stay-awake --max-size=1920 --video-codec=h264 >> "C:\xampp\htdocs\agente\tela_hd.bat"

echo @echo off > "C:\xampp\htdocs\agente\terminal.bat"
echo %ADB% shell >> "C:\xampp\htdocs\agente\terminal.bat"

echo @echo off > "C:\xampp\htdocs\agente\screenshot.bat"
echo %ADB% shell screencap -p /sdcard/screen.png >> "C:\xampp\htdocs\agente\screenshot.bat"
echo %ADB% pull /sdcard/screen.png "%USERPROFILE%\Desktop\screenshot.png" >> "C:\xampp\htdocs\agente\screenshot.bat"
echo %ADB% shell rm /sdcard/screen.png >> "C:\xampp\htdocs\agente\screenshot.bat"
echo echo Screenshot salva no Desktop! >> "C:\xampp\htdocs\agente\screenshot.bat"
echo pause >> "C:\xampp\htdocs\agente\screenshot.bat"

echo.
echo  ========================================
echo   INSTALACAO COMPLETA!
echo  ========================================
echo.
echo  ATALHOS CRIADOS:
echo  - Tronix Remote (Area de Trabalho)
echo  - tela.bat (espelhar rapido)
echo  - tela_hd.bat (espelhar HD)
echo  - terminal.bat (shell ADB)
echo  - screenshot.bat (tela)
echo.
echo  Para iniciar o servidor web:
echo  C:\xampp\htdocs\agente\remote\iniciar.bat
echo.
echo  Para espelhar agora:
echo  C:\xampp\htdocs\agente\tela.bat
echo.
pause
