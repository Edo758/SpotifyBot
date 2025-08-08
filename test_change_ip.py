import os
import time
import tempfile
import shutil
import sys
import winreg
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
EXTENSION_DIR = os.path.join(BASE_DIR, "CyberGhost")
EXTENSION_ID = "clnceilhfmekjpiacjjlmdohilnogoej"  # cambia se diverso

# === CREA PROFILO TEMPORANEO ===
temp_profile = tempfile.mkdtemp()

def printi(*args, **kwargs):
    if 'flush' not in kwargs:
        kwargs['flush'] = True
    print(*args, **kwargs)

# === TROVA IL PERCORSO DEL BROWSER ===
def find_browser_path_from_registry(browser_exe_name):
    try:
        key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{browser_exe_name}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            path, _ = winreg.QueryValueEx(key, "")
            return path
    except Exception:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                path, _ = winreg.QueryValueEx(key, "")
                return path
        except Exception:
            return None

def find_browser_path_default(browser_name):
    possibles = [
        rf"C:\Program Files\{browser_name}\Application\{browser_name}.exe",
        rf"C:\Program Files (x86)\{browser_name}\Application\{browser_name}.exe",
    ]
    for path in possibles:
        if os.path.isfile(path):
            return path
    return None

def find_brave_path():
    path = find_browser_path_from_registry("brave.exe")
    if path:
        return path
    return find_browser_path_default("BraveSoftware\\Brave-Browser")

def find_chrome_path():
    path = find_browser_path_from_registry("chrome.exe")
    if path:
        return path
    return find_browser_path_default("Google\\Chrome")

# === FUNZIONI DI PULIZIA ===
def cleanup():
    global driver
    try:
        driver.quit()
    except:
        pass
    if os.path.exists(temp_profile):
        shutil.rmtree(temp_profile)
    print("[INFO] Pulizia completata.")

# === FUNZIONI PER LOGGARE L'IP CORRENTE ===
def log_current_ip():
    try:
        driver.get("https://api.ipify.org?format=text")
        time.sleep(3)
        ip = driver.find_element(By.TAG_NAME, "body").text
        printi(f"[ NUOVO IP] {ip}")
    except Exception as e:
        printi("Errore nel rilevamento IP:", e)

# === VERIFICA ESTENSIONE ===
def verify_extension_loaded():
    """Verifica che l'estensione sia caricata correttamente"""
    try:
        # Verifica che la cartella dell'estensione esista
        if not os.path.exists(EXTENSION_DIR):
            printi(f"[ERRORE] Cartella estensione non trovata: {EXTENSION_DIR}")
            return False
        
        # Verifica che esista il manifest.json
        manifest_path = os.path.join(EXTENSION_DIR, "manifest.json")
        if not os.path.exists(manifest_path):
            printi(f"[ERRORE] manifest.json non trovato: {manifest_path}")
            return False
            
        printi(f"[OK] Estensione trovata in: {EXTENSION_DIR}")
        return True
    except Exception as e:
        printi(f"[ERRORE] Errore nella verifica estensione: {e}")
        return False

# === TROVA BROWSER ===
browser_path = find_brave_path()
if browser_path:
    printi(f"[INFO] Brave trovato: {browser_path}")
else:
    browser_path = find_chrome_path()
    if browser_path:
        printi(f"[INFO] Brave non trovato, uso Chrome: {browser_path}")
    else:
        printi("[ERRORE] Né Brave né Chrome sono stati trovati. Esco.")
        sys.exit(1)

# === VERIFICA ESTENSIONE PRIMA DI INIZIARE ===
if not verify_extension_loaded():
    printi("[ERRORE] Impossibile procedere senza estensione.")
    sys.exit(1)

# === OPZIONI CHROME ===
options = Options()
options.add_argument("--start-maximized")
options.add_argument(f'--user-data-dir={temp_profile}')
options.add_argument(f"--load-extension={EXTENSION_DIR}")  # ← CARICA ESTENSIONE
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-features=ExternalProtocolRequestPrompt")
options.add_argument("--disable-external-intent-requests")

# Imposta il percorso del browser trovato automaticamente
options.binary_location = browser_path

service = Service(CHROMEDRIVER_PATH)

try:
    driver = webdriver.Chrome(service=service, options=options)
    printi("[OK] Browser avviato con estensione caricata.")
    
    # === ASPETTA CHE L'ESTENSIONE SIA CARICATA ===
    printi("[INFO] Attendo 5 secondi per il caricamento dell'estensione...")
    time.sleep(5)

    # === VERIFICA CHE L'ESTENSIONE SIA ACCESSIBILE ===
    try:
        printi(f"[TEST] Tentativo accesso a: chrome-extension://{EXTENSION_ID}/index.html")
        driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")
        printi("[OK] Estensione accessibile!")
    except Exception as e:
        printi(f"[WARN] Impossibile accedere all'estensione: {e}")
        printi("[INFO] Provo ad aprire chrome://extensions per verificare...")
        driver.get("chrome://extensions/")
        time.sleep(2)
        input("Verifica manualmente se l'estensione è caricata e premi invio...")

    # === LOG IP INIZIALE ===
    printi("IP prima del test")
    log_current_ip()
    time.sleep(2)
    driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")

    # === TEST CONNESSIONE ===
    printi("[TEST] Connessione alla VPN (NL)...")
    try:
        driver.execute_script("vpn.connect('nl')")
        time.sleep(4)
        log_current_ip()
        driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")
        time.sleep(1.5)
    except Exception as e:
        printi(f"[ERRORE] Errore nella connessione VPN: {e}")

    # === TEST DISCONNESSIONE ===
    printi("[TEST] Disconnessione dalla VPN...")
    try:
        driver.execute_script("vpn.disconnect()")
        time.sleep(4)
        log_current_ip()
    except Exception as e:
        printi(f"[ERRORE] Errore nella disconnessione VPN: {e}")

    printi("[OK] Test completato.")
    input("Premi invio per chiudere...")

except Exception as e:
    printi(f"[ERRORE] Errore durante l'avvio del browser: {e}")
finally:
    cleanup()