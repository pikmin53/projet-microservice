from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime, Interval
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os



DATABASE_TENSORFLOW_URL = os.getenv("DATABASE_TENSORFLOW_URL")
engine = create_engine(DATABASE_TENSORFLOW_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MetricsTensorflow(Base):
    __tablename__ = "metricsTensorflow"

    id = Column(Integer, primary_key=True, index=True)
    cpu = Column(Float, nullable=False)
    ram = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    duration = Column(Interval, nullable=False)
    time = Column(DateTime, nullable=False)


Base.metadata.create_all(bind=engine)

# API MODELS
class MetricsTensorflowCreate(BaseModel):
    cpu: float
    ram: float
    accuracy: float
    duration: str
    time: str


def add_metrics(metrics: MetricsTensorflowCreate, db: Session = Depends(get_db)):
    if db.query(MetricsTensorflow).filter(MetricsTensorflow.time == metrics.time).first():
        raise HTTPException(status_code=400, detail="Metrics déjà enregistrées")
    
    new_metrics = MetricsTensorflow(
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