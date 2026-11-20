# Logistics Anomaly Detection

This project grew out of my time working at an Amazon sorting facility.
Seeing how many packages moved through one shift made me curious about the
scan data behind that movement.

The project replays synthetic package records through Kafka. A consumer scores
each record's transit time with an Isolation Forest model and sends flagged
records to a FastAPI service, which stores the alerts in Postgres.

## Running it

Start Docker Desktop or Docker Engine, then clone the repo and start the services.
The repo includes the sample CSV.

```bash
git clone https://github.com/adampang27/logistics-anomaly-detection.git
cd logistics-anomaly-detection
docker compose up --build -d
```

Open `http://localhost:8000/alerts` in your browser or check it from a terminal.

```bash
curl http://localhost:8000/alerts
```

Once an alert appears, look up its `package_id` in `data/dummy_logistics_data.csv`
and compare the transit time. The full replay takes about 17 minutes.

If the endpoint stays down or the list stays empty after startup, check the logs.

```bash
docker compose ps -a
docker compose logs --tail=50 postgres kafka alert-api producer anomaly-detector
```

When you're done, run `docker compose down`. Alerts persist in a Postgres volume.

## How it works

```text
generated CSV -> Kafka -> Isolation Forest -> FastAPI -> Postgres
```

`src/data_generator.py` creates 10,000 package records. Most transit times sit
between 24 and 72 hours. I plant 250 unusually fast ones and 250 late ones,
then label times below 12 hours or above 72 hours as anomalous (`is_anomaly = 1`).

`src/kafka_producer.py` reads the CSV and sends one row every tenth of a second
to the `package-scans` topic. At startup, `src/anomaly_detector.py` fits a
scikit-learn Isolation Forest on the transit times from that same CSV. The
`is_anomaly` labels are there for comparison.

When the model flags a record, the consumer sends it to `POST /alerts`.
The FastAPI service in `src/alert_api.py` saves the alert to Postgres through
SQLAlchemy. `GET /alerts` returns up to 50 alerts, newest first.

Everything runs locally with Docker Compose on a single Kafka broker. The model
only looks at transit time. That kept the problem small enough to finish the
full path through the pipeline.

## Running the tests

Use Python 3.11 from the project folder.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

You can run the tests with the Compose stack stopped. The API tests use
in-memory SQLite.

## Batch archiving (MinIO)

MinIO starts with the rest of the stack. You can also start it on its own with
`docker compose up -d minio`. With the Python environment active, run
`python src/upload_to_minio.py` to upload the CSV to the `logistics-data` bucket.
The script creates the bucket if needed and saves the file under the current
date, for example `year=2025/month=07/day=30/batch.csv`. You can find the file in
the MinIO console at `http://localhost:9001`.

## Saving a trained model

`retrain_model()` in `src/anomaly_detector.py` reads the CSV and saves a fitted
model to `models/isolation_forest.pkl`. The Compose detector fits its own model
from the CSV each time it starts.
