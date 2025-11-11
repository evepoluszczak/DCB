#Imports: JSON I/O, Pandas for data wrangling, OS for paths/dir change, time() for timing, and tqdm for a progress bar.
import json
import pandas as pd
import os
from time import time
from tqdm import tqdm 

def load_data(name): #helper to open a JSON file from a fixed UNC folder, Builds .../Input/Autre/<name>.json, opens it UTF-8, returns parsed JSON (Python dict/list)
    DATA_FOLDER = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Autre"
    # Parcourir les fichiers du dossier Actuel
    fichier = os.path.join(DATA_FOLDER,name+".json")
    with open(fichier, 'r', encoding='utf-8') as file:
        return json.load(file)

def trouve_gate_zone(Gate, Gates_zone, gates_unique_zones):
    for gz in Gates_zone.keys():
        if Gate in gz.split("-"):
            zd = "Gate : " + Gates_zone[gz]
            break
    else:
        zd = "TBN"
    for gz in gates_unique_zones:
        if Gate in gz.split("-"):
            zs = gz
            break
    else:
        zs = "TBN"
    return zd, zs

def trouve_checkin_zone(Checkin):
    if Checkin == 17:
        return "1-17"
    elif Checkin <= 48:
        return "18-48"
    elif Checkin <= 106:
        return "49-106"
    elif Checkin <= 120:
        return "109-120"
    else:
        return "T2"

def find_SUP(Al, j, per, sns, zone, proc, proc_map):
    SUPs_proc = proc_map.get(proc)
    if SUPs_proc is None:
        raise ValueError(f"Le processeur {proc} n'existe pas!")
    fl = 0
    SUPs_al = SUPs_proc.loc[SUPs_proc["Airline IATA"] == Al]
    if SUPs_al.empty:
        SUPs_al = SUPs_proc.loc[SUPs_proc["Airline IATA"] == "ALL"]
        fl += 16
    SUPs_zone = SUPs_al.loc[SUPs_al["Zone"] == zone]
    if SUPs_zone.empty:
        SUPs_zone = SUPs_al
        fl += 8
    SUPs_schengen = SUPs_zone.loc[SUPs_zone["Schengen"] == sns]
    if SUPs_schengen.empty:
        SUPs_schengen = SUPs_zone
        fl += 4
    SUPs_periode = SUPs_schengen.loc[SUPs_schengen["Période"] == per]
    if SUPs_periode.empty:
        SUPs_periode = SUPs_schengen
        fl += 2
    SUPs_jour = SUPs_periode.loc[SUPs_periode["Jour"] == j]
    if SUPs_jour.empty:
        SUPs_jour = SUPs_periode
        fl += 1

    pivot = SUPs_jour.pivot_table(index='UID', columns='Minutes', values='Pourcentage', aggfunc='sum').fillna(0)
    mean_per_minute = pivot.mean(axis=0).reset_index()
    mean_per_minute.columns = ['Minutes', 'Pourcentage']
    mean_per_minute.sort_values('Minutes', ascending=False, inplace=True)
    minutes_new = pd.Series(range(mean_per_minute['Minutes'].max(), mean_per_minute['Minutes'].min() - 1, -5))
    interpolated = pd.merge(minutes_new.to_frame(name='Minutes'), mean_per_minute, on='Minutes', how='left')
    interpolated['Pourcentage'] = interpolated['Pourcentage'].interpolate(method='linear')
    interpolated['Pourcentage'] /= interpolated['Pourcentage'].sum()
    return interpolated, fl

