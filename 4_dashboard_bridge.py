import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import sys
import queue

# --- CONFIGURATION ---
BROKER = "broker.emqx.io"
WS_HOST = "127.0.0.1"
WS_PORT = 9090
TOPIC_SUB = "usi-os/#"

# --- QUEUE & CLIENTS ---
msg_queue = queue.SimpleQueue()
clients = set()

# --- WEBSOCKETS ---
async def broadcast_loop():
    print("🔄 Bridge Broadcast Loop Active")
    while True:
        if not msg_queue.empty():
            message = msg_queue.get()
            if clients:
                await asyncio.gather(*[ws.send(message) for ws in clients], return_exceptions=True)
        await asyncio.sleep(0.01)

async def handle_client(websocket):
    print(f"✅ Dashboard Connected!")
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "SIMULATION":
                    payload = json.dumps(data["payload"])
                    mqtt_client.publish("usi-os/control/simulate", payload)
                    print(f"🎛️ Sim Command: {payload}")
            except: pass
    finally:
        clients.remove(websocket)
        print("❌ Dashboard Disconnected.")

# --- MQTT ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Bridge Connected to {BROKER}")
        client.subscribe(TOPIC_SUB)
    else:
        print(f"❌ Connection Failed: {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode()
        try: payload_json = json.loads(payload_str)
        except: payload_json = {"raw_data": payload_str}

        ws_packet = json.dumps({ "topic": msg.topic, "payload": payload_json })
        msg_queue.put(ws_packet)
    except: pass

# --- MAIN ---
if hasattr(mqtt, "CallbackAPIVersion"):
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
else:
    mqtt_client = mqtt.Client()

async def main():
    print(f"🚀 Starting Bridge Service...")
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(BROKER, 1883, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"⚠️ MQTT Start Failed: {e}")

    print(f"✅ WebSocket Listening on ws://{WS_HOST}:{WS_PORT}")
    asyncio.create_task(broadcast_loop())
    
    async with websockets.serve(handle_client, WS_HOST, WS_PORT):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped.")