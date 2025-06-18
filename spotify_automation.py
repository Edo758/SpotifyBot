from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.service import Service  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
import time
import pyautogui  # type: ignore
import os
import tempfile
import shutil
import sys
import signal
import win32gui
import win32con
import win32process
import psutil

# === COSTANTI ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
EXTENSION_PATH = os.path.join(BASE_DIR, "CyberGhost.crx")

# === CREA PROFILO TEMPORANEO ===
temp_profile = tempfile.mkdtemp()

# === OPZIONI CHROME ===
options = Options()
options.add_argument("--start-maximized")
options.add_argument(f'--user-data-dir={temp_profile}')  # profilo temporaneo
options.add_extension(EXTENSION_PATH)
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

service = Service(CHROMEDRIVER_PATH)

driver = None

def cleanup_and_exit(signum=None, frame=None):
    global driver, temp_profile
    print("\n[INFO] Arresto script, chiudo Chrome e cancello profilo temporaneo...")
    if driver:
        try:
            driver.quit()
        except:
            pass
    if os.path.exists(temp_profile):
        shutil.rmtree(temp_profile)
        print("[INFO] Profilo temporaneo eliminato.")
    else:
        print("[INFO] Profilo temporaneo già rimosso.")
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
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)  # <-- Aggiunto
                win32gui.SetForegroundWindow(hwnd)
                print(f"[🪟] Finestra con PID {pid} massimizzata e portata in primo piano.")
                return
        print("[⚠️] Nessuna finestra Chrome trovata tra i processi figli.")
    except Exception as e:
        print("[⚠️] Errore durante il focus della finestra:", e)

# Cattura segnali di interruzione (CTRL+C) e terminazione
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

# === AVVIO CHROME ===
try:
    driver = webdriver.Chrome(service=service, options=options)
except Exception as e:
    print("[ERRORE] Chrome non si è avviato correttamente:\n", e)
    cleanup_and_exit()

# === APRI SPOTIFY ===
driver.get("https://open.spotify.com")
print("Avvia manualmente una canzone su Spotify...")
time.sleep(10)

# === FUNZIONI DI SUPPORTO ===
def to_seconds(t):
    mins, secs = map(int, t.split(':'))
    return mins * 60 + secs

def change_ip():
    try:
        print("[🔌 VPN] Apro l'estensione CyberGhost con clic GUI...")
        focus_chrome_window()
        pyautogui.moveTo(1737, 61)  # ← personalizza se necessario
        pyautogui.click()
        time.sleep(0.5)

        print("[🔒 VPN] Disconnetto...")
        pyautogui.moveTo(1595, 260)
        pyautogui.click()
        time.sleep(3)

        print("[🌍 VPN] Riconnetto...")
        pyautogui.moveTo(1595, 260)
        pyautogui.click()
        time.sleep(3)
        print("[✅ VPN] Connessione stabilita.")
    except Exception as e:
        print("Errore nel cambio IP/VPN (GUI):", e)

def log_current_ip():
    try:
        driver.get("https://api.ipify.org?format=text")
        time.sleep(3)
        ip = driver.find_element(By.TAG_NAME, "body").text
        print(f"[🆕 NUOVO IP] {ip}")
    except Exception as e:
        print("Errore nel rilevamento IP:", e)

def play_song():
    track_url = "https://open.spotify.com/track/25J3gcZhNjzBwcaDfZjQli"
    driver.get(track_url)
    time.sleep(2)
    try:
        play_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Play"]')
        play_button.click()
        print("Canzone avviata.")
    except Exception as e:
        print("Errore nell'avviare la canzone:", e)

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
            print("Errore nel recupero tempi o stato canzone, riprovo...", e)
            time.sleep(5)

# === LOOP PRINCIPALE ===
while True:
    print("Aspetto che la canzone finisca o cambi...")
    wait_song_or_track_change()

    print("Cambiando IP...")
    change_ip()

    print("Verifico l’IP corrente...")
    log_current_ip()

    print("Avvio nuova canzone...")
    play_song()
