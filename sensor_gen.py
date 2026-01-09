import random

class SensorGenerator:
    def get_data(self, scenario="NORMAL"):
        # Base Healthy Data
        data = {
            "temperature": round(random.uniform(70, 80), 1),
            "vibration": round(random.uniform(2.0, 3.5), 2),
            "speed_rpm": 1500,
            "torque": 180,
            "pressure": 6.0,
            "tool_wear": random.randint(10, 30)
        }

        # Apply Scenario Logic
        if scenario == "OVERHEAT":
            data["temperature"] = round(random.uniform(105, 120), 1)
        elif scenario == "VIBRATION":
            data["vibration"] = round(random.uniform(6.5, 9.0), 2)
            data["speed_rpm"] = 1450
        elif scenario == "DEFECTIVE":
            data["pressure"] = round(random.uniform(1.0, 3.0), 1)
            data["tool_wear"] = 90
        
        return data