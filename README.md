# projet-microservice

## Description

Ce projet est une architecture de microservices composée de plusieurs services indépendants pour comparer 2 librairie dans l'entrainement d'un même modèle selon des métriques comme le cpu, la ram, l'accuracy. Il inclut une API principale, un frontend web, un service d'authentification, de logging, et d'entraînement de modèles de classification sur la base de donnée CIFAR100 qui contient 60000 images et 100 classes dont 20 super classe (PyTorch et TensorFlow).

## Technologies Utilisées

- **Backend** : Python, FastAPI
- **Frontend** : React, Vite, JavaScript
- **Machine Learning** : PyTorch, TensorFlow/Keras
- **Conteneurisation** : Docker, Docker Compose
- **Base de données** : PostgreSQL


## Installation

1. Clonez ce repository suivant :

  ```bash
  git clone https://github.com/pikmin53/projet-microservice
  cd projet-microservice
  ```

2. Docker et Docker Compose doivent être installés.

## Lancement

Pour démarrer le projet, la commande suivante a executé dans le dossier projet-microserice :

```
docker compose up
```

L'application sera accessible sur :

- Frontend : http://localhost:3000 
- API : http://localhost:8000 
- Authentification : http://localhost:8001
- Adminer : http://localhost:8080
- Pytorch : http://localhost:8002
- Tensorflow : http://localhost:8003
- BDD : http://localhost:8004

Pour arrêter les dockers :

```
docker compose down
```

## Services Détaillés

### API (api/)
- **Port** : 8000
- **Description** : API principale avec FastAPI.
- **Endpoints** : Consultez la documentation automatique sur http://localhost:8000/docs une fois lancé.

### Frontend (front/)
- **Port** : 3000
- **Description** : Application React avec Vite pour le front.

### Service Authentification (service_authentification/)
- **Description** : Gère l'authentification et l'autorisation pour les utilisateurs.

### Service Log (service_log/)
- **Description** : Enregistre les logs de l'application.

### Service BDD 
- **Description** : L'affiche sur postgres est légèrement buggé et limité puisqu'il n'affiche pas les bon montant mais on a vérifié qu'on stocké bien les données

### Services Training (services_training/)
- **PyTorch Model** : Modèle de réseau de neurones convolutionnel (CNN).
- **TensorFlow Model** : Modèle CNN avec Keras.

### Service Kafka 
- **Description** : Automatise le transfert d'information en continu entre les différents services(log, training, front.)

## Licence

Ce projet est sous licence MIT.

