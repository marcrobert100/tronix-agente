@echo off
REM mtkclient - motor MediaTek: dump, leitura/escrita eMMC, FRP, BROM.
REM Driver: UsbDk instalado (msi em bin\UsbDk). Nao precisa mais de Zadig.
REM Antes de usar, rode a opcao 10 pra confirmar que o aparelho entrou em BROM.
setlocal
set BASE=%~dp0
cd /d "%BASE%mtk\mtkclient"
echo.
echo  Para o mtkclient funcionar, o aparelho precisa estar em MODO BROM:
echo    1. Desligue o aparelho completamente
echo    2. Segure vol+ e vol- juntos
echo    3. Conecte o cabo USB (sem soltar os botoes)
echo    4. Quando aparecer "0x0E8D" na opcao 10, volte aqui
echo.
echo  === mtkclient CLI ===
python mtk.py
echo.
echo  === mtkclient GUI ===
echo  (rode python mtk_gui.py para a interface grafica)
pause
