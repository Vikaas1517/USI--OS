import json, sys, os
import paho.mqtt.client as mqtt
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.digital_twin import DigitalTwin

BROKER = "broker.emqx.io"
SUB_SENSOR = "usi-os/sensor_data"
SUB_SIM = "usi-os/control/simulate"
PUB_TOPIC = "usi-os/digital_twin"

dt = DigitalTwin()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Twin Engine Connected.")
        client.subscribe(SUB_SENSOR)
        client.subscribe(SUB_SIM)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        is_sim = (msg.topic == SUB_SIM)

        # Physics Calc
        risk = 90 if data.get("temperature", 0) > 100 else 0
        metrics = dt.calculate(data, fail_risk=risk)

        out = {
            # ✅ PASS THE ID SO DASHBOARD KNOWS WHO IS IN CONTROL
            "machine_id": data.get("machine_id", "SIM-01"),
            "simulation_state": metrics["status"],
            "efficiency": metrics["efficiency"],
            "energy": metrics["energy_kwh"],
            "rul": metrics["rul_hours"],
            "rpm": data.get("speed_rpm", 0),
            "temp": data.get("temperature", 0),
            "is_simulation": is_sim
        }
        client.publish(PUB_TOPIC, json.dumps(out))

    except: pass

if hasattr(mqtt, "CallbackAPIVersion"):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
else:
    client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()