from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from vpn_lock_manager import VPNLock
import time
import pyautogui
import os
import tempfile
import shutil
import sys
import atexit
import glob
sys.stdout.reconfigure(encoding='utf-8')

# === PREFISSO ISTANZA ===
if len(sys.argv) > 1:
    ISTANZA_ID = sys.argv[1]
else:
    ISTANZA_ID = "?"
def printi(*args, **kwargs):
    if 'flush' not in kwargs:
        kwargs['flush'] = True
    print(f"[ISTANZA {ISTANZA_ID}]", *args, **kwargs)

import signal
import win32gui
import win32con
import win32process
import psutil
import winreg
import ctypes


# === COSTANTI ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
EXTENSION_DIR = os.path.join(BASE_DIR, "CyberGhost")

# === CREA PROFILO TEMPORANEO ===
# Leggi l'ID istanza dal primo argomento della riga di comando, se presente
if len(sys.argv) > 1:
    ISTANZA_ID = sys.argv[1]
else:
    ISTANZA_ID = "?"

temp_profile = tempfile.mkdtemp()

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

browser_path = find_brave_path()
if browser_path:
    printi("[INFO] Brave trovato:")
else:
    browser_path = find_chrome_path()
    if browser_path:
        printi("[INFO] Brave non trovato, uso Chrome:", browser_path)
    else:
        printi("[ERRORE] Né Brave né Chrome sono stati trovati. Esco.")
        sys.exit(1)


# === OPZIONI CHROME ===
options = Options()
options.add_argument("--start-maximized")
options.add_argument(f'--user-data-dir={temp_profile}')  # profilo temporaneo
options.add_argument(f"--load-extension={EXTENSION_DIR}")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-features=ExternalProtocolRequestPrompt")  # Disabilita la notifica "Apri nell'app"
options.add_argument("--disable-external-intent-requests")  # Blocca richieste intent esterne
options.binary_location = browser_path

service = Service(CHROMEDRIVER_PATH)

driver = None

done_cleanup = False

def cleanup_and_exit(signum=None, frame=None, from_atexit=False):
    global driver, temp_profile, done_cleanup
    if done_cleanup:
        return
    done_cleanup = True
    printi("\n[INFO] Arresto script, chiudo Chrome e cancello profilo temporaneo...")
    if driver:
        try:
            driver.quit()
        except:
            pass
    if os.path.exists(temp_profile):
        shutil.rmtree(temp_profile)
        printi("[INFO] Profilo temporaneo eliminato.")
    else:
        printi("[INFO] Profilo temporaneo già rimosso.")

    temp_dir = tempfile.gettempdir()
    for pattern in ['chrome_url_fetcher_*', 'scoped_dir*', 'tmp*']:
        for folder in glob.glob(os.path.join(temp_dir, pattern)):
            try:
                shutil.rmtree(folder)
            except Exception:
                pass
    if not from_atexit:
        sys.exit(0)

# === FUNZIONI PER TROVARE LA FINESTRA DI CHROME DAL PID ===
def get_hwnds_for_pid(pid):
    hwnds = []
    def enum_window_callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True
    win32gui.EnumWindows(enum_window_callback, hwnds)
    return hwnds

def minimize_chrome_window():
    try:
        chromedriver_pid = driver.service.process.pid
        p = psutil.Process(chromedriver_pid)
        child_pids = [child.pid for child in p.children(recursive=True)]
        child_pids.append(chromedriver_pid)

        for pid in child_pids:
            hwnds = get_hwnds_for_pid(pid)
            if hwnds:
                hwnd = hwnds[0]
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                printi(f"[INFO] Finestra Chrome minimizzata (PID={pid}).")
                return
        printi("[INFO] Nessuna finestra trovata da minimizzare.")
    except Exception as e:
        printi(f"[ERRORE] Errore durante la minimizzazione: {e}")

