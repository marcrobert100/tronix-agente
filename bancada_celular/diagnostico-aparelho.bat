@echo off
REM Le device e grava tudo no PC. Nao apaga nada. Bom pra confirmar modelo/IMEI na recepcao.
setlocal
echo  === ADB devices ===
adb devices -l
echo.
echo  === ADB version ===
adb version
echo.
echo  === Fastboot version ===
fastboot --version
echo.
echo  === LockKnife: info do aparelho conectado ===
lockknife device info
echo.
echo  === FONE NA MESA? ===
echo  Conecte o cabo USB, ative Depuracao USB e feche essa janela.
pause
