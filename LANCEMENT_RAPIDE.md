# 🚀 Lancement Rapide DCB App

## Application DCB - Demand Capacity Balancing
**Version Streamlit Moderne et Optimisée**

---

## 🎯 Lancement en 1 clic

### **Windows** 🪟
Double-cliquez sur :
```
launch_dcb.bat
```

### **Linux / Mac** 🐧 🍎
Exécutez dans le terminal :
```bash
./launch_dcb.sh
```

**C'est tout !** L'application s'ouvre automatiquement dans votre navigateur.

---

## 📝 Prérequis

- **Python 3.8+** installé
- **Connexion internet** (première fois uniquement, pour installer les dépendances)

---

## 🌐 Accès à l'application

Une fois lancée, l'application est accessible sur :
```
http://localhost:8501
```

L'URL s'ouvre automatiquement dans votre navigateur par défaut.

---

## 📦 Première utilisation

Si c'est la première fois que vous lancez l'app :

1. Le script **vérifie automatiquement** les dépendances
2. **Installe** ce qui manque (Streamlit, Plotly, etc.)
3. **Lance** l'application

**Durée** : ~1-2 minutes la première fois, instantané ensuite.

---

## 🎨 Fonctionnalités

### Interface Moderne
- ✅ Design professionnel avec animations fluides
- ✅ Dashboard interactif avec KPIs
- ✅ Graphiques Plotly haute qualité
- ✅ Navigation intuitive par onglets
- ✅ Mode d'accueil pour nouveaux utilisateurs

### Vues Disponibles

#### 📊 Dashboard
Vue d'ensemble avec :
- KPIs globaux (statut, jours, processeurs)
- Graphiques de synthèse (Stands, Piste)
- 4 onglets : Vue d'ensemble, Opérations, Passagers, Analytique

#### 📅 Calendrier
Visualisation mensuelle avec codes couleur :
- 🟢 **Vert** : Conditions excellentes
- 🟡 **Jaune** : Conditions acceptables
- 🔴 **Rouge** : Conditions critiques

#### 📋 Détails
Analyse approfondie :
- Comparaison Demande vs Capacité
- Files d'attente et temps d'attente
- Graphiques interactifs par processeur

---

## ⚙️ Configuration

L'application utilise les fichiers de configuration dans `.streamlit/` :

```toml
[theme]
primaryColor = "#1E3A8A"      # Bleu aviation
backgroundColor = "#FFFFFF"    # Fond blanc
[server]
port = 8501                    # Port par défaut
```

Vous pouvez modifier ces paramètres si besoin.

---

## 📂 Structure des Données

L'application cherche les données dans :
```
Data Source/
├── Demande/Actuel/
├── Capacite/Aeroport/Actuel/
├── Capacite/Planning/Actuel/
├── Capacite/TempsProcess/Actuel/
├── LevelOfService/Actuel/
└── Annexe/Actuel/
```

### Si les données sont manquantes

L'application affiche un message et propose :
1. **Page Administration** : Upload de données ZIP
2. **Génération locale** : Exécuter `Traitement_donnee.py`

---

## 🛠️ Dépannage

### L'application ne se lance pas

**Vérifiez :**
```bash
# Python est installé
python --version
# ou
python3 --version

# Streamlit est installé
pip show streamlit
```

**Réinstallez si besoin :**
```bash
pip install -r requirements.txt
```

### Port 8501 déjà utilisé

Changez le port dans le script de lancement :
```bash
streamlit run DCB_app_streamlit.py --server.port=8502
```

### Erreur "Module not found"

Installez les dépendances manuellement :
```bash
pip install streamlit plotly pandas numpy
```

---

## 🔄 Arrêter l'application

Dans le terminal où l'app tourne :
- **Windows** : `Ctrl + C` puis `Y`
- **Linux/Mac** : `Ctrl + C`

---

## 🌐 Partage Multi-Utilisateurs

### Option 1 : Réseau Local

Sur la machine hôte, notez l'IP :
```bash
# Linux/Mac
ifconfig | grep "inet "

# Windows
ipconfig
```

Les autres utilisateurs accèdent via :
```
http://[IP_HOTE]:8501
```

