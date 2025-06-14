from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.common.by import By # type: ignore
import time
import pyautogui # type: ignore
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
EXTENSION_PATH = os.path.join(BASE_DIR, "CyberGhost.crx")
USER_DATA_DIR = os.path.join(BASE_DIR, "UserDataChrome")
EXTENSION_ID = "ffbkglfijbcbgblgflchnbphjdllaogb"

options = Options()
options.add_argument("--start-maximized")
options.add_extension(EXTENSION_PATH)
options.add_argument(f'--user-data-dir={USER_DATA_DIR}')

# Avvia il browser con le opzioni specificate
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# === APRI SPOTIFY ===
driver.get("https://open.spotify.com")
print("Avvia manualmente una canzone su Spotify...")
time.sleep(10)

# === FUNZIONI ===
def to_seconds(t): 
    mins, secs = map(int, t.split(':'))
    return mins * 60 + secs

def change_ip():
    try:
        print("[🔌 VPN] Apro l'estensione CyberGhost con clic GUI...")
        # Posizione dell'icona dell'estensione nella barra: personalizza queste coordinate
        pyautogui.moveTo(1735, 60)  # Cambia con le coordinate effettive del tuo schermo
        pyautogui.click()
        time.sleep(4)

        print("[🔒 VPN] Disconnetto...")
        pyautogui.moveTo(1592, 260)  # Coordinate del pulsante "Connect"
        pyautogui.click()
        time.sleep(10)

        print("[🌍 VPN] Seleziono Connect...")
        pyautogui.moveTo(1592, 260)  # Coordinate del pulsante "Connect"
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
                print("Nuova canzone rilevata (tempo rimanente è aumentato).")
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
