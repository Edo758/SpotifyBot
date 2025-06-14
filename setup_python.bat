@echo off
REM Percorso della cartella dove si trova il batch (e il file .ps1)
set SCRIPT_DIR=%~dp0

REM Esegui lo script PowerShell con esecuzione bypassata per policy (solo per questo comando)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%setup_python.ps1"

pause