def projette_SUPs_sur_vol(row, Gates_zone, gates_unique_zones, proc_map, ouverture_checkin, fermeture_checkin, DCB_forecast, PlanningCheckin, SUPT2surete, SUPT2checkin):
    STD = row["Local Schedule Time"]
    Airline = row["Airline IATA Code"]
    Schengen = "Schengen" if row["Official Schengen Airport"] == "Y" else "Non Schengen"
    Checkin = row["Checkin desks OOP+"]

    if Checkin != "TBN":
        Checkin = Checkin.split("-")
        if Checkin[1] == "57F":
            Checkin[1] = "57"
            NbCheckin = 63 - int(Checkin[0])
        elif Checkin[1] == "17":
            NbCheckin = 30
        else:
            if Checkin[1] == "":
                Checkin[1] = Checkin[0]
            NbCheckin = int(Checkin[1]) - int(Checkin[0]) + 1
        CheckinZoneSUP = trouve_checkin_zone(int(Checkin[1]))
    else:
        CheckinZoneSUP = "49-106"
        NbCheckin = 7
    CheckinZoneDCB = "Check-in : " + row["Checkin sector OOP+"]
    Gate = row["Gate OOP+"]
    GateSec = row["Gate Zone OOP+"]
    if Gate == "TBN":
        if GateSec == "A":
            Gate = "A6"
        elif GateSec == "B":
            Gate = "B43"
        elif GateSec == "C":
            Gate = "C63"
        elif GateSec == "D":
            Gate = "D27"
        elif GateSec in ["E","F"]:
            Gate = GateSec + "17"
        else:
            Gate = "B43" if Schengen == "Schengen" else "C63"
            GateSec = "B" if Schengen == "Schengen" else "C"

    Pax = row["Better Forecast Pax Published"]
    Bag = min(row["Bag Factor Forecast"], 1.0)
    PaxCheckin = Pax * Bag
    Periode = "AM" if STD.hour < 12 else "PM"
    GateZoneDCB, GateZoneSUP = trouve_gate_zone(Gate,Gates_zone,gates_unique_zones)

    if Schengen == "Non Schengen":
        if GateSec == "B":
            DouaneZoneDCB, DouaneZoneSUP = "Douane : Trompette", "Trompette"
        elif GateSec == "C":
            DouaneZoneDCB, DouaneZoneSUP = "Douane : Aile est départ", "Aile est départ"
        elif GateSec == "D":
            DouaneZoneDCB, DouaneZoneSUP = "Douane : Satellite 10", "Satellite 10"
        else:
            DouaneZoneDCB, DouaneZoneSUP = None, None
    else:
        DouaneZoneDCB, DouaneZoneSUP = None, None

    SureteZoneDCB = "Sûreté : TERMINAL 2" if CheckinZoneSUP == "T2" else "Sûreté : France" if CheckinZoneSUP == "109-120" else "Sûreté : International"

    mask_checkin = (PlanningCheckin["Date et heure"] >= STD - ouverture_checkin) & \
                   (PlanningCheckin["Date et heure"] <= STD - fermeture_checkin) & \
                   (PlanningCheckin[CheckinZoneDCB] < NbCheckin)
    PlanningCheckin.loc[mask_checkin, CheckinZoneDCB] = NbCheckin

    if CheckinZoneSUP == "T2":
        SupCheckin = SUPT2checkin
        flci = 32
    else:
        SupCheckin, flci = find_SUP(Airline, STD.dayofweek, Periode, Schengen, CheckinZoneSUP, "ci", proc_map)

    for _, sup_row in SupCheckin.iterrows():
        DCB_forecast.at[STD - pd.Timedelta(minutes=sup_row["Minutes"]), CheckinZoneDCB] += sup_row["Pourcentage"] * PaxCheckin

    if CheckinZoneSUP == "T2":
        SupSurete = SUPT2surete
        fls = 32
    else:
        SupSurete, fls = find_SUP(Airline, STD.dayofweek, Periode, Schengen, "All", "s", proc_map)

    for _, sup_row in SupSurete.iterrows():
        DCB_forecast.at[STD - pd.Timedelta(minutes=sup_row["Minutes"]), SureteZoneDCB] += sup_row["Pourcentage"] * Pax

    if DouaneZoneDCB:
        SupDouane, fld = find_SUP(Airline, STD.dayofweek, Periode, Schengen, DouaneZoneSUP, "d", proc_map)
        for _, sup_row in SupDouane.iterrows():
            DCB_forecast.at[STD - pd.Timedelta(minutes=sup_row["Minutes"]), DouaneZoneDCB] += sup_row["Pourcentage"] * Pax
    else:
        fld = -1

    SupGate, flg = find_SUP(Airline, STD.dayofweek, Periode, Schengen, GateZoneSUP, "g", proc_map)
    for _, sup_row in SupGate.iterrows():
        if GateZoneDCB in DCB_forecast.columns:
            DCB_forecast.at[STD - pd.Timedelta(minutes=sup_row["Minutes"]), GateZoneDCB] += sup_row["Pourcentage"] * Pax
        else:
            # Optionnel : vous pouvez ajouter un print ici pour être averti si d'autres valeurs inattendues apparaissent
            pass        

    return [flci, fls, fld, flg]

