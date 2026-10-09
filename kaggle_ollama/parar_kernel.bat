@echo off
chcp 65001 >nul
title TRONIX - Derrubar o kernel do Kaggle (libera a cota de GPU)
cd /d "%~dp0"

echo.
echo ATENCAO: isso apaga o kernel e a URL do tunel morre.
echo.
set /p ok=Confirma? (digite SIM): 
if /i not "%ok%"=="SIM" (
    echo cancelado.
    pause
    exit /b 0
)

echo.
kaggle kernels delete "pontinhodainformtica/tronix-ollama-gpu-32gb-tunel-cloudflare" --yes
echo.
echo kernels restantes:
kaggle kernels list --mine
echo.
echo cota de GPU agora:
kaggle quota
echo.
echo Para religar depois:  python subir_kernel.py
pause
