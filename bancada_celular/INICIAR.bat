@echo off
chcp 65001 >nul
title BANCADA CELULAR - Menu
setlocal
cd /d "%~dp0"
:menu
cls
echo.
echo   ==========================================================
echo      B A N C A D A   C E L U L A R  -  kit de bancada
echo   ==========================================================
echo.
echo   0. Diagnostico: ver aparelhos conectados (leitura)
echo.
echo   --- FRP (Factory Reset Protection) ---
echo   1. Samsung FRP via navegador  [patch antes de Ago/2022]
echo   2. FRP universal Android 5-15 (GUI)
echo   3. Samsung FRP via ADB (GUI)
echo.
echo   --- Tela de bloqueio (PIN / pattern / senha) ---
echo   4. dlock - desabilita lock screen (sem root)
echo   5. LockKnife - forensics Android
echo.
echo   --- MediaTek (leitura/escrita eMMC, FRP, BROM) ---
echo   6. mtkclient
echo.
echo   --- Firmware / dados ---
echo   7. DumprX - extrair firmware (precisa WSL/Git Bash)
echo   8. Abrir pasta de databases (open-device-db, PhonePCB)
echo.
echo   --- Boardview / Schematic (hardware) ---
echo   9. BoardRipper - abrir boardview + PDF do schematic
echo.
echo   --- Infraestrutura USB ---
echo   10. Diagnostico USB/MTK (UsbDk, BROM, ADB)
echo   11. Monitorar modo BROM (fica esperando o 0x0E8D)
echo.
echo   --- Xiaomi ---
echo   12. Mi Unlock Tool (destrava bootloader - APAGA TUDO)
echo.
echo   --- Servicos de bancada ---
echo   15. Reset de fabrica via recovery (confere conta Google antes)
echo.
echo   --- Manutencao ---
echo   14. Doctor (verifica o kit inteiro e o que o manual errou)
echo.
echo   ==========================================================
echo.
set /p op="Escolha: "
if "%op%"=="0" call "%~dp0diagnostico-aparelho.bat"
if "%op%"=="1" call "%~dp0"1-frp-samsung-web.bat
if "%op%"=="2" call "%~dp0"2-frp-freedom.bat
if "%op%"=="3" call "%~dp0"3-frp-samsung-gui.bat
if "%op%"=="4" call "%~dp0"4-lockscreen-dlock.bat
if "%op%"=="5" call "%~dp0"5-lockscreen-lockknife.bat
if "%op%"=="6" call "%~dp0"6-mtkclient.bat
if "%op%"=="7" (explorer.exe "%~dp0firmware\DumprX" & echo DumprX e Linux tool. Instale com: bash firmware\DumprX\setup.sh)
if "%op%"=="8" explorer.exe "%~dp0dados"
if "%op%"=="9" start "" "%~dp0dados\BoardRipper-lite.html"
if "%op%"=="10" call "%~dp0"10-usb-diagnostico.bat
if "%op%"=="11" call "%~dp0"11-modo-brom.bat
if "%op%"=="12" call "%~dp0"12-mi-unlock.bat
if "%op%"=="14" call "%~dp0"14-doctor.bat
if "%op%"=="15" call "%~dp0"15-reset-recovery.bat
goto menu
