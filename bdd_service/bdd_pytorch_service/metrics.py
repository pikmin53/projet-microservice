from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime, Time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import datetime



DATABASE_API_URL = os.getenv("DATABASE_API_URL")
engine = create_engine(DATABASE_API_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MetricsPytorch(Base):
    __tablename__ = "metricsPytorch"

    id = Column(Integer, primary_key=True, index=True)
    cpu = Column(Float, nullable=False)
    ram = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    duration = Column(Time, nullable=False)
    time = Column(DateTime, nullable=False)


Base.metadata.create_all(bind=engine)


# API MODELS
class MetricsPytorchCreate(BaseModel):
    cpu: float
    ram: float
    accuracy: float
    duration: datetime.time
    time: datetime.datetime


def add_metrics(metrics: MetricsPytorchCreate, db: Session = Depends(get_db)):
    if db.query(MetricsPytorch).filter(MetricsPytorch.time == metrics.time).first():
        raise HTTPException(status_code=400, detail="Metrics déjà enregistrées")
    
    new_metrics = MetricsPytorch(
        cpu=metrics.cpu,
        ram=metrics.ram,
        accuracy=metrics.accuracy,
        duration=metrics.duration,
        time=metrics.time
    )
    db.add(new_metrics)
    db.commit()
    db.refresh(new_metrics)
    return new_metrics