import pandas as pd

from src.anomaly_detector import train_model

def test_model_predictions():
    # Fake dataset to train on
    df = pd.DataFrame({
        "transit_time_hours": [27,21,29,20,31,18,33,16,35,14,37],
        "is_anomaly": [0,0,0,0,0,0,0,0,0,0,0],
    })

    model = train_model(df)

    assert model.predict([[500]])[0] == -1  # flagged anomalous
