# BloodFlow - Application d'Analyse des Dons de Sang

## Description
BloodFlow est une application web interactive développée avec Dash pour analyser et visualiser les données relatives aux dons de sang. Elle permet de suivre les tendances, prédire l'éligibilité des donneurs et optimiser les campagnes de don.

## Fonctionnalités

### 1. Dashboard Principal
- Vue d'ensemble des statistiques clés
- Graphiques interactifs des tendances
- Indicateurs de performance

### 2. Profils Donneurs
- Analyse démographique des donneurs
- Segmentation par âge, genre, localisation
- Visualisation des comportements de don

### 3. Analyse des Campagnes
- Suivi des performances des campagnes
- Analyse géographique des dons
- Identification des zones à fort potentiel

### 4. Prédiction d'Éligibilité
- Modèle ML pour prédire l'éligibilité
- Interface intuitive pour les prédictions
- Explications des résultats

### 5. Analyse de Rétention
- Taux de rétention des donneurs
- Analyse des facteurs de fidélisation
- Recommandations pour améliorer la rétention

## Installation

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)

### Configuration de l'environnement

1. Cloner le dépôt :
```bash
git clone <url-du-repo>
cd bloodflow
```

2. Créer et activer l'environnement virtuel :
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\\Scripts\\activate   # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Démarrage de l'Application

### Application Principale (Dash)
```bash
python app.py
```
L'application sera accessible à l'adresse : http://localhost:8050

### API de Prédiction (FastAPI)

1. Naviguer vers le dossier de l'API :
```bash
cd api
```

2. Démarrer l'API :
```bash
uvicorn main:app --reload
```
L'API sera accessible à l'adresse : http://localhost:8000

## Architecture de l'API FastAPI

L'API de prédiction est construite avec FastAPI et suit une architecture RESTful :

### Endpoints

1. Prédiction d'éligibilité :
```
POST /predict
```
- Entrée : Données du donneur (JSON)
- Sortie : Prédiction d'éligibilité et probabilité

2. Statut de l'API :
```
GET /health
```
- Vérifie l'état de l'API

### Structure des Données

Format d'entrée pour la prédiction :
```json
{
    "age": 25,
    "genre": "Homme",
    "poids": 70,
    "dernier_don": "2023-01-01",
    "antecedents_medicaux": ["aucun"],
    "medication_actuelle": false
}
```

### Modèle ML
- Utilise un modèle RandomForest pré-entraîné
- Stocké dans `api/models/model.pkl`
- Mis à jour périodiquement avec de nouvelles données

## Structure du Projet
```
bloodflow/
├── app.py                 # Application Dash principale
├── requirements.txt       # Dépendances
├── api/                   # API FastAPI
│   ├── main.py           # Point d'entrée API
│   ├── models/           # Modèles ML
│   └── schemas.py        # Schémas Pydantic
├── assets/               # Fichiers statiques
├── callbacks/           # Callbacks Dash
├── layouts/            # Layouts des pages
├── utils/             # Utilitaires
└── data/              # Données
```

## Contribution
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence
Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## Contact
Votre Nom - email@example.com
Lien du projet : https://github.com/votre-username/bloodflow
