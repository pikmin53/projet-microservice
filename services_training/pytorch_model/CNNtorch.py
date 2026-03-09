import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.datasets import CIFAR100
import torchvision.transforms as transforms
import time
import psutil
import os

def train_model():
    device = torch.device("cpu")

    # =========================
    # Dataset CIFAR-100
    # =========================
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5),
                            (0.5, 0.5, 0.5))
    ])

    trainset = CIFAR100(
        root="./data",
        train=True,
        download=True,
        transform=transform
    )

    trainloader = torch.utils.data.DataLoader(
        trainset,
        batch_size=64,
        shuffle=True,
        num_workers=2
    )

    # =========================
    # CNN Model
    # =========================
    class SimpleCNN(nn.Module):
        def __init__(self):
            super().__init__()
            
            self.conv1 = nn.Conv2d(3, 32, 3)
            self.conv2 = nn.Conv2d(32, 64, 3)
            self.pool = nn.MaxPool2d(2, 2)
            
            self.fc1 = nn.Linear(64 * 6 * 6, 128)
            self.fc2 = nn.Linear(128, 100)

        def forward(self, x):
            x = self.pool(torch.relu(self.conv1(x)))
            x = self.pool(torch.relu(self.conv2(x)))
            x = torch.flatten(x, 1)
            x = torch.relu(self.fc1(x))
            return self.fc2(x)

    model = SimpleCNN().to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # =========================
    # Monitoring setup
    # =========================
    process = psutil.Process(os.getpid())
    cpu_count = psutil.cpu_count()
    last_time = time.time()
    begin_time = last_time

    # =========================
    # Training Loop
    # =========================
    epochs = 20

    for epoch in range(epochs):
        model.train()
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        for i, (inputs, labels) in enumerate(trainloader):
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
            
            # ===== Monitoring every 5 seconds =====
            current_time = time.time()
            if current_time - last_time >= 5:
                
                cpu_raw = psutil.cpu_percent()
                cpu_normalized = cpu_raw / cpu_count
                
                #ram_process = process.memory_info().rss / 1024**2
                ram_system = psutil.virtual_memory().percent
                
                last_time = current_time

    print("Training finished.")