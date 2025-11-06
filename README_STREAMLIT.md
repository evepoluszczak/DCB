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

### Option 1 : Interface d'administration (Recommandée) ✨

**Nouvelle fonctionnalité !** L'application dispose maintenant d'une interface d'administration pour gérer les données.

#### Étapes rapides :

1. **Générer les données en local** :
   ```bash
   cd TraitementDonnee/Code
   python Traitement_donnee.py
   ```

2. **Créer un ZIP** :
   - Windows : Clic droit sur `Data Source` → Envoyer vers → Dossier compressé
   - Linux/Mac : `zip -r Data_Source.zip "Data Source"`

3. **Upload dans l'application** :
   - Lancez l'app : `streamlit run DCB_app_streamlit.py`
   - Allez dans la sidebar → "📤 Administration"
   - Uploadez le ZIP
   - Cliquez sur "Extraire et installer"
   - Actualisez la page principale

**Avantages :**
- ✅ Pas besoin de commit Git
- ✅ Fonctionne sur Streamlit Cloud
- ✅ Mise à jour instantanée
- ✅ Interface visuelle simple

Consultez [GUIDE_ADMINISTRATION.md](GUIDE_ADMINISTRATION.md) pour plus de détails.

### Option 2 : Méthode manuelle (Classique)

### 1. Préparer les données

#### a) Configurer le dossier de données

L'application cherche automatiquement un dossier de données dans cet ordre :
1. `Data Source/` (à la racine du projet)
2. `DataSource/` (sans espace)
3. `data/` ou `Data/`
4. Chemin réseau (pour serveur Windows uniquement)

**Créez le dossier si nécessaire :**
```bash
mkdir "Data Source"
```

#### b) Générer les données

Exécutez le script de traitement pour générer les fichiers JSON :

```bash
cd TraitementDonnee/Code
python Traitement_donnee.py
```

Ce script va :
- Traiter les données historiques et futures depuis WEBI
- Calculer les retards prévus
- Calculer les mouvements par heure
- Calculer les embarquements
- Appliquer les show-up profiles
- Générer les plannings idéaux (sûreté, douane)
- Exporter toutes les données au format JSON dans `Data Source/`

⚠️ **Important :** Le script `Traitement_donnee.py` doit être exécuté avec accès aux données sources (exports WEBI). Sur votre serveur local, le chemin est configuré vers `//gva.tld/aig/O/...`

### 2. Lancer l'application Streamlit

**En local :**
```bash
streamlit run DCB_app_streamlit.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut à l'adresse `http://localhost:8501`

### 3. Déploiement sur Streamlit Cloud

Pour déployer sur Streamlit Cloud :

1. **Préparez votre repository :**
   - Commitez tous les fichiers nécessaires
   - **Important :** Vous devez inclure le dossier `Data Source/` avec toutes les données JSON générées

2. **Configurez Streamlit Cloud :**
   - Connectez votre repository GitHub
   - Sélectionnez `DCB_app_streamlit.py` comme fichier principal
   - Les dépendances seront installées automatiquement depuis `requirements.txt`

3. **Limitations :**
   - Le script `Traitement_donnee.py` ne peut PAS s'exécuter sur Streamlit Cloud (pas d'accès aux données WEBI)
   - Vous devez générer les données EN LOCAL puis les commiter dans le repository
   - Mettez à jour les données régulièrement en local et poussez les changements

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

## Dépannage

### Erreur : "Aucun dossier de données trouvé"

**Cause :** L'application ne trouve pas le dossier `Data Source/`

**Solutions :**
1. Vérifiez que le dossier `Data Source` existe à la racine du projet
2. Vérifiez l'orthographe (majuscules, espace)
3. Générez les données avec `python Traitement_donnee.py`

### Erreur : "Le dossier ... n'existe pas"

**Cause :** La structure de dossiers n'est pas complète

**Solution :** Assurez-vous que tous les sous-dossiers existent :
```
Data Source/
├── Demande/Actuel/
├── Capacite/Aeroport/Actuel/
├── Capacite/Planning/Actuel/
├── Capacite/TempsProcess/Actuel/
├── LevelOfService/Actuel/
└── Annexe/Actuel/
```

### Erreur : "Fichier ... introuvable"

**Cause :** Les fichiers JSON n'ont pas été générés

**Solution :**
1. Exécutez `Traitement_donnee.py` pour générer tous les fichiers
2. Vérifiez que le script s'est exécuté sans erreur
3. Vérifiez que les fichiers JSON sont bien dans les dossiers `Actuel/`

### Erreur : "Impossible d'extraire deux dates du fichier"

**Cause :** Le nom du fichier ne contient pas deux dates au format YYYYMMDD

**Solution :** Les fichiers doivent être nommés avec deux dates, par exemple :
- `ForecastPisteUtilisation_20250101_20250131.json`
- `SUPForecastSurete_20250101_20250131.json`

### Performance lente

**Causes possibles :**
- Trop de données chargées en mémoire
- Période d'analyse trop longue

**Solutions :**
1. Réduire la période d'analyse dans `Traitement_donnee.py`
2. Désactiver le cache Streamlit et relancer : `streamlit run DCB_app_streamlit.py --server.enableCORS=false`
3. Augmenter les ressources (RAM) si possible

## Support

Pour toute question ou problème, contactez l'équipe de développement.

## Changelog

### Version 2.0 (Streamlit)
- Migration de Dash vers Streamlit
- Interface utilisateur modernisée
- Détection automatique du dossier de données
- Gestion des erreurs améliorée
- Messages d'aide contextuels
- Documentation complète
