import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.datasets import CIFAR100
import torchvision.transforms as transforms
import time
import psutil
from confluent_kafka import Producer
import os
import json
from models.metrics import MetricsPytorchCreate, add_metrics
from datetime import timedelta

producer_config = {
	"bootstrap.servers" : "kafka:9092"
     
}

producer = Producer(producer_config)
def delivery_report(err,msg):
	if err : 
		print(f"Erreur de reception du message : {err}")
	else :
		print(f"Message envoyé : {msg.value().decode('utf-8')}")



def train_model():
    device = torch.device("cpu") #selection du device (CPU) car pas de gpu sur machine
    transform = transforms.Compose([ #transformation des données d'entrée pour les rendre compatibles avec le modèle
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5),
                            (0.5, 0.5, 0.5))
    ])

    trainset = CIFAR100( #téléchargement du dataset CIFAR-100 pour l'entraînement
        root="./data",
        train=True,
        download=True,
        transform=transform
    )

    trainloader = torch.utils.data.DataLoader( #création d'un DataLoader pour itérer sur le dataset d'entraînement
        trainset,
        batch_size=64,
        shuffle=True,
        num_workers=2
    )

   
    class SimpleCNN(nn.Module): # création d'un petit modèle simple de cnn pour classifier les images du dataset CIFAR-100
        def __init__(self):
            super().__init__()
            
            self.conv1 = nn.Conv2d(3, 32, 3) #première couche de convolution qui prend en entrée des images RGB (3 canaux) et produit 32 cartes de caractéristiques avec un noyau de convolution de taille 3x3
            self.conv2 = nn.Conv2d(32, 64, 3)#deuxième couche de convolution qui prend en entrée les 32 cartes de caractéristiques produites par la première couche et en produit 64 avec un noyau de convolution de taille 3x3
            self.pool = nn.MaxPool2d(2, 2)#couche de pooling qui réduit la taille spatiale des cartes de caractéristiques de moitié en utilisant une fenêtre de 2x2
            
            self.fc1 = nn.Linear(64 * 6 * 6, 128)#première couche entièrement connectée qui produit 128 neurones
            self.fc2 = nn.Linear(128, 100)#deuxième couche entièrement connectée qui produit 100 neurones, correspondant aux 100 classes du dataset CIFAR-100

        def forward(self, x):
            x = self.pool(torch.relu(self.conv1(x)))
            x = self.pool(torch.relu(self.conv2(x)))
            x = torch.flatten(x, 1)
            x = torch.relu(self.fc1(x))
            return self.fc2(x)

    model = SimpleCNN().to(device)

    criterion = nn.CrossEntropyLoss()#choix de la fonction de perte
    optimizer = optim.Adam(model.parameters(), lr=0.001)#utilisation de l'optimiseur Adam pour mettre à jour les poids du modèle pendant l'entraînement, taux apprentissage=0.001


    process = psutil.Process(os.getpid())#focus sur le processus actuel qui est celui du modèle pour ressortir les métric
    cpu_raw = process.cpu_percent()
    cpu_count = psutil.cpu_count() #nb coeur processesseur
    last_time = time.time()
    begin_time = last_time
    epochs = 20 #nb d'itération sur l'ensemble du dataset d'entraînement

    for epoch in range(epochs):
        model.train() #entrainement du modèle
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        for i, (inputs, labels) in enumerate(trainloader): #itération sur les batches d'entraînement, inputs sont les images et labels sont les classes correspondantes
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            current_time = time.time()
            if current_time - last_time >= 5:#retour des métrics souhaitez toutes les 5 secondes
                
                cpu_raw = process.cpu_percent()
                cpu_normalized = cpu_raw / cpu_count #normalisation de l'utilisation du cpu en fonction du nombre de coeur du processeur
                
                ram_process = process.memory_info().rss / 1024**2
                duration= timedelta(seconds=current_time - begin_time)
                metrics = {
                    "cpu" : cpu_normalized,
                    "ram" : ram_process,
                    "accuracy" : 100 * correct / total,
                    "duration" : str(duration),
                    "time" : time.time()
                }
                value = json.dumps(metrics).encode("utf-8") #encodage des métrics en json pour les envoyer dans le topic kafka
                producer.produce(topic="metrics_pytorch",value=value,callback=delivery_report)
                producer.flush() #force l'envoie de ce format de message dans le topic kafka
                print(f"Epoch {epoch+1}, Batch {i+1}, Loss: {running_loss/(i+1):.4f}, Accuracy: {100 * correct / total:.2f}%")
                last_time = current_time
