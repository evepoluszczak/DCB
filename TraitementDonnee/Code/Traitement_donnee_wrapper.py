"""
Wrapper pour Traitement_donnee.py - Exécutable depuis l'app Streamlit
Permet de spécifier le dossier des fichiers WEBI et le dossier de sortie
"""

import os
import sys
from pathlib import Path
from time import time
from datetime import datetime

def run_traitement(input_folder, output_folder=None, progress_callback=None):
    """
    Exécute le traitement des données DCB

    Args:
        input_folder: Chemin vers le dossier contenant les fichiers WEBI
        output_folder: Chemin vers le dossier de sortie (Data Source/)
        progress_callback: Fonction à appeler pour mettre à jour la progression (facultatif)

    Returns:
        dict: Résultat avec 'success' (bool), 'message' (str), 'duration' (float)
    """

    def log(message):
        """Helper pour logger avec callback optionnel"""
        print(message)
        if progress_callback:
            progress_callback(message)

    try:
        a = time()

        # Sauvegarder le répertoire actuel
        original_dir = os.getcwd()

        # Se déplacer vers le dossier d'input
        if not os.path.exists(input_folder):
            return {
                'success': False,
                'message': f"Le dossier d'entrée n'existe pas : {input_folder}",
                'duration': 0
            }

        os.chdir(input_folder)
        log(f"📁 Dossier d'entrée : {input_folder}")

        # Vérifier les dates des fichiers WEBI
        log("\n🔍 Vérification des fichiers WEBI...")
        for file in os.listdir():
            if os.path.isfile(file):
                date = datetime.fromtimestamp(os.path.getmtime(file)).date()
                if date != datetime.now().date():
                    log(f"⚠️  L'export WEBI {file} n'a pas fonctionné aujourd'hui. Version du {date}.")

        # Ajouter le dossier Code au path si nécessaire
        code_folder = Path(__file__).parent.resolve()
        log(f"📂 Dossier des modules : {code_folder}")

        # S'assurer que le dossier est dans sys.path
        if str(code_folder) not in sys.path:
            sys.path.insert(0, str(code_folder))
            log(f"✅ Ajouté au sys.path : {code_folder}")

        # Vérifier que les fichiers modules existent
        required_modules = [
            'Avion_LinkHisto.py', 'Avion_LinkFutur.py', 'Avion_ExpectedTime.py',
            'Avion_Mouvements.py', 'Pax_Embarquement.py', 'Pax_ApplicationSUP.py',
            'Pax_PlanningIdealDouane.py', 'Pax_PlanningIdealSurete.py',
            'Pax_SUPjson.py', 'PBI_CalculPowerBI.py', 'Pax_PlaningSurete.py'
        ]

        missing_modules = []
        for module_file in required_modules:
            if not (code_folder / module_file).exists():
                missing_modules.append(module_file)

        if missing_modules:
            log(f"⚠️  Modules manquants : {', '.join(missing_modules)}")
            log(f"📁 Contenu du dossier : {list(os.listdir(code_folder))}")
            return {
                'success': False,
                'message': f"Modules manquants dans {code_folder}: {', '.join(missing_modules)}",
                'duration': 0
            }

        # Imports des modules de traitement
        log("\n📦 Chargement des modules de traitement...")
        try:
            from Avion_LinkHisto import Historique
            from Avion_LinkFutur import Futur
            from Avion_ExpectedTime import Delai
            from Avion_Mouvements import Mouvements
            from Pax_Embarquement import Embarquement
            from Pax_ApplicationSUP import ApplicationSUP
            from Pax_PlanningIdealDouane import PlanningIdealDouane
            from Pax_PlanningIdealSurete import PlanningIdealSurete
            from Pax_SUPjson import SUPjson
            from PBI_CalculPowerBI import CalculPBI
            from Pax_PlaningSurete import PlanningSurete
            log("✅ Tous les modules ont été importés avec succès")
        except ImportError as e:
            log(f"❌ Erreur d'import : {str(e)}")
            log(f"📁 sys.path actuel : {sys.path[:3]}...")
            log(f"📁 Fichiers dans {code_folder} : {list(os.listdir(code_folder))}")
            return {
                'success': False,
                'message': f"Erreur d'import des modules : {str(e)}\nDossier modules : {code_folder}",
                'duration': 0
            }

        # Étape 1 : Traitement de la donnée historique
        log("\n1️⃣  Traitement de la donnée historique...")
        data_histo, conv_MTOW, conv_airline = Historique()

        # Étape 2 : Traitement de la donnée future
        log("2️⃣  Traitement de la donnée future...")
        data_futur = Futur(data_histo)

        # Étape 3 : Calcul des retards
        log("3️⃣  Calcul des retards...")
        data_predi = Delai(conv_MTOW, conv_airline, data_histo, data_futur)

        # Étape 4 : Calcul du nombre de mouvements par heure roulante
        log("4️⃣  Calcul du nombre de mouvements par heure roulante...")
        Mouvements(data_predi)

        # Étape 5 : Calcul des embarquements par tranche de 5 minutes
        log("5️⃣  Calcul des embarquements par tranche de 5 minutes...")
        Embarquement(data_predi)

        # Étape 6 : Application des show-up profiles aux vols
        log("6️⃣  Application des show-up profiles aux vols...")
        DCB_xlsx, PlanningCI_xlsx = ApplicationSUP()

        # Étape 7 : Transformation du planning sûreté au format DCB app python
        log("7️⃣  Transformation du planning sûreté au format DCB app python...")
        PlanningSurete("csv")

        # Étape 8 : Calcul du planning idéal à la douane
        log("8️⃣  Calcul du planning idéal à la douane...")
        PlanningIdealDouane(DCB_xlsx)

        # Étape 9 : Calcul du planning idéal à la sûreté
        log("9️⃣  Calcul du planning idéal à la sûreté...")
        PlanningIdealSurete(DCB_xlsx)

        # Étape 10 : Transformation de la donnée au format DCB app python
        log("🔟 Transformation de la donnée au format DCB app python...")
        SUPjson(DCB_xlsx, PlanningCI_xlsx)

        # Étape 11 : Transformation de la donnée au format DCB PowerBI
        log("1️⃣1️⃣  Transformation de la donnée au format DCB PowerBI...")
        CalculPBI()

        # Restaurer le répertoire original
        os.chdir(original_dir)

        # Calculer la durée
        b = time()
        t = b - a

        log(f"\n✅ Fini!")
        log(f"⏱️  Temps de process total : {int(t/60)} minutes et {int(t%60)} secondes!")

        # Si un dossier de sortie est spécifié, déplacer les fichiers générés
        if output_folder:
            log(f"\n📤 Copie des fichiers vers {output_folder}...")
            # TODO: Implémenter la copie des fichiers JSON générés
            # vers le dossier output_folder spécifié

        return {
            'success': True,
            'message': f'Traitement terminé avec succès en {int(t/60)}m {int(t%60)}s',
            'duration': t
        }

    except Exception as e:
        # Restaurer le répertoire en cas d'erreur
        try:
            os.chdir(original_dir)
        except:
            pass

        return {
            'success': False,
            'message': f'Erreur lors du traitement : {str(e)}',
            'duration': time() - a,
            'error': str(e)
        }


def run_traitement_with_network_path(progress_callback=None):
    """
    Exécute le traitement avec le chemin réseau par défaut
    (pour exécution locale uniquement)
    """
    network_path = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI"

    if not os.path.exists(network_path):
        return {
            'success': False,
            'message': f'Le chemin réseau n\'est pas accessible : {network_path}\n'
                      f'Cette fonction ne peut s\'exécuter que sur une machine avec accès au réseau local.',
            'duration': 0
        }

    return run_traitement(network_path, progress_callback=progress_callback)


if __name__ == "__main__":
    # Si exécuté directement, utiliser le chemin réseau par défaut
    print("Démarrage du traitement des données DCB...")
    result = run_traitement_with_network_path()

    if result['success']:
        print(f"\n✅ {result['message']}")
        sys.exit(0)
    else:
        print(f"\n❌ {result['message']}")
        sys.exit(1)
