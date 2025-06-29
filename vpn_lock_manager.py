import os
import time

LOCK_FILE = "vpn_change.lock"

class VPNLock:
    def __init__(self):
        self.fd = None

    def acquire(self, timeout=60):
        start_time = time.time()
        while True:
            try:
                self.fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                print("[] Lock acquisito per cambio IP.")
                break
            except FileExistsError:
                if time.time() - start_time > timeout:
                    print(f"[!] Timeout: lock ancora presente dopo {timeout} secondi. Lo elimino forzatamente.")
                    try:
                        os.remove(LOCK_FILE)
                    except Exception as e:
                        print("[!] Errore nel cancellare il lock file:", e)
                    continue  # riprova subito
                print("[] In attesa del lock per cambio IP...")
                time.sleep(1)

                        

    def release(self):
        if self.fd:
            os.close(self.fd)
            os.remove(LOCK_FILE)
            print("[] Lock rilasciato.")