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
from Pax_PlanningSurete import PlanningSurete
from time import time
import os
from datetime import datetime
# CORRECTIONS : Imports supplémentaires nécessaires pour le chargement
from chemin_dossier import CHEMIN_INPUT, CHEMIN_OUTPUT
from pathlib import Path
import pandas as pd

a = time()

# --- VÉRIFICATION WEBI (GARDÉE) ---
webi_path = CHEMIN_INPUT / "WEBI"
if webi_path.exists():
    for file_path in webi_path.iterdir():
        date = datetime.fromtimestamp(file_path.stat().st_mtime).date()
        if date != datetime.now().date():
            print(f"L'export WEBI {file_path.name} n'a pas fonctionné aujourd'hui. La version utilisée sera celle du {date}.")
else:
    print(f"Erreur : Dossier WEBI non trouvé à l'emplacement : {webi_path}")


print("Traitement de la donnée historique")
data_histo, conv_MTOW, conv_airline = Historique()

print("Traitement de la donnée future")
data_futur = Futur(data_histo)

print("Calcul des retards")
data_predi = Delai(conv_MTOW,conv_airline,data_histo,data_futur)

print("Calcul du nombre de mouvements par heure roulante")
Mouvements(data_predi)

print("Calcul des embarquements par tranche de 5 minutes")
Embarquement(data_predi)

print("Application des show-up profiles aux vols")
DCB_xlsx, PlanningCI_xlsx = ApplicationSUP()

""" # --- CHARGEMENT RAPIDE (REMPLACEMENT) ---
print("CHARGEMENT RAPIDE : Lecture des sorties CSV existantes (au lieu de les re-générer)...")

# 1. Charger DCB_xlsx (la sortie de ApplicationSUP)
dcb_path = CHEMIN_OUTPUT / "DCB_output.csv"
if not dcb_path.exists():
    print(f"ERREUR: {dcb_path} non trouvé. Veuillez d'abord exécuter ApplicationSUP() au moins une fois.")
else:
    print(f"Chargement de {dcb_path}")
    DCB_xlsx = pd.read_csv(dcb_path)
    DCB_xlsx["Date et heure"] = pd.to_datetime(DCB_xlsx["Date et heure"]) # Très important

# 2. Charger PlanningCI_xlsx (la sortie de ApplicationSUP)
plan_ci_path = CHEMIN_OUTPUT / "PlanningCheckin.csv"
if not plan_ci_path.exists():
    print(f"ERREUR: {plan_ci_path} non trouvé. Veuillez d'abord exécuter ApplicationSUP() au moins une fois.")
else:
    print(f"Chargement de {plan_ci_path}")
    PlanningCI_xlsx = pd.read_csv(plan_ci_path)
    PlanningCI_xlsx["Date et heure"] = pd.to_datetime(PlanningCI_xlsx["Date et heure"]) # Très important

# --- FIN DE LA MODIFICATION --- """

print("Transformation du planning sûreté au format DCB app python")
# Nous passons DCB_xlsx pour que PlanningSurete utilise la bonne plage de dates
PlanningSurete(DCB_xlsx, "csv")

print("Calcul du planning idéal à la douane")
PlanningIdealDouane(DCB_xlsx)

print("Calcul du planning idéal à la sûreté")
PlanningIdealSurete(DCB_xlsx)

print("Transformation de la donnée au format DCB app python")
SUPjson(DCB_xlsx, PlanningCI_xlsx)

print("Transformation de la donnée au format DCB PowerBI")
CalculPBI()

print("Fini!")

b=time()
t=b-a
print(f"Temps de process total : {int(t/60)} minutes et {int(t%60)} secondes!")