def focus_chrome_window():
    try:
        chromedriver_pid = driver.service.process.pid
        p = psutil.Process(chromedriver_pid)
        child_pids = [child.pid for child in p.children(recursive=True)]
        child_pids.append(chromedriver_pid)

        for pid in child_pids:
            hwnds = get_hwnds_for_pid(pid)
            if hwnds:
                hwnd = hwnds[0]
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                try:
                    ctypes.windll.user32.AllowSetForegroundWindow(pid)
                    win32gui.SetForegroundWindow(hwnd)
                    if win32gui.GetForegroundWindow() != hwnd:
                        raise Exception("Finestra non in primo piano dopo SetForegroundWindow")

                except Exception as fe:
                    printi(f"[] SetForegroundWindow fallito, provo fallback: {fe}")
                    try:
                        win32gui.BringWindowToTop(hwnd)
                        win32gui.SetActiveWindow(hwnd)
                    except Exception as fallback_e:
                        printi(f"[] Fallback fallito: {fallback_e}")
                printi(f"[] Finestra con PID {pid} massimizzata e portata in primo piano.")
                return

        printi("[] Nessuna finestra Chrome trovata tra i processi figli.")
    except Exception as e:
        printi("[] Errore durante il focus della finestra:", e)

def safe_get(url, retries=3, delay=5):
    for attempt in range(retries):  # ripeti fino a 3 tentativi
        try:
            driver.get(url)  # prova ad aprire la pagina
            return True  # se va, esci subito
        except Exception as e:
            printi(f"[!] Tentativo {attempt+1}] Errore nel caricamento URL: {e}")
            time.sleep(delay)  # aspetta qualche secondo e riprova
    printi(f"[X] Impossibile raggiungere {url} dopo {retries} tentativi.")
    return False  # dopo 3 fallimenti, restituisci False



# Cattura segnali di interruzione (CTRL+C), terminazione e break (Windows)
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, cleanup_and_exit)

# Registra la funzione di cleanup anche con atexit
atexit.register(lambda: cleanup_and_exit(from_atexit=True))

# === AVVIO CHROME ===
try:
    driver = webdriver.Chrome(service=service, options=options)
except Exception as e:
    printi("[ERRORE] Chrome non si è avviato correttamente:\n", e)
    cleanup_and_exit()

# === APRI SPOTIFY ===
if not safe_get("https://open.spotify.com"):
    # esci dallo script se non riesce a caricare
    cleanup_and_exit()

printi("Avvia manualmente una canzone su Spotify...")
time.sleep(10)

# === FUNZIONI DI SUPPORTO ===
def to_seconds(t):
    mins, secs = map(int, t.split(':'))
    return mins * 60 + secs

def change_ip():
    lock = VPNLock()
    try:
        lock.acquire()
        printi("[ VPN] Lock acquisito.")
        printi("[ VPN] Apro l'estensione CyberGhost con clic GUI...")
        focus_chrome_window()
        time.sleep(0.3)
        # 🔑 Simula scorciatoia tastiera: Ctrl + Shift + Y
        pyautogui.hotkey('ctrl', 'shift', 'y')
        time.sleep(0.7)

        printi("[ VPN] Disconnetto...")
        pyautogui.moveTo(1582, 252) # ← tasto ON/OFF
        pyautogui.click()
        time.sleep(3)

        printi("[ VPN] Riconnetto...")
        pyautogui.hotkey('ctrl', 'shift', 'y') # Riapre il popus dell'estensione se si chiudesse (se fosse ancora aperto non si chiude)
        time.sleep(0.1)
        pyautogui.moveTo(1582, 252) # ← tasto ON/OFF
        pyautogui.click()
        time.sleep(3)
        printi("[ VPN] Connessione stabilita.")
    except Exception as e:
        printi("Errore nel cambio IP/VPN (GUI):", e)
    finally:
        try:
            lock.release()
        except Exception as e:
            printi("Errore nel rilascio del lock:", e)


def log_current_ip():
    try:
        driver.get("https://api.ipify.org?format=text")
        time.sleep(3)
        ip = driver.find_element(By.TAG_NAME, "body").text
        printi(f"[ NUOVO IP] {ip}")
    except Exception as e:
        printi("Errore nel rilevamento IP:", e)

