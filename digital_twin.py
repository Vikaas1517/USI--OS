import random

class DigitalTwin:
    def __init__(self):
        # ✅ FIX: Initialize constants here so the Publisher can access them
        self.OPTIMAL_RPM = 1500
        self.MAX_RPM = 3000
        self.BASE_QUALITY = 100

    def calculate(self, data, fail_risk=0):
        """
        Inputs: Sensor Data (dict), Failure Risk % (from AI Brain)
        Outputs: Rich Digital Twin Telemetry
        """
        rpm = data.get("speed_rpm", 0)
        torque = data.get("torque", 0)
        vib = data.get("vibration", 0)
        temp = data.get("temperature", 0)

        # --- 1. Efficiency Calculation ---
        if rpm > 0:
            deviation = abs(rpm - self.OPTIMAL_RPM)
            efficiency = max(0, 100 - (deviation / self.OPTIMAL_RPM * 100))
        else:
            efficiency = 0

        # --- 2. Energy Consumption ---
        safe_torque = torque if torque > 0 else (rpm * 0.05)
        energy_kwh = (safe_torque * rpm) / 9550

        # --- 3. Output Quality Prediction ---
        quality_score = self.BASE_QUALITY - (vib * 15)
        quality_score = max(0, min(100, quality_score))
        
        quality_grade = "A (Perfect)"
        if quality_score < 90: quality_grade = "B (Good)"
        if quality_score < 75: quality_grade = "C (Fair)"
        if quality_score < 60: quality_grade = "D (Poor)"

        # --- 4. RUL Calculation ---
        if fail_risk > 80:
            rul = 4
            status = "CRITICAL"
        elif fail_risk > 50:
            rul = 48
            status = "WARNING"
        else:
            rul = 720
            status = "OPTIMAL"

        return {
            "efficiency": round(efficiency, 1),
            "energy_kwh": round(energy_kwh, 2),
            "quality_score": round(quality_score, 1),
            "quality_grade": quality_grade,
            "rul_hours": rul,
            "status": status
        }