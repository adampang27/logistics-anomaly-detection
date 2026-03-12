set -e

PROJECT_ID="logistics-pipeline-490002"
REGION="us-east1"
BQ_DATASET="logistics_anomaly"
RAW_BUCKET="${PROJECT_ID}-logistics-raw"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  secretmanager.googleapis.com \
  maps-backend.googleapis.com

gsutil mb -l $REGION gs://$RAW_BUCKET || true

gcloud artifacts repositories create logistics \
  --repository-format=docker \
  --location=$REGION || true

gcloud pubsub topics create scan-events || true
gcloud pubsub topics create scan-events-dlq || true

gcloud pubsub subscriptions create scan-events-sub \
  --topic=scan-events \
  --dead-letter-topic=scan-events-dlq \
  --max-delivery-attempts=5 || true

bq --location=US mk -d ${PROJECT_ID}:${BQ_DATASET} || true
