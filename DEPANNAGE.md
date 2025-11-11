# 🔧 Guide de Dépannage DCB App

## Diagnostic Rapide

Si vous voyez le message **"Les données n'ont pas été chargées correctement"**, suivez ces étapes :

---

## ✅ 1. Vérification Automatique

Exécutez le script de diagnostic :

```bash
python3 test_chargement.py
```

Ce script vérifie :
- ✅ Import du module `chemin_dossier`
- ✅ Existence du dossier `Data Source`
- ✅ Structure des sous-dossiers
- ✅ Chargement des fichiers JSON
- ✅ Dépendances Python (Streamlit, Plotly, etc.)

---

## 🔍 2. Problèmes Courants et Solutions

### Problème : "Aucun dossier de données trouvé"

**Cause** : Le dossier `Data Source` n'existe pas ou n'est pas au bon endroit.

**Solution** :
```bash
# Vérifier que le dossier existe
ls -la "Data Source"

# S'il n'existe pas, créez-le
mkdir -p "Data Source"/{Demande,Capacite,LevelOfService,Annexe}/Actuel
```

---

### Problème : "Le dossier ... n'existe pas"

**Cause** : La structure des sous-dossiers est incomplète.

**Solution** :
```bash
# Créer toute la structure
mkdir -p "Data Source/Demande/Actuel"
mkdir -p "Data Source/Capacite/Aeroport/Actuel"
mkdir -p "Data Source/Capacite/Planning/Actuel"
mkdir -p "Data Source/Capacite/TempsProcess/Actuel"
mkdir -p "Data Source/LevelOfService/Actuel"
mkdir -p "Data Source/Annexe/Actuel"
```

---

### Problème : "Fichier ... introuvable"

**Cause** : Les fichiers JSON ne sont pas dans les bons dossiers.

**Solution** :

1. **Vérifiez les fichiers présents** :
   ```bash
   find "Data Source" -name "*.json" | sort
   ```

