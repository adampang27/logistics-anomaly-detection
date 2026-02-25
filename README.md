# Real-Time Logistics Anomaly Detection 

## The Problem
During my time working in Amazon sorting facilities, I wondered what systems they had to catch errors constantly and in real time. When millions of packages are moving, the data tracking them needs to match the physical reality. If a package scan says it crossed the country in six hours, or sat in transit for 500 hours, something or someone messed up. I wanted to understand how massive warehouses catch these system glitches, misroutes, or missing packages right away, instead of hours later.

## The Solution
I built a streaming data pipeline to simulate how a system like that could work. This end-to-end system takes in high-volume package scan events, detects anomalies in near real time, and sets off alerts—allowing the business to identify data corruption, potential theft, or severe transit delays before they morph into larger operational failures.

## Architecture & Data Flow

- **Mocking Production Data (`01_data_generator.py`)**: To simulate a live supply chain, I built a data generator that mimics warehouse scanning operations. To stress-test the pipeline, I intentionally mixed in bad data, such as physically impossible transit times or duplicate scans.

- **The Event Bus (`02_kafka_producer.py`)**: To ensure the system can handle production-level scale without dropping data, I implemented Apache Kafka. It ingests the continuous stream of JSON package payloads, acting as the bridge between the raw data and the processing mode.

- **Real-Time Scoring (`03_anomaly_detector.py`)**: This consumer service continuously polls the Kafka topic and evaluates each scan on the fly. It uses an Isolation Forest machine learning model (scikit-learn) to score events, instantly flagging anything that looks outside normal patterns without creating bottlenecks in the pipeline.

- **Actionable Alerting (`04_alert_api.py`)**: Detecting an anomaly is only useful if someone can act on it. When the model flags a critical issue (e.g., transit times that fall outside normal patterns), the pipeline fires a POST request to a FastAPI microservice. In a live environment, this endpoint would ping a dashboard so someone could look into the error.

## Tech Stack

- **Language:** Python
- **Streaming & Big Data:** Apache Kafka
- **Machine Learning:** scikit-learn (Isolation Forest)
- **API Framework:** FastAPI
- **Data Manipulation:** pandas, NumPy
- **Containerization & Orchestration:** Docker, Docker Compose