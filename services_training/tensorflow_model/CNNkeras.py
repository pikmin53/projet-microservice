import os
# Suppress TensorFlow logging messages because we don't GPU on our machine #CYTech
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from tensorflow.keras import layers
import tensorflow as tf
from tensorflow.keras import Model, Sequential
from tensorflow.keras.datasets import cifar100
import time
import psutil
from models.metrics import MetricsTensorflowCreate, add_metrics
from confluent_kafka import Producer
import json



producer_config = {
	"bootstrap.servers" : "kafka:9092"    
}

producer = Producer(producer_config)
def delivery_report(err,msg):
	if err : 
		print(f"Erreur de reception du message : {err}")
	else :
		print(f"Message envoyé : {msg.value().decode('utf-8')}")


class LiveMetricsCallback(tf.keras.callbacks.Callback):
    
    def on_train_begin(self, logs=None):
        self.last_print_time = time.time()
        self.begin_time = self.last_print_time
        self.process = psutil.Process(os.getpid())
    
    def on_batch_end(self, batch, logs=None):
        current_time = time.time()
        
        # Print every 5 seconds
        if current_time - self.last_print_time >= 5:
            cpu_count = psutil.cpu_count()
            cpu_usage = self.process.cpu_percent()/cpu_count
            # RAM utilisée par le process Python (en MB)
            ram_usage = self.process.memory_info().rss / 1024**2
            
            metrics = {
                "cpu" : cpu_usage,
                "ram" : ram_usage,
                "accuracy" : logs.get("accuracy", 0),
                "duration" : time.time() - self.begin_time,
                "time" : time.time()
            }
            value = json.dumps(metrics).encode("utf-8") #encodage des métrics en json pour les envoyer dans le topic kafka
            producer.produce(topic="metrics_tensorflow",value=value,callback=delivery_report)
            producer.flush() #force l'envoie de ce format de message dans le topic kafka
        
            self.last_print_time = current_time


def train_model():
    #download the dataset and split it into training and test sets
    image_size = (32, 32, 3)
    nb_classes = 100


    (x_train, y_train), (x_test, y_test) = cifar100.load_data()
    assert x_train.shape == (50000, 32, 32, 3)
    assert x_test.shape == (10000, 32, 32, 3)
    assert y_train.shape == (50000, 1)
    assert y_test.shape == (10000, 1)

    # Normalize
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    #data augmentation of cifar100 dataset because only 600 image per class and we have 100 classes, so we need to augment the data to increase the number of images per class and improve the performance of the model
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
        layers.Dense(nb_classes)  # 100 classes in CIFAR-100 dataset
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