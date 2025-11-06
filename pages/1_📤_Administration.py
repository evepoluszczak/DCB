"""
Page d'administration DCB - Gestion des données
"""

import streamlit as st
import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
import sys

# Ajouter le dossier parent au path pour les imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

st.set_page_config(
    page_title="Administration DCB",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Administration - Gestion des données DCB")

st.markdown("""
Cette page permet de gérer les données de l'application DCB.

Il existe deux méthodes pour mettre à jour les données :
1. **Upload de fichiers JSON** (recommandé pour Streamlit Cloud)
2. **Exécution du traitement** (nécessite accès au réseau local)
""")

# Fonction pour obtenir le dossier Data Source
def get_data_source_folder():
    base_path = Path(__file__).parent.parent
    data_source = base_path / "Data Source"
    return data_source

# Tabs pour les différentes méthodes
tab1, tab2, tab3 = st.tabs(["📤 Upload JSON", "⚙️ Exécuter le traitement", "📊 État des données"])

# ========================
# TAB 1 : Upload de fichiers JSON
# ========================
with tab1:
    st.header("Upload de fichiers JSON")

    st.info("""
    **Processus recommandé :**
    1. Exécutez `Traitement_donnee.py` sur votre machine locale (avec accès au réseau)
    2. Compressez le dossier `Data Source` en fichier ZIP
    3. Uploadez le fichier ZIP ici
    4. L'application extraira automatiquement les fichiers
    """)

    uploaded_file = st.file_uploader(
        "Choisir un fichier ZIP contenant le dossier 'Data Source'",
        type=['zip'],
        help="Le ZIP doit contenir un dossier 'Data Source' avec tous les sous-dossiers et fichiers JSON"
    )

    if uploaded_file is not None:
        st.success(f"Fichier uploadé : {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")

        if st.button("📦 Extraire et installer les données", type="primary"):
            with st.spinner("Extraction en cours..."):
                try:
                    # Créer un dossier temporaire
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Sauvegarder le ZIP
                        zip_path = Path(temp_dir) / "data.zip"
                        with open(zip_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())

                        # Extraire le ZIP
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)

                        # Trouver le dossier Data Source
                        data_source_path = None
                        for root, dirs, files in os.walk(temp_dir):
                            if 'Data Source' in dirs:
                                data_source_path = Path(root) / 'Data Source'
                                break
                            # Cas où on est directement dans Data Source
                            if Path(root).name == 'Data Source':
                                data_source_path = Path(root)
                                break

                        if data_source_path is None:
                            st.error("❌ Le dossier 'Data Source' n'a pas été trouvé dans le ZIP")
                        else:
                            # Copier vers le dossier de l'application
                            target_path = get_data_source_folder()

                            # Créer le dossier cible si nécessaire
                            target_path.parent.mkdir(parents=True, exist_ok=True)

                            # Supprimer l'ancien dossier Data Source s'il existe
                            if target_path.exists():
                                shutil.rmtree(target_path)

                            # Copier le nouveau
                            shutil.copytree(data_source_path, target_path)

                            st.success("✅ Données installées avec succès !")
                            st.info("🔄 Actualisez la page principale pour voir les nouvelles données")

                            # Afficher un résumé
                            file_count = sum(1 for _ in target_path.rglob('*.json'))
                            st.metric("Fichiers JSON installés", file_count)

                            # Bouton pour effacer le cache
                            if st.button("🗑️ Effacer le cache et recharger"):
                                st.cache_data.clear()
                                st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'extraction : {str(e)}")
                    st.exception(e)

    st.markdown("---")

    st.subheader("📥 Upload de fichiers individuels")
    st.warning("Option avancée : upload de fichiers JSON individuels")

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
            "Catégorie",
            ["Demande", "Capacite/Aeroport", "Capacite/Planning", "Capacite/TempsProcess", "LevelOfService", "Annexe"]
        )

    with col2:
        uploaded_json = st.file_uploader(
            "Choisir un fichier JSON",
            type=['json'],
            key="individual_json"
        )

    if uploaded_json and st.button("💾 Installer ce fichier"):
        st.info("Fonctionnalité à implémenter")

