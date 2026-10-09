@echo off
REM Desabilita tela de bloqueio (PIN/pattern/senha) via ADB. Sem root. Multi-aparelho.
setlocal
set BASE=%~dp0
"%BASE%bin\dlock\dlock.exe"
pause
