import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class AIBrain:
    def __init__(self):
        self.maint_model = RandomForestClassifier(n_estimators=100)
        self.is_trained = False

    def train_internal(self):
        # Generate Synthetic Data
        df = pd.DataFrame({
            'temperature': np.random.uniform(60, 90, 500),
            'vibration': np.random.uniform(2, 4, 500),
            'speed_rpm': np.random.uniform(1400, 1600, 500),
            'torque': np.random.uniform(150, 200, 500),
            'pressure': np.random.uniform(5, 7, 500),
            'tool_wear': np.random.uniform(0, 100, 500)
        })
        # Define Failure Logic
        df['failure'] = np.where((df['temperature'] > 100) | (df['vibration'] > 6), 1, 0)
        
        X = df[['temperature', 'vibration', 'speed_rpm', 'torque', 'pressure', 'tool_wear']]
        y = df['failure']
        
        self.maint_model.fit(X, y)
        self.is_trained = True

    def predict(self, data):
        if not self.is_trained: self.train_internal()
        input_df = pd.DataFrame([data])[['temperature', 'vibration', 'speed_rpm', 'torque', 'pressure', 'tool_wear']]
        probs = self.maint_model.predict_proba(input_df)
        return round(probs[0][1] * 100, 2)