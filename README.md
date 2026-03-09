# projet-microservice

## Description

Ce projet est une architecture de microservices composée de plusieurs services indépendants pour comparer 2 librairie dans l'entrainement d'un même modèle selon des métriques comme le cpu, la ram, l'accuracy. Il inclut une API principale, un frontend web, des services d'authentification, de logging, et d'entraînement de modèles d'intelligence artificielle (PyTorch et TensorFlow).

## Architecture

Le projet est organisé en plusieurs services :

- **api/** : API principale construite avec FastAPI (Python). Gère les endpoints principaux de l'application.
- **front/** : Frontend web utilisant React et Vite. Interface utilisateur pour interagir avec l'API.
- **service_authentification/** : Service d'authentification en Python. Gère l'authentification des utilisateurs.
- **service_log/** : Service de logging en Python. Collecte et gère les logs de l'application.
- **services_training/** : Services d'entraînement de modèles ML.
  - **pytorch_model/** : Modèle CNN avec PyTorch.
  - **tensorflow_model/** : Modèle CNN avec TensorFlow/Keras.

Tous les services sont conteneurisés avec Docker et orchestrés via Docker Compose.

## Technologies Utilisées

- **Backend** : Python, FastAPI
- **Frontend** : React, Vite, JavaScript
- **Machine Learning** : PyTorch, TensorFlow/Keras
- **Conteneurisation** : Docker, Docker Compose
- **Base de données** : PostgreSQL (via Docker)

## Prérequis

- Docker
- Docker Compose

## Installation

1. Clonez ce repository :
   ```bash
   git clone https://github.com/pikmin53/projet-microservice.git
   cd projet-microservice
   ```

2. Assurez-vous que Docker et Docker Compose sont installés et en cours d'exécution.

## Lancement

Pour démarrer tous les services :

```bash
docker compose up
```

Cela construira et démarrera tous les conteneurs nécessaires. L'application sera accessible sur :

- Frontend : http://localhost:3000 (ou le port configuré)
- API : http://localhost:8000 (ou le port configuré)

Pour arrêter les services :

```bash
docker compose down
```

## Services Détaillés

### API (api/)
- **Port** : 8000
- **Description** : API REST principale avec FastAPI.
- **Endpoints** : Consultez la documentation automatique sur http://localhost:8000/docs une fois lancé.

### Frontend (front/)
- **Port** : 3000
- **Description** : Application React avec Vite pour le développement rapide.
- **Commandes** :
  - Développement : `npm run dev`
  - Build : `npm run build`

### Service Authentification (service_authentification/)
- **Description** : Gère l'authentification et l'autorisation des utilisateurs.

### Service Log (service_log/)
- **Description** : Collecte et stocke les logs de l'application.

### Services Training (services_training/)
- **PyTorch Model** : Modèle de réseau de neurones convolutionnel (CNN) pour l'entraînement.
- **TensorFlow Model** : Modèle CNN avec Keras pour l'entraînement.

## Configuration

Les configurations spécifiques à chaque service se trouvent dans leurs dossiers respectifs (requirements.txt, package.json, etc.).

Pour la base de données PostgreSQL, elle est configurée via Docker Compose.

## Licence

Ce projet est sous licence MIT.

