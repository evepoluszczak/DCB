import pandas as pd
import datetime
import shutil
import os
import re 
from math import ceil
from pathlib import Path 
from chemin_dossier import CHEMIN_DATA_SOURCE 
import json # <-- CORRECTION : L'import est ici

def load_data(name, sous_dossier):
    # CORRECTION : Utilisation de pathlib
    dossier_path = CHEMIN_DATA_SOURCE / sous_dossier / "Actuel"
    
    # Gérer le cas où le dossier "Actuel" n'existe pas
    if not dossier_path.exists():
        print(f"Dossier 'Actuel' non trouvé : {dossier_path}")
        return None # Retourner None pour éviter une erreur

    target_file = None
    # CORRECTION : Utilisation de iterdir() pour les objets Path
    for fichier_path in dossier_path.iterdir():
        if name in fichier_path.name:
            target_file = fichier_path
            break
    
    if target_file:
        with open(target_file, 'r', encoding='utf-8') as file: # target_file est déjà le chemin complet
            return json.load(file) # <-- Cette ligne ne plantera plus
    else:
        print(f"Aucun fichier contenant '{name}' trouvé dans '{dossier_path}'")
        return None # Gérer le cas où aucun fichier n'est trouvé

def repls(liste,nb=6):
    return [valeur for valeur in liste for _ in range(nb)]

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

def PlanningIdealSurete(data):
    TempsProcess = load_data("TempsProcess","Capacite/TempsProcess")
    if TempsProcess is None: # S'assurer que les données sont chargées
        print("Erreur: Impossible de charger TempsProcess. Arrêt.")
        return

    surete_cols = []
    for col in data.columns:
        if col.startswith("Sûreté"):
            surete_cols.append(col)

    data = data[["Date et heure"]+surete_cols]

    data[surete_cols] = data[surete_cols].astype(int)

    data.set_index("Date et heure", inplace=True)
    data = data.resample("30min").sum()
    data = data.reset_index()

    MaxLigne = {"Sûreté : International" : 18, "Sûreté : France" : 3, "Sûreté : TERMINAL 2" : 4}

    for zone in surete_cols:
        # Assurer que la zone existe dans TempsProcess avant de l'utiliser
        if zone not in TempsProcess:
            print(f"Avertissement : Zone '{zone}' non trouvée dans TempsProcess. Utilisation d'une valeur par défaut.")
            temps_process_zone = 1.0 # Mettez une valeur par défaut ou gérez l'erreur
        else:
            temps_process_zone = TempsProcess[zone]

        data[f"Planning {zone}"] = data[zone]/(30/temps_process_zone)
        for i in range(len(data)-1):
            d = data.loc[i,f"Planning {zone}"].copy()
            if data.loc[i,"Date et heure"].time() < datetime.time(4,0):
                data.loc[i,f"Planning {zone}"] = 0
                data.loc[i+1,f"Planning {zone}"] += d
            elif d > MaxLigne[zone]:
                data.loc[i,f"Planning {zone}"] = MaxLigne[zone]
                data.loc[i+1,f"Planning {zone}"] += (d-MaxLigne[zone])
        data[f"Planning {zone}"] = data[f"Planning {zone}"].apply(ceil)
        
        smoothed = data[f"Planning {zone}"].copy()

        skip = False
        for i in range(1, len(data)-1):
            if skip:
                skip = False
            else:
                prec = data[f"Planning {zone}"].iloc[i-1]
                cur = data[f"Planning {zone}"].iloc[i]
                suiv = data[f"Planning {zone}"].iloc[i+1]
                dif_prec = cur-prec
                dif_suiv = suiv-cur

                if dif_prec > 0 and dif_suiv < 0:
                    if prec == 0:
                        smoothed.iloc[i+1] = cur
                        skip = True
                    # CORRECTION : Ajout de la vérification i+2 (comme dans IdealDouane)
                    elif i+2 < len(data): 
                        smoothed.iloc[i] = max(prec,suiv)
                        suiv2 = data[f"Planning {zone}"].iloc[i+2]
                        if suiv2-suiv < 0:
                            smoothed.iloc[i+2] = suiv2 + 1
                elif dif_prec < 0 and dif_suiv > 0:
                    smoothed.iloc[i] = min(prec,suiv)
                
        data[f"Planning {zone} lissé"] = smoothed.copy()
        skip = False
        skip2 = False
        for i in range(1, len(data)-1):
            if skip:
                skip = False
            elif skip2:
                skip2 = False
            else:
                prec = data[f"Planning {zone} lissé"].iloc[i-1]
                if prec != 0:
                    cur = data[f"Planning {zone} lissé"].iloc[i]
                    suiv = data[f"Planning {zone} lissé"].iloc[i+1]
                    dif_prec = cur-prec
                    dif_suiv = suiv-cur

                    # CORRECTION : Ajout de la vérification i+2 (comme dans IdealDouane)
                    if dif_prec > 0 and dif_suiv > 0 and i+2 < len(data):
                        suiv2 = data[f"Planning {zone} lissé"].iloc[i+2]
                        if suiv2-suiv > 0:
                            smoothed.iloc[i] = prec
                            smoothed.iloc[i+1] = suiv2
                            skip = True
                            skip2 = True
                        elif dif_prec > min(dif_suiv,prec-1):
                            smoothed.iloc[i] = suiv
                        else:
                            smoothed.iloc[i] = prec
                    # CORRECTION : Ajout de la vérification i+2 (comme dans IdealDouane)
                    if dif_prec < 0 and dif_suiv < 0 and -dif_suiv < suiv and i+2 < len(data):
                        suiv2 = data[f"Planning {zone} lissé"].iloc[i+2]
                        if suiv2-suiv < 0 and suiv2-suiv > -3:
                            smoothed.iloc[i] = suiv
                            smoothed.iloc[i+2] = suiv
                            skip = True
                            skip2 = True
                        elif max(dif_prec,-suiv/2) < dif_suiv:
                            smoothed.iloc[i] = suiv
                        else:
                            smoothed.iloc[i] = prec
                            
        data[f"Planning {zone} lissé"] = smoothed

    dates = data["Date et heure"].dt.date.drop_duplicates()
    debut = dates.min().strftime(format="%Y%m%d")
    fin = dates.max().strftime(format="%Y%m%d")
    mnt = datetime.datetime.now().strftime(format="%Y%m%d%H%M")

    planning_surete = {}

    for date in dates:
        data_jour = data[data["Date et heure"].dt.date == date]
        planning_surete[date.strftime(format="%Y-%m-%d")] = {}
        for zone in surete_cols:
            planning_surete[date.strftime(format="%Y-%m-%d")][zone] = repls(data_jour[f"Planning {zone} lissé"].to_list())

    nom = "PlanningSureteIdeal"
    # CORRECTION : Utilisation de pathlib
    dossier_destination = CHEMIN_DATA_SOURCE / "Capacite" / "Planning"
    
    deplacer_fichier(nom, dossier_destination, "SureteIdeal") # dossier_destination est maintenant un Path
    
    file = f"{mnt}{nom}{debut}-{fin}.json"

    # CORRECTION : Utilisation de pathlib pour écrire le fichier
    (dossier_destination / "Actuel").mkdir(parents=True, exist_ok=True)
    
    with open(dossier_destination / "Actuel" / file, "w") as f:
        json.dump(planning_surete,f)
