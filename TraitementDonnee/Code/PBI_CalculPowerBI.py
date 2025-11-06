import json
import pandas as pd
from tqdm import tqdm
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

def melt_df(df, value_name):
    return df.melt(id_vars='Date et heure', 
                   var_name='Processeur', 
                   value_name=value_name)

def list_mult(liste, coef):
    res = []
    for i in range(len(liste)):
        res.append(liste[i] * coef)
    return res

def calcul_queue(demande,capacite):
    queue = [0]
    for i in range(len(demande)-1):
        queue.append(max(0,queue[i] + demande[i] - capacite[i]))
    return queue

def calcul_attente(queue, capacite):
    attente = []
    for i in range(len(queue)):
        if capacite[i] != 0:
            wait = ceil(queue[i]/capacite[i]*5)
        else:
            wait = 0
        attente.append(wait)
    return attente

def value_to_color(value, var, seuil):
    if var in seuil["Processeur"].to_list():
        o = seuil.loc[seuil["Processeur"]==var,"Seuil orange"].iloc[0]
        r = seuil.loc[seuil["Processeur"]==var,"Seuil rouge"].iloc[0]
        if type(value) == list:
            resultat = []
            for val in value:
                if val <= o:
                    resultat.append("green")
                elif val <= r:
                    resultat.append("orange")
                else:
                    resultat.append("red")
            return resultat
        if value <= o:
            return "green"
        elif value <= r:
            return "orange"
        return "red"
    return ["lightblue"]*len(value) if type(value)==list else "lightblue"

def worst_color(l):
    if "red" in l:
        return "red"
    elif "orange" in l:
        return "orange"
    elif "green" in l:
        return "green"
    return "lightblue"

