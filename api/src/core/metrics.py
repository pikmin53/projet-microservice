from confluent_kafka import Consumer
import json

#configuration du consomateur kafka pour les métriques
consumer_config = {
	"bootstrap.servers": "kafka:9092",
	"group.id": "metrics-tracker",
	"auto.offset.reset": "earliest"
}

def create_consumer(topic):
	consumer = Consumer(consumer_config)
	consumer.subscribe([topic])
	print(f"Ce champs est inscrit à {topic}")
	return consumer

def consume_metrics(consumer):
	msg = consumer.poll(1.0)
	if msg is None:
		return None
	if msg.error():
		print("Erreur dans la récupération des données kafka")
		return None
	value = msg.value().decode("utf-8")
	metrics = json.loads(value) 
	print(f"Metrics reçues : {metrics}")
	return metrics
