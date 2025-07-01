import os
import time
import psutil

LOCK_FILE = "vpn_change.lock"

class VPNLock:
    def __init__(self):
        self.fd = None
        self.own_pid = os.getpid()

    def acquire(self, timeout=60):
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(self.fd, str(self.own_pid).encode())
                print("[] Lock acquisito per cambio IP.")
                break
            except FileExistsError:
                if time.time() - start_time > timeout:
                    print(f"[!] Timeout: lock ancora presente dopo {timeout} secondi.")
                    try:
                        with open(LOCK_FILE, 'r') as f:
                            pid_str = f.read().strip()
                            pid = int(pid_str)
                        if not psutil.pid_exists(pid):
                            print(f"[!] Il processo {pid} non esiste più. Elimino il lock.")
                            os.remove(LOCK_FILE)
                            continue  # riprova subito
                        else:
                            print(f"[!] Il lock è ancora attivo da parte del processo {pid}. Attendo...")
                    except Exception as e:
                        print(f"[!] Errore nella lettura del lock file: {e}. Elimino il lock forzatamente.")
                        try:
                            os.remove(LOCK_FILE)
                        except Exception as e2:
                            print(f"[!] Errore nel cancellare il lock file: {e2}")
                    time.sleep(1)
                else:
                    print("[] In attesa del lock per cambio IP...")
                    time.sleep(1)

    def release(self):
        if self.fd:
            try:
                os.close(self.fd)
                with open(LOCK_FILE, 'r') as f:
                    pid_in_file = int(f.read().strip())
                if pid_in_file == self.own_pid:
                    os.remove(LOCK_FILE)
                    print("[] Lock rilasciato.")
                else:
                    print(f"[!] Non posso rilasciare il lock: è posseduto da PID {pid_in_file}.")
            except Exception as e:
                print(f"[!] Errore nel rilascio del lock: {e}")