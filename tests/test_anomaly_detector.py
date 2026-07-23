import pandas as pd
import numpy as np
import random
import importlib

def test_model_predictions():
    # Using importlib to be able to import files that start with digits
    anomaly_detector = importlib.import_module("src.03_anomaly_detector")
    train_model = anomaly_detector.train_model
    # Fake dataset to train on
    df = pd.DataFrame({
        "transit_time_hours": [27,21,29,20,31,18,33,16,35,14,37],
        "is_anomaly": [0,0,0,0,0,0,0,0,0,0,0],
    })

    model = train_model(df)
    
    assert model.predict([[500]])[0] == -1  # flagged anomalous