**Exemple :** `http://192.168.1.10:8501`

### Option 2 : Streamlit Cloud (Recommandé)

Pour un partage public/équipe :

1. **Pushez** votre code sur GitHub
2. Allez sur **[share.streamlit.io](https://share.streamlit.io)**
3. **Connectez** votre repo
4. **Déployez** en 1 clic

Vous obtenez une URL publique :
```
https://votre-app.streamlit.app
```

**Partagez cette URL** avec votre équipe !

#### Avantages Streamlit Cloud
- ✅ Gratuit pour usage public
- ✅ HTTPS automatique
- ✅ Mises à jour auto (git push)
- ✅ Pas de maintenance serveur
- ✅ Supporte 100+ utilisateurs simultanés

---

## 📊 Utilisation Optimale

### Navigation Rapide

1. **Sidebar** : Contrôle toutes les options
   - Mode de vue (Dashboard/Calendrier/Détails)
   - Type de données (Forecast/Schedule)
   - Type de planning (Réel/Idéal/Perso)
   - Sélection processeurs

2. **Onglets** : 4 sections d'analyse
   - Vue d'ensemble
   - Opérations
   - Passagers
   - Analytique

3. **Bouton Aide** : Réaffiche le guide

### Workflow Type

**Analyse quotidienne :**
1. Dashboard → Onglet "Opérations"
2. Sélectionner la date
3. Analyser Piste + Stands

**Analyse passagers :**
1. Dashboard → Onglet "Passagers"
2. Choisir processeur (Sûreté, Check-in, etc.)
3. Comparer Demande vs Capacité

**Vue d'ensemble mensuelle :**
1. Mode "Calendrier"
2. Identifier les jours critiques (🔴)
3. Cliquer pour détails

---

## 💡 Astuces

### Raccourcis Streamlit
- `R` : Réexécuter l'app
- `C` : Effacer le cache
- `?` : Aide Streamlit

### Performance
- Les données sont **cachées** après le premier chargement
- Changements de vue = **instantanés**
- Rechargement complet = **~2 secondes**

### Personnalisation
- Modifiez les couleurs dans `.streamlit/config.toml`
- Ajustez les seuils dans le code (section Thresholds)
- Créez vos propres graphiques (fonctions `generate_*`)

---

## 📚 Documentation Complète

Consultez les autres fichiers :
- `README_STREAMLIT.md` : Documentation technique
- `DESIGN_MODERNE.md` : Guide du design
- `GUIDE_ADMINISTRATION.md` : Gestion des données
- `INSTALLATION.md` : Installation détaillée

---

## 🎉 Fonctionnalités Avancées

### En Production

- ✅ **Animations CSS** : Transitions fluides
- ✅ **Micro-interactions** : Effets hover avancés
- ✅ **Mode d'accueil** : Guide les nouveaux utilisateurs
- ✅ **Graphiques enrichis** : Plotly interactif
- ✅ **Design responsive** : Mobile/Tablet/Desktop
- ✅ **Performance optimisée** : Cache intelligent

### Prochainement

- 🔜 **Export données** : PDF, Excel, CSV
- 🔜 **Mode sombre** : Thème dark
- 🔜 **Notifications** : Alertes temps réel
- 🔜 **Comparaisons** : Multi-dates
- 🔜 **Prédictions** : ML models

---

## 📞 Support

**Besoin d'aide ?**

1. Consultez le **bouton "ℹ️ Aide & Guide"** dans la sidebar
2. Lisez les **README** du projet
3. Contactez l'équipe de développement

---

## ✨ Résumé

| Action | Commande |
|--------|----------|
| **Lancer** | Double-clic sur `launch_dcb.bat` ou `./launch_dcb.sh` |
| **Accéder** | `http://localhost:8501` |
| **Arrêter** | `Ctrl + C` dans le terminal |
| **Partager** | Déployer sur Streamlit Cloud |

---

**Version** : 2.0 - Modern UI/UX
**Dernière mise à jour** : Novembre 2025
**Plateforme** : Streamlit Cloud Ready

Profitez de votre expérience DCB ! ✈️
