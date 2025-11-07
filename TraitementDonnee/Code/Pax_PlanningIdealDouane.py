import pandas as pd
import json
import datetime
import shutil
import os
from math import ceil

DATA_FOLDER = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source"
def load_data(name, sous_dossier):
    # Parcourir les fichiers du dossier Actuel
    dossier = os.path.join(DATA_FOLDER,sous_dossier,"Actuel")
    for fichier in os.listdir(dossier):
        if name in fichier:
            file_name = fichier
            break
    with open(os.path.join(dossier,file_name), 'r', encoding='utf-8') as file:
        return json.load(file)

def repls(liste,nb=6):
    return [valeur for valeur in liste for _ in range(nb)]

def deplacer_fichier(nom_cible, super_dossier, sous_dossier = None):
    # Obtenir le chemin absolu des dossiers
    chemin_actuel = os.path.join(super_dossier, 'Actuel')
    chemin_historique = os.path.join(super_dossier, 'Historique')
    if sous_dossier:
        chemin_historique = os.path.join(chemin_historique,sous_dossier)

    # Parcourir les fichiers du dossier Actuel
    for fichier in os.listdir(chemin_actuel):
        if nom_cible in fichier:
            source = os.path.join(chemin_actuel, fichier)
            destination = os.path.join(chemin_historique, fichier)
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")
    
def PlanningIdealDouane(data):
    TempsProcess = load_data("TempsProcess","Capacite/TempsProcess")

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
                        else:
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
                    if dif_prec < 0 and dif_suiv < 0 and -dif_suiv < suiv:
                        if dif_suiv < -2:
                            smoothed.iloc[i] = prec
                        else:
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

    # data.to_csv("D:/users/bastien.schneuwly/workfolders/documents/Stage_Bastien/cpdouane.csv",index=False)

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
    dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source/Capacite/Planning"
    deplacer_fichier(nom,dossier,"DouaneIdeal")
    file = f"{mnt}{nom}{debut}-{fin}.json"

    with open(os.path.join(dossier,"Actuel",file),"w") as f:

        json.dump(planning_surete,f)
