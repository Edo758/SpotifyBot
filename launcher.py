import subprocess
import os
import signal
import time
import sys
import random
import threading
from rich.live import Live
from rich.table import Table

NUM_INSTANZE = 2
SCRIPT_PATH = os.path.join(os.getcwd(), "spotify_automation.py")
processi = []
stati = {i: {"stato": "ATTESA", "dettaglio": "-"} for i in range(1, NUM_INSTANZE + 1)}

def build_table():
    table = Table(title="Dashboard Istanze", expand=True)
    table.add_column("Istanza", justify="center")
    table.add_column("Stato", justify="center")
    table.add_column("Dettaglio", justify="center")
    for i in range(1, NUM_INSTANZE + 1):
        table.add_row(str(i), stati[i]["stato"], stati[i]["dettaglio"])
    return table

def reader(pipe, idx):
    for line in iter(pipe.readline, b''):
        try:
            line = line.decode("utf-8").strip()
        except:
            continue

        # Se il log contiene un aggiornamento di stato
        if line.startswith("STATE|"):
            try:
                _, stato, dettaglio = line.split("|", 2)
                stati[idx]["stato"] = stato
                stati[idx]["dettaglio"] = dettaglio
            except:
                pass
        # Altrimenti è solo log normale → lo stampiamo a console
        else:
            print(line, flush=True)
    pipe.close()


# Funzione di cleanup
def cleanup():
    print("\n[LAUNCHER] Terminazione in corso...")
    for p in processi:
        if p.poll() is None:
            try:
                p.terminate()  # Invia SIGTERM anche su Windows ai processi Python
                print(f"[LAUNCHER] Terminato PID {p.pid}")
            except Exception as e:
                print(f"[ERRORE] Impossibile terminare PID {p.pid}: {e}")
    print("[LAUNCHER] Tutti i processi chiusi. Esco.")
    sys.exit(0)

# Intercetta CTRL+C
signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

print(f"\nAvvio di {NUM_INSTANZE} istanze di spotify_automation.py...\n")

for i in range(1, NUM_INSTANZE + 1):
    p = subprocess.Popen(
        [sys.executable, SCRIPT_PATH, str(i)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1
    )
    processi.append(p)
    threading.Thread(target=reader, args=(p.stdout, i), daemon=True).start()
    if i < NUM_INSTANZE:
        time.sleep(random.uniform(4, 9))

print("\nTutte le istanze sono state avviate.")
print(" Premi CTRL+C per terminare tutte le istanze.")

with Live(build_table(), refresh_per_second=4, screen=False) as live:
    try:
        while True:
            live.update(build_table())
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()