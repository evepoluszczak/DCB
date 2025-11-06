# Guide d'Administration - Application DCB

## Vue d'ensemble

L'application DCB dispose maintenant d'une interface d'administration accessible via la sidebar qui permet de gérer les données sans avoir à faire des commits Git.

## Accès à l'administration

1. Lancez l'application Streamlit
2. Dans la sidebar à gauche, cliquez sur "📤 Administration"
3. Vous accédez à la page de gestion des données

## Méthodes de mise à jour des données

### Méthode 1 : Upload de fichiers JSON (Recommandée pour Streamlit Cloud)

**Avantages :**
- Fonctionne sur Streamlit Cloud
- Pas besoin d'accès Git
- Mise à jour instantanée

**Processus :**

1. **Sur votre machine locale** (avec accès au réseau de l'aéroport) :
   ```bash
   cd /chemin/vers/DCB/TraitementDonnee/Code
   python Traitement_donnee.py
   ```

2. **Créer un ZIP du dossier Data Source** :
   - Windows : Clic droit sur `Data Source` → Envoyer vers → Dossier compressé
   - Linux/Mac : `zip -r Data_Source.zip "Data Source"`

3. **Sur l'application Streamlit** :
   - Allez dans l'onglet "📤 Upload JSON"
   - Uploadez le fichier ZIP
   - Cliquez sur "📦 Extraire et installer les données"
   - Actualisez la page principale (F5)

**Résultat :** Les données sont immédiatement disponibles dans l'application !

### Méthode 2 : Exécution directe du traitement

**Note :** Cette méthode n'est disponible qu'en local (pas sur Streamlit Cloud)

**Prérequis :**
- Accès au partage réseau `//gva.tld/aig/O/...`
- Application lancée en local avec `streamlit run DCB_app_streamlit.py`

**Processus :**
1. Allez dans l'onglet "⚙️ Exécuter le traitement"
2. Vérifiez l'accès au réseau avec le bouton de vérification
3. Cliquez sur "▶️ Lancer le traitement"
4. Le traitement s'exécute et met à jour automatiquement les données

**Note :** Cette fonctionnalité sera implémentée dans une future version.

## Vérification de l'état des données

L'onglet "📊 État des données" permet de :
- Voir la structure actuelle du dossier Data Source
- Vérifier quels fichiers sont présents
- Voir les statistiques (nombre de fichiers, taille totale, dernière modification)
- Télécharger un ZIP des données actuelles (pour sauvegarde ou transfert)

### Structure attendue

```
Data Source/
├── Demande/Actuel/
│   ├── ForecastPisteUtilisation_*.json
│   ├── SUPForecastSurete_*.json
│   └── ... (autres fichiers)
├── Capacite/
│   ├── Aeroport/Actuel/
│   ├── Planning/Actuel/
│   └── TempsProcess/Actuel/
├── LevelOfService/Actuel/
└── Annexe/Actuel/
```

## Workflow recommandé

### Pour Streamlit Cloud (Production)

1. **Hebdomadaire** (ou selon besoin) :
   - Exécutez `Traitement_donnee.py` en local
   - Créez un ZIP du dossier Data Source
   - Uploadez via l'interface d'administration
   - Vérifiez que tout fonctionne

2. **Sauvegarde** :
   - Téléchargez régulièrement un ZIP des données via l'onglet "État des données"
   - Conservez ces archives pour référence

### Pour déploiement local

1. **Initial** :
   - Clonez le repository
   - Exécutez `Traitement_donnee.py`
   - Lancez l'application

2. **Mise à jour** :
   - Option A : Ré-exécutez `Traitement_donnee.py` directement
   - Option B : Uploadez un ZIP via l'interface

## Dépannage

### "Le dossier Data Source n'existe pas"

**Solution :**
1. Allez dans l'onglet "📤 Upload JSON"
2. Uploadez un ZIP contenant les données
3. Ou exécutez `Traitement_donnee.py` en local

### "Fichiers JSON manquants"

**Vérification :**
1. Allez dans "📊 État des données"
2. Vérifiez quels dossiers/fichiers manquent
3. Ré-exécutez `Traitement_donnee.py` pour régénérer toutes les données

### "L'upload échoue"

**Solutions :**
- Vérifiez que le ZIP contient bien un dossier "Data Source" à la racine
- Vérifiez la taille du fichier (max ~200MB sur Streamlit Cloud)
- Essayez de réduire la période de données si le fichier est trop gros

## Sécurité

⚠️ **Important :**
- Vérifiez que les fichiers JSON ne contiennent pas de données sensibles
- Sur Streamlit Cloud, n'importe qui avec l'URL peut accéder à l'app
- Considérez l'ajout d'une authentification pour la page admin

## Automatisation (Future)

Possibilités d'automatisation futures :
- Script automatique qui exécute le traitement chaque nuit
- Upload automatique vers Streamlit Cloud via API
- Notifications par email quand les données sont mises à jour
- Versioning des données avec historique

## Support

Pour toute question ou problème :
1. Consultez l'onglet "📊 État des données" pour diagnostiquer
2. Vérifiez les logs de l'application
3. Contactez l'équipe de développement
