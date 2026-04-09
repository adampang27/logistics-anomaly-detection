from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

"""
FastAPI Alert Microservice

Receives POST requests from the anomaly detector when an anomalous
package scan is flagged. Stores alerts in memory and exposes a GET
endpoint so downstream consumers (e.g. a dashboard) can query them.

In production, the in-memory store would be replaced with a database.
"""

# FastAPI auto-generates interactive docs at /docs, useful for a demo
app = FastAPI(title="Logistics Alert API")

# Simple python list acting as a database for the prototype.
# Faster and zero setup, clears on every instance.
alerts_db = []

# Pydantic validates incoming JSON against this automatically.
# If the consumer sends a string where it would expect an int,
# FastAPI will reject it with a 422 before it reaches the main code.
class AnomalyAlert(BaseModel):
    package_id: int
    transit_time_hours: float
    anomaly_score: float
    reason: str

@app.post("/alerts", status_code=201)
def trigger_alert(alert: AnomalyAlert):
    # Convert to dict so a timestamp can be appended
    record = alert.dict()
    record["timestamp"] = str(datetime.now())
    alerts_db.append(record)
    print(f"ALERT: package {alert.package_id} | {alert.reason}")
    return {"message": "Alert logged", "total_alerts": len(alerts)db)}

@app.get("/alerts")
def get_alerts():
    # Get only the last 50 so the who list isn't dumped on each call
    # Real version would be split into pages with date filters.
    return {"alerts": alerts_db[-50:]}