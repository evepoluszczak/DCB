##chemin_dossier_aero = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/"
##chemin_dossier_maison = "/Users/bastien/Documents/Aéroport/Consulting/DCB_Standalone_App/"

##chemin_app = chemin_dossier_aero #A changer quand le code est lancé depuis l'aéroport

from pathlib import Path

# 1. Obtenir le chemin absolu du fichier actuel (chemin_dossier.py)
#    Path(__file__) -> Donne le chemin de CE fichier
#    .resolve()    -> Donne le chemin complet et absolu
#    .parent        -> "Remonte" d'un dossier
CHEMIN_FICHIER_ACTUEL = Path(__file__).resolve()

# 2. Remonter dans l'arborescence pour trouver les dossiers clés
#    En supposant que ce fichier est dans : .../DCB_Standalone_App/TraitementDonnee/Code/
DOSSIER_CODE = CHEMIN_FICHIER_ACTUEL.parent
DOSSIER_TRAITEMENT = DOSSIER_CODE.parent
CHEMIN_APP_RACINE = DOSSIER_TRAITEMENT.parent # C'est la racine : .../DCB_Standalone_App

DOSSIER_DATA = DOSSIER_TRAITEMENT / "Data"
CHEMIN_INPUT = DOSSIER_DATA / "Input"
CHEMIN_OUTPUT = DOSSIER_DATA / "Output"

CHEMIN_DATA_SOURCE = CHEMIN_APP_RACINE / "Data Source"

CHEMIN_AUTRE = CHEMIN_INPUT / "Autre"