# ========================
# TAB 2 : Exécuter le traitement
# ========================
with tab2:
    st.header("⚙️ Exécuter le traitement des données")

    st.warning("""
    ⚠️ **Important** : Cette fonctionnalité ne peut s'exécuter que sur une machine
    avec accès au partage réseau `//gva.tld/aig/O/...`

    Sur Streamlit Cloud, cette fonctionnalité n'est pas disponible.
    """)

    # Vérifier si on est en local ou sur Streamlit Cloud
    is_local = not os.path.exists('/mount/src')  # Streamlit Cloud utilise /mount/src

    if is_local:
        st.success("✅ Vous êtes en local - Le traitement peut être exécuté")

        st.markdown("""
        ### Processus de traitement

        Le script va exécuter les étapes suivantes :
        1. Traitement de la donnée historique
        2. Traitement de la donnée future
        3. Calcul des retards
        4. Calcul du nombre de mouvements par heure roulante
        5. Calcul des embarquements par tranche de 5 minutes
        6. Application des show-up profiles aux vols
        7. Transformation du planning sûreté
        8. Calcul des plannings idéaux (douane, sûreté)
        9. Transformation de la donnée au format DCB app
        10. Transformation de la donnée au format PowerBI
        """)

        # Vérifier que le chemin réseau est accessible
        network_path = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI"

        if st.button("🔍 Vérifier l'accès au réseau"):
            if os.path.exists(network_path):
                st.success(f"✅ Le chemin réseau est accessible : {network_path}")
            else:
                st.error(f"❌ Le chemin réseau n'est pas accessible : {network_path}")

        st.markdown("---")

        if st.button("▶️ Lancer le traitement", type="primary"):
            st.warning("🚧 Cette fonctionnalité sera implémentée dans une prochaine version")
            st.info("""
            Pour l'instant, veuillez :
            1. Exécuter `python Traitement_donnee.py` depuis le terminal
            2. Compresser le dossier `Data Source` résultant
            3. Uploader le ZIP dans l'onglet "Upload JSON"
            """)
    else:
        st.error("""
        ❌ Vous êtes sur Streamlit Cloud - Le traitement ne peut pas s'exécuter ici

        **Solution :**
        1. Exécutez `Traitement_donnee.py` sur votre machine locale
        2. Utilisez l'onglet "Upload JSON" pour uploader les résultats
        """)

# ========================
# TAB 3 : État des données
# ========================
with tab3:
    st.header("📊 État actuel des données")

    data_source = get_data_source_folder()

    if not data_source.exists():
        st.error("❌ Le dossier 'Data Source' n'existe pas")
        st.info("Utilisez l'onglet 'Upload JSON' pour installer des données")
    else:
        st.success(f"✅ Dossier Data Source trouvé : `{data_source}`")

        # Analyser la structure
        st.subheader("Structure des dossiers")

        expected_folders = [
            "Demande/Actuel",
            "Capacite/Aeroport/Actuel",
            "Capacite/Planning/Actuel",
            "Capacite/TempsProcess/Actuel",
            "LevelOfService/Actuel",
            "Annexe/Actuel"
        ]

        for folder in expected_folders:
            folder_path = data_source / folder
            if folder_path.exists():
                json_files = list(folder_path.glob('*.json'))
                st.success(f"✅ {folder} ({len(json_files)} fichiers JSON)")

                # Afficher les fichiers dans un expander
                with st.expander(f"Voir les fichiers de {folder}"):
                    for json_file in json_files:
                        file_size = json_file.stat().st_size / 1024  # KB
                        st.text(f"  📄 {json_file.name} ({file_size:.1f} KB)")
            else:
                st.error(f"❌ {folder} - Dossier manquant")

        # Statistiques globales
        st.markdown("---")
        st.subheader("Statistiques")

        total_json = sum(1 for _ in data_source.rglob('*.json'))
        total_size = sum(f.stat().st_size for f in data_source.rglob('*.json'))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fichiers JSON", total_json)
        with col2:
            st.metric("Taille totale", f"{total_size / 1024 / 1024:.2f} MB")
        with col3:
            # Trouver la date la plus récente
            json_files = list(data_source.rglob('*.json'))
            if json_files:
                most_recent = max(json_files, key=lambda f: f.stat().st_mtime)
                import datetime
                mod_time = datetime.datetime.fromtimestamp(most_recent.stat().st_mtime)
                st.metric("Dernière modification", mod_time.strftime("%d/%m/%Y %H:%M"))

        # Bouton pour télécharger les données actuelles
        st.markdown("---")
        st.subheader("💾 Télécharger les données actuelles")

        if st.button("📦 Créer un ZIP des données actuelles"):
            with st.spinner("Création du ZIP..."):
                try:
                    # Créer un ZIP en mémoire
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_path = Path(temp_dir) / "Data_Source.zip"

                        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for file in data_source.rglob('*'):
                                if file.is_file():
                                    arcname = file.relative_to(data_source.parent)
                                    zipf.write(file, arcname)

                        # Lire le ZIP
                        with open(zip_path, 'rb') as f:
                            zip_data = f.read()

                        st.download_button(
                            label="⬇️ Télécharger Data_Source.zip",
                            data=zip_data,
                            file_name="Data_Source.zip",
                            mime="application/zip"
                        )

                        st.success("✅ ZIP créé avec succès!")

                except Exception as e:
                    st.error(f"❌ Erreur lors de la création du ZIP : {str(e)}")

st.markdown("---")
st.caption("Application DCB - Page d'administration")
