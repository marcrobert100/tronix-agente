@echo off
REM Diagnostico USB/MTK - confirma se o UsbDk e o libusb estao enxergando o aparelho.
REM Se aparecer 0E8D = MediaTek em modo BROM, pronto pro mtkclient.
chcp 65001 >nul
setlocal
set BASE=%~dp0
cd /d "%BASE%"

echo.
echo  ==========================================================
echo    DIAGNOSTICO USB / MEDIA TEK
echo  ==========================================================
echo.

echo  --- 1. Servico UsbDk (driver de acesso USB) ---
sc.exe query UsbDk | findstr /i "ESTADO"
if errorlevel 1 (
  echo  [X] UsbDk NAO esta instalado ou parado
  echo      Instale: bin\UsbDk\UsbDk_1.0.22_x64.msi
) else (
  echo  [OK] UsbDk rodando
)
echo.

echo  --- 2. Dispositivos vistos pelo UsbDkController ---
if exist "C:\Program Files\UsbDk Runtime Library\UsbDkController.exe" (
  "C:\Program Files\UsbDk Runtime Library\UsbDkController.exe" -n | findstr /i "ID: USB"
) else (
  echo  UsbDkController nao encontrado
)
echo.

echo  --- 3. Dispositivos vistos pelo libusb (mtkclient) ---
python "%BASE%usb_diagnostico.py"
echo.

echo  --- 4. ADB ---
where adb >nul 2>&1
if errorlevel 1 (
  echo  [X] adb nao encontrado
) else (
  adb devices
)
echo.

echo  ==========================================================
echo  Como ler o resultado:
echo.
echo    VID=0x0E8D  -> MediaTek em BROM. Roda o mtkclient (opcao 6).
echo    VID=0x2717  -> aparelho em modo normal. mtkclient so funciona
echo                    se voce botar em BROM: desligue, segure
echo                    vol+ e vol- juntos, conecte o cabo.
echo    (sem 0E8D)  -> ainda nao esta em BROM. Repita o passo acima.
echo ==========================================================
echo.
pause
