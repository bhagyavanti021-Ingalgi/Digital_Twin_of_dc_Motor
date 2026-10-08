import asyncio
import websockets
import json
import random
import RPi.GPIO as GPIO

# ── GPIO SETUP FIRST ──
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
VIB_PIN = 17
GPIO.setup(VIB_PIN, GPIO.IN)

# ── DHT SETUP AFTER GPIO ──
import board
import adafruit_dht
dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)

# ── SERVER CONFIG ──
SERVER_IP   = "192.168.1.105"   # ← Your laptop IP
SERVER_PORT = 3000

last_temp     = 32.5
last_humidity = 36.0

print("✅ Real sensors ready!")
print("   DHT11     → GPIO4")
print("   Vibration → GPIO17")
print(f"   Server    → {SERVER_IP}:{SERVER_PORT}")

def read_sensors():
    global last_temp, last_humidity

    # ── REAL DHT11 Temperature ──
    try:
        t = dht.temperature
        h = dht.humidity
        if t is not None and h is not None:
            last_temp     = t
            last_humidity = h
    except Exception:
        pass  # use last good value

    # ── REAL Vibration ──
    try:
        vib_raw = GPIO.input(VIB_PIN)
    except Exception:
        vib_raw = 0
    vib = 1.5 if vib_raw == 1 else 0.1

    # ── Warning check ──
    warning = "None"
    if last_temp > 40:
        warning = "Overheating"
    elif vib_raw == 1:
        warning = "Vibration"

    print(f"REAL → Temp:{last_temp}C  "
          f"Humidity:{last_humidity}%  "
          f"Vib:{'YES' if vib_raw else 'No'}  "
          f"Warning:{warning}")

    return {
        "temp":      round(float(last_temp), 2),
        "humidity":  round(float(last_humidity), 2),
        "vib":       vib,
        "cur":       round(180 + random.uniform(-5, 10), 1),
        "rpm":       round(1480 + random.uniform(-20, 20), 1),
        "brg":       round(float(last_temp) * 0.65, 2),
        "pf":        round(0.88 + random.uniform(-0.02, 0.02), 3),
        "eff":       round(95 + random.uniform(-1, 1), 2),
        "warning":   warning,
        "latencyMs": 12
    }

async def stream():
    uri = f"ws://{SERVER_IP}:{SERVER_PORT}"
    print(f"\nConnecting to Digital Twin at {uri}...")
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("✅ Connected to Digital Twin!")
                while True:
                    data = read_sensors()
                    await ws.send(json.dumps({
                        "type": "iot_reading",
                        "data": data
                    }))
                    await asyncio.sleep(1)
        except Exception as e:
            if 'GPIO' in str(e):
                try:
                    GPIO.cleanup()
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(VIB_PIN, GPIO.IN)
                except:
                    pass
            print(f"❌ Error: {e} - retrying in 3s...")
            await asyncio.sleep(3)

try:
    asyncio.run(stream())
except KeyboardInterrupt:
    print("\nStopped by user")
    GPIO.cleanup()
