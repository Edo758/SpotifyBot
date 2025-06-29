import subprocess
import time
import os

SCRIPT_NAME = "spotify_automation.py"
NUM_ISTANZE = 5 # numero di istanze da avviare
DELAY_AVVIO = 2  # secondi tra un lancio e l'altro
LOG_DIR = "log_istanze"

def assicurati_cartella_log():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def avvia_istanze():
    assicurati_cartella_log()
    
    for i in range(1, NUM_ISTANZE + 1):
        log_file = os.path.join(LOG_DIR, f"log_{i}.txt")
        print(f"[] Avvio istanza {i}... (log in {log_file})")

        # Avvia il processo in background con output redirezionato
        subprocess.Popen(
            ["python", SCRIPT_NAME],
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW  # Nessuna finestra cmd
        )

        time.sleep(DELAY_AVVIO)

if __name__ == "__main__":
    print(f" Avvio di {NUM_ISTANZE} istanze di {SCRIPT_NAME}...\n")
    avvia_istanze()
    print("\n Tutte le istanze sono state avviate.")
