# Logistics Anomaly Detection

This is a local learning project inspired by my time working at an Amazon
sorting facility. Seeing how many packages moved through one shift made me
curious about how the scan data behind that movement gets monitored.

The project replays synthetic package records through Kafka. A consumer scores
each record with an Isolation Forest model, sends flagged records to a FastAPI
service, and stores the alerts in Postgres.

## How it works

```text
generated CSV -> Kafka -> Isolation Forest -> FastAPI -> Postgres
```

`data_generator.py` creates 10,000 package records. Most transit times sit
between 24 and 72 hours. I plant 250 unusually fast ones and 250 late ones,
then label anything below 12 hours or above 72 as anomalous so the pipeline
has known failures to catch.

`kafka_producer.py` reads the CSV and sends one row every tenth of a second so
the data arrives like a feed instead of one big batch. `anomaly_detector.py`
scores the transit time with Isolation Forest. If the model flags it, the
consumer posts an alert to FastAPI, and the API writes the row to Postgres.
`GET /alerts` returns the 50 newest alerts.

Everything runs locally with Docker Compose on a single Kafka broker. The model
only looks at transit time. That kept the problem small enough to finish the
full path: generate, stream, score, alert, and store.

## Running it

```bash
docker compose up --build
```

```bash
curl http://localhost:8000/alerts
```

The full replay takes a while because of the delay between records. Compose
starts the services in order, but it doesn't wait for each one to be ready
before starting the next.

To run the tests without the Compose stack:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The API tests use in-memory SQLite, so they don't need Postgres running. There
is also a MinIO upload script for archiving a generated batch under a
date-based key, and a separate Airflow DAG for regenerating data and
retraining the model. Airflow runs in standalone mode outside this Compose
stack.

## Batch archiving (MinIO)

`upload_to_minio.py` pushes the generated CSV to local MinIO under a
Hive-style date key (`year=2025/month=07/day=30/batch.csv`). The bucket
is created on first run if it doesn't exist.

## Retraining (Airflow)

A standalone Airflow DAG calls `generate_batch()` and `retrain_model()`
on a schedule, serializing the updated model to `models/isolation_forest.pkl`.
Runs outside the Compose stack in Airflow standalone mode.

## Stack

Python, Kafka, scikit-learn, FastAPI, SQLAlchemy, Postgres, Docker Compose,
and MinIO.
