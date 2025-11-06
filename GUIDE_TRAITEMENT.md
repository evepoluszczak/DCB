# Guide : Exécuter le traitement des données depuis l'app

## 🎯 Nouveauté

Vous pouvez maintenant **exécuter le traitement des données directement depuis l'application**, sans avoir besoin d'installer Python localement ou d'accéder au réseau de l'aéroport !

## 📋 Deux méthodes disponibles

### Méthode 1 : Upload des fichiers WEBI (Recommandée) ✨

**Avantages :**
- ✅ Fonctionne sur Streamlit Cloud
- ✅ Pas besoin d'accès au réseau local
- ✅ Exécution dans l'interface avec progression en temps réel
- ✅ Génération automatique des données JSON

**Processus :**

1. **Exportez les fichiers depuis WEBI** (sur votre machine ou serveur avec accès)

2. **Créez un ZIP** :
   - Mettez tous les fichiers Excel/CSV exportés dans un dossier
   - Compressez ce dossier en fichier ZIP

   Exemple de fichiers requis :
   ```
   fichiers_webi.zip
   ├── historique_vols.xlsx
   ├── previsions_vols.xlsx
   ├── planning_surete.csv
   ├── planning_douane.csv
   └── ... (autres fichiers)
   ```

3. **Dans l'application** :
   - Allez sur **📤 Administration** (dans la sidebar)
   - Cliquez sur l'onglet **"⚙️ Exécuter le traitement"**
   - Sélectionnez **"📤 Upload fichiers WEBI"**
   - Uploadez votre fichier ZIP
   - Cliquez sur **"▶️ Lancer le traitement"**

4. **Suivez la progression** :
   - Une zone de texte affiche les étapes en temps réel
   - Le traitement prend généralement 2-5 minutes
   - À la fin, vous verrez un message de succès avec 🎈

5. **Actualisez la page principale** :
   - Cliquez sur le bouton "🗑️ Effacer le cache et actualiser"
   - Ou retournez sur la page principale et appuyez sur F5

**C'est tout !** Les données sont maintenant disponibles dans l'application DCB.

### Méthode 2 : Utiliser le chemin réseau (Local uniquement)

**Prérequis :**
- Application lancée en local (`streamlit run DCB_app_streamlit.py`)
- Accès au partage réseau `//gva.tld/aig/O/...`

**Processus :**

1. Dans l'application, allez sur **📤 Administration**
2. Onglet **"⚙️ Exécuter le traitement"**
3. Sélectionnez **"🌐 Utiliser chemin réseau"**
4. Cliquez sur **"🔍 Vérifier l'accès au réseau"** pour confirmer
5. Cliquez sur **"▶️ Lancer le traitement avec chemin réseau"**
6. Suivez la progression en temps réel

## 🔄 Étapes du traitement

Le traitement exécute automatiquement ces 11 étapes :

1. ✅ Traitement de la donnée historique
2. ✅ Traitement de la donnée future
3. ✅ Calcul des retards
4. ✅ Calcul du nombre de mouvements par heure roulante
5. ✅ Calcul des embarquements par tranche de 5 minutes
6. ✅ Application des show-up profiles aux vols
7. ✅ Transformation du planning sûreté au format DCB app
8. ✅ Calcul du planning idéal à la douane
9. ✅ Calcul du planning idéal à la sûreté
10. ✅ Transformation de la donnée au format DCB app python
11. ✅ Transformation de la donnée au format DCB PowerBI

## 📊 Fichiers générés

Le traitement génère automatiquement tous les fichiers JSON requis dans `Data Source/` :

```
Data Source/
├── Demande/Actuel/
│   ├── ForecastPisteUtilisation_*.json
│   ├── SchedulePisteUtilisation_*.json
│   ├── SUPForecastSurete_*.json
│   ├── SUPForecastCheckIn_*.json
│   ├── SUPForecastDouane_*.json
│   └── SUPForecastGate_*.json
├── Capacite/
│   ├── Aeroport/Actuel/
│   ├── Planning/Actuel/
│   └── TempsProcess/Actuel/
├── LevelOfService/Actuel/
└── Annexe/Actuel/
```

## ⚡ Workflow recommandé

### Pour Streamlit Cloud (Production)

**Hebdomadaire ou selon besoin :**

1. Exportez les fichiers WEBI depuis votre système
2. Créez un ZIP avec ces fichiers
3. Allez sur votre app Streamlit Cloud
4. Page Administration → Exécuter le traitement → Upload fichiers WEBI
5. Uploadez le ZIP et lancez le traitement
6. Attendez 2-5 minutes
7. Actualisez la page principale

**Avantage :** Tout se fait depuis le navigateur, pas besoin d'installation locale !

### Pour environnement local

**Option A - Avec l'interface (Recommandée) :**
- Même processus que ci-dessus via l'interface web

**Option B - En ligne de commande :**
```bash
cd TraitementDonnee/Code
python Traitement_donnee.py
```

## 🔍 Vérification

Après le traitement, vérifiez que tout s'est bien passé :

1. Allez sur **📤 Administration** → Onglet **"📊 État des données"**
2. Vérifiez que tous les dossiers sont présents (✅)
3. Vérifiez le nombre de fichiers JSON générés
4. Vérifiez la date de dernière modification

Si tout est vert ✅, les données sont prêtes !

## ❓ Dépannage

### "Erreur d'import des modules"

**Cause :** Les modules Python du traitement ne sont pas trouvés

**Solution :**
- Vérifiez que tous les fichiers sont dans `TraitementDonnee/Code/`
- Les fichiers requis : `Avion_LinkHisto.py`, `Avion_LinkFutur.py`, etc.

### "Le dossier d'entrée n'existe pas"

**Cause :** Le ZIP uploadé n'a pas été correctement extrait

**Solution :**
- Vérifiez que votre ZIP contient bien les fichiers à la racine (pas dans un sous-dossier)
- Réessayez l'upload

### "Erreur lors du traitement"

**Solution :**
1. Regardez les détails de l'erreur (cliquez sur "Détails de l'erreur")
2. Vérifiez que tous les fichiers WEBI nécessaires sont présents
3. Vérifiez le format des fichiers (Excel .xlsx ou CSV)

### Le traitement est très long

**Normal :** Le traitement peut prendre 2-10 minutes selon :
- La quantité de données
- La période analysée
- Les performances du serveur

**Si ça prend plus de 15 minutes :**
- Vérifiez qu'il n'y a pas eu d'erreur dans les logs
- Essayez avec une période plus courte

## 🔐 Sécurité

- Les fichiers uploadés sont stockés temporairement et supprimés après traitement
- Aucune donnée n'est conservée sur le serveur
- Les fichiers JSON générés restent dans `Data Source/` pour l'application

## 📚 Voir aussi

- [GUIDE_ADMINISTRATION.md](GUIDE_ADMINISTRATION.md) - Guide complet de l'interface Admin
- [README_STREAMLIT.md](README_STREAMLIT.md) - Documentation générale
- [ACCES_ADMIN.md](ACCES_ADMIN.md) - Comment accéder à la page Admin
