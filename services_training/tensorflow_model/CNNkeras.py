import os
# Suppress TensorFlow logging messages because we don't GPU on our machine #CYTech
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
# Configurer le répertoire Keras pour utiliser le volume
os.environ["KERAS_HOME"] = "/app/data"

from tensorflow.keras import layers
import tensorflow as tf
from tensorflow.keras import Model, Sequential
from tensorflow.keras.datasets import cifar100
import time
import psutil
from confluent_kafka import Producer
import json
from datetime import timedelta

## Configuration du producteur Kafka pour envoyer les métrics d'entraînement au topic "metrics_tensorflow"
producer_config = {
	"bootstrap.servers" : "kafka:9092"    
}

producer = Producer(producer_config)
def delivery_report(err,msg):
	if err : 
		print(f"Erreur de reception du message : {err}")
	else :
		print(f"Message envoyé : {msg.value().decode('utf-8')}")

## Limitation des coeurs CPU
CPU_CORES_LIMIT = 2  # Nombre de cœurs à utiliser (ajuste selon tes besoins)

# Limitation au niveau TensorFlow (inter = entre opérations, intra = dans une opération)
tf.config.threading.set_inter_op_parallelism_threads(CPU_CORES_LIMIT)
tf.config.threading.set_intra_op_parallelism_threads(CPU_CORES_LIMIT)

# Limitation au niveau OS (affinity sur les coeurs physiques)
process = psutil.Process(os.getpid())
available_cores = list(range(psutil.cpu_count()))
limited_cores = available_cores[:CPU_CORES_LIMIT]
process.cpu_affinity(limited_cores)


class LiveMetricsCallback(tf.keras.callbacks.Callback):
    
    def on_train_begin(self, logs=None):
        self.last_print_time = time.time()
        self.begin_time = self.last_print_time
        self.process = psutil.Process(os.getpid())
        self.samples_processed = 0
        self.batch_size = self.params.get("batch_size") or self.params.get("steps", 1)
    def on_batch_end(self, batch, logs=None):
        current_time = time.time()
        
        
        if current_time - self.last_print_time >= 4: #retour métrics toutes les 4 secondes 
            self.samples_processed += self.batch_size
            # CPU utilisée par le process Python (en %) sachnat qu'on limite à 2 coeurs le contenaire
            cpu_usage = self.process.cpu_percent()/CPU_CORES_LIMIT
            # RAM utilisée par le process Python (en MB)
            ram_usage = self.process.memory_info().rss / 1024**2
            metrics = {
                "cpu" : cpu_usage,
                "ram" : ram_usage,
                "accuracy" : logs.get("accuracy", 0),
                "vitesse_exec" : self.samples_processed / (current_time - self.begin_time),
                "time" : time.time()
            }
            value = json.dumps(metrics).encode("utf-8") #encodage des métrics en json pour les envoyer dans le topic kafka
            producer.produce(topic="metrics_tensorflow",value=value,callback=delivery_report)
            producer.flush() #force l'envoie de ce format de message dans le topic kafka
            self.last_print_time = current_time


def train_model():
    # Configuration du modèle CNN pour la classification d'images du dataset CIFAR-100
    image_size = (32, 32, 3)
    nb_classes = 100

    (x_train, y_train), (x_test, y_test) = cifar100.load_data()
    assert x_train.shape == (50000, 32, 32, 3)
    assert x_test.shape == (10000, 32, 32, 3)
    assert y_train.shape == (50000, 1)
    assert y_test.shape == (10000, 1)

    # Normalisation
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    #augmentation des images d'entraînement car 600 images par classe seulement
    data_augmentation = Sequential(
        [
            layers.Normalization(),
            layers.Resizing(image_size, image_size),
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(factor=0.02),
            layers.RandomZoom(
                height_factor=0.2, width_factor=0.2
            ),
        ],
        name="data_augmentation",
    )
    data_augmentation.layers[0].adapt(x_train)



    model = Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=image_size),
        layers.MaxPooling2D((2,2)),
        
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D((2,2)),
        
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(nb_classes)  # 100 classes
    ])


    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )


    model.fit(
        x_train,
        y_train,
        epochs=20,
        batch_size=64,
        callbacks=[LiveMetricsCallback()]
    )