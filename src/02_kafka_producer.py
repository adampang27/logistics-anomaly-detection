import json
import time
import pandas as pd 
import os
from kafka import KafkaProducer

"""
Kafka Producer

Reads the generated CSV and streams each row as a JSON payload to a Kafka topic.
Simulates live warehouse package scans.
"""

#for future cloud hosting
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "package-scans"

def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )


def stream_data(producer):
    # Ensure the path is correct no matter where
    file_path = "data/dummy_logistics_data.csv"
    if not os.path.exists(file_path):
        file_path = "../data/dummy_logistics_data.csv"

    df = pd.read_csv(file_path)

    for index, row in df.iterrows():
        # Convert Pandas Series to dict so json.dumps() can seralize it
        packageScanPayload = row.to_dict()
        # Send to Kafka
        producer.send(TOPIC, value=packageScanPayload)
        
        # After 100 records kafka pops the payload and sends it
        if index % 100 == 0:
            producer.flush()

        time.sleep(0.1)  # To simulate real-time warehouse scans

if __name__ == "__main__":
    producer = create_producer()
    stream_data(producer)