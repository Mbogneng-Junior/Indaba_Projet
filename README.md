# Tableau de Bord - Campagne de Don de Sang

## Description
Tableau de bord interactif pour l'analyse et la visualisation des données des campagnes de don de sang.

## Fonctionnalités
- 📍 Cartographie de la répartition des donneurs
- 🏥 Analyse des conditions de santé et éligibilité
- 🔬 Profilage des donneurs
- 📊 Analyse de l'efficacité des campagnes
- 🔄 Analyse de la fidélisation des donneurs
- 💬 Analyse des retours/sondages

## Installation

1. Cloner le repository
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python app.py
```

## Structure du Projet
```
├── app.py                 # Point d'entrée de l'application
├── assets/               # Fichiers statiques (CSS, images)
├── components/          # Composants réutilisables du dashboard
├── data/               # Données et scripts de traitement
├── layouts/            # Layouts des différentes pages
└── utils/             # Fonctions utilitaires
```

## Technologies Utilisées
- Backend : Python, Dash, Flask
- Visualisation : Plotly, Folium
- Frontend : Dash Bootstrap Components, CSS personnalisé