def switch_to_spotify_tab_or_none():
    """
    Cerca tra tutte le schede aperte una di Spotify,
    se la trova la seleziona e ritorna True,
    altrimenti ritorna False.
    """
    handles = driver.window_handles
    for handle in handles:
        try:
            driver.switch_to.window(handle)
            url = driver.current_url
            if "open.spotify.com" in url:
                print("[INFO] Trovata scheda Spotify:", url)
                return True
        except Exception as e:
            print("[WARN] Scheda non disponibile o chiusa:", handle, e)
            continue
    return False

def play_song():
    track_url = "https://open.spotify.com/intl-it/track/2IUePLNmTEAXB7swaR9J2b?si=adf2ec19d0ea4e84"
    driver.get(track_url)
    # Prova a chiudere eventuali popup di protocollo
    try:
        driver.execute_script("window.onbeforeunload = null;")
    except Exception:
        pass
    printi(" Caricamento della pagina del brano...")

    try:
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label]')))
        time.sleep(1)

        for attempt in range(3):  # solo 3 tentativi
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label]')
            play_button = None
            is_playing = False

            for btn in buttons:
                label = btn.get_attribute("aria-label")
                if label == "Pause":
                    is_playing = True
                    break
                elif label == "Play" and play_button is None:
                    play_button = btn

            if is_playing:
                printi(" Canzone in riproduzione confermata.")
                return

            if play_button:
                printi(f" Tentativo {attempt+1}: clic sul pulsante Play...")
                try:
                    play_button.click()
                    time.sleep(2)
                except Exception as e:
                    printi(" Errore nel clic:", e)
            else:
                printi(f" Tentativo {attempt+1}: pulsante Play non trovato. Riprovo...")

            time.sleep(2)

        printi(" Impossibile avviare la canzone dopo 3 tentativi.")

    except Exception as e:
        printi(" Errore durante il caricamento o l'avvio:", e)



def wait_song_or_track_change():
    last_remaining = None
    while True:
        time.sleep(1)
        try:
            current_time = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="playback-position"]').text
            total_time = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="playback-duration"]').text

            current_sec = to_seconds(current_time)
            total_sec = to_seconds(total_time)
            remaining = total_sec - current_sec

            print(f"Canzone in riproduzione: tempo rimanente {remaining} secondi")

            if last_remaining is not None and remaining > last_remaining + 1:
                print("Nuova canzone rilevata.")
                break

            if remaining <= 0:
                print("Canzone terminata.")
                break

            last_remaining = remaining

        except Exception as e:
            # Se il problema è che la scheda è chiusa
            if "no such window" in str(e).lower():
                print("[WARN] Scheda chiusa o non più disponibile, cerco un'altra scheda Spotify...")
                if switch_to_spotify_tab_or_none():
                    print("[INFO] Passato a nuova scheda Spotify, continuo...")
                    continue
                else:
                    print("[ERRORE] Nessuna scheda Spotify trovata, ricarico Spotify...")
                    try:
                        driver.get("https://open.spotify.com")
                        time.sleep(5)
                    except Exception as e2:
                        print("[ERRORE] Impossibile ricaricare Spotify:", e2)
                    continue
            else:
                print("[ERRORE] Errore imprevisto:", e)
                time.sleep(5)

# Ottimizzazione attesa iniziale
printi(" Attendere 20 secondi prima dell'inizio del ciclo...")
for i in range(5, 0, -1):
    printi(f"Inizio in {i} secondi...", end='\r', flush=True)
    time.sleep(1)
printi("")
printi("\n Inizio del ciclo principale.\n")

# === LOOP PRINCIPALE ===
while True:
    printi("Aspetto che la canzone finisca o cambi...")
    wait_song_or_track_change()

    printi("Cambiando IP...")
    change_ip()

    printi("Verifico l’IP corrente...")
    log_current_ip()
    minimize_chrome_window()

    printi("Avvio nuova canzone...")
    play_song()
