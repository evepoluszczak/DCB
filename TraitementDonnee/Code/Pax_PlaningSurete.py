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
        if nom_cible in fichier and not (nom_cible == "PlanningSurete" and "PlanningSureteIdeal" in fichier):
            source = os.path.join(chemin_actuel, fichier)
            destination = os.path.join(chemin_historique, fichier)
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")

def PlanningSurete(format):
    mnt = datetime.datetime.now()
    debut = mnt.date()
    fin = datetime.date(2025,10,25)
    dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Autre"
    surete = {}

    if format == "excel":
        for fichier in os.listdir(dossier):
            if "LanePlan_CSC" in fichier:
                break

        planningSurete = pd.read_excel(dossier + "/" + fichier)
        planningSurete = planningSurete.set_index("Lane Plan")
        planningSurete = planningSurete.drop(columns=datetime.time(22,0))

        for date in pd.date_range(start=debut,end=fin):
            data_jour = planningSurete.loc[date]
            date_str = date.strftime(format="%Y-%m-%d")
            CSC = [0]*4*12
            for ligne in data_jour:
                CSC += [int(ligne)]*6
            CSC += [0]*2*12
            SF = [0]*54 + [3]*35*6 + [0]*24

            surete[date_str] = {"Sûreté : International" : CSC, "Sûreté : France" : SF}
    elif format == "csv":
        for fichier in os.listdir(dossier):
            if "LanePlans_CheckpointGroups" in fichier:
                break

        planningSurete = pd.read_csv(dossier + "/" + fichier,sep=";")
        planningSurete = planningSurete[["Time", "1_NEW CSC.1_NEW CSC.Lanes", "2_SF.2_SF.Lanes"]]
        planningSurete["Time"] = pd.to_datetime(planningSurete["Time"].str[:19])
        planningSurete.columns = ["Date et heure", "CSC", "SF"]

        for date in pd.date_range(start=debut,end=fin):
            data_jour = planningSurete[planningSurete["Date et heure"].dt.date == date.date()]
            date_str = date.strftime(format="%Y-%m-%d")
            CSC = data_jour["CSC"].to_list()
            SF = data_jour["SF"].to_list()
            T2 = [4]*12*24
            surete[date_str] = {"Sûreté : International" : CSC, "Sûreté : France" : SF, "Sûreté : TERMINAL 2" : T2}
    
    else:
        print("Mauvais format: veuillez spécifiez 'csv' ou 'excel'!")
        return 0

    dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source/Capacite/Planning"

    nom = "PlanningSurete"
    deplacer_fichier(nom,dossier,"Surete")
    file = mnt.strftime(format="%Y%m%d%H%M") + nom + str(debut).replace("-","") + "-" + str(fin).replace("-","") + ".json"
    with open(os.path.join(dossier,"Actuel",file),"w") as f:
        json.dump(surete,f)