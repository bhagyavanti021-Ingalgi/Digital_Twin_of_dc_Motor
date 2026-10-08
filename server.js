const WebSocket = require('ws');

const server = new WebSocket.Server({ port: 3000 });
console.log('✅ Server running on ws://localhost:3000');
console.log('   Waiting for Raspberry Pi and Browser...');

const clients = new Set();

server.on('connection', (ws, req) => {
    const ip = req.socket.remoteAddress;
    console.log(`🔌 Connected: ${ip}`);
    clients.add(ws);

    ws.on('message', (raw) => {
        try {
            const msg = JSON.parse(raw);

            // Forward ALL messages to ALL other clients
            clients.forEach(client => {
                if (client !== ws && client.readyState === WebSocket.OPEN) {
                    client.send(raw.toString());
                }
            });

            // Log Pi sensor data
            if (msg.type === 'iot_reading') {
                console.log(`📡 Pi data → temp:${msg.data.temp} vib:${msg.data.vib} rpm:${msg.data.rpm}`);
            }
        } catch(e) {
            console.log('Parse error:', e);
        }
    });

    ws.on('close', () => {
        clients.delete(ws);
        console.log(`❌ Disconnected: ${ip}`);
    });
});