def ApplicationSUP():
    # Timer
    start_time = time()

    # Constantes
    ouverture_checkin = pd.Timedelta(hours=3)
    fermeture_checkin = pd.Timedelta(minutes=15)
    semaine = {"lundi":0, "mardi":1, "mercredi":2, "jeudi":3, "vendredi":4, "samedi":5, "dimanche":6}

    # Dossiers
    os.chdir("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data")

    # Chargement des données
    SUPs = pd.read_excel("Input/Autre/Show Up Profiles - 2023 2024 - Departure PAX.xlsx")
    SUPs.columns = ["Zone","UID","Jour","Airline IATA","Période","Schengen","Minutes","Pourcentage"]
    zone = load_data("ZoneSUP")
    airline = load_data("AirlineSUP")

    SUPs["Airline IATA"] = SUPs["Airline IATA"].map(airline)
    SUPs["Zone"] = SUPs["Zone"].map(zone)
    SUPs["Jour"] = SUPs["Jour"].map(semaine)
    SUPs["UID"] = SUPs["Zone"] + "-" + SUPs["UID"]
    SUPs["Minutes"] = SUPs["Minutes"].apply(lambda x: x.hour*60 + x.minute)
    SUPs = SUPs[-SUPs["Zone"].isna()]

    # Séparation par procédure
    SUPs_CSC = SUPs[SUPs["Zone"].str.startswith("Sûreté")].copy()
    SUPs_CI = SUPs[SUPs["Zone"].str.startswith("Check-in")].copy()
    SUPs_PAF = SUPs[SUPs["Zone"].str.startswith("Douane")].copy()
    SUPs_G = SUPs[SUPs["Zone"].str.startswith("Gate")].copy()

    SUPs_G["Zone"] = SUPs_G["Zone"].str.split(" : ").str[1]
    SUPs_CI["Zone"] = SUPs_CI["Zone"].str.split(" : ").str[1]
    SUPs_PAF["Zone"] = SUPs_PAF["Zone"].str.split(" : ").str[1]
    SUPs_CSC["Zone"] = "All"
    
    SUPT2surete = pd.read_csv("Input/Autre/Show up profile rules in T2.csv")
    SUPT2checkin = SUPT2surete.copy()
    SUPT2checkin["Minutes"] += 20

    # Chargement vols
    vols = pd.read_csv("Input/WEBI/DCB_BSH_Landside.csv")
    vols["Date"] = pd.to_datetime(vols["Date"])
    vols["Local Schedule Time"] = pd.to_datetime(vols["Local Schedule Time"])
    vols["Better Forecast Pax Published"] = vols["Better Forecast Pax Published"].fillna(0)
    vols["Bag Factor Forecast"] = vols["Bag Factor Forecast"].fillna("0,5").str.replace(",", ".").astype(float)
    vols = vols.replace("ND","TBN")
    vols["Checkin sector OOP+"] = vols["Checkin sector OOP+"].str.replace(".","")
    debut = vols["Date"].min()
    fin = vols["Date"].max() + pd.Timedelta(hours=23, minutes=55)


    Gates_zone = load_data("GateZone")
    Checkin_zone = vols["Checkin sector OOP+"].drop_duplicates().tolist()
    Sûreté_zone = ["International", "France", "TERMINAL 2"]
    Douane_zone = ["Aile est départ", "Satellite 10", "Trompette"]

    DCB_cols = ["Check-in : " + ci for ci in Checkin_zone] + ["Sûreté : " + s for s in Sûreté_zone] + ["Douane : " + d for d in Douane_zone] + ["Gate : " + g for g in Gates_zone.values()]
    DCB_forecast = pd.DataFrame(0, index=pd.date_range(start=debut, end=fin, freq='5min'), columns=DCB_cols, dtype=float)
    DCB_forecast.index.name = "Date et heure"

    PlanningCheckin = pd.DataFrame({"Date et heure": pd.date_range(start=debut, end=fin, freq='5min')})
    for ci in Checkin_zone:
        PlanningCheckin["Check-in : " + ci] = 0

    # Cache unique zones pour optimisations
    gates_unique_zones = SUPs_G["Zone"].drop_duplicates().tolist()

    proc_map = {"ci": SUPs_CI, "s": SUPs_CSC, "d": SUPs_PAF, "g": SUPs_G}

    # Remplacer apply par une boucle
    fallbacks = []
    for _, row in tqdm(vols.iterrows(), total=len(vols), desc="Projection des vols"):
        result = projette_SUPs_sur_vol(row,Gates_zone,gates_unique_zones,proc_map,ouverture_checkin,fermeture_checkin,DCB_forecast,PlanningCheckin, SUPT2surete, SUPT2checkin)
        fallbacks.append(result)

    fallbacks_df = pd.DataFrame(fallbacks, columns=["Fallback level check-in", "Fallback level sûreté", "Fallback level douane", "Fallback level gate"])
    vols = pd.concat([vols.reset_index(drop=True), fallbacks_df], axis=1)

    for col in DCB_cols:
        if DCB_forecast[col].sum() == 0:
            DCB_forecast = DCB_forecast.drop(columns = col)
    # Export
    vols.to_csv("Output/Fallback.csv", index=False)
    DCB_forecast.to_csv("Output/DCB_output.csv")
    PlanningCheckin.to_csv("Output/PlanningCheckin.csv", index=False)

    print(f"Temps d'exécution : {(time() - start_time)/60:.2f} minutes")

    return DCB_forecast.reset_index(), PlanningCheckin
