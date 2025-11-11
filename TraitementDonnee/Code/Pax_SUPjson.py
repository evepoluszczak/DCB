import pandas as pd
import json
import datetime
import shutil
import os
import re # Ajouté pour la fonction deplacer_fichier
from pathlib import Path # Ajouté pour la nouvelle gestion des chemins
from tqdm import tqdm
from chemin_dossier import CHEMIN_DATA_SOURCE # <-- Correction de l'import

def deplacer_fichier(nom_cible, super_dossier: Path, sous_dossier: str = None):
    # CORRECTION : Remplacement par la version pathlib
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
        if nom_cible in fichier_nom:
            source = fichier_path
            destination = chemin_historique / fichier_nom
            
            # shutil.move fonctionne parfaitement avec les objets Path
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier_nom}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")

def SUPjson(data, data_planning):
    # CORRECTION : Ajout d'une vérification pour les DataFrames vides
    if data.empty or "Date et heure" not in data.columns:
        print("Erreur dans SUPjson: Le DataFrame 'data' (DCB_xlsx) est vide ou invalide. Exportation JSON annulée.")
        return
    if data_planning.empty or "Date et heure" not in data_planning.columns:
        print("Erreur dans SUPjson: Le DataFrame 'data_planning' (PlanningCI_xlsx) est vide ou invalide. Exportation JSON annulée.")
        return

    mnt = datetime.datetime.now()
    debut = mnt.date()
    # Cette ligne est maintenant sécurisée grâce à la vérification ci-dessus
    fin = data["Date et heure"].dt.date.max()

    checkin = {}
    surete = {}
    douane = {}
    gate = {}
    planning_checkin = {}

    colonnes = data.columns
    graph_names = {"Check-in" : [], "Sûreté" : [], "Douane" : [], "Gate" : [], "Stand" : ["Stand : C","Stand : D","Stand : E"], "Piste" : ["Piste : Atterrissage", "Piste : Décollage"]}

    for col in colonnes:
        if col.startswith("Check-in"):
            graph_names["Check-in"].append(col)
        if col.startswith("Sûreté"):
            graph_names["Sûreté"].append(col)
        if col.startswith("Douane"):
            graph_names["Douane"].append(col)
        if col.startswith("Gate"):
            graph_names["Gate"].append(col)

    for date in pd.date_range(start=debut,end=fin):
        data_jour = data[data["Date et heure"].dt.date == date.date()]
        data_planning_jour = data_planning[data_planning["Date et heure"].dt.date == date.date()]
        date_str = date.strftime(format="%Y-%m-%d")

        checkin[date_str] = {}
        surete[date_str] = {}
        douane[date_str] = {}
        gate[date_str] = {}
        planning_checkin[date_str] = {}

        for col in colonnes:
            if col.startswith("Check-in"):
                checkin[date_str][col] = data_jour[col].to_list()
                planning_checkin[date_str][col] = data_planning_jour[col].to_list()
            if col.startswith("Sûreté"):
                surete[date_str][col] = data_jour[col].to_list()
            if col.startswith("Douane"):
                douane[date_str][col] = data_jour[col].to_list()
            if col.startswith("Gate"):
                gate[date_str][col] = data_jour[col].to_list()

    # CORRECTION : Utilisation de pathlib
    dossier_demande = CHEMIN_DATA_SOURCE / "Demande"
    dossier_demande_actuel = dossier_demande / "Actuel"
    dossier_demande_actuel.mkdir(parents=True, exist_ok=True)
    
    pre = mnt.strftime(format="%Y%m%d%H%M")
    post = str(debut).replace("-","") + "-" + str(fin).replace("-","") + ".json"

    nom = "SUPForecastCheckIn"
    deplacer_fichier(nom,dossier_demande,"CheckIn")
    file = pre + nom + post
    with open(dossier_demande_actuel / file,"w",encoding="utf-8") as f:
        json.dump(checkin,f)

    nom = "SUPForecastSurete"
    deplacer_fichier(nom,dossier_demande,"Surete")
    file = pre + nom + post
    with open(dossier_demande_actuel / file,"w",encoding="utf-8") as f:
        json.dump(surete,f)

    nom = "SUPForecastDouane"
    deplacer_fichier(nom,dossier_demande,"Douane")
    file = pre + nom + post
    with open(dossier_demande_actuel / file,"w",encoding="utf-8") as f:
        json.dump(douane,f)

    nom = "SUPForecastGate"
    deplacer_fichier(nom,dossier_demande,"Gate/SUP")
    file = pre + nom + post
    with open(dossier_demande_actuel / file,"w",encoding="utf-8") as f:
        json.dump(gate,f)

    # CORRECTION : Utilisation de pathlib
    dossier_planning = CHEMIN_DATA_SOURCE / "Capacite" / "Planning"
    dossier_planning_actuel = dossier_planning / "Actuel"
    dossier_planning_actuel.mkdir(parents=True, exist_ok=True)

    nom = "PlanningCheckIn"
    deplacer_fichier(nom,dossier_planning,"CheckIn")
    file = pre + nom + post
    with open(dossier_planning_actuel / file,"w",encoding="utf-8") as f:
        json.dump(planning_checkin,f)

    # CORRECTION : Utilisation de pathlib
    dossier_annexe = CHEMIN_DATA_SOURCE / "Annexe"
    dossier_annexe_actuel = dossier_annexe / "Actuel"
    dossier_annexe_actuel.mkdir(parents=True, exist_ok=True)

    nom = "GraphNames"
    deplacer_fichier(nom,dossier_annexe,"GraphNames")
    file = pre + nom + ".json"
    with open(dossier_annexe_actuel / file,"w",encoding="utf-8") as f:
        json.dump(graph_names,f)
