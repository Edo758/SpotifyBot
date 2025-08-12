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
import time

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

# === LOG IP ===
def log_current_ip():
    try:
        driver.get("https://api.ipify.org?format=text")
        time.sleep(2)
        ip = driver.find_element(By.TAG_NAME, "body").text
        printi(f"[ NUOVO IP] {ip}")
        return ip
    except Exception as e:
        printi("Errore nel rilevamento IP:", e)
        return None

# === POLLING LOG CONSOLE ===
def wait_for_console_message(driver, keyword, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        logs = driver.get_log("browser")
        for entry in logs:
            if keyword in entry["message"]:
                printi(f"[LOG MATCH] '{keyword}' trovato")
                return True
        time.sleep(0.3)
    printi(f"[TIMEOUT] Nessun match per '{keyword}'")
    return False

# === VERIFICA ESTENSIONE ===
def verify_extension_loaded():
    if not os.path.exists(EXTENSION_DIR):
        printi(f"[ERRORE] Cartella estensione non trovata: {EXTENSION_DIR}")
        return False
    manifest_path = os.path.join(EXTENSION_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        printi(f"[ERRORE] manifest.json non trovato: {manifest_path}")
        return False
    printi(f"[OK] Estensione trovata in: {EXTENSION_DIR}")
    return True

# === TROVA BROWSER ===
browser_path = find_brave_path() or find_chrome_path()
if not browser_path:
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
options.add_argument(f"--load-extension={EXTENSION_DIR}")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-features=ExternalProtocolRequestPrompt")
options.add_argument("--disable-external-intent-requests")
options.binary_location = browser_path

service = Service(CHROMEDRIVER_PATH)

try:
    driver = webdriver.Chrome(service=service, options=options)
    printi("[OK] Browser avviato con estensione caricata.")
    time.sleep(5)

    printi(f"[TEST] Tentativo accesso a: chrome-extension://{EXTENSION_ID}/index.html")
    driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")
    printi("[OK] Estensione accessibile!")

    # === IP iniziale ===
    printi("IP prima del test")
    ip_before = log_current_ip()

    # === DISCONNESSIONE ===
    

    # === CONNESSIONE ===
    driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")
    printi("[TEST] Connessione alla VPN (NL)...")
    driver.execute_script("vpn.connect('nl')")
    wait_for_console_message(driver, "forced handshake to the proxy server successfully", timeout=15)
    ip_after_connect = log_current_ip()

    # === DISCONNESSIONE ===
    driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")
    printi("[TEST] Disconnessione VPN...")
    driver.execute_script("vpn.disconnect()")
    if wait_for_console_message(driver, "-- connection disabled"):
        time.sleep(2)  # margine di sicurezza
    ip_after_disconnect = log_current_ip()
    
    printi(f"IP iniziale: {ip_before}")
    printi(f"IP dopo disconnessione: {ip_after_disconnect}")
    printi(f"IP dopo connessione: {ip_after_connect}")

    input("Premi invio per chiudere...")

except Exception as e:
    printi(f"[ERRORE] Errore durante l'avvio del browser: {e}")
finally:
    cleanup()