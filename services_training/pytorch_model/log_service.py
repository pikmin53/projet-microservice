from confluent_kafka import Producer
import json
from datetime import datetime

producer  = Producer(
    {"bootstrap.servers" : "kafka:9092"})

def delivery_report(err,msg):
    if err : 
        print(f"Erreur de reception du message : {err}")
    else :
        print(f"Message envoyé : {msg.value().decode('utf-8')}")
                                                     
# fonction de création d'un log
def log_event(service: str, level: str, message: str):
    log_data={
        "service" : service,
        "level" : level,
        "message" : message,
        "time" : datetime.utcnow().isoformat()
    }
    producer.produce(topic = "logs", value = json.dumps(log_data).encode("utf-8"), callback = delivery_report)
    producer.flush()