@echo off
REM LockKnife - forensics Android. Comandos uteis de bancada:
REM   lockknife device list      lista aparelhos ADB
REM   lockknife device info      info detalhada
REM   lockknife crack --help     recuperacao de credencial (offline/autorizado)
REM So usar em aparelhos com autorizacao do dono.
setlocal
cd /d "%~dp0"
lockknife %*
pause
