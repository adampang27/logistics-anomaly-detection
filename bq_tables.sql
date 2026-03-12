CREATE TABLE IF NOT EXISTS `logistics_anomaly.raw_scan_events` (
  event_id STRING,
  package_id STRING,
  event_ts TIMESTAMP,
  hub STRING,
  transit_time_hours FLOAT64,
  is_seeded_anomaly INT64,
  inserted_at TIMESTAMP
)
PARTITION BY DATE(inserted_at);

CREATE TABLE IF NOT EXISTS `logistics_anomaly.anomaly_events` (
  event_id STRING,
  package_id STRING,
  event_ts TIMESTAMP,
  anomaly_type STRING,
  anomaly_score FLOAT64,
  maps_validated BOOL,
  expected_minutes FLOAT64,
  observed_minutes FLOAT64,
  inserted_at TIMESTAMP
)
PARTITION BY DATE(inserted_at);

CREATE TABLE IF NOT EXISTS `logistics_anomaly.pipeline_statistics` (
  metric_ts TIMESTAMP,
  metric_name STRING,
  metric_value FLOAT64,
  labels STRING
)
PARTITION BY DATE(metric_ts);
