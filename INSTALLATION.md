# Guide d'installation - Application DCB

## 🏠 Lancement en local

L'application DCB utilise maintenant un système de chemins dynamiques pour faciliter le lancement en local, que ce soit depuis l'aéroport ou depuis votre domicile.

### Configuration automatique des chemins

Le fichier `TraitementDonnee/Code/chemin_dossier.py` gère automatiquement tous les chemins :

```python
# Structure détectée automatiquement :
CHEMIN_APP_RACINE      → /chemin/vers/DCB/
CHEMIN_DATA_SOURCE     → /chemin/vers/DCB/Data Source/
DOSSIER_TRAITEMENT     → /chemin/vers/DCB/TraitementDonnee/
DOSSIER_DATA           → /chemin/vers/DCB/TraitementDonnee/Data/
CHEMIN_INPUT           → /chemin/vers/DCB/TraitementDonnee/Data/Input/
CHEMIN_OUTPUT          → /chemin/vers/DCB/TraitementDonnee/Data/Output/
```

### Test de la configuration

Avant de lancer l'application, vérifiez que tous les chemins sont correctement configurés :

```bash
python test_chemins_local.py
```

Vous devriez voir :
```
============================================================
TEST DES CHEMINS LOCAUX - DCB APPLICATION
============================================================
✅ Import du module chemin_dossier réussi!

CHEMINS CONFIGURÉS:
  📁 CHEMIN_APP_RACINE    : /home/user/DCB
  📊 CHEMIN_DATA_SOURCE   : /home/user/DCB/Data Source
  ...

✅ TOUS LES CHEMINS SONT VALIDES!
✅ L'application peut être lancée en local avec:
   streamlit run DCB_app_streamlit.py
============================================================
```

### Lancement rapide

```bash
# 1. Se placer dans le dossier DCB
cd /chemin/vers/DCB

# 2. Activer l'environnement virtuel (si utilisé)
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Lancer l'application
streamlit run DCB_app_streamlit.py

# L'application s'ouvrira dans votre navigateur par défaut
# URL : http://localhost:8501
```

### Structure de dossiers requise

```
DCB/
├── DCB_app_streamlit.py        # Application principale
├── TraitementDonnee/
│   ├── Code/
│   │   └── chemin_dossier.py   # Configuration des chemins
│   └── Data/
│       ├── Input/              # Données d'entrée
│       └── Output/             # Résultats
├── Data Source/                # Données sources
│   ├── Demande/
│   │   └── Actuel/            # Fichiers JSON de demande
│   ├── Capacite/
│   │   └── Actuel/            # Fichiers JSON de capacité
│   ├── LevelOfService/
│   │   └── Actuel/            # Fichiers JSON LOS
│   └── Annexe/
│       └── Actuel/            # Fichiers JSON annexes
└── requirements.txt            # Dépendances Python
```

## 📦 Installation des dépendances

### Installation standard

```bash
pip install -r requirements.txt
```

### Installation pour développement

Si vous développez ou modifiez le code de traitement :

```bash
pip install -r requirements.txt

# Optionnel : outils de développement
pip install jupyter notebook ipython
```

## 📋 Dépendances requises

### Pour l'interface Streamlit (minimum)

```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
```

### Pour le traitement des données (complet)

```
# Data processing
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0          # Pour lire les fichiers Excel

# Machine Learning
scikit-learn>=1.3.0      # RandomForest, LinearRegression, etc.
xgboost>=2.0.0           # Gradient boosting

# Utilities
tqdm>=4.65.0             # Barres de progression
python-dateutil>=2.8.0   # Manipulation de dates
```

## 🚀 Installation rapide

### Windows

```powershell
# Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run DCB_app_streamlit.py
```

### Linux / macOS

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run DCB_app_streamlit.py
```

## 🔍 Vérification de l'installation

Pour vérifier que toutes les dépendances sont installées :

```python
# test_imports.py
try:
    import streamlit
    print("✅ streamlit")
