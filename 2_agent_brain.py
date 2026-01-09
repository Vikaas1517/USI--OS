import json
import sys
import random
import time
import smtplib # ✅ REQUIRED FOR EMAIL
from email.mime.text import MIMEText # ✅ REQUIRED FOR EMAIL
import paho.mqtt.client as mqtt

# CONFIG
BROKER = "broker.emqx.io"
TOPIC_SENSOR = "usi-os/sensor_data"
TOPIC_SIM = "usi-os/control/simulate"
TOPIC_PUB = "usi-os/agent_msg"

# --- 📧 EMAIL CONFIGURATION (YOUR SETTINGS KEPT) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "vikaas1517@gmail.com"      # <--- YOUR EMAIL
SENDER_PASSWORD = "jglr zjpo aipo fump"    # <--- YOUR PASSWORD
RECEIVER_EMAIL = "sabariraja350@gmail.com" # <--- RECEIVER EMAIL

# --- EMAIL SENDER FUNCTION ---
def send_email_alert(temp, reason):
    try:
        subject = f"🚨 CRITICAL ALERT: Machine Unit-01 STOPPED"
        body = f"""
        URGENT MAINTENANCE REQUEST
        --------------------------
        STATUS: EMERGENCY STOP EXECUTED
        REASON: {reason}
        DETECTED TEMP: {temp}°C
        TIMESTAMP: {time.ctime()}
        
        ACTION REQUIRED:
        1. Inspect Cooling System.
        2. Reset Safety Lockout.
        3. Log Incident in Blockchain Ledger.
        
        -- USI-OS AUTOGUARD AGENT --
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # Connect to Server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Secure connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        
        print("📧 EMAIL ALERT SENT SUCCESSFULLY!")
        return True
    except Exception as e:
        print(f"❌ EMAIL FAILED: {e}")
        return False

# --- 1. ACTIVE INTERVENTION LOGIC (UPDATED WITH DELAY) ---
def take_action(client, data):
    temp = int(data.get("temperature", 0))
    rpm = int(data.get("speed_rpm", 0))
    
    # TRIGGER: Force stop if Temp > 105
    if temp > 105 and rpm > 0:
        # ✅ ADDED: THE 2-SECOND DELAY FOR DEMO VISIBILITY
        print(f"⚠️ HIGH RISK ({temp}°C). PAUSING 2s FOR VISUAL ALERT...")
        time.sleep(2.0) 
        
        print("⚡ AI INTERVENTION: STOPPING MACHINE")
        
        # Stop the machine
        packet = { "speed_rpm": 0, "temperature": 60, "machine_id": "AI-AUTOGUARD", "vibration": 0 }
        client.publish(TOPIC_SIM, json.dumps(packet))
        
        # ✅ KEPT: SEND EMAIL ALERT
        send_email_alert(temp, "Thermal Runaway Detected")
        
        return True
    return False

# --- 2. MESSAGE LOGIC (YOURS KEPT) ---
def generate_advice(data, action_taken):
    temp = int(data.get("temperature", 0))
    rpm = int(data.get("speed_rpm", 0))
    
    if action_taken:
        return f"🔴 CRITICAL INTERVENTION: Machine stopped by AI Autoguard.\n📧 STATUS: Maintenance Email Sent to Supervisor.\n🛠️ ACTION: Manual Reset Required."

    if temp > 100:
        # Slightly updated text to reflect the delay mechanism
        return f"🔴 DANGER: OVERHEATING ({temp}°C)! FAILSAFE ENGAGING IN 2s...\n🔍 DIAGNOSIS: Cooling failure.\n🛠️ ACTION: STAND CLEAR."
    
    if temp > 85:
        return f"⚠️ WARNING: Machine hot ({temp}°C).\n🔍 ANALYSIS: Efficiency drop.\n🛠️ RECOMMENDATION: Reduce speed."

    status = random.choice(["Thermal gradient stable.", "Rotor phasing synchronized.", "Power consumption nominal."])
    step = random.choice(["Maintain current RPM.", "Log batch completion.", "Continue standard cycle."])
    return (
        f"✅ SYSTEM NOMINAL: Operating at peak efficiency ({rpm} RPM).\n"
        f"🔍 DIAGNOSTICS: {status}\n"
        f"🛠️ INSTRUCTION: {step}"
    )

# --- MQTT HANDLERS ---
if hasattr(mqtt, "CallbackAPIVersion"):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
else:
    client = mqtt.Client()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ AI Brain Connected")
        client.subscribe(TOPIC_SENSOR)
        client.subscribe(TOPIC_SIM)
    else:
        print(f"❌ Connection Failed: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        
        action_taken = False
        if payload.get("machine_id") != "AI-AUTOGUARD":
            action_taken = take_action(client, payload)

        advice = generate_advice(payload, action_taken)
        
        response = { "nlp_message": advice, "timestamp": payload.get("timestamp") }
        client.publish(TOPIC_PUB, json.dumps(response))
        
        if action_taken: print(f"⚡ ACTION: Stop Signal Sent")
        else: print(f"📤 Advice: {advice.splitlines()[0]}")

    except Exception as e: print(e)

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()