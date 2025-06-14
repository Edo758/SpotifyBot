# === setup_python.ps1 ===

# Scarica la pagina ufficiale dei download Python per Windows
$downloadPage = Invoke-WebRequest -Uri "https://www.python.org/downloads/windows/" -UseBasicParsing

# Estrae l'ultima versione stabile di Python 3 (es. 3.13.2)
$latestVersion = ""
if ($downloadPage.Content -match 'Latest Python 3 Release - Python ([\d\.]+)') {
    $latestVersion = $Matches[1]
    Write-Host " Ultima versione disponibile: Python $latestVersion"
} else {
    Write-Host " Impossibile trovare la versione più recente di Python."
    exit 1
}

# Controlla se Python è già installato
$pythonInstalled = $false
$currentVersion = ""
try {
    $output = python --version 2>&1
    if ($output -match 'Python ([\d\.]+)') {
        $currentVersion = $Matches[1]
        $pythonInstalled = $true
        Write-Host " Python installato: $currentVersion"
    }  # <-- questa parentesi chiude l'if
}  # <-- questa parentesi chiude il try
catch {
    Write-Host " Python non è installato o non è nel PATH."
}



# Installa Python se non presente o se la versione è vecchia
if (-not $pythonInstalled -or ($currentVersion -lt $latestVersion)) {
    $installerUrl = "https://www.python.org/ftp/python/$latestVersion/python-$latestVersion-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"

    Write-Host "⬇ Scarico Python $latestVersion da: $installerUrl"
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

    Write-Host " Installo Python in modalità silenziosa..."
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

    Write-Host " Installazione Python completata."
}

# Controlla se pip è disponibile, altrimenti lo installa
python -m pip --version 2>$null
if (-not $?) {
    Write-Host " pip non trovato. Lo installo manualmente..."
    $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
    $getPipPath = "$env:TEMP\get-pip.py"
    Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipPath
    python $getPipPath
} else {
    Write-Host " pip e' gia' presente."
}

# Lista delle dipendenze Python da installare direttamente nello script
$dependencies = @(
    "selenium",
    "pyautogui",
    "pynput"
)

Write-Host " Installo dipendenze specificate nello script..."

foreach ($dep in $dependencies) {
    python -m pip install $dep --upgrade
}

Write-Host "`nSetup completato! Puoi ora eseguire lo script Python."