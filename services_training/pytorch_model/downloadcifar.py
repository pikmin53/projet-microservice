from torchvision.datasets import CIFAR100
import torchvision.transforms as transforms


cirfar=CIFAR100(
    root='./data',
    train=True,
    download=True,
    transform=transforms.ToTensor()
)
