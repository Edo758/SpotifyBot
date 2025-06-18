import os
import time

LOCK_FILE = os.path.join(os.path.dirname(__file__), "vpn_change.lock")

class VPNLock:
    def __init__(self, wait_interval=1):
        self.wait_interval = wait_interval
        self.lock_acquired = False

    def acquire(self):
        while True:
            try:
                # modalità 'x' fallisce se il file esiste
                self.fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.lock_acquired = True
                print("[🔒] Lock acquisito per cambio IP")
                break
            except FileExistsError:
                print("[⏳] In attesa del lock per cambio IP...")
                time.sleep(self.wait_interval)

    def release(self):
        if self.lock_acquired:
            os.close(self.fd)
            os.remove(LOCK_FILE)
            self.lock_acquired = False
            print("[✅] Lock rilasciato dopo cambio IP")