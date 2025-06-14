# SpotifyBot - Setup Python Environment

Questo script automatizza l'installazione di Python, pip e delle dipendenze per il progetto SpotifyBot.

---

## Come eseguire lo script di setup

Puoi eseguire lo script di setup Python direttamente da PowerShell con questo comando:

```powershell
iex "& { $(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/Edo758/SpotifyBot/master/setup_python.ps1').Content }"
