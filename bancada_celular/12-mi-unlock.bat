@echo off
REM Mi Unlock Tool - oficial da Xiaomi (baixado de miuirom.xiaomi.com).
REM Destrava o bootloader do Xiaomi. ATENCAO: apaga TUDO do celular.
REM
REM Antes de usar, no celular:
REM   1. Configurações > Contas > Xiaomi Account > entrar com a conta Mi
REM   2. Ligar "Procurar dispositivo" (Find Mi)
REM   3. https://en.miui.com/unlock/  -> clicar "Unlock Now" e esperar a Xiaomi liberar
REM A Xiaomi segura de 72h a 168h. Sem conta Mi no aparelho, nao libera.
chcp 65001 >nul
setlocal
set D=%~dp0bin\mi-unlock
cd /d "%D%"

if not exist "%D%\miflash_unlock.exe" (
  echo  ERRO: miflash_unlock.exe nao encontrado em %D%
  pause
  exit /b 1
)

echo.
echo  ==========================================================
echo    MI UNLOCK TOOL  -  oficial Xiaomi v6.5.224.28
echo  ==========================================================
echo.
echo  !! DESTRAVAR O BOOTLOADER APAGA TODOS OS DADOS !!
echo  !! Facca backup antes. Sem volta.
echo.
echo  Se ainda nao esperou a liberacao da Xiaomi, vai dar erro.
echo  O certo e esperar o prazo terminar.
echo.

start "" "%D%\miflash_unlock.exe"
echo  Mi Unlock aberto. Use a MESMA conta Mi que esta no celular.
echo.
pause
