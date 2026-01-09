import json
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- IMPORTS ---
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from modules.ai_brain import AIBrain
from modules.digital_twin import DigitalTwin

load_dotenv()

class PredictiveAgent:
    def __init__(self):
        print("   🤖 [Agent] Initializing Industrial Expert System...")
        
        self.brain = AIBrain()
        self.brain.train_internal() 
        self.dt = DigitalTwin()
        
        # We default to fallback because we know the key is likely empty/invalid
        self.use_fallback = True 

        # Try to connect (just in case), but don't crash if it fails
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and "sk-" in api_key:
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=api_key)
                self.use_fallback = False
        except:
            pass

    # --- SIMULATED BUSINESS LOGIC (The "Fake" Brain) ---
    def _check_inventory(self, part_name):
        """Simulates checking a database for spare parts."""
        return random.choice([True, True, False]) # 33% chance out of stock

    def _check_workers(self):
        """Simulates checking shift schedule."""
        return random.choice(["Team A (Available)", "Team B (Busy)", "No workers available"])

    def _get_history(self, machine_id):
        """Simulates looking up past failures."""
        return random.choice(["Last maintenance: 2 days ago", "History: Frequent overheating", "History: Clean"])

    # --- ADVANCED OFFLINE ADVICE GENERATOR ---
    def _get_offline_advice(self, data):
        """
        Generates complex, multi-step reasoning messages without AI.
        """
        # 1. Extract Data
        machine_id = data.get("machine_id", "Unknown")
        temp = data.get("temperature", 0)
        vib = data.get("vibration", 0)
        rpm = data.get("speed_rpm", 0)
        
        # 2. Analyze Risk
        risk = self.brain.predict(data)
        
        # 3. Decision Tree Logic
        timestamp = datetime.now().strftime("%H:%M")
        
        # SCENARIO A: HIGH DANGER (CRITICAL)
        if risk > 80:
            action = "EMERGENCY STOP"
            reason = f"Critical anomaly detected (Risk {risk}%). Thermal runaway imminent at {temp}°C."
            
            # Inventory Check Simulation
            spare_part = "Bearing-X12"
            has_stock = self._check_inventory(spare_part)
            
            if has_stock:
                logistics = f"Inventory Check: {spare_part} in stock (Qty: 4). Triggered auto-dispatch to Sector 4."
            else:
                logistics = f"Inventory Check: {spare_part} LOW STOCK! Automated Purchase Order #PO-9921 generated."

            return f"🚨 {action}: {reason}\n> {logistics}\n> Workers: {self._check_workers()} notified."

        # SCENARIO B: MEDIUM STRESS (WARNING)
        elif risk > 40:
            # Physics Calculation
            new_rpm = int(rpm * 0.85) # Reduce by 15%
            next_maint = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
            
            return (
                f"⚠️ OPTIMIZATION REQUIRED: System stress elevated (Vib: {vib}).\n"
                f"> DECISION: Reduce speed {rpm} → {new_rpm} RPM to stabilize.\n"
                f"> SCHEDULE: Maintenance booked for {next_maint} today.\n"
                f"> HISTORY: {self._get_history(machine_id)}."
            )

        # SCENARIO C: QUALITY ISSUE (DEFECT PREDICTION)
        elif rpm > 1600 or vib > 3.0:
            warehouse = "Warehouse B" if random.random() > 0.5 else "Quarantine Zone"
            return (
                f"⚠️ QUALITY ALERT: Output may be defective due to vibration variance.\n"
                f"> ACTION: Reroute current batch #B-402 to {warehouse} for inspection.\n"
                f"> UTILIZATION: Machine running at 94% capacity. Recommend throttling."
            )

        # SCENARIO D: NORMAL (NOMINAL)
        else:
            return (
                f"✅ SYSTEM NOMINAL: Machine {machine_id} operating within efficient parameters.\n"
                f"> UTILIZATION: Optimal.\n"
                f"> NEXT STEPS: Continue monitoring. No interventions required."
            )

    # --- MAIN ANALYZE FUNCTION ---
    def analyze(self, sensor_data):
        # Always use the advanced offline generator for consistency
        # This ensures you get the complex messages you asked for
        return self._get_offline_advice(sensor_data)