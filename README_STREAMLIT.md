# Application DCB - Version Streamlit

## Description

Cette application permet de visualiser et d'analyser les données DCB (Demand Capacity Balancing) pour l'aéroport de Genève.

## Fichiers

- **DCB_app_streamlit.py** : Application Streamlit (nouvelle version)
- **DCB_app.py** : Application Dash (version originale)
- **Traitement_donnee.py** : Script de traitement des données

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application Streamlit

```bash
streamlit run DCB_app_streamlit.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut.

### Mettre à jour les données

Avant de lancer l'application, vous devez exécuter le script de traitement des données :

```bash
cd TraitementDonnee/Code
python Traitement_donnee.py
```

Ce script va :
- Traiter les données historiques
- Traiter les données futures
- Calculer les retards
- Calculer les mouvements par heure
- Calculer les embarquements
- Appliquer les show-up profiles
- Générer les plannings idéaux
- Exporter les données au format JSON pour l'application

## Fonctionnalités

### Vue calendrier
- Affichage d'un calendrier avec des indicateurs de couleur pour chaque jour
- Vert : Conditions normales
- Jaune : Conditions tendues
- Rouge : Conditions critiques

### Vue détaillée
- Graphiques détaillés pour chaque processeur (piste, stand, sûreté, check-in, douane, gate)
- Comparaison demande vs capacité
- Calcul des KPIs (file d'attente, temps d'attente)

### Options
- Sélection des processeurs à afficher
- Choix entre horaires Expected ou Schedule
- Choix du planning (réel, idéal, ou personnalisé)

### Personnalisation (en développement)
- Modification des plannings
- Ajustement des seuils

## Structure des données

Les données doivent être organisées dans le dossier `Data Source` avec la structure suivante :
```
Data Source/
├── Demande/
│   ├── Actuel/
│   │   ├── ForecastPisteUtilisation_*.json
│   │   ├── SchedulePisteUtilisation_*.json
│   │   ├── ForecastStandUtilisation_*.json
│   │   ├── ScheduleStandUtilisation_*.json
│   │   ├── SUPForecastSurete_*.json
│   │   ├── SUPForecastCheckIn_*.json
│   │   ├── SUPForecastDouane_*.json
│   │   ├── SUPForecastGate_*.json
│   │   └── ...
├── Capacite/
│   ├── Aeroport/
│   ├── Planning/
│   └── TempsProcess/
├── LevelOfService/
└── Annexe/
```

## Différences avec la version Dash

La version Streamlit offre :
- Interface plus moderne et intuitive
- Meilleure performance
- Code plus simple et maintenable
- Déploiement facilité

## Support

Pour toute question ou problème, contactez l'équipe de développement.
