import subprocess
import os
import signal
import time
import sys

NUM_INSTANZE = 5
SCRIPT_PATH = os.path.join(os.getcwd(), "spotify_automation.py")
LOG_DIR = os.path.join(os.getcwd(), "log_istanze")
processi = []

# Crea la cartella log se non esiste
os.makedirs(LOG_DIR, exist_ok=True)

def cleanup():
    print("\n[LAUNCHER] Terminazione in corso...")
    for p in processi:
        if p.poll() is None:
            try:
                os.kill(p.pid, signal.SIGTERM)  # Invia segnale di terminazione
                print(f"[LAUNCHER] Terminato PID {p.pid}")
            except Exception as e:
                print(f"[ERRORE] Impossibile terminare PID {p.pid}: {e}")
    print("[LAUNCHER] Tutti i processi chiusi. Esco.")
    sys.exit(0)

# Intercetta CTRL+C
signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

print(f"\nAvvio di {NUM_INSTANZE} istanze di spotify_automation.py...\n")

for i in range(1, NUM_INSTANZE + 1):
    log_file_path = os.path.join(LOG_DIR, f"log_{i}.txt")
    with open(log_file_path, "w") as log_file:
        print(f"[] Avvio istanza {i}... (log in {log_file_path})")
        p = subprocess.Popen(
            [sys.executable, SCRIPT_PATH],
            stdout=log_file,
            stderr=log_file,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # consente terminazione pulita
        )
        processi.append(p)

print("\nTutte le istanze sono state avviate.")
print(" Premi CTRL+C per terminare tutte le istanze.")

# Mantieni vivo il launcher finché le istanze girano
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()
