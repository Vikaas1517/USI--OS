import json
import time
import paho.mqtt.client as mqtt
from modules.blockchain import IndustrialBlockchain

# CONFIG
BROKER = "broker.emqx.io"
TOPIC_LISTEN = "usi-os/agent_msg"  # Listen to AI Advice
TOPIC_PUB_LEDGER = "usi-os/blockchain"

# Initialize Blockchain
ledger = IndustrialBlockchain()
print("🔗 Blockchain Node Online & Listening...")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connected to {BROKER}")
        client.subscribe(TOPIC_LISTEN)
    else:
        print(f"❌ Connection Failed: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        nlp_text = payload.get("nlp_message", "")
        
        # --- SMART FILTER ---
        # We trigger a blockchain entry if the AI text contains specific alert markers.
        # The new AI uses emojis: 🔴 for Danger, ⚠️ for Warning.
        is_critical = "🔴" in nlp_text or "DANGER" in nlp_text
        is_warning = "⚠️" in nlp_text or "WARNING" in nlp_text
        
        if is_critical or is_warning:
            severity = "CRITICAL" if is_critical else "WARNING"
            
            # Create Block
            new_block = ledger.add_block({
                "machine": "UNIT-01", # Default if missing
                "event": f"{severity}_ALERT",
                "details": nlp_text.split("\n")[0] # Save just the headline
            })
            
            # Broadcast to Dashboard
            block_data = {
                "index": new_block.index,
                "hash": new_block.hash,
                "data": new_block.data,
                "timestamp": new_block.timestamp
            }
            client.publish(TOPIC_PUB_LEDGER, json.dumps(block_data))
            
            print(f"🧱 Block #{new_block.index} Mined! [{severity}]")

    except Exception as e:
        print(f"Error processing block: {e}")

# --- MQTT SETUP ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) if hasattr(mqtt, "CallbackAPIVersion") else mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()