except ImportError:
    print("❌ streamlit manquant")

try:
    import plotly
    print("✅ plotly")
except ImportError:
    print("❌ plotly manquant")

try:
    import pandas
    print("✅ pandas")
except ImportError:
    print("❌ pandas manquant")

try:
    import numpy
    print("✅ numpy")
except ImportError:
    print("❌ numpy manquant")

try:
    import sklearn
    print("✅ scikit-learn")
except ImportError:
    print("❌ scikit-learn manquant")

try:
    import xgboost
    print("✅ xgboost")
except ImportError:
    print("❌ xgboost manquant")

try:
    import tqdm
    print("✅ tqdm")
except ImportError:
    print("❌ tqdm manquant")

try:
    import openpyxl
    print("✅ openpyxl")
except ImportError:
    print("❌ openpyxl manquant")

print("\n✨ Si tous les packages affichent ✅, vous êtes prêt !")
```

Exécutez ce script avec :
```bash
python test_imports.py
```

## 🐛 Problèmes courants

### "No module named 'xxx'"

**Solution :**
```bash
pip install xxx
```

Ou réinstallez tous les requirements :
```bash
pip install -r requirements.txt --upgrade
```

### Erreur avec xgboost sur Windows

**Solution :**
1. Installez Visual C++ Build Tools
2. Ou utilisez une version pré-compilée :
```bash
pip install xgboost --no-cache-dir
```

### Erreur avec scikit-learn

**Solution :**
```bash
pip install scikit-learn --upgrade
```

### Conflits de versions

**Solution :** Utilisez un environnement virtuel propre :
```bash
# Supprimer l'ancien venv
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Recréer
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Réinstaller
pip install -r requirements.txt
```

## 📊 Sur Streamlit Cloud

Sur Streamlit Cloud, les dépendances sont installées automatiquement depuis `requirements.txt`.

**Important :**
- Pas besoin d'installation manuelle
- Le fichier `requirements.txt` doit être à la racine du repository
- Les dépendances sont installées à chaque déploiement
- Redémarrez l'app si vous modifiez `requirements.txt`

**Pour forcer la réinstallation :**
1. Allez dans "Manage app" sur Streamlit Cloud
2. Cliquez "Reboot app"
3. Attendez la réinstallation (1-2 minutes)

## 💾 Taille totale des dépendances

Environ **500-800 MB** pour une installation complète incluant :
- Streamlit + dépendances web
- Pandas + Numpy (calculs scientifiques)
- Scikit-learn (machine learning)
- XGBoost (gradient boosting)

**Conseil :** Utilisez toujours un environnement virtuel pour éviter les conflits.

## 🔄 Mise à jour des dépendances

Pour mettre à jour toutes les dépendances :

```bash
pip install -r requirements.txt --upgrade
```

Pour mettre à jour un package spécifique :

```bash
pip install --upgrade streamlit
```

## 📝 Générer un nouveau requirements.txt

Si vous avez ajouté des dépendances manuellement :

```bash
pip freeze > requirements.txt
```

**Attention :** Cela inclut TOUTES les dépendances, y compris transitives.
Préférez maintenir `requirements.txt` manuellement avec seulement les dépendances principales.

## 🆘 Support

Si vous rencontrez des problèmes d'installation :

1. Vérifiez votre version de Python : `python --version` (3.8+ requis)
2. Mettez à jour pip : `pip install --upgrade pip`
3. Vérifiez les logs d'erreur
4. Essayez dans un nouvel environnement virtuel

## 📚 Documentation des dépendances principales

- [Streamlit](https://docs.streamlit.io/)
- [Plotly](https://plotly.com/python/)
- [Pandas](https://pandas.pydata.org/docs/)
- [Scikit-learn](https://scikit-learn.org/stable/)
- [XGBoost](https://xgboost.readthedocs.io/)
