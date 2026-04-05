import os, json
import numpy as np
import pandas as pd
from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest

"""
Kafka Consumer

Subscribes to the 'package-scans' Kafka topic and processes incoming events in real time.
On startup, it trains a scikit-learn Isolation forest model on historical transit data
to establish a baseline of normal behavior.
Flags events with anamolous transit times.
"""

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

def train_model():
    df = pd.read_csv('../data/dummy_logistics_data.csv')
    transit_time_hours = df.loc[:,'transit_time_hours']
    # model.fit() needs a 2d array
    transit_time_hours = transit_time_hours.reshape(-1,1)
    clf = IsolationForest(random_state=42)
    clf.fit(transit_time_hours)
    return clf

def consume_and_detect():

    # Train the model once before polling Kafka
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
        
        

if __name__ == "__main__":
    consume_and_detect()