# Migration vers le système de chemins locaux

## 📊 État actuel de la migration

### ✅ Complété

1. **Système de chemins centralisé**
   - ✅ `TraitementDonnee/Code/chemin_dossier.py` créé
   - ✅ Détection automatique de la racine du projet
   - ✅ Tous les chemins principaux définis (CHEMIN_INPUT, CHEMIN_OUTPUT, etc.)

2. **Application principale**
   - ✅ `DCB_app_streamlit.py` mis à jour pour utiliser `chemin_dossier.py`
   - ✅ Fonctionne en local avec `streamlit run DCB_app_streamlit.py`
   - ✅ Documentation ajoutée dans `INSTALLATION.md`

3. **Script de traitement principal**
   - ✅ `Traitement_donnee.py` mis à jour pour utiliser `chemin_dossier.py`
   - ✅ Vérification du dossier WEBI avec chemins dynamiques
   - ✅ Correction de la faute de frappe : `Pax_PlaningSurete` → `Pax_PlanningSurete`

4. **Outils de test et analyse**
   - ✅ `test_chemins_local.py` : vérifie la configuration des chemins
   - ✅ `test_traitement_imports.py` : vérifie les imports des modules
   - ✅ `analyse_chemins_en_dur.py` : identifie les chemins en dur restants
   - ✅ `rapport_chemins_en_dur.txt` : rapport détaillé des chemins à migrer

### ⚠️ En attente

**12 modules utilisent encore des chemins en dur** (31 occurrences au total)

| Fichier | Occurrences | Priorité |
|---------|-------------|----------|
| `Avion_LinkFutur.py` | 6 | 🔴 Haute |
| `Avion_ExpectedTime.py` | 5 | 🔴 Haute |
| `Pax_SUPjson.py` | 3 | 🟡 Moyenne |
| `PBI_CalculPowerBI.py` | 3 | 🟡 Moyenne |
| `Avion_LinkHisto.py` | 2 | 🟡 Moyenne |
| `Pax_ApplicationSUP.py` | 2 | 🟡 Moyenne |
| `Pax_Embarquement.py` | 2 | 🟡 Moyenne |
| `Pax_PlanningIdealDouane.py` | 2 | 🟡 Moyenne |
| `Pax_PlanningIdealSurete.py` | 2 | 🟡 Moyenne |
| `Pax_PlanningSurete.py` | 2 | 🟡 Moyenne |
| `Avion_Mouvements.py` | 1 | 🟢 Basse |
| `Avion_Fonctions_data_future.py` | 1 | 🟢 Basse |

## 🔧 Comment migrer un module

### Exemple : Migration de `Pax_PlanningSurete.py`

**Avant :**
```python
dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Autre"
```

**Après :**
```python
from chemin_dossier import CHEMIN_INPUT

dossier = CHEMIN_INPUT / "Autre"  # Utilise pathlib.Path
# OU
dossier = str(CHEMIN_INPUT / "Autre")  # Si vous avez besoin d'un string
```

### Variables disponibles dans `chemin_dossier.py`

```python
CHEMIN_APP_RACINE      # /chemin/vers/DCB/
CHEMIN_DATA_SOURCE     # /chemin/vers/DCB/Data Source/
DOSSIER_TRAITEMENT     # /chemin/vers/DCB/TraitementDonnee/
DOSSIER_CODE           # /chemin/vers/DCB/TraitementDonnee/Code/
DOSSIER_DATA           # /chemin/vers/DCB/TraitementDonnee/Data/
CHEMIN_INPUT           # /chemin/vers/DCB/TraitementDonnee/Data/Input/
CHEMIN_OUTPUT          # /chemin/vers/DCB/TraitementDonnee/Data/Output/
CHEMIN_AUTRE           # /chemin/vers/DCB/TraitementDonnee/Data/Input/Autre/
```

### Pattern de remplacement

1. **Ajouter l'import en haut du fichier :**
   ```python
   from chemin_dossier import CHEMIN_INPUT, CHEMIN_OUTPUT, CHEMIN_DATA_SOURCE
   from pathlib import Path  # Si pas déjà importé
   ```

2. **Remplacer les chemins en dur :**

   | Type de chemin | Remplacement |
   |----------------|--------------|
   | `.../TraitementDonnee/Data/Input` | `CHEMIN_INPUT` |
   | `.../TraitementDonnee/Data/Output` | `CHEMIN_OUTPUT` |
   | `.../Data Source` | `CHEMIN_DATA_SOURCE` |
   | `.../TraitementDonnee/Data/Input/WEBI` | `CHEMIN_INPUT / "WEBI"` |
   | `.../TraitementDonnee/Data/Input/Autre` | `CHEMIN_AUTRE` |

