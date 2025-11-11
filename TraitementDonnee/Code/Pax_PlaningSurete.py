import pandas as pd
import datetime
import os
import shutil
import json
import re 
from pathlib import Path 
from tqdm import tqdm 
from chemin_dossier import CHEMIN_AUTRE, CHEMIN_DATA_SOURCE

def deplacer_fichier(nom_cible, super_dossier: Path, sous_dossier: str = None):
    # CORRECTION : Remplacement par la version pathlib
    # super_dossier est maintenant un objet Path
    chemin_actuel = super_dossier / 'Actuel'
    chemin_historique = super_dossier / 'Historique'
    if sous_dossier:
        chemin_historique = chemin_historique / sous_dossier

    # S'assurer que le dossier de destination existe
    chemin_historique.mkdir(parents=True, exist_ok=True)
    
    # Gérer le cas où le dossier "Actuel" n'existe pas
    if not chemin_actuel.exists():
        print(f"Dossier 'Actuel' non trouvé : {chemin_actuel}")
        return

    # Parcourir les fichiers du dossier Actuel avec iterdir()
    for fichier_path in chemin_actuel.iterdir():
        fichier_nom = fichier_path.name # Obtenir le nom du fichier
        
        # Logique de ce script
        if nom_cible in fichier_nom and not (nom_cible == "PlanningSurete" and "PlanningSureteIdeal" in fichier_nom):
            source = fichier_path
            destination = chemin_historique / fichier_nom
            
            # shutil.move fonctionne parfaitement avec les objets Path
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier_nom}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")


# CORRECTION : La fonction accepte maintenant 'data' (qui sera DCB_xlsx)
def PlanningSurete(data, format):
    mnt = datetime.datetime.now()
    
    # --- CORRECTION DES DATES ---
    # Obtenir la plage de dates depuis les données de vol, pas en dur
    if data.empty or "Date et heure" not in data.columns:
        print("Erreur: Le DataFrame 'data' (DCB_xlsx) est vide ou invalide. Arrêt de PlanningSurete.")
        return 0
        
    dates_in_data = data["Date et heure"].dt.date.drop_duplicates()
    debut = dates_in_data.min() # Date de début réelle
    fin = dates_in_data.max()   # Date de fin réelle
    # --- FIN DE LA CORRECTION ---
    
    dossier_autre = CHEMIN_AUTRE
    surete = {}

    if format == "excel":
        fichier_excel = None
        # Utilise iterdir() pour une approche pathlib cohérente
        for fichier_path in dossier_autre.iterdir():
            if "LanePlan_CSC" in fichier_path.name:
                fichier_excel = fichier_path
                break
        
        if fichier_excel:
            planningSurete = pd.read_excel(fichier_excel) # Chemin complet
            planningSurete = planningSurete.set_index("Lane Plan")
            planningSurete = planningSurete.drop(columns=datetime.time(22,0))

            # Utilise la plage de dates dynamique
            for date in pd.date_range(start=debut,end=fin):
                data_jour = planningSurete.loc[date]
                date_str = date.strftime(format="%Y-%m-%d")
                CSC = [0]*4*12
                for ligne in data_jour:
                    CSC += [int(ligne)]*6
                CSC += [0]*2*12
                SF = [0]*54 + [3]*35*6 + [0]*24

                surete[date_str] = {"Sûreté : International" : CSC, "Sûreté : France" : SF}
        else:
            print("Erreur : Fichier 'LanePlan_CSC' non trouvé.")
            return 0
            
    elif format == "csv":
        fichier_csv = None
        # Utilise iterdir() pour une approche pathlib cohérente
        for fichier_path in dossier_autre.iterdir():
            if "LanePlans_CheckpointGroups" in fichier_path.name:
                fichier_csv = fichier_path
                break
        
        if fichier_csv:
            planningSurete = pd.read_csv(fichier_csv, sep=";") # Chemin complet
            planningSurete = planningSurete[["Time", "1_NEW CSC.1_NEW CSC.Lanes", "2_SF.2_SF.Lanes"]]
            planningSurete["Time"] = pd.to_datetime(planningSurete["Time"].str[:19])
            planningSurete.columns = ["Date et heure", "CSC", "SF"]

            # Utilise la plage de dates dynamique
            for date in pd.date_range(start=debut,end=fin):
                data_jour = planningSurete[planningSurete["Date et heure"].dt.date == date.date()]
                date_str = date.strftime(format="%Y-%m-%d")
                CSC = data_jour["CSC"].to_list()
                SF = data_jour["SF"].to_list()
                T2 = [4]*12*24
                surete[date_str] = {"Sûreté : International" : CSC, "Sûreté : France" : SF, "Sûreté : TERMINAL 2" : T2}
        else:
            print("Erreur : Fichier 'LanePlans_CheckpointGroups' non trouvé.")
            return 0
    else:
        print("Mauvais format: veuillez spécifiez 'csv' ou 'excel'!")
        return 0

    dossier_destination = CHEMIN_DATA_SOURCE / "Capacite" / "Planning"
    nom = "PlanningSurete"
    
    deplacer_fichier(nom, dossier_destination, "Surete") # dossier_destination est maintenant un Path
    
    # Utilise les dates dynamiques pour le nom du fichier
    file = mnt.strftime(format="%Y%m%d%H%M") + nom + str(debut).replace("-","") + "-" + str(fin).replace("-","") + ".json"
    
    (dossier_destination / "Actuel").mkdir(parents=True, exist_ok=True)
    
    with open(dossier_destination / "Actuel" / file, "w") as f:
        json.dump(surete,f)
