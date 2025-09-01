import os
import sys
import tempfile
import shutil
import atexit
import signal
import random
import time
import winreg
import subprocess
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# === CONFIGURAZIONE ===
NUM_INSTANZE = 10   # <-- cambia qui quante istanze vuoi
EXTENSION_ID = "clnceilhfmekjpiacjjlmdohilnogoej"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
EXTENSION_DIR = os.path.join(BASE_DIR, "CyberGhost")

# Lista processi webdriver
drivers = []
profiles = []

# === FUNZIONI DI RICERCA BROWSER ===
def find_browser_path_from_registry(browser_exe_name):
    key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{browser_exe_name}"
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        try:
            with winreg.OpenKey(root, key_path) as key:
                path, _ = winreg.QueryValueEx(key, "")
                return path
        except Exception:
            pass
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
    return (find_browser_path_from_registry("brave.exe") or
            find_browser_path_default("BraveSoftware\\Brave-Browser"))

def find_chrome_path():
    return (find_browser_path_from_registry("chrome.exe") or
            find_browser_path_default("Google\\Chrome"))

# === SCELTA BROWSER (Brave → fallback su Chrome) ===
browser_path = find_brave_path() or find_chrome_path()
if not browser_path:
    print("[ERRORE] Nessun browser trovato.")
    sys.exit(1)

print("[INFO] Browser trovato:", browser_path)

# === CREAZIONE ISTANZE ===
def start_instance(idx):
    temp_profile = tempfile.mkdtemp()
    profiles.append(temp_profile)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={temp_profile}")
    options.add_argument(f"--load-extension={EXTENSION_DIR}")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-features=ExternalProtocolRequestPrompt")
    options.add_argument("--disable-external-intent-requests")
    options.binary_location = browser_path

    service = Service(CHROMEDRIVER_PATH)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        drivers.append(driver)
        print(f"[ISTANZA {idx}] Avviata con profilo {temp_profile}")

        # Apri CyberGhost
        driver.get(f"chrome-extension://{EXTENSION_ID}/index.html")
        time.sleep(2)

        # Apri Spotify
        driver.switch_to.new_window('tab')
        driver.get("https://open.spotify.com")
        print(f"[ISTANZA {idx}] Spotify aperto.")

    except Exception as e:
        print(f"[ERRORE] Impossibile avviare istanza {idx}:", e)

# === CLEANUP ===
def cleanup_and_exit(signum=None, frame=None, from_atexit=False):
    print("\n[INFO] Arresto in corso, chiusura istanze...")
    for d in drivers:
        try:
            d.quit()
        except:
            pass
    for p in profiles:
        try:
            shutil.rmtree(p)
            print("[INFO] Profilo eliminato:", p)
        except:
            pass
    if not from_atexit:
        sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, cleanup_and_exit)
atexit.register(lambda: cleanup_and_exit(from_atexit=True))

# === AVVIO TUTTE LE ISTANZE ===
for i in range(1, NUM_INSTANZE + 1):
    start_instance(i)
    time.sleep(random.uniform(2, 5))  # leggero delay tra le aperture

print("\n[INFO] Tutte le istanze sono state avviate.")
print("[INFO] Rimarranno attive finché non premi CTRL+C.\n")

# === LOOP PRINCIPALE ===
while True:
    time.sleep(5)
