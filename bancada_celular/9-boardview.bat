@echo off
REM BoardRipper - viewer de boardview (.brd .fz .tvw .pcb .cad etc) + schematic PDF lado a lado.
REM Arquivo unico de 8MB, roda offline, sem servidor. Chrome/Edge recomendado.
setlocal
set BR=C:\xampp\htdocs\agente\bancada_celular\dados\BoardRipper-lite.html
start "" "%BR%"
echo.
echo  BoardRipper aberto.
echo.
echo  COMO USAR:
echo   1. Ctrl+O - abrir arquivo de boardview
echo   2. Ctrl+P - abrir o schematic em PDF
echo   3. Clique num pino: a net inteira acende
echo   4. Botao direito na net: busca ela no schematic
echo   5. Space - vira a board (frente/verso)
echo.
echo  Formatos: .brd .bv .bdv .fz .cad .pcb .tvw .kicad_pcb .PcbDoc .brd(EAGLE)
echo  Dica: arraste o arquivo direto pra janela.
echo.
pause
