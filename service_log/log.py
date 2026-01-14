from fastapi import FastAPI, HTTPException
from kafka import KafkaProducer, KafkaConsumer
import psycopg2
import os
import time

app = FastAPI()
#consummer = KafkaConsumer('order.created', bootstrap_servers='localhost:9092', group_id='inventory-group', value_deserializer=lambda m: json.loads(m.decode('utf-8')))


def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "log_db"),
            dbname=os.getenv("DB_NAME", "log_db"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", "password"),
        )
        
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50),
            event_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Base de données initialisée avec succès")
        return True
    except psycopg2.OperationalError as e:
        print("Erreur de connexion à la base de données:", e)


@app.on_event("startup")
async def startup_event():
    """Initialiser la BD au démarrage de l'app"""
    try:
        init_db()
    except Exception as e:
        print(f"Erreur lors de l'initialisation: {e}")
        # L'app démarre quand même pour permettre au health check de fonctionner

