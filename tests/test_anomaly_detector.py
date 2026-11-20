import pandas as pd

from src.anomaly_detector import train_model

def test_model_flags_an_isolated_transit_time():
    training_data = pd.DataFrame({
        # Cluster of typical times and a single anomaly
        "transit_time_hours": list(range(20, 41)) + [120],
    })
    model = train_model(training_data)

    shipments = pd.DataFrame({"transit_time_hours": [30, 125]})

    assert model.predict(shipments).tolist() == [1, -1]
