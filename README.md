# ✈️ DCB Tool - Demand Capacity Balancing

**Application Streamlit moderne pour l'analyse DCB de l'Aéroport de Genève**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red)
![Status](https://img.shields.io/badge/status-production-success)

---

## 🚀 Lancement Rapide

### Windows 🪟
```cmd
launch_dcb.bat
```

### Linux / Mac 🐧 🍎
```bash
./launch_dcb.sh
```

**C'est tout !** L'application s'ouvre automatiquement sur `http://localhost:8501`

---

## 📖 Documentation

- **[LANCEMENT_RAPIDE.md](LANCEMENT_RAPIDE.md)** - Guide de démarrage complet
- **[README_STREAMLIT.md](README_STREAMLIT.md)** - Documentation technique détaillée
- **[DESIGN_MODERNE.md](DESIGN_MODERNE.md)** - Guide du design et des fonctionnalités
- **[OPTIMISATIONS_VISUELLES.md](OPTIMISATIONS_VISUELLES.md)** - Détails des améliorations UX/UI

---

## ✨ Fonctionnalités

### Interface Moderne
- 🎨 Design professionnel avec animations fluides
- 📊 Dashboard interactif avec KPIs en temps réel
- 📈 Graphiques Plotly haute qualité et interactifs
- 🎯 Navigation intuitive par onglets
- 👋 Mode d'accueil pour nouveaux utilisateurs

### Analyses Disponibles

#### 📊 Dashboard Principal
- Vue d'ensemble avec KPIs globaux
- 4 onglets : Vue d'ensemble, Opérations, Passagers, Analytique
- Métriques clés : statut système, jours de données, processeurs actifs

#### 📅 Vue Calendrier
- Visualisation mensuelle avec codes couleur
- 🟢 Vert : Conditions excellentes (< 5 min d'attente)
- 🟡 Jaune : Conditions acceptables (5-10 min)
- 🔴 Rouge : Conditions critiques (> 10 min)

#### 🛫 Opérations Aéroportuaires
- Mouvements de piste
- Occupation des stands
- Graphiques détaillés par date

#### 👥 Flux Passagers
- Sûreté (International, Schengen, Transfer)
- Check-in (zones A, B, C)
- Douane (différentes zones)
- Gate/Embarquement
- Comparaison Demande vs Capacité
- Calcul des files d'attente et temps d'attente

---

## 📦 Structure du Projet

```
DCB/
├── DCB_app_streamlit.py       # Application Streamlit principale
├── requirements.txt            # Dépendances Python
├── launch_dcb.sh              # Script de lancement Linux/Mac
├── launch_dcb.bat             # Script de lancement Windows
│
├── .streamlit/
│   └── config.toml            # Configuration Streamlit (thème, serveur)
│
├── Data Source/               # Données JSON (générées en local)
│   ├── Demande/Actuel/       # Données de demande
│   ├── Capacite/             # Capacités (Aeroport, Planning, TempsProcess)
│   ├── LevelOfService/       # Seuils LOS
│   └── Annexe/               # Métadonnées
│
├── pages/
│   └── 1_Administration.py    # Page admin pour upload de données
│
├── TraitementDonnee/Code/
│   └── chemin_dossier.py     # Utilitaire pour chemins de données
│
└── Documentation (*.md)       # Guides et documentation
```

---

## 🔧 Installation

### Prérequis
- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **pip** (inclus avec Python)

### Installation Automatique (Recommandé)

Les scripts de lancement installent automatiquement les dépendances :

- **Windows** : Double-cliquez sur `launch_dcb.bat`
- **Linux/Mac** : Exécutez `./launch_dcb.sh`

### Installation Manuelle

```bash
# 1. Cloner le repository
git clone <repository-url>
cd DCB

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run DCB_app_streamlit.py
```

---

## 📊 Données

### Structure des Données

L'application nécessite des fichiers JSON dans `Data Source/` avec la structure suivante :

```
Data Source/
├── Demande/Actuel/
│   ├── ForecastPisteUtilisation_YYYYMMDD_YYYYMMDD.json
│   ├── SchedulePisteUtilisation_YYYYMMDD_YYYYMMDD.json
│   ├── ForecastStandUtilisation_YYYYMMDD_YYYYMMDD.json
│   ├── SUPForecastSurete_YYYYMMDD_YYYYMMDD.json
│   ├── SUPForecastCheckIn_YYYYMMDD_YYYYMMDD.json
│   └── ...
├── Capacite/Aeroport/Actuel/
│   ├── CapacitePiste.json
│   ├── CapaciteGate.json
│   └── ...
└── ...
```

### Génération des Données

**Important** : Les données sont générées **en local** par un processus séparé de traitement.

Les fichiers JSON doivent être placés dans le dossier `Data Source/` ou uploadés via l'interface d'administration.

---

## 🌐 Partage Multi-Utilisateurs

### Option 1 : Réseau Local

1. Lancez l'app sur une machine hôte
2. Notez l'adresse IP de la machine : `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
3. Les autres accèdent via `http://[IP]:8501`

### Option 2 : Streamlit Cloud (Recommandé)

1. Poussez le code sur GitHub
2. Connectez-vous sur [share.streamlit.io](https://share.streamlit.io)
3. Déployez votre repository
4. Partagez l'URL : `https://votre-app.streamlit.app`

**Avantages** :
- ✅ Gratuit pour usage public
- ✅ HTTPS automatique
- ✅ Mises à jour auto (git push)
- ✅ Supporte 100+ utilisateurs simultanés

---

## ⚙️ Configuration

Modifiez `.streamlit/config.toml` pour personnaliser le thème et les paramètres serveur.

---

## 🛠️ Dépannage

### L'application ne démarre pas

```bash
# Vérifier Python
python --version  # ou python3 --version

# Réinstaller les dépendances
pip install -r requirements.txt

# Changer le port si occupé
streamlit run DCB_app_streamlit.py --server.port=8502
```

### Aucune donnée affichée

1. Vérifiez que `Data Source/` existe à la racine
2. Utilisez la page **Administration** pour uploader des données
3. Vérifiez la structure des sous-dossiers

---

## 📈 Performance

| Métrique | Valeur |
|----------|--------|
| Premier chargement | ~3s |
| Chargements suivants | ~0.5s |
| Changement de vue | <100ms |
| Utilisateurs simultanés | 100+ |

---

## 🎯 Utilisation

### Workflows Types

1. **Analyse Quotidienne** : Dashboard → Opérations → Sélectionner date
2. **Analyse Passagers** : Dashboard → Passagers → Choisir processeur
3. **Vue Mensuelle** : Calendrier → Identifier jours critiques (🔴)

### Raccourcis

- `R` : Réexécuter l'app
- `C` : Effacer le cache
- `?` : Aide Streamlit

---

## 🚧 Roadmap

### ✅ v2.0 (Actuel)
- Design moderne avec animations
- Dashboard multi-onglets
- Mode d'accueil interactif
- Scripts de lancement automatiques

### 🔜 v2.1+
- Export de données (PDF, Excel)
- Mode sombre
- Notifications temps réel
- Prédictions ML

---

## 📞 Support

1. Consultez [LANCEMENT_RAPIDE.md](LANCEMENT_RAPIDE.md)
2. Utilisez le bouton **"ℹ️ Aide & Guide"** dans l'app
3. Contactez l'équipe de développement

---

**Version** : 2.0 - Visual Optimization
**Dernière mise à jour** : Novembre 2025
**Plateforme** : Streamlit
**Statut** : ✅ Production Ready

---

<div align="center">

**Développé avec ❤️ pour l'Aéroport de Genève**

[Documentation](README_STREAMLIT.md) • [Guide Rapide](LANCEMENT_RAPIDE.md) • [Design](DESIGN_MODERNE.md)

</div>