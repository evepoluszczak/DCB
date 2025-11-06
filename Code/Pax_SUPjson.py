import pandas as pd
import datetime
import os
import shutil
import json

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

def SUPjson(data, data_planning):
    mnt = datetime.datetime.now()
    debut = mnt.date()
    fin = datetime.date(2025,10,25)

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

    dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source/Demande"
    pre = mnt.strftime(format="%Y%m%d%H%M")
    post = str(debut).replace("-","") + "-" + str(fin).replace("-","") + ".json"

    nom = "SUPForecastCheckIn"
    deplacer_fichier(nom,dossier,"CheckIn")
    file = pre + nom + post
    with open(os.path.join(dossier,"Actuel",file),"w",encoding="utf-8") as f:
        json.dump(checkin,f)

    nom = "SUPForecastSurete"
    deplacer_fichier(nom,dossier,"Surete")
    file = pre + nom + post
    with open(os.path.join(dossier,"Actuel",file),"w",encoding="utf-8") as f:
        json.dump(surete,f)

    nom = "SUPForecastDouane"
    deplacer_fichier(nom,dossier,"Douane")
    file = pre + nom + post
    with open(os.path.join(dossier,"Actuel",file),"w",encoding="utf-8") as f:
        json.dump(douane,f)

    nom = "SUPForecastGate"
    deplacer_fichier(nom,dossier,"Gate/SUP")
    file = pre + nom + post
    with open(os.path.join(dossier,"Actuel",file),"w",encoding="utf-8") as f:
        json.dump(gate,f)

    dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source/Capacite/Planning"

    nom = "PlanningCheckIn"
    deplacer_fichier(nom,dossier,"CheckIn")
    file = pre + nom + post
    with open(os.path.join(dossier,"Actuel",file),"w",encoding="utf-8") as f:
        json.dump(planning_checkin,f)

    dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source/Annexe"

    nom = "GraphNames"
    deplacer_fichier(nom,dossier,"GraphNames")
    file = pre + nom + ".json"
    with open(os.path.join(dossier,"Actuel",file),"w",encoding="utf-8") as f:
        json.dump(graph_names,f)