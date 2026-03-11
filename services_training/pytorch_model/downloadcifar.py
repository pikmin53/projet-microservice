import os

from torchvision.datasets import CIFAR100
import torchvision.transforms as transforms

data_dir = '/app/data'
os.makedirs(data_dir, exist_ok=True)

cirfar=CIFAR100(
    root=data_dir,
    train=True,
    download=True,
    transform=transforms.ToTensor()
)
