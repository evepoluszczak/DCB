# Comment accéder à la page d'Administration

## 🔍 Localisation

La page d'administration est accessible via la **sidebar** (barre latérale gauche) de l'application Streamlit.

## 📍 Instructions étape par étape

### 1. Lancer l'application

```bash
streamlit run DCB_app_streamlit.py
```

### 2. Ouvrir la sidebar

- La sidebar s'ouvre automatiquement par défaut
- Si elle est fermée, cliquez sur la flèche `>` en haut à gauche de l'écran
- Ou appuyez sur la touche `[` de votre clavier

### 3. Naviguer vers Administration

Dans la sidebar, vous verrez :
```
📊 DCB - Demand Capacity Balancing  ← Page principale (actuelle)
📤 Administration                    ← Cliquez ici !
```

Cliquez sur "📤 Administration" pour accéder à la page de gestion des données.

## ❓ Problèmes fréquents

### Je ne vois pas la page "Administration" dans la sidebar

**Solutions :**

1. **Relancez l'application** :
   - Arrêtez l'application (Ctrl+C dans le terminal)
   - Relancez : `streamlit run DCB_app_streamlit.py`

2. **Vérifiez la structure des fichiers** :
   ```
   DCB/
   ├── DCB_app_streamlit.py  ← Fichier principal
   ├── pages/
   │   └── 1_Administration.py  ← Page admin
   └── ...
   ```

3. **Effacez le cache Streamlit** :
   - Dans l'app, menu en haut à droite (⋮)
   - Cliquez sur "Clear cache"
   - Rechargez la page

4. **Vérifiez les permissions** :
   ```bash
   chmod +x pages/1_Administration.py
   ```

### La sidebar ne s'ouvre pas

**Solutions :**

- Cliquez sur la flèche `>` en haut à gauche
- Appuyez sur `[` (crochet ouvrant) sur votre clavier
- Vérifiez que votre navigateur n'est pas en mode lecture

### L'application ne démarre pas

**Solutions :**

1. Vérifiez que Streamlit est installé :
   ```bash
   pip install streamlit
   ```

2. Vérifiez que vous êtes dans le bon dossier :
   ```bash
   cd /chemin/vers/DCB
   ls -la DCB_app_streamlit.py  # Doit afficher le fichier
   ```

3. Vérifiez les erreurs dans le terminal

## 🎯 Référence rapide

| Action | Raccourci clavier |
|--------|------------------|
| Ouvrir/Fermer sidebar | `[` |
| Actualiser l'app | `R` |
| Effacer le cache | `C` |

## 📚 Documentation

Pour plus d'informations sur l'utilisation de la page d'administration, consultez :
- [GUIDE_ADMINISTRATION.md](GUIDE_ADMINISTRATION.md) - Guide complet
- [README_STREAMLIT.md](README_STREAMLIT.md) - Documentation générale

## 🆘 Support

Si vous ne voyez toujours pas la page d'administration après avoir suivi ces étapes :

1. Vérifiez les logs dans le terminal où vous avez lancé Streamlit
2. Vérifiez que le fichier `pages/1_Administration.py` existe bien
3. Essayez avec un navigateur différent
4. Redémarrez complètement votre ordinateur (cas extrême)