2. **Fichiers requis** :

   **Annexe/Actuel/**
   - `GraphNames.json`

   **Capacite/Aeroport/Actuel/**
   - `CapacitePiste.json`
   - `CapaciteGate.json`
   - `CapaciteQueue.json`
   - `StandDispo.json`
   - `MaxPlanning.json`

   **Capacite/TempsProcess/Actuel/**
   - `TempsProcess.json`

   **LevelOfService/Actuel/**
   - `ValeursCritiquesDuree.json`
   - `ValeursCritiquesSurface.json`

   **Capacite/Planning/Actuel/**
   - `PlanningSurete_YYYYMMDD-YYYYMMDD.json`
   - `PlanningSureteIdeal_YYYYMMDD-YYYYMMDD.json`
   - `PlanningCheckIn_YYYYMMDD-YYYYMMDD.json`
   - `PlanningDouane_YYYYMMDD-YYYYMMDD.json`
   - `PlanningDouaneIdeal_YYYYMMDD-YYYYMMDD.json`

   **Demande/Actuel/**
   - `ForecastPisteUtilisation_YYYYMMDD-YYYYMMDD.json`
   - `SchedulePisteUtilisation_YYYYMMDD-YYYYMMDD.json`
   - `ForecastStandUtilisation_YYYYMMDD-YYYYMMDD.json`
   - `ScheduleStandUtilisation_YYYYMMDD-YYYYMMDD.json`
   - `SUPForecastSurete_YYYYMMDD-YYYYMMDD.json`
   - `SUPForecastCheckIn_YYYYMMDD-YYYYMMDD.json`
   - `SUPForecastDouane_YYYYMMDD-YYYYMMDD.json`
   - `SUPForecastGate_YYYYMMDD-YYYYMMDD.json`
   - `ForecastGateEmbarquement_YYYYMMDD-YYYYMMDD.json`
   - `ScheduleGateEmbarquement_YYYYMMDD-YYYYMMDD.json`

3. **Si des fichiers manquent**, générez-les en local ou utilisez la page **Administration** pour les uploader.

---

### Problème : "ModuleNotFoundError"

**Cause** : Dépendances Python non installées.

**Solution** :
```bash
# Réinstaller toutes les dépendances
pip install -r requirements.txt

# Ou avec pip3
pip3 install -r requirements.txt

# Vérifier l'installation
python3 -c "import streamlit; print('Streamlit OK')"
python3 -c "import plotly; print('Plotly OK')"
```

---

### Problème : L'application se lance mais affiche "Data loaded: False"

**Cause** : Erreur lors du chargement des fichiers JSON.

**Solution** :

1. **Vérifier les logs** en lançant avec debug :
   ```bash
   streamlit run DCB_app_streamlit.py --logger.level=debug
   ```

2. **Vérifier l'intégrité d'un fichier JSON** :
   ```bash
   # Tester un fichier JSON
   python3 -m json.tool "Data Source/Annexe/Actuel/GraphNames.json"
   ```

3. **Si un fichier est corrompu**, régénérez-le ou uploadez-en un nouveau.

---

### Problème : Port 8501 déjà utilisé

**Cause** : Une autre instance de Streamlit tourne déjà.

**Solution** :
```bash
# Option 1 : Utiliser un autre port
streamlit run DCB_app_streamlit.py --server.port=8502

# Option 2 : Tuer le processus existant
# Linux/Mac
pkill -f streamlit

# Windows
taskkill /IM streamlit.exe /F
```

---

### Problème : "Erreur de syntaxe dans config.toml"

**Cause** : Configuration Streamlit invalide.

**Solution** :

Vérifiez `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#1E3A8A"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8FAFC"
textColor = "#1E293B"
font = "sans serif"  # ATTENTION: avec un espace, pas un tiret!

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

**Note** : `font` doit être `"sans serif"` (avec espace), pas `"sans-serif"` (avec tiret).

---

## 🚀 3. Relancer l'Application

Après avoir corrigé le problème :

### **Option A : Scripts automatiques**

```bash
# Linux/Mac
./launch_dcb.sh

# Windows
launch_dcb.bat
```

### **Option B : Manuel**

```bash
streamlit run DCB_app_streamlit.py
```

---

## 📊 4. Vérifier le Chargement

Une fois l'app lancée, vérifiez :

1. **Dans le terminal**, vous devriez voir :
   ```
   Chargement des fichiers de données...
   Données chargées avec succès.
   ```

2. **Dans l'application** :
   - Le dashboard affiche des KPIs
   - Les graphiques se chargent
   - Aucun message d'erreur rouge

---

## 🔍 5. Diagnostic Avancé

### Activer le mode debug

Modifiez temporairement `.streamlit/config.toml` :

```toml
[logger]
level = "debug"
messageFormat = "%(asctime)s %(message)s"
```

Puis relancez :

```bash
streamlit run DCB_app_streamlit.py
```

Les logs détaillés apparaîtront dans le terminal.

---

### Vérifier les permissions

```bash
# Vérifier que les fichiers sont lisibles
ls -lh "Data Source/Annexe/Actuel/"

# Si nécessaire, corriger les permissions
chmod -R 755 "Data Source"
```

---

### Tester le chargement manuel

Créez un script de test `test_manuel.py` :

```python
import sys
import os
import json

sys.path.insert(0, 'TraitementDonnee/Code')
from chemin_dossier import CHEMIN_DATA_SOURCE

# Tester le chargement d'un fichier
fichier = CHEMIN_DATA_SOURCE / "Annexe/Actuel/202507250828GraphNames.json"

try:
    with open(fichier, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Chargement réussi!")
    print(f"Données: {data.keys()}")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

Exécutez :
```bash
python3 test_manuel.py
```

---

## 📞 6. Support

Si le problème persiste après avoir suivi ce guide :

1. **Collectez les informations** :
   ```bash
   # Version Python
   python3 --version

   # Version Streamlit
   streamlit --version

   # Structure des données
   tree "Data Source" -L 3

   # Logs de l'application
   streamlit run DCB_app_streamlit.py > logs.txt 2>&1
   ```

2. **Consultez les autres guides** :
   - [README.md](README.md) - Vue d'ensemble
   - [LANCEMENT_RAPIDE.md](LANCEMENT_RAPIDE.md) - Guide démarrage
   - [README_STREAMLIT.md](README_STREAMLIT.md) - Documentation technique

3. **Contactez le support** avec :
   - Le message d'erreur exact
   - Les logs collectés
   - Résultat de `python3 test_chargement.py`

---

## ✅ Checklist de Vérification

Avant de demander de l'aide, vérifiez que vous avez :

- [ ] Exécuté `python3 test_chargement.py` ✅
- [ ] Vérifié que `Data Source/` existe à la racine
- [ ] Confirmé la présence des sous-dossiers `/Actuel/`
- [ ] Vérifié qu'il y a des fichiers JSON dans chaque dossier
- [ ] Installé toutes les dépendances (`pip install -r requirements.txt`)
- [ ] Testé le chargement d'au moins un fichier JSON manuellement
- [ ] Vérifié que le port 8501 est libre
- [ ] Corrigé `.streamlit/config.toml` (font = "sans serif")
- [ ] Lancé avec `./launch_dcb.sh` ou `launch_dcb.bat`

---

## 🎯 Solution Rapide (90% des cas)

```bash
# 1. Vérifier les données
python3 test_chargement.py

# 2. Réinstaller les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
./launch_dcb.sh  # ou launch_dcb.bat sur Windows

# 4. Ouvrir http://localhost:8501
```

---

**Version** : 1.0
**Dernière mise à jour** : Novembre 2025
**Compatible avec** : DCB App v2.0
