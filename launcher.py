import subprocess
import os
import signal
import time
import sys

NUM_INSTANZE = 1
SCRIPT_PATH = os.path.join(os.getcwd(), "spotify_automation.py")
processi = []

# Funzione di cleanup
def cleanup():
    print("\n[LAUNCHER] Terminazione in corso...")
    for p in processi:
        if p.poll() is None:
            try:
                if os.name == 'nt':
                    os.kill(p.pid, signal.CTRL_BREAK_EVENT)
                else:
                    p.terminate()
                print(f"[LAUNCHER] Terminato PID {p.pid}")
            except Exception as e:
                print(f"[ERRORE] Impossibile terminare PID {p.pid}: {e}")
    print("[LAUNCHER] Tutti i processi chiusi. Esco.")
    sys.exit(0)

# Intercetta CTRL+C
signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

print(f"\nAvvio di {NUM_INSTANZE} istanze di spotify_automation.py...\n")

for i in range(1, NUM_INSTANZE + 1):
    print(f"[] Avvio istanza {i}...")
    p = subprocess.Popen(
        [sys.executable, SCRIPT_PATH, str(i)],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
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
