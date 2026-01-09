import json, random, time
from datetime import datetime
import paho.mqtt.client as mqtt

# CONFIG
BROKER = "broker.emqx.io"
# ✅ CHANGED: Standardized Topic
TOPIC = "usi-os/sensor_data"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

machines = ["TURBINE-01", "PUMP-02", "CNC-03"]

print(f"🚀 Streaming to {TOPIC}...")

while True:
    try:
        machine = random.choice(machines)
        # Simulate crisis randomly (10% chance)
        is_crisis = random.random() > 0.9 
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "machine_id": machine,
            "temperature": round(random.uniform(105, 120) if is_crisis else random.uniform(70, 80), 1),
            "vibration": round(random.uniform(2.0, 3.5), 2),
            "speed_rpm": random.randint(1400, 1600),
            "torque": 180,
            "pressure": 6.0,
            "tool_wear": random.randint(10, 30)
        }
        
        client.publish(TOPIC, json.dumps(payload))
        print(f"[SENT] {machine} | Temp: {payload['temperature']}")
        time.sleep(3)
    except Exception as e:
        print(f"Error: {e}")