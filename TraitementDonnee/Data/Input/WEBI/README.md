# Dossier WEBI - Fichiers sources

Ce dossier doit contenir les fichiers CSV/Excel exportés depuis WEBI.

## Fichiers requis

Les fichiers suivants sont nécessaires pour exécuter le traitement des données :

- `DCB_BSH_link.csv` - Données de liaison BSH
- Autres fichiers d'export WEBI (historique, prévisions, plannings, etc.)

## ⚠️ Important

Ces fichiers sont **exclus de Git** car ils sont trop volumineux pour être versionnés.

## Comment utiliser ces fichiers

### Option 1 : Exécution locale (recommandé)

Si vous avez accès au réseau local :
1. Les fichiers sont automatiquement lus depuis le chemin réseau configuré
2. Aucune action manuelle nécessaire

### Option 2 : Upload via l'interface Streamlit

1. Compressez tous vos fichiers WEBI dans un fichier ZIP
2. Allez sur la page **Administration** de l'application Streamlit
3. Utilisez l'option "Upload fichiers WEBI"
4. Uploadez votre fichier ZIP
5. Lancez le traitement

### Option 3 : Copie manuelle

1. Copiez vos fichiers WEBI dans ce dossier
2. Exécutez le script de traitement :
   ```bash
   cd TraitementDonnee/Code
   python Traitement_donnee.py
   ```

## Emplacement réseau (pour référence)

Chemin réseau par défaut :
```
//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI/
```

## Alternative : Git LFS

Si vous souhaitez absolument versionner ces fichiers volumineux, vous pouvez utiliser **Git Large File Storage (LFS)** :

```bash
# Installer Git LFS
git lfs install

# Tracker les fichiers CSV dans ce dossier
git lfs track "TraitementDonnee/Data/Input/WEBI/*.csv"

# Ajouter et commiter
git add .gitattributes
git add TraitementDonnee/Data/Input/WEBI/*.csv
git commit -m "Add WEBI CSV files with Git LFS"
```

**Note :** Git LFS a des limites de stockage selon votre plan GitHub.
