import json
import time
import threading

from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime, Interval, Text, VARCHAR
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


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(VARCHAR(100), nullable=False)
    level = Column(VARCHAR(100), nullable=False)
    message = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)


Base.metadata.create_all(bind=engine)




# ajouter log
def add_log(log : json):
    db: Session = SessionLocal()
    new_log = Logs(
        service=log["service"],
        level=log["level"],
        message=log["message"],
        time=log["time"]
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log



def run_consumer():
    consumer_config = {
        "bootstrap.servers": "kafka:9092",
        "group.id" : "metrics-tracker",
        "auto.offset.reset":"earliest"
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(["logs"])
    print("Ce champs est inscrit à logs")

    while True : 
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Erreur dans la récupération des données kafka")
            continue

        value = msg.value().decode('utf-8')
        log_data = json.loads(value)
        new_log = add_log(log_data)
        print(f"Données reçues : {new_log}")


# Démarrer le consumer dans un thread séparé
consumer_thread = threading.Thread(target=run_consumer, daemon=True)
consumer_thread.start()

    



