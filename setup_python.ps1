# Nome file suggerito: setup_python.ps1

# URL dell'installer Python ufficiale (Windows x64)
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

Write-Host "Scarico Python 3.13.2..."
Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath

Write-Host "Eseguo installazione Python in modalità silenziosa..."
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

Write-Host "Python installato. Controllo versione:"
python --version

Write-Host "Installazione dipendenze pip dal requirements.txt..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Setup completato! Puoi ora eseguire lo script Python."
