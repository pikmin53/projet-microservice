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

- Frontend : http://localhost:3000 (ou le port configuré)
- API : http://localhost:8000 (ou le port configuré)

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

### Services Training (services_training/)
- **PyTorch Model** : Modèle de réseau de neurones convolutionnel (CNN).
- **TensorFlow Model** : Modèle CNN avec Keras.

### Utilisateurs par défault : 
- userAdmin1 = UserCreate("Georgette", "Cy", "georgette.cy@coucou.com", "admin", "password")
- userAdmin2 = UserCreate("Victor", "Tech", "victor.tech@coucou.com", "admin", "password")
- user1 = UserCreate("Laura", "Carotte", "laura.carotte@coucou.com", "", "password")
- user2 = UserCreate("George", "Cy", "george.cy@coucou.com", "", "password")
- user3 = UserCreate("Prince", "Petit", "petit.prince@coucou.com", "", "password")

## Licence

Ce projet est sous licence MIT.

