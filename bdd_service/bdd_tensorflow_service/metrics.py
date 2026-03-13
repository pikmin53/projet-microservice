import json
import time
import threading

from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime, VARCHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import datetime
from log_service import log_event

from confluent_kafka import Consumer


DATABASE_API_URL = os.getenv("DATABASE_API_URL")
engine = create_engine(DATABASE_API_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


# classe correspondant à une table de la bdd
class MetricsTensorflow(Base):
    __tablename__ = "metricsTensorflow"

    id = Column(Integer, primary_key=True, index=True)
    cpu = Column(Float, nullable=False)
    ram = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    vitesse_exec = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

# ajout de la table en bdd
def init_db() :
    Base.metadata.create_all(bind=engine)

# ajout des metrcis
def add_metrics(metrics: json):
    db: Session = SessionLocal()

    new_metrics = MetricsTensorflow(
        cpu=metrics["cpu"],
        ram=metrics["ram"],
        accuracy=metrics["accuracy"],
        vitesse_exec=metrics["vitesse_exec"],
        time=metrics["time"]
    )
    db.add(new_metrics)
    db.commit()
    db.refresh(new_metrics)
    log_event("BDD-service", "INFO", "metrics Tensorflow ajoutees")
    total = db.query(MetricsTensorflow).count()
    db.close()
    print(f"Total lignes metricsTensorflow : {total}")
    return new_metrics

# consummer kafka qui récupère les données pour les mettre en bdd
def run_consumer():
    consumer_config = {
        "bootstrap.servers": "kafka:9092",
        "group.id" : "tensorflow-consumer",
        "auto.offset.reset":"earliest"
    }


    consumer = Consumer(consumer_config)
    consumer.subscribe(["metrics_tensorflow"])
    print("Ce champs est inscrit à metrics_tensorflow")

    while True : 
        msg = consumer.poll(1.0)
        if msg is None:
            time.sleep(0.1)
            continue
        if msg.error():
            print(msg.error())
            print("Erreur dans la récupération des données kafka")
            continue

        value = msg.value().decode('utf-8')
        metrics = json.loads(value)
        new_metrics = add_metrics(metrics)
        print(f"Données reçues : {new_metrics}")


# Démarrer le consumer dans un thread séparé
def start_consumer() :
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()

    

