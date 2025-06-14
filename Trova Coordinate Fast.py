from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Cliccato a posizione: x={x}, y={y}")

print("Fai click per vedere le coordinate.")
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
