import pandas as pd
import datetime
import shutil
import os
import re # Ajouté pour la fonction deplacer_fichier
from math import ceil
from pathlib import Path # Ajouté pour la nouvelle gestion des chemins
from chemin_dossier import CHEMIN_DATA_SOURCE # <-- Correction de l'import
import json # Ajouté, car json.load est utilisé

# DATA_FOLDER n'est plus nécessaire, CHEMIN_DATA_SOURCE le remplace

def load_data(name, sous_dossier):
    # CORRECTION : Utilisation de pathlib
    dossier_path = CHEMIN_DATA_SOURCE / sous_dossier / "Actuel"
    
    # Gérer le cas où le dossier "Actuel" n'existe pas
    if not dossier_path.exists():
        print(f"Dossier 'Actuel' non trouvé : {dossier_path}")
        return None # Retourner None pour éviter une erreur

    target_file = None
    for fichier_path in dossier_path.iterdir():
        if name in fichier_path.name:
            target_file = fichier_path
            break
    
    if target_file:
        with open(target_file, 'r', encoding='utf-8') as file:
            return json.load(file)
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
        
        # Logique de ce script (différente de Pax_PlanningSurete)
        if nom_cible in fichier_nom:
            source = fichier_path
            destination = chemin_historique / fichier_nom
            
            # shutil.move fonctionne parfaitement avec les objets Path
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier_nom}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")

    
def PlanningIdealDouane(data):
    TempsProcess = load_data("TempsProcess","Capacite/TempsProcess")
    if TempsProcess is None: # S'assurer que les données sont chargées
        print("Erreur: Impossible de charger TempsProcess. Arrêt.")
        return

    douane_cols = []
    for col in data.columns:
        if col.startswith("Douane"):
            douane_cols.append(col)

    data = data[["Date et heure"]+douane_cols]

    data[douane_cols] = data[douane_cols].astype(int)

    data.set_index("Date et heure", inplace=True)
    data = data.resample("30min").sum()
    data = data.reset_index()

    MaxLigne = {"Douane : Aile est départ" : 21, "Douane : Trompette" : 4, "Douane : Satellite 10" : 4}

    for zone in douane_cols:
        data[f"Planning {zone}"] = data[zone]/(30/TempsProcess["Douane"])
        for i in range(len(data)-1):
            d = data.loc[i,f"Planning {zone}"].copy()
            if data.loc[i,"Date et heure"].time() < datetime.time(5,0):
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
                    elif min(dif_prec,-dif_suiv) < min(cur/2,3):
                        if dif_prec < -dif_suiv:
                            smoothed.iloc[i] = max(prec,suiv)
                            smoothed.iloc[i+1] = suiv + 1
                        elif i+2 < len(data): # Ajout de la vérification
                            suiv2 = data[f"Planning {zone}"].iloc[i+2]
                            if suiv2-suiv < 0:
                                smoothed.iloc[i] = max(prec,suiv)
                                smoothed.iloc[i+2] = suiv2 + 1
                                data.loc[i+2,f"Planning {zone}"] = suiv2 + 1
                            elif suiv2-suiv > 0:
                                smoothed.iloc[i+1] = min(cur,suiv2)
                                skip = True
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

                    if dif_prec > 0 and dif_suiv > 0:
                        if i+2 < len(data): # S'assurer que suiv2 existe
                            suiv2 = data[f"Planning {zone} lissé"].iloc[i+2]
                            if suiv2-suiv > 0:
                                smoothed.iloc[i] = prec
                                smoothed.iloc[i+1] = suiv2
                                skip = True
                                skip2 = True
                            elif dif_prec > dif_suiv or dif_prec > 2:
                                smoothed.iloc[i] = suiv
                            else:
                                smoothed.iloc[i] = prec
                        elif dif_prec > dif_suiv or dif_prec > 2: # Gérer le cas de la fin du dataframe
                            smoothed.iloc[i] = suiv
                        else:
                            smoothed.iloc[i] = prec
                    if dif_prec < 0 and dif_suiv < 0 and -dif_suiv < suiv:
                        if dif_suiv < -2:
                            smoothed.iloc[i] = prec
                        else:
                            if i+2 < len(data): # S'assurer que suiv2 existe
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
                            elif max(dif_prec,-suiv/2) < dif_suiv: # Gérer le cas de la fin du dataframe
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
        for zone in douane_cols:
            planning_surete[date.strftime(format="%Y-%m-%d")][zone] = repls(data_jour[f"Planning {zone} lissé"].to_list())

    nom = "PlanningDouaneIdeal"
    # CORRECTION : Utilisation de pathlib
    dossier_destination = CHEMIN_DATA_SOURCE / "Capacite" / "Planning"
    
    deplacer_fichier(nom, dossier_destination, "DouaneIdeal") # dossier_destination est maintenant un Path
    
    file = f"{mnt}{nom}{debut}-{fin}.json"

    # CORRECTION : Utilisation de pathlib pour écrire le fichier
    (dossier_destination / "Actuel").mkdir(parents=True, exist_ok=True)
    
    with open(dossier_destination / "Actuel" / file, "w") as f:
        json.dump(planning_surete,f)
