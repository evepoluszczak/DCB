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

def main():
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
                        with tempfile.TemporaryDirectory() as temp_dir:
                            zip_path = Path(temp_dir) / "data.zip"
                            with open(zip_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())

                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_ref.extractall(temp_dir)

                            data_source_path = None
                            for root, dirs, files in os.walk(temp_dir):
                                if "Data Source" in root or any("Actuel" in d for d in dirs):
                                    data_source_path = Path(root)
                                    if data_source_path.name != "Data Source":
                                        for parent in data_source_path.parents:
                                            if parent.name == "Data Source":
                                                data_source_path = parent
                                                break
                                    break

                            if data_source_path is None:
                                st.error("Le dossier 'Data Source' n'a pas été trouvé dans le ZIP")
                            else:
                                target_folder = get_data_source_folder()

                                if target_folder.exists():
                                    shutil.rmtree(target_folder)
                                target_folder.parent.mkdir(parents=True, exist_ok=True)

                                shutil.copytree(data_source_path, target_folder)

                                st.success("✅ Les données ont été extraites et installées avec succès!")
                                st.balloons()

                                if st.button("🔄 Actualiser l'application"):
                                    st.cache_data.clear()
                                    st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'extraction : {str(e)}")
                        st.exception(e)

    # ========================
    # TAB 2 : Exécution du traitement
    # ========================
    with tab2:
        st.header("Exécuter le traitement des données")

        st.info("""
        **Nouvelle fonctionnalité !** Vous pouvez maintenant uploader les fichiers WEBI sources
        et lancer le traitement directement depuis l'interface, sans accès au réseau local.
        """)

        st.markdown("""
        ### Options disponibles

        **Option A : Upload des fichiers WEBI (Fonctionne partout)**
        - Uploadez un ZIP contenant vos fichiers sources WEBI
        - Le traitement s'exécute dans l'app
        - Les données JSON sont générées automatiquement

        **Option B : Utiliser le chemin réseau (Local uniquement)**
        - Si vous êtes en local avec accès au réseau
        - Le traitement accède directement aux fichiers WEBI
        """)

        method = st.radio(
            "Choisissez une méthode :",
            ["📤 Upload fichiers WEBI", "🌐 Utiliser chemin réseau"],
            key="method_choice"
        )

        if method == "📤 Upload fichiers WEBI":
            st.markdown("---")
            st.subheader("📤 Upload des fichiers sources WEBI")

            st.warning("""
            **Fichiers requis :** Uploadez un ZIP contenant tous les fichiers Excel/CSV exportés depuis WEBI.

            Ces fichiers incluent généralement :
            - Données historiques de vols
            - Données futures de vols
            - Plannings sûreté/douane
            - Autres fichiers de configuration
            """)

            uploaded_webi = st.file_uploader(
                "Choisir un fichier ZIP contenant les fichiers WEBI",
                type=['zip'],
                help="ZIP avec tous les fichiers Excel/CSV exportés depuis WEBI",
                key="webi_upload"
            )

            if uploaded_webi is not None:
                st.success(f"Fichier uploadé : {uploaded_webi.name} ({uploaded_webi.size / 1024 / 1024:.2f} MB)")

                if st.button("▶️ Lancer le traitement", type="primary", key="run_with_upload"):
                    with st.spinner("🔄 Traitement en cours..."):
                        try:
                            with tempfile.TemporaryDirectory() as temp_dir:
                                zip_path = Path(temp_dir) / "webi_files.zip"
                                with open(zip_path, 'wb') as f:
                                    f.write(uploaded_webi.getbuffer())

                                webi_folder = Path(temp_dir) / "WEBI"
                                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                    zip_ref.extractall(webi_folder)

                                st.info("✅ Fichiers extraits")

                                # Ajouter le dossier parent au path pour les imports
                                parent_dir = str(Path(__file__).parent.parent)
                                if parent_dir not in sys.path:
                                    sys.path.insert(0, parent_dir)

                                sys.path.insert(0, str(Path(__file__).parent.parent / "TraitementDonnee" / "Code"))
                                from Traitement_donnee_wrapper import run_traitement

                                progress_placeholder = st.empty()
                                progress_messages = []

                                def progress_callback(message):
                                    progress_messages.append(message)
                                    progress_placeholder.text_area(
                                        "Progression :",
                                        value="\n".join(progress_messages[-20:]),
                                        height=300
                                    )

                                output_folder = get_data_source_folder()
                                result = run_traitement(
                                    str(webi_folder),
                                    str(output_folder),
                                    progress_callback=progress_callback
                                )

                                if result['success']:
                                    st.success(f"✅ {result['message']}")
                                    st.balloons()
                                    st.info("🔄 Actualisez la page principale pour voir les nouvelles données")

                                    if st.button("🗑️ Effacer le cache et actualiser"):
                                        st.cache_data.clear()
                                        st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                                    if 'error' in result:
                                        with st.expander("Détails de l'erreur"):
                                            st.code(result['error'])

                        except Exception as e:
                            st.error(f"❌ Erreur lors du traitement : {str(e)}")
                            st.exception(e)

        else:  # Utiliser chemin réseau
            st.markdown("---")
            st.subheader("🌐 Utiliser le chemin réseau local")

            # Vérifier si on est en local ou sur Streamlit Cloud
            try:
                is_local = not os.path.exists('/mount/src')
            except:
                is_local = False

            if not is_local:
                st.error("""
                ❌ Vous êtes sur Streamlit Cloud - Cette option n'est pas disponible

                **Solution :** Utilisez l'option "Upload fichiers WEBI" ci-dessus
                """)
            else:
                st.success("✅ Vous êtes en local - Le traitement peut être exécuté")

                network_path = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI"

                if st.button("🔍 Vérifier l'accès au réseau"):
                    try:
                        if os.path.exists(network_path):
                            st.success(f"✅ Le chemin réseau est accessible : {network_path}")
                        else:
                            st.error(f"❌ Le chemin réseau n'est pas accessible : {network_path}")
                    except:
                        st.error(f"❌ Erreur lors de la vérification du chemin réseau")

                st.markdown("---")

                if st.button("▶️ Lancer le traitement avec chemin réseau", type="primary", key="run_with_network"):
                    with st.spinner("🔄 Traitement en cours..."):
                        try:
                            # Ajouter le dossier parent au path pour les imports
                            parent_dir = str(Path(__file__).parent.parent)
                            if parent_dir not in sys.path:
                                sys.path.insert(0, parent_dir)

                            sys.path.insert(0, str(Path(__file__).parent.parent / "TraitementDonnee" / "Code"))
                            from Traitement_donnee_wrapper import run_traitement_with_network_path

                            progress_placeholder = st.empty()
                            progress_messages = []

                            def progress_callback(message):
                                progress_messages.append(message)
                                progress_placeholder.text_area(
                                    "Progression :",
                                    value="\n".join(progress_messages[-20:]),
                                    height=300
                                )

                            result = run_traitement_with_network_path(progress_callback=progress_callback)

                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                st.balloons()
                                st.info("🔄 Actualisez la page principale pour voir les nouvelles données")

                                if st.button("🗑️ Effacer le cache et actualiser"):
                                    st.cache_data.clear()
                                    st.rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                                if 'error' in result:
                                    with st.expander("Détails de l'erreur"):
                                        st.code(result['error'])

                        except Exception as e:
                            st.error(f"❌ Erreur lors du traitement : {str(e)}")
                            st.exception(e)

    # ========================
    # TAB 3 : État des données
    # ========================
    with tab3:
        st.header("État actuel des données")

        data_source = get_data_source_folder()

        if data_source.exists():
            st.success(f"✅ Dossier 'Data Source' trouvé : `{data_source}`")

            st.subheader("Structure des dossiers")

            try:
                subdirs = [d for d in data_source.iterdir() if d.is_dir()]

                for subdir in sorted(subdirs):
                    with st.expander(f"📁 {subdir.name}"):
                        actuel_path = subdir / "Actuel"
                        if actuel_path.exists():
                            files = list(actuel_path.glob("*.json"))
                            if files:
                                st.write(f"**{len(files)} fichiers JSON trouvés:**")
                                for f in sorted(files)[:10]:
                                    file_size = f.stat().st_size / 1024
                                    st.write(f"- {f.name} ({file_size:.1f} KB)")
                                if len(files) > 10:
                                    st.write(f"... et {len(files) - 10} autres fichiers")
                            else:
                                st.warning("Aucun fichier JSON trouvé")
                        else:
                            st.warning("Le sous-dossier 'Actuel' n'existe pas")

            except Exception as e:
                st.error(f"Erreur lors de la lecture du dossier : {str(e)}")

            if st.button("🗑️ Supprimer toutes les données", key="delete_all"):
                if st.checkbox("Je confirme vouloir supprimer toutes les données", key="confirm_delete"):
                    try:
                        shutil.rmtree(data_source)
                        st.success("✅ Toutes les données ont été supprimées")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la suppression : {str(e)}")

        else:
            st.warning(f"⚠️ Le dossier 'Data Source' n'existe pas encore : `{data_source}`")
            st.info("Uploadez des données ou exécutez le traitement pour créer ce dossier")

    st.markdown("---")
    st.caption("💡 Consultez la documentation pour plus d'informations sur la gestion des données")

if __name__ == "__main__":
    main()

# Exécuter main() directement (pas dans if __name__)
main()
