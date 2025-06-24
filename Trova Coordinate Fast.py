from pynput import mouse
import time

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Cliccato a posizione: x={x}, y={y}")

print("Fai click per vedere le coordinate. Premi Ctrl+C per uscire.")

listener = mouse.Listener(on_click=on_click)
listener.start()

try:
    while True:
        time.sleep(0.1)  # mantiene vivo lo script senza bloccare il main thread
except KeyboardInterrupt:
    print("\nInterruzione richiesta")
    listener.stop()
