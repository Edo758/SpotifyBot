@echo off
REM Imposta la cartella corrente dove si trova il .bat (e il .ps1)
set SCRIPT_DIR=%~dp0

REM Esegue il file PowerShell in modalità bypass per evitare restrizioni
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%setup_python.ps1"

pause