3. **Utiliser pathlib pour construire les chemins :**
   ```python
   # ❌ Ancien style
   fichier = dossier + "/" + nom_fichier

   # ✅ Nouveau style
   fichier = dossier / nom_fichier
   ```

## 📝 Problèmes identifiés

### 1. Signature de fonction incorrecte

**Fichier :** `Pax_PlanningSurete.py`

**Problème :**
```python
def PlanningSurete(format):  # ❌ Signature actuelle
    ...
```

**Appelé comme :**
```python
PlanningSurete(DCB_xlsx, "csv")  # ❌ 2 arguments mais fonction n'en attend qu'1
```

**Solution :**
```python
def PlanningSurete(DCB_xlsx, format):  # ✅ Accepter les 2 paramètres
    # Utiliser DCB_xlsx pour extraire les dates de début/fin
    debut = DCB_xlsx["Date et heure"].min().date()
    fin = DCB_xlsx["Date et heure"].max().date()
    ...
```

### 2. Chemins externes (hors projet)

Certains modules accèdent à des dossiers externes :
- `//gva.tld/.../17_PBI/01 - Data/...` (données PowerBI)
- `//gva.tld/.../10_PERSONAL_FOLDERS/7_LOUISE/...` (dossier Louise)

**Question :** Ces chemins doivent-ils être :
- Ajoutés à `chemin_dossier.py` ?
- Configurés via un fichier de configuration ?
- Rendus optionnels ?

## 🚀 Prochaines étapes recommandées

### Option 1 : Migration manuelle progressive

Migrer les modules un par un, en commençant par les plus utilisés :

1. `Avion_LinkHisto.py` et `Avion_LinkFutur.py` (chargement des données)
2. `Pax_ApplicationSUP.py` (traitement principal)
3. Les autres modules `Pax_*.py`
4. Les utilitaires et modules secondaires

### Option 2 : Migration automatisée

Créer un script qui :
1. Détecte les patterns de chemins en dur
2. Les remplace automatiquement par les variables appropriées
3. Ajoute les imports nécessaires
4. Génère un rapport des modifications

### Option 3 : Migration ciblée

Ne migrer que les modules essentiels au fonctionnement local :
- Garder les modules PowerBI avec chemins en dur (utilisés uniquement à l'aéroport)
- Migrer uniquement les modules appelés par `Traitement_donnee.py`

## ✅ Comment vérifier que tout fonctionne

### 1. Test des chemins
```bash
python test_chemins_local.py
```

Résultat attendu :
```
✅ TOUS LES CHEMINS SONT VALIDES!
✅ L'application peut être lancée en local avec:
   streamlit run DCB_app_streamlit.py
```

### 2. Test des imports
```bash
python test_traitement_imports.py
```

**Note :** Les erreurs "No module named 'pandas'" sont normales si pandas n'est pas installé dans cet environnement.

### 3. Test de l'application
```bash
streamlit run DCB_app_streamlit.py
```

L'application devrait se lancer sans erreur sur `http://localhost:8501`

### 4. Test du traitement complet (si données disponibles)
```bash
cd TraitementDonnee/Code
python Traitement_donnee.py
```

## 📚 Ressources

- **Guide d'installation :** `INSTALLATION.md`
- **Rapport des chemins en dur :** `rapport_chemins_en_dur.txt`
- **Système de chemins :** `TraitementDonnee/Code/chemin_dossier.py`
- **Tests :**
  - `test_chemins_local.py`
  - `test_traitement_imports.py`
- **Analyse :** `analyse_chemins_en_dur.py`

## 🎯 Objectif final

Permettre à n'importe qui de cloner le repo et de lancer l'application depuis n'importe quel emplacement :

```bash
# Cloner le repo
git clone [url]
cd DCB

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run DCB_app_streamlit.py

# ✅ L'application fonctionne immédiatement, sans configuration !
```

## 💡 Avantages de la migration complète

- ✅ **Portabilité** : Fonctionne depuis n'importe quel emplacement
- ✅ **Multi-environnement** : Aéroport, domicile, cloud, etc.
- ✅ **Multi-OS** : Windows, Linux, macOS
- ✅ **Maintenance** : Un seul fichier à modifier pour changer les chemins
- ✅ **Collaboration** : Partage simplifié du code entre équipes
- ✅ **Tests** : Facilite les tests automatisés
- ✅ **Déploiement** : Compatible avec Docker, CI/CD, etc.
