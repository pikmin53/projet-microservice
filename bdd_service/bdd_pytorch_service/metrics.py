import json
import time
import threading

from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime, Time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import datetime
from confluent_kafka import Consumer


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



def add_metrics(metrics: json):
    db: Session = SessionLocal()
    new_metrics = MetricsPytorch(
        cpu=metrics["cpu"],
        ram=metrics["ram"],
        accuracy=metrics["accuracy"],
        duration=metrics["duration"],
        time=metrics["time"]
    )
    db.add(new_metrics)
    db.commit()
    db.refresh(new_metrics)
    return new_metrics


def run_consumer():
    consumer_config = {
        "bootstrap.servers": "kafka:9092",
        "group.id" : "metrics-tracker",
        "auto.offset.reset":"earliest"
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(["metrics_pytorch"])
    print("Ce champs est inscrit à metrics_pytorch")

    while True : 
        msg = consumer.poll(1.0)
        if msg is None:
            time.sleep(0.1)
            continue
        if msg.error():
            print("Erreur dans la récupération des données kafka")
            continue

        value = msg.value().decode('utf-8')
        metrics = json.loads(value)
        new_log = add_metrics(metrics)
        print(f"Données reçues : {new_log}")


# Démarrer le consumer dans un thread séparé
consumer_thread = threading.Thread(target=run_consumer, daemon=True)
consumer_thread.start()

    