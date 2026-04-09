import os, json
import numpy as np
import pandas as pd
from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest
import urllib.request

"""
Kafka Consumer

Subscribes to the 'package-scans' Kafka topic and processes incoming events in real time.
On startup, it trains a scikit-learn Isolation forest model on historical transit data
to establish a baseline of normal behavior.
Flags events with anamolous transit times and associated HTTP alerts.
"""

# Constants
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
ALERT_API_URL = os.getenv("ALERT_API_URL", "http://alert-api:8000/alerts")

def train_model():
    df = pd.read_csv('../data/dummy_logistics_data.csv')
    # Train only on normal data
    df = df[df['is_anomaly'] == 0] 
    transit_time_hours = df[['transit_time_hours']] 
    clf = IsolationForest(random_state=42)
    clf.fit(transit_time_hours)
    return clf

def consume_and_detect():

    # Train the model once before polling Kafka
    # Trains on the full CSV which contains anomalies
    model = train_model()

    # Setup the consumer
    consumer = KafkaConsumer(
        "package-scans",
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )

    # Block and process messages as they arrive
    for message in consumer:
        # for the already deseralized dict
        data = message.value 
        # get the column from the dict
        transit_time_hours = data["transit_time_hours"]
        # however its just a column so reshape into a 2D array
        feature = np.array([[transit_time_hours]])
        # -1 if anomalous, 1 if not
        # Make it return just an integer
        prediction = model.predict(feature)[0] 
        # Float value for anomaly, More negative = further from normal
        # For severity ranking in the alert
        anomaly_score = model.decision_function(feature)[0]

        if prediction == -1:

            print(f"Anomalous time detected: {transit_time_hours}")

            alert = { 
                "package_id" : int(data["package_id"]),
                "transit_time_hours": float(transit_time_hours),
                "anomaly_score": float(anomaly_score),
                "reason": f"Abnormal transit time: {transit_time_hours} hrs"
            }
            req = urllib.request.Request(
                ALERT_API_URL,
                data=json.dumps(alert).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                urllib.request.urlopen(req)
            except Exception as e:
                # To log and continue
                print(f"Failed to send alert: {e}") 
        

if __name__ == "__main__":
    consume_and_detect()