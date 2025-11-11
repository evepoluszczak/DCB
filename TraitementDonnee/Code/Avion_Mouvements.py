import pandas as pd
import tqdm
import numpy as np
import json
from datetime import datetime
import os
import re
import shutil
from chemin_dossier import CHEMIN_DATA_SOURCE
from pathlib import Path 

def get_matrice_mvt (data) :
    """
    Fonction qui retourne les dictionaires du mouvement pour chaque key jour YYYY-MM-DD value 
    2 list avec atterissage 1ere liste et décolage 2eme liste pour
    chaque heure roulante à partir de chaque 5 minutes pour toute la journée. Un dictionaire pour schedule et un pour la prediction.
    """
    date_min = max(data["Local Schedule Time_ARR"].min().date(),datetime.now().date())
    date_max = data["Local Schedule Time_DEP"].max().replace(hour=23,minute=59)

    date_range = pd.date_range(date_min, date_max, freq = '5min')

    mvt_pred, mvt_schedule = {}, {}

    liste_A1, liste_D1, liste_A2, liste_D2, = [], [], [], []
    current_day = date_range[0].date()
    
    
    for date in tqdm.tqdm(date_range) :
        
        if current_day is None or date.date() != current_day:
            
            mvt_schedule[str(current_day)[:10]] = {"Piste : Atterrissage" : liste_A1, "Piste : Décollage" : liste_D1}
            mvt_pred[str(current_day)[:10]] = {"Piste : Atterrissage" : liste_A2, "Piste : Décollage" : liste_D2}
            liste_A1, liste_D1, liste_A2, liste_D2, = [], [], [], []
            
            current_day = date.date()
        
        liste_A1.append(int(np.sum((data["Local Schedule Time_ARR"] >= date) & (data["Local Schedule Time_ARR"] < date + pd.Timedelta(hours=1)))))
        liste_D1.append(int(np.sum((data["Local Schedule Time_DEP"] >= date) & (data["Local Schedule Time_DEP"] < date + pd.Timedelta(hours=1)))))
        
        liste_A2.append(int(np.sum((data["predictions_ARR"] >= date) & (data["predictions_ARR"] < date + pd.Timedelta(hours=1)))))
        liste_D2.append(int(np.sum((data["predictions_DEP"] >= date) & (data["predictions_DEP"] < date + pd.Timedelta(hours=1)))))

    mvt_schedule[str(current_day)[:10]] = {"Piste : Atterrissage" : liste_A1, "Piste : Décollage" : liste_D1}
    mvt_pred[str(current_day)[:10]] = {"Piste : Atterrissage" : liste_A2, "Piste : Décollage" : liste_D2}
    
    return mvt_pred, mvt_schedule

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

def Mouvements(data):
    mvt_pred, mvt_schedule = get_matrice_mvt(data)

    dates = list(mvt_pred.keys())
    mnt = datetime.now().strftime(format="%Y%m%d%H%M")
    first_date = dates[0].replace("-","")
    last_date = dates[len(dates)-1].replace("-","")
    fn = "ForecastPisteUtilisation"
    sn = "SchedulePisteUtilisation"
    forecast_name = mnt + fn + first_date + "-" + last_date + ".json"
    schedule_name = mnt + sn + first_date + "-" + last_date + ".json"

    # Exemple d'utilisation
    super_dossier = CHEMIN_DATA_SOURCE / "Demande"
    deplacer_fichier(fn,super_dossier,"Piste/Forecast")
    deplacer_fichier(sn,super_dossier,"Piste/Schedule")

    # S'assurer que le dossier "Actuel" existe avant d'écrire
    (super_dossier / "Actuel").mkdir(parents=True, exist_ok=True)

    # Utiliser l'opérateur / pour construire le chemin
    with open(super_dossier / "Actuel" / forecast_name,"w") as f:
        json.dump(mvt_pred,f)
    with open(super_dossier / "Actuel" / schedule_name,"w") as f:
        json.dump(mvt_schedule,f)
