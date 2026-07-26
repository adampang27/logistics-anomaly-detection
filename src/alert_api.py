from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


"""
FastAPI alert service

Receives anomaly alerts, persists them to Postgres through SQLAlchemy,
and returns the 50 newest alerts for downstream consumers.s
"""

# SQLAlchemy's base registry
class Base(DeclarativeBase):
    pass

# Using SQLAlchemy ORM instead of raw psycopg2
# Same code works against Postgres and SQLite in tests without needing to rewrite every query
class Alert(Base):
    __tablename__ = "alerts"

    # Surrogate primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int]
    transit_time_hours: Mapped[float]
    anomaly_score: Mapped[float]
    reason: Mapped[str] = mapped_column(String(200)) # Text capped at 200 char
    timestamp: Mapped[str] = mapped_column(String(50))


# create_engine stores the database configuration; create_all then conects
# and creates the alerts table fi it does not exist.
# 'postgres' is the Docker Compose service name used inside its network
engine = create_engine("postgresql+psycopg2://postgres:password@postgres:5432/logistics")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


# FastAPI's interactive docs at /docs
app = FastAPI(title="Logistics Alert API", lifespan=lifespan)


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
    # Session groups this database operation
    with Session(engine) as session:
        new_alert = Alert(
            # Pulls in each field from Pydantic's Alert
            package_id=alert.package_id,
            transit_time_hours=alert.transit_time_hours,
            anomaly_score=alert.anomaly_score,
            reason=alert.reason,
            timestamp=str(datetime.now())
        )
        # add() stages the row and commit() makes the insert permanent
        session.add(new_alert)
        session.commit()

        # Ask the database for 50 newest alerts instead of loading every row
        total = session.query(Alert).count()

    # Gets how may rows in the alerts table
    return {"message": "Alert logged", "total_alerts": total}


@app.get("/alerts")
def get_alerts():
    # Get only the last 50 alerts so the whole list isn't dumped on each call
    with Session(engine) as session:
        # Querys the table for a list of Alert objects
        alerts = session.query(Alert).order_by(Alert.id.desc()).limit(50).all()

    # Converting each Alert object back to a dict before returning it
    return {
        "alerts" : [
            {
                "package_id" : a.package_id,
                "transit_time_hours" : a.transit_time_hours,
                "anomaly_score" : a.anomaly_score,
                "reason" : a.reason,
                "timestamp" : a.timestamp,
            }
            for a in alerts
        ]
    }

