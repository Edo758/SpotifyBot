# Comando PowerShell per eseguire lo script di setup Python da remoto
iex "& { $(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/Edo758/SpotifyBot/master/setup_python.ps1').Content }"
