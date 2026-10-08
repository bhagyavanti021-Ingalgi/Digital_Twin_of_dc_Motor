# Hyundai Motor Digital Twin

## Files
- `index.html`        → Dashboard (open with Live Server in VS Code)
- `server.js`         → WebSocket server (run on laptop)
- `package.json`      → Node.js dependencies
- `sensor_client1.py` → Raspberry Pi sensor script

## Setup

### Laptop
```bash
npm install
node server.js
```

### Raspberry Pi
```bash
pip install websockets adafruit-circuitpython-dht --break-system-packages
sudo apt install libgpiod2 -y
python3 sensor_client1.py
```

### Dashboard
Open index.html with VS Code Live Server

## Sensors
- DHT11 Temperature/Humidity → GPIO4
- Vibration Sensor           → GPIO17

## Run Order
1. Laptop CMD  → node server.js
2. Pi terminal → python3 sensor_client1.py
3. VS Code     → Go Live
