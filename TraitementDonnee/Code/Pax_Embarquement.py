import pandas as pd
import json
from datetime import datetime
import re
import os
import shutil
from tqdm import tqdm
# CORRECTION : Imports des chemins dynamiques
from chemin_dossier import CHEMIN_INPUT, CHEMIN_DATA_SOURCE
from pathlib import Path

# CORRECTION : Remplacement par la version pathlib
def deplacer_fichier(nom_cible, super_dossier: Path, sous_dossier: str = None):
    # super_dossier est maintenant un objet Path
    chemin_actuel = super_dossier / 'Actuel'
    chemin_historique = super_dossier / 'Historique'
    if sous_dossier:
        chemin_historique = chemin_historique / sous_dossier

    # S'assurer que le dossier de destination existe
    chemin_historique.mkdir(parents=True, exist_ok=True)

    # Expression régulière : date + nom + date-date.json
    pattern = re.compile(rf'^(\d{{12}}){re.escape(nom_cible)}(\d{{8}}-\d{{8}})\.json$')

    # Gérer le cas où le dossier "Actuel" n'existe pas
    if not chemin_actuel.exists():
        print(f"Dossier 'Actuel' non trouvé : {chemin_actuel}")
        return

    # Parcourir les fichiers du dossier Actuel avec iterdir()
    for fichier_path in chemin_actuel.iterdir():
        fichier_nom = fichier_path.name # Obtenir le nom du fichier
        
        if pattern.match(fichier_nom):
            source = fichier_path
            destination = chemin_historique / fichier_nom
            
            # shutil.move fonctionne parfaitement avec les objets Path
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier_nom}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")

Gates_zone = {"Gate : A1 à A2":["A1","A2"], "Gate : A3":["A3"], "Gate : A4 à A5":["A4","A5"], "Gate : A6 à A7":["A6","A7"], "Gate : A8":["A8"], "Gate : A9 à A10":["A9","A10"], "Gate : B31 à B34":["B31","B32","B33","B34"], "Gate : B41 à B44":["B41","B42","B43","B44"], "Gate : C51 à C52":["C51","C52"], "Gate : C53 à C54":["C53","C54"], "Gate : C55":["C55"], "Gate : C56":["C56"], "Gate : C57 à C63":["C57","C58","C59","C60","C61","C62","C63"], "Gate : D21 à D27":["D21","D22","D23","D24","D25","D26","D27"], "Gate : D71/81 à D74/84":["D71","D72","D73","D74","D81","D82","D83","D84"], "Gate : D75/85 à D76/86":["D75","D76","D85","D86"], "Gate : E/F10 à E/F11":["E10","E11","F10","F11","A11"], "Gate : E/F12":["E12","F12"], "Gate : E/F14 à E/F17":["E14","E15","E16","E17","F14","F15","F16","F17"]}

def trouve_gate_zone(row):
    Gate = row["Gate OOP+"]
    zd = "ND"
    for gz in Gates_zone.keys():
        if Gate in Gates_zone[gz]:
            zd = gz
            break
    if zd == "ND":
        if row["Official Schengen Airport"] == "Y":
            zd = "Gate : B41 à B44"
        else:
            zd = "Gate : C57 à C63"
    return zd

def Embarquement(predi):
    predi = predi[["Date_DEP", "Call Sign - IATA_DEP", "predictions_DEP"]]
    predi.columns = ["Date", "Call Sign - IATA","Local Expected Time"]
    # CORRECTION : Utilisation de CHEMIN_INPUT
    data = pd.read_csv(CHEMIN_INPUT / "WEBI" / "DCB_BSH_Landside.csv")
    data = data[["Date", "Call Sign - IATA", "Gate OOP+", "Official Schengen Airport", "Better Forecast Pax Published", "Local Schedule Time"]]
    data["Date"] = pd.to_datetime(data["Date"])
    data["Local Schedule Time"] = pd.to_datetime(data["Local Schedule Time"])
    data = pd.merge(data,predi,on=["Date","Call Sign - IATA"],how="left")
    data.loc[data["Local Expected Time"].isna(),"Local Expected Time"] = data.loc[data["Local Expected Time"].isna(),"Local Schedule Time"]

    data["Gate Zone"] = data[["Gate OOP+","Official Schengen Airport"]].apply(trouve_gate_zone,axis=1)
    start = data["Local Schedule Time"].dt.date.min()
    end = data["Local Schedule Time"].dt.date.max()
    schedule = {}
    prediction = {}
    for date in tqdm(pd.date_range(start=start,end=end)):
        date_str = date.strftime(format="%Y-%m-%d")
        schedule[date_str] = {zone : [] for zone in Gates_zone.keys()}
        prediction[date_str] = {zone : [] for zone in Gates_zone.keys()}
        for heure in range(24):
            for minute in range(0,60,5):
                temps = date + pd.Timedelta(hours=heure, minutes=minute)
                min = temps + pd.Timedelta(minutes=30)
                max = min + pd.Timedelta(minutes=20)
                data_sched = data[(data["Local Schedule Time"]>=min)&(data["Local Schedule Time"]<max)]
                data_pred = data[(data["Local Expected Time"]>=min)&(data["Local Expected Time"]<max)]
                for zone in Gates_zone:
                    schedule[date_str][zone].append(int(data_sched.loc[data_sched["Gate Zone"] == zone, "Better Forecast Pax Published"].sum())/4)
                    prediction[date_str][zone].append(int(data_pred.loc[data_pred["Gate Zone"] == zone, "Better Forecast Pax Published"].sum())/4)

    dates = list(schedule.keys())
    mnt = datetime.now().strftime(format="%Y%m%d%H%M")
    first_date = dates[0].replace("-","")
    last_date = dates[-1].replace("-","")
    fn = "ForecastGateEmbarquement"
    sn = "ScheduleGateEmbarquement"
    forecast_name = mnt + fn + first_date + "-" + last_date + ".json"
    schedule_name = mnt + sn + first_date + "-" + last_date + ".json"

    # Exemple d'utilisation
    # CORRECTION : Utilisation de CHEMIN_DATA_SOURCE et pathlib
    super_dossier = CHEMIN_DATA_SOURCE / "Demande"
    deplacer_fichier(fn,super_dossier,"Gate/Embarquement/Forecast")
    deplacer_fichier(sn,super_dossier,"Gate/Embarquement/Schedule")

    # CORRECTION : S'assurer que le dossier "Actuel" existe et utiliser pathlib
    (super_dossier / "Actuel").mkdir(parents=True, exist_ok=True)

    with open(super_dossier / "Actuel" / forecast_name,"w") as f:
        json.dump(prediction,f)
    with open(super_dossier / "Actuel" / schedule_name,"w") as f:
        json.dump(schedule,f)