def CalculPBI():
    data_stand = load_data("ForecastStandUtilisation","Demande")
    data_piste = load_data("ForecastPisteUtilisation","Demande")
    data_surete = load_data("SUPForecastSurete","Demande")
    data_checkin = load_data("SUPForecastCheckIn","Demande")
    planning_checkin = load_data("PlanningCheckIn","Capacite/Planning")
    data_douane = load_data("SUPForecastDouane","Demande")
    planning_douane = load_data("PlanningDouane","Capacite/Planning")
    planning_douane_ideal = load_data("PlanningDouaneIdeal","Capacite/Planning")
    data_gate = load_data("SUPForecastGate","Demande")
    embarquement_gate = load_data("ForecastGateEmbarquement","Demande")
    planning_surete = load_data("PlanningSurete","Capacite/Planning")
    planning_surete_ideal = load_data("PlanningSureteIdeal","Capacite/Planning")

    checkin_zone = list(list(data_checkin.values())[0].keys())
    surete_zone = list(list(data_surete.values())[0].keys())
    douane_zone = list(list(data_douane.values())[0].keys())
    gate_zone = list(list(data_gate.values())[0].keys())

    #gate_zone_conversion = load_data("GateZone","Annexe")
    
    TEMPS_PROCESS = load_data("TempsProcess", "Capacite/TempsProcess")
    temps = pd.DataFrame(columns=["Processeur","Temps de process"])
    for zone in checkin_zone+surete_zone+douane_zone:
        if zone in TEMPS_PROCESS.keys():
            value = TEMPS_PROCESS[zone]
        else:
            value = TEMPS_PROCESS[zone.split(" : ")[0]]
        if zone.startswith("Sûreté") or zone.startswith("Douane"):
            temps.loc[len(temps)] = [zone+"_reel",value]
            temps.loc[len(temps)] = [zone+"_ideal",value]
        else:
            temps.loc[len(temps)] = [zone,value]

    data_frame_columns = checkin_zone + [zone+"_reel" for zone in surete_zone] + [zone+"_ideal" for zone in surete_zone] + [zone+"_reel" for zone in douane_zone] + [zone+"_ideal" for zone in douane_zone] + gate_zone + ["Stand : C", "Stand : D", "Stand : E", "Piste : Atterrissage", "Piste : Décollage"]
    planning_columns = checkin_zone + [zone+"_reel" for zone in surete_zone] + [zone+"_ideal" for zone in surete_zone] + [zone+"_reel" for zone in douane_zone] + [zone+"_ideal" for zone in douane_zone]
    #missing_columns = gate_zone+["Stand : C", "Stand : D", "Stand : E", "Piste : Atterrissage", "Piste : Décollage"]

    LOS = load_data("ValeursCritiquesDuree","LevelOfService")
    PISTE_THRESHOLDS = load_data("CapacitePiste", "Capacite/Aeroport")
    GATE_THRESHOLDS = load_data("CapaciteGate", "Capacite/Aeroport")
    stand_ouv = load_data("StandDispo", "Capacite/Aeroport")
    standTot = sum(stand_ouv.values()) + stand_ouv["Dv"] + stand_ouv["Ev"]
    standC = stand_ouv["Cf"] + 2*stand_ouv["Dv"] + 2*stand_ouv["Ev"]
    standD = stand_ouv["Df"] + stand_ouv["Dv"]
    standE = stand_ouv["Ef"] + stand_ouv["Ev"]
    STAND_THRESHOLDS = {"Stand" : [standTot*0.6,standTot], "Stand : C" : [standC*0.6,standC], "Stand : D" : [standD*0.8,standD], "Stand : E" : [standE*0.6,standE]}
    SURETE_THRESHOLDS = {zone : LOS["Sûreté"] for zone in surete_zone}
    CHECKIN_THRESHOLDS = {zone : LOS["Check-in"] for zone in checkin_zone}
    DOUANE_THRESHOLDS = {zone : LOS["Douane"] for zone in douane_zone}

    occupation_gate = {}
    for date in data_gate.keys():
        occ_jour = {}
        for zone in data_gate[date].keys():
            occ_zone = [data_gate[date][zone][0]-embarquement_gate[date][zone][0]]
            for j in range(1,len(embarquement_gate[date][zone])):
                occ_zone.append(occ_zone[j-1]+data_gate[date][zone][j]-embarquement_gate[date][zone][j])
            occ_jour[zone] = occ_zone
        occupation_gate[date] = occ_jour

    indices = pd.Index(pd.date_range(start=list(data_checkin.keys())[0]+" 00:00:00",end=list(data_checkin.keys())[-1]+" 23:55:00", freq='5min'),name="Date et heure")
    demande = pd.DataFrame(index=indices,columns=data_frame_columns)
    planning = pd.DataFrame(index=indices,columns=planning_columns)
    for date in tqdm(pd.date_range(start=list(data_checkin.keys())[0],end=list(data_checkin.keys())[-1])):
        date_str = date.strftime(format="%Y-%m-%d")
        for i in range(288):
            date_heure = date + pd.Timedelta(minutes=i*5)
            for zone in checkin_zone:
                demande.loc[date_heure,zone] = data_checkin[date_str][zone][i]
                planning.loc[date_heure,zone] = planning_checkin[date_str][zone][i]
            for zone in surete_zone:
                demande.loc[date_heure,zone+"_reel"] = data_surete[date_str][zone][i]
                demande.loc[date_heure,zone+"_ideal"] = data_surete[date_str][zone][i]
                planning.loc[date_heure,zone+"_reel"] = planning_surete[date_str][zone][i]
                planning.loc[date_heure,zone+"_ideal"] = planning_surete_ideal[date_str][zone][i]
            for zone in douane_zone:
                demande.loc[date_heure,zone+"_reel"] = data_douane[date_str][zone][i]
                demande.loc[date_heure,zone+"_ideal"] = data_douane[date_str][zone][i]
                planning.loc[date_heure,zone+"_reel"] = planning_douane[date_str][zone][i]
                planning.loc[date_heure,zone+"_ideal"] = planning_douane_ideal[date_str][zone][i]
            for zone in gate_zone:
                demande.loc[date_heure,zone] = occupation_gate[date_str][zone][i]
            for zone in ["Stand : C", "Stand : D", "Stand : E"]:
                demande.loc[date_heure,zone] = data_stand[date_str][zone][i]
            for zone in ["Piste : Atterrissage", "Piste : Décollage"]:
                demande.loc[date_heure,zone] = data_piste[date_str][zone][i]

    Thresholds = {}
    Thresholds.update(PISTE_THRESHOLDS)
    Thresholds.update(STAND_THRESHOLDS)
    Thresholds.update(SURETE_THRESHOLDS)
    Thresholds.update(CHECKIN_THRESHOLDS)
    Thresholds.update(DOUANE_THRESHOLDS)
    Thresholds.update(GATE_THRESHOLDS)

    seuil = pd.DataFrame(columns=["Processeur","Seuil orange","Seuil rouge"])
    for key,value in Thresholds.items():
        if key.startswith("Sûreté") or key.startswith("Douane"):
            seuil.loc[len(seuil)] = [key+"_reel",value[0],value[1]]
            seuil.loc[len(seuil)] = [key+"_ideal",value[0],value[1]]
        else:
            seuil.loc[len(seuil)] = [key,value[0],value[1]]

    seuil.to_csv("//gva.tld/aig/O/12_EM-DO/4_OOP/17_PBI/02 - Dashboards en développement/EPL/15. DCB/Power BI DCB/Power BI DCB/Data/seuil.csv",index=False)

    demande = demande.reset_index()
    planning = planning.reset_index()

    demande["Date"] = demande["Date et heure"].dt.date
    planning["Date"] = planning["Date et heure"].dt.date

    dates = planning["Date"].copy()
    dates.index = indices
    capacite = pd.DataFrame(index=indices,columns=planning_columns)
    capacite["Date"] = dates
    queue = pd.DataFrame(index=indices,columns=planning_columns)
    queue["Date"] = dates
    attente = pd.DataFrame(index=indices,columns=planning_columns)
    attente["Date"] = dates
    pourcentage_seuil_80 = pd.DataFrame(index=indices,columns=planning_columns)
    pourcentage_seuil_80["Date"] = dates
    pourcentage_seuil_99 = pd.DataFrame(index=indices,columns=planning_columns)
    pourcentage_seuil_99["Date"] = dates
    alerte_seuil_80 = pd.DataFrame(index=indices,columns=planning_columns)
    alerte_seuil_80["Date"] = dates
    alerte_seuil_99 = pd.DataFrame(index=indices,columns=planning_columns)
    alerte_seuil_99["Date"] = dates
    #couleurs = pd.DataFrame(columns=data_frame_columns)
    #couleurs["Date et heure"] = planning["Date et heure"]
    #couleurs["Date"] = planning["Date"]
    for date in demande["Date"].drop_duplicates().to_list():
        demande_jour = demande[demande["Date"] == date]
        planning_jour = planning[planning["Date"] == date]
        for processeur in planning_columns:
            demande_proc = demande_jour[processeur].to_list()
            planning_proc = planning_jour[processeur].to_list()
            capacite_proc = list_mult(planning_proc,float(5/temps.loc[temps["Processeur"]==processeur,"Temps de process"].iloc[0]))
            queue_proc = calcul_queue(demande_proc,capacite_proc)
            attente_proc = calcul_attente(queue_proc,capacite_proc)
            capacite.loc[capacite["Date"]==date,processeur] = capacite_proc
            queue.loc[queue["Date"]==date,processeur] = queue_proc
            attente.loc[attente["Date"]==date,processeur] = attente_proc
    #        couleurs.loc[couleurs["Date"]==date,processeur] = value_to_color(attente_proc,processeur,seuil)

    attente.drop(columns="Date",inplace=True)
    attente_moyenne = attente.rolling(window=7, center=True, min_periods=1).mean()
    attente_moyenne = attente_moyenne.map(ceil)
    attente_moyenne["Date"] = dates

    for date in attente_moyenne["Date"].drop_duplicates().to_list():
        for processeur in planning_columns:
            amdp = attente_moyenne.loc[(capacite["Date"]==date)&(capacite[processeur]!=0),processeur]
            seuil_proc = seuil[seuil["Processeur"]==processeur].iloc[0].to_list()
            tot_ouv = len(amdp)
            if tot_ouv != 0:
                plus_seuil_80 = (amdp<=seuil_proc[1]).sum()
                plus_seuil_99 = (amdp<=seuil_proc[2]).sum()
                pcs80 = plus_seuil_80/tot_ouv
                pcs99 = plus_seuil_99/tot_ouv
            else:
                pcs80 = 1
                pcs99 = 1
            pourcentage_seuil_80.loc[pourcentage_seuil_80["Date"]==date,processeur] = pcs80
            pourcentage_seuil_99.loc[pourcentage_seuil_99["Date"]==date,processeur] = pcs99
            alerte_seuil_80.loc[alerte_seuil_80["Date"]==date,processeur] = int((pcs80 < 0.8)) + int((pcs80 < 0.89))
            alerte_seuil_99.loc[alerte_seuil_99["Date"]==date,processeur] = int((pcs99 < 0.96)) + int((pcs99 < 0.98))

    #for processeur in missing_columns:
    #    couleurs[processeur] = value_to_color(demande[processeur].to_list(),processeur,seuil)
    #for processeur in list(graph_names.keys())[:4]:
    #    for date in couleurs["Date et heure"].to_list():
    #        couleurs.loc[couleurs["Date et heure"]==date,processeur] = worst_color(couleurs.loc[couleurs["Date et heure"] == date,[processeur + " : " + s for s in graph_names[processeur]]].iloc[0].to_list())

    capacite = capacite.reset_index()
    queue = queue.reset_index()
    attente = attente.reset_index()
    attente_moyenne = attente_moyenne.reset_index()
    pourcentage_seuil_80 = pourcentage_seuil_80.reset_index()
    pourcentage_seuil_99 = pourcentage_seuil_99.reset_index()
    alerte_seuil_80 = alerte_seuil_80.reset_index()
    alerte_seuil_99 = alerte_seuil_99.reset_index()

    demande.drop(columns="Date",inplace=True)
    planning.drop(columns="Date",inplace=True)
    capacite.drop(columns="Date",inplace=True)
    queue.drop(columns="Date",inplace=True)
    attente_moyenne.drop(columns="Date",inplace=True)
    pourcentage_seuil_80.drop(columns="Date",inplace=True)
    pourcentage_seuil_99.drop(columns="Date",inplace=True)
    alerte_seuil_80.drop(columns="Date",inplace=True)
    alerte_seuil_99.drop(columns="Date",inplace=True)

    # Étape 1 : transformation en format long
    df_demande = melt_df(demande, 'Demande')
    df_planning = melt_df(planning, 'Planning')
    df_capacite = melt_df(capacite, 'Capacité')
    df_queue = melt_df(queue, 'Queue')
    df_attente = melt_df(attente, 'Attente')
    df_attente_moyenne = melt_df(attente_moyenne, 'Attente moyene sur 30 minutes')
    df_pourcentage_seuil_80 = melt_df(pourcentage_seuil_80, 'Pourcentage du temps en dessous du seuil inférieur')
    df_pourcentage_seuil_99 = melt_df(pourcentage_seuil_99, 'Pourcentage du temps en dessous du seuil supérieur')
    df_alerte_seuil_80 = melt_df(alerte_seuil_80, 'Alerte seuil inférieur')
    df_alerte_seuil_99 = melt_df(alerte_seuil_99, 'Alerte seuil supérieur')

    # Étape 2 : fusion successive
    df_final = df_demande.merge(df_planning, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_capacite, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_queue, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_attente, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_attente_moyenne, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_pourcentage_seuil_80, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_pourcentage_seuil_99, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_alerte_seuil_80, on=['Date et heure', 'Processeur'], how='outer')
    df_final = df_final.merge(df_alerte_seuil_99, on=['Date et heure', 'Processeur'], how='outer')

    for processeur in seuil["Processeur"].to_list():
        df_final.loc[df_final["Processeur"]==processeur,"Seuil orange"] = seuil.loc[seuil["Processeur"] == processeur, "Seuil orange"].iloc[0]
        df_final.loc[df_final["Processeur"]==processeur,"Seuil rouge"] = seuil.loc[seuil["Processeur"] == processeur, "Seuil rouge"].iloc[0]
    for processeur in temps["Processeur"].to_list():
        df_final.loc[df_final["Processeur"]==processeur,"Temps de process"] = temps.loc[temps["Processeur"]==processeur, "Temps de process"].iloc[0]

    df_final.to_csv("//gva.tld/aig/O/12_EM-DO/4_OOP/17_PBI/02 - Dashboards en développement/EPL/15. DCB/Power BI DCB/Power BI DCB/Data/global.csv",index=False)