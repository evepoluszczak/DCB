post_ops = False # True pour voir des prévisions faites dans le passé, NE PAS TOUCHER
import sys

dossier_python = ""
for dossier in sys.path:
    if dossier[-15:] =="Python-Portable":
        dossier_python = dossier
if dossier != "":
    sys.path.append(dossier_python + "\\Lib\\site-packages")

import dash
from dash import html, dcc, Input, Output, State, MATCH, ALL, callback_context, ctx
import calendar
import datetime
import threading
import webbrowser
import json
import os
import plotly.graph_objs as go
import re
from math import ceil
#import subprocess
#import time
#import tempfile
#import psutil
from dash import ClientsideFunction
import copy

# Configuration

def get_base_path():
    if getattr(sys, 'frozen', False):  # Exécutable PyInstaller
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

ASSETS_FOLDER = os.path.join(get_base_path(), 'assets')

if post_ops:
    DATA_FOLDER = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source PostOps"
else:
    DATA_FOLDER = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source"

# French months
FRENCH_MONTHS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

FRENCH_JOURS = ["","lundis","mardis","mercredis","jeudis","vendredis","samedis","dimanches"]

def jours(weekday):
    j = weekday.replace(".","")
    nb_j = len(j)
    jstr = ""
    for i in range(nb_j):
        jstr += FRENCH_JOURS[int(j[i])]
        if i == nb_j-2:
            jstr += " et "
        elif i < nb_j-2:
            jstr += ", "
    return jstr

# Initialize Dash app
app = dash.Dash(__name__, assets_folder=ASSETS_FOLDER)
app.config.suppress_callback_exceptions = True
app.title = "Outil DCB - Demand Capacity Balancing"

# Extract start and end dates from the filename
def extract_dates_from_filename(filename):
    dates = re.findall("[0-9]+", filename)
    date_list = []
    for date in dates:
        if len(date) == 8:
            date_list.append(datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8])))
    if len(date_list) != 2:
        raise ValueError(f"Erreur: Impossible d'extraire deux dates du fichier {filename}. Vérifiez le nom du fichier.")
    return date_list

# Read JSON file and parse data
def load_data(name, sous_dossier):
    # Parcourir les fichiers du dossier Actuel
    dossier = os.path.join(DATA_FOLDER,sous_dossier,"Actuel")
    for fichier in os.listdir(dossier):
        if name in fichier:
            file_name = fichier
            break
    if sous_dossier in ["Capacite/Aeroport", "LevelOfService", "Capacite/TempsProcess", "Annexe"]:
        dates = 0
    else:
        dates = extract_dates_from_filename(file_name)
    with open(os.path.join(dossier,file_name), 'r', encoding='utf-8') as file:
        return json.load(file), dates

graph_names, _ = load_data("GraphNames","Annexe")
gate_secteurs = ["A","B","C","D","E/F"]
graph_names["Gate"] += ["Gate : " + secteur for secteur in gate_secteurs]
graph_names["Check-in"].sort()
graph_names_list = [val for value in graph_names.values() for val in value] 

TEMPS_PROCESS, _ = load_data("TempsProcess", "Capacite/TempsProcess")
process_present = list(TEMPS_PROCESS.keys())
for process in graph_names["Check-in"] + graph_names["Sûreté"] + graph_names["Douane"]:
    if process not in process_present:
        TEMPS_PROCESS[process] = TEMPS_PROCESS[process.split(" : ")[0]]

max_planning, _ = load_data("MaxPlanning", "Capacite/Aeroport")
max_plan_ci = max_planning["Check-in"]
for zone in graph_names["Check-in"]:
    max_planning[zone] = max_plan_ci

LOSduree, _ = load_data("ValeursCritiquesDuree","LevelOfService")
LOSsurface, _ = load_data("ValeursCritiquesSurface","LevelOfService")
SurfaceQueue, _ = load_data("CapaciteQueue", "Capacite/Aeroport")
PISTE_THRESHOLDS, _ = load_data("CapacitePiste", "Capacite/Aeroport")
GATE_THRESHOLDS, _ = load_data("CapaciteGate", "Capacite/Aeroport")
stand_ouv, _ = load_data("StandDispo", "Capacite/Aeroport")
standTot = sum(stand_ouv.values()) + stand_ouv["Dv"] + stand_ouv["Ev"]
standC = stand_ouv["Cf"] + 2*stand_ouv["Dv"] + 2*stand_ouv["Ev"]
standD = stand_ouv["Df"] + stand_ouv["Dv"]
standE = stand_ouv["Ef"] + stand_ouv["Ev"]
STAND_THRESHOLDS = {"Stand" : [standTot*0.6,standTot], "Stand : C" : [standC*0.6,standC], "Stand : D" : [standD*0.8,standD], "Stand : E" : [standE*0.6,standE]}
SURETE_THRESHOLDS = {processeur : LOSduree["Sûreté"] for processeur in graph_names["Sûreté"]}
CHECKIN_THRESHOLDS = {processeur : LOSduree["Check-in"] for processeur in graph_names["Check-in"]}
DOUANE_THRESHOLDS = {processeur : LOSduree["Douane"] for processeur in graph_names["Douane"]}

Thresholds = {}
Thresholds.update(PISTE_THRESHOLDS)
Thresholds.update(STAND_THRESHOLDS)
Thresholds.update(SURETE_THRESHOLDS)
Thresholds.update(CHECKIN_THRESHOLDS)
Thresholds.update(DOUANE_THRESHOLDS)
Thresholds.update(GATE_THRESHOLDS)

Thresholds_perso = copy.deepcopy(Thresholds)

data_stand_forecast, dates_in_filename_stand_forecast = load_data("ForecastStandUtilisation","Demande")
data_stand_schedule, dates_in_filename_stand_schedule = load_data("ScheduleStandUtilisation","Demande")
data_piste_forecast, dates_in_filename_piste_forecast = load_data("ForecastPisteUtilisation","Demande")
data_piste_schedule, dates_in_filename_piste_schedule = load_data("SchedulePisteUtilisation","Demande")
data_surete, dates_in_filename_surete = load_data("SUPForecastSurete","Demande")
planning_surete_reel, dates_in_filename_planning_surete_reel = load_data("PlanningSurete","Capacite/Planning")
planning_surete_ideal, dates_in_filename_planning_surete_ideal = load_data("PlanningSureteIdeal","Capacite/Planning")
data_checkin, dates_in_filename_checkin = load_data("SUPForecastCheckIn","Demande")
planning_checkin_reel, dates_in_filename_planning_checkin = load_data("PlanningCheckIn","Capacite/Planning")
data_douane, dates_in_filename_douane = load_data("SUPForecastDouane","Demande")
planning_douane_reel, dates_in_filename_planning_douane_reel = load_data("PlanningDouane","Capacite/Planning")
planning_douane_ideal, dates_in_filename_planning_douane_ideal = load_data("PlanningDouaneIdeal","Capacite/Planning")
data_gate, dates_in_filename_gate = load_data("SUPForecastGate","Demande")
embarquement_gate_forecast, dates_in_filename_embarquement_gate_forecast = load_data("ForecastGateEmbarquement","Demande")
embarquement_gate_schedule, dates_in_filename_embarquement_gate_schedule = load_data("ScheduleGateEmbarquement","Demande")

planning_checkin_ideal = copy.deepcopy(planning_checkin_reel)
planning_checkin_perso = copy.deepcopy(planning_checkin_reel)
planning_surete_perso = copy.deepcopy(planning_surete_ideal)
planning_douane_perso = copy.deepcopy(planning_douane_ideal)

if dates_in_filename_stand_forecast != dates_in_filename_stand_schedule:
    print("Attention, pas les mêmes dates pour le shceule stand que les prévisions stand!")
if dates_in_filename_stand_forecast != dates_in_filename_piste_forecast:
    print("Attention, pas les mêmes dates pour les prévisions piste que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_piste_schedule:
    print("Attention, pas les mêmes dates pour les schedule piste que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_surete:
    print("Attention, pas les mêmes dates pour les prévisions sûreté que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_planning_surete_reel:
    print("Attention, pas les mêmes dates pour le planning sûreté que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_planning_surete_reel:
    print("Attention, pas les mêmes dates pour le planning sûreté idéal que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_checkin:
    print("Attention, pas les mêmes dates pour les prévisions check-in que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_planning_checkin:
    print("Attention, pas les mêmes dates pour le planning check-in que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_douane:
    print("Attention, pas les mêmes dates pour les prévisions douane que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_planning_douane_reel:
    print("Attention, pas les mêmes dates pour le planning douane que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_planning_douane_ideal:
    print("Attention, pas les mêmes dates pour le planning douane idéal que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_gate:
    print("Attention, pas les mêmes dates pour les prévisions gate que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_embarquement_gate_forecast:
    print("Attention, pas les mêmes dates pour l'embarquement au gate forecasté que stand!")
if dates_in_filename_stand_forecast != dates_in_filename_embarquement_gate_schedule:
    print("Attention, pas les mêmes dates pour l'embarquement au gate schedule que stand!")


start_date = dates_in_filename_surete[0]
end_date = dates_in_filename_surete[1]
start_month_date = datetime.date(start_date.year, start_date.month, 1)

def sum_list(dict_of_list):
    l = len(dict_of_list[list(dict_of_list.keys())[0]])
    s = [0]*l
    for ls in dict_of_list.values():
        if len(ls) != l:
            raise ValueError("Les listes n'ont pas toutes la même longueur!")
        for i in range(l):
            s[i] += ls[i]
    return s

def list_mult(liste, coef):
    res = []
    for i in range(len(liste)):
        res.append(liste[i] * coef)
    return res

def list_sub(liste, base):
    res = []
    for i in range(len(liste)):
        res.append(base-liste[i])
    return res

def calcul_queue(demande,capacite):
    queue = [0]
    for i in range(len(demande)):
        queue.append(max(0,queue[i] + demande[i] - capacite[i]))
    return queue[:-1]

def calcul_attente(queue, capacite):
    attente = []
    for i in range(len(queue)):
        if capacite[i] != 0:
            wait = ceil(queue[i]/capacite[i]*5)
        else:
            wait = 0
        attente.append(wait)
    return attente

def calcul_attente_moyenne(attente):
    l = len(attente)
    temp = [0]*3 + attente + [0]*3
    return [ceil(sum(temp[i-3:i+4])/7) for i in range(3,3+l)]

def calcul_KPI(attente_moyenne,planning,seuil):
    tot = 0
    s80 = 0
    s99 = 0
    for i in range(len(attente_moyenne)):
        if planning[i] != 0:
            tot += 1
            if attente_moyenne[i] <= seuil[0]:
                s80 += 1
            if attente_moyenne[i] <= seuil[1]:
                s99 += 1
    if tot == 0:
        return[1,1]
    return [s80/tot,s99/tot]

def calcul_file_attente(data, planning):
    capacite = {}
    queue = {}
    attente = {}
    attente_moyenne = {}
    KPI = {}
    for date in data_surete.keys():
        capacite[date] = {}
        queue[date] = {}
        attente[date] = {}
        attente_moyenne[date] = {}
        KPI[date] = {}
        for zone in data[date].keys():
            dem = data[date][zone]
            plan = planning[date][zone]
            cap = list_mult(plan,5/TEMPS_PROCESS[zone])
            capacite[date][zone] = cap.copy()
            q = calcul_queue(dem,cap)
            queue[date][zone] = q.copy()
            att = calcul_attente(q,cap)
            attente[date][zone] = att.copy()
            att_moy = calcul_attente_moyenne(att)
            attente_moyenne[date][zone] = att_moy.copy()
            KPI[date][zone] = calcul_KPI(att_moy,plan,Thresholds[zone])
    return capacite, queue, attente, attente_moyenne, KPI

def update_file_attente(processeur, zone, date, heure_debut, minute_debut, heure_fin, minute_fin, nouvelle_valeur = None):
    if processeur == "Check-in":
        dem = data_checkin[date][zone]
        plan = planning_checkin_perso[date][zone]
        for i in range(12*heure_debut+minute_debut//5, 12*heure_fin+minute_fin//5):
            if nouvelle_valeur != None:
                plan[i] = nouvelle_valeur
            else:
                plan[i] = planning_checkin_ideal[date][zone][i]
        cap = list_mult(plan.copy(),5/TEMPS_PROCESS[zone])
        capacite_checkin_perso[date][zone] = cap.copy()
        q = calcul_queue(dem,cap)
        queue_checkin_perso[date][zone] = q.copy()
        att = calcul_attente(q,cap)
        attente_checkin_perso[date][zone] = att.copy()
        att_moy = calcul_attente_moyenne(att)
        attente_moyenne_checkin_perso[date][zone] = att_moy.copy()
        KPI_checkin_perso[date][zone] = calcul_KPI(att_moy,plan.copy(),Thresholds_perso[zone])
    elif processeur == "Sûreté":
        dem = data_surete[date][zone]
        plan = planning_surete_perso[date][zone]
        for i in range(12*heure_debut+minute_debut//5, 12*heure_fin+minute_fin//5):
            if nouvelle_valeur != None:
                plan[i] = nouvelle_valeur
            else:
                plan[i] = planning_surete_ideal[date][zone][i]
        cap = list_mult(plan.copy(),5/TEMPS_PROCESS[zone])
        capacite_surete_perso[date][zone] = cap.copy()
        q = calcul_queue(dem,cap)
        queue_surete_perso[date][zone] = q.copy()
        att = calcul_attente(q,cap)
        attente_surete_perso[date][zone] = att.copy()
        att_moy = calcul_attente_moyenne(att)
        attente_moyenne_surete_perso[date][zone] = att_moy.copy()
        KPI_surete_perso[date][zone] = calcul_KPI(att_moy,plan.copy(),Thresholds_perso[zone])
    elif processeur == "Douane":
        dem = data_douane[date][zone]
        plan = planning_douane_perso[date][zone]
        for i in range(12*heure_debut+minute_debut//5, 12*heure_fin+minute_fin//5):
            if nouvelle_valeur != None:
                plan[i] = nouvelle_valeur
            else:
                plan[i] = planning_douane_ideal[date][zone][i]
        cap = list_mult(plan.copy(),5/TEMPS_PROCESS[zone])
        capacite_douane_perso[date][zone] = cap.copy()
        q = calcul_queue(dem,cap)
        queue_douane_perso[date][zone] = q.copy()
        att = calcul_attente(q,cap)
        attente_douane_perso[date][zone] = att.copy()
        att_moy = calcul_attente_moyenne(att)
        attente_moyenne_douane_perso[date][zone] = att_moy.copy()
        KPI_douane_perso[date][zone] = calcul_KPI(att_moy,plan.copy(),Thresholds_perso[zone])
    else:
        print("Processeur invalide")

capacite_surete_reel, queue_surete_reel, attente_surete_reel, attente_moyenne_surete_reel, KPI_surete_reel = calcul_file_attente(data_surete, planning_surete_reel)
capacite_surete_ideal, queue_surete_ideal, attente_surete_ideal, attente_moyenne_surete_ideal, KPI_surete_ideal = calcul_file_attente(data_surete, planning_surete_ideal)
capacite_surete_perso, queue_surete_perso, attente_surete_perso, attente_moyenne_surete_perso, KPI_surete_perso = copy.deepcopy(capacite_surete_ideal), copy.deepcopy(queue_surete_ideal), copy.deepcopy(attente_surete_ideal), copy.deepcopy(attente_moyenne_surete_ideal), copy.deepcopy(KPI_surete_ideal)
capacite_checkin_reel, queue_checkin_reel, attente_checkin_reel, attente_moyenne_checkin_reel, KPI_checkin_reel = calcul_file_attente(data_checkin, planning_checkin_reel)
capacite_checkin_ideal, queue_checkin_ideal, attente_checkin_ideal, attente_moyenne_checkin_ideal, KPI_checkin_ideal = copy.deepcopy(capacite_checkin_reel), copy.deepcopy(queue_checkin_reel), copy.deepcopy(attente_checkin_reel), copy.deepcopy(attente_moyenne_checkin_reel), copy.deepcopy(KPI_checkin_reel)
capacite_checkin_perso, queue_checkin_perso, attente_checkin_perso, attente_moyenne_checkin_perso, KPI_checkin_perso = copy.deepcopy(capacite_checkin_reel), copy.deepcopy(queue_checkin_reel), copy.deepcopy(attente_checkin_reel), copy.deepcopy(attente_moyenne_checkin_reel), copy.deepcopy(KPI_checkin_reel)
capacite_douane_reel, queue_douane_reel, attente_douane_reel, attente_moyenne_douane_reel, KPI_douane_reel = calcul_file_attente(data_douane, planning_douane_reel)
capacite_douane_ideal, queue_douane_ideal, attente_douane_ideal, attente_moyenne_douane_ideal, KPI_douane_ideal = calcul_file_attente(data_douane, planning_douane_ideal)
capacite_douane_perso, queue_douane_perso, attente_douane_perso, attente_moyenne_douane_perso, KPI_douane_perso = copy.deepcopy(capacite_douane_ideal), copy.deepcopy(queue_douane_ideal), copy.deepcopy(attente_douane_ideal), copy.deepcopy(attente_moyenne_douane_ideal), copy.deepcopy(KPI_douane_ideal)

occupation_gate_forecast = {}
for date in data_gate.keys():
    occ_jour = {}
    for zone in embarquement_gate_forecast[date].keys():
        occ_zone = [data_gate[date][zone][0]-embarquement_gate_forecast[date][zone][0]]
        for j in range(1,len(embarquement_gate_forecast[date][zone])):
            occ_zone.append(occ_zone[j-1]+data_gate[date][zone][j]-embarquement_gate_forecast[date][zone][j])
        occ_jour[zone] = occ_zone.copy()
    occ_jour["Gate"] = sum_list(occ_jour)
    for secteur in gate_secteurs:
        occ_jour["Gate : " + secteur] = sum_list({k:v for k,v in occ_jour.items() if k != "Gate" and k.split(" : ")[1].startswith(secteur)})
    occupation_gate_forecast[date] = copy.deepcopy(occ_jour)

occupation_gate_schedule = {}
for date in data_gate.keys():
    occ_jour = {}
    for zone in embarquement_gate_schedule[date].keys():
        occ_zone = [data_gate[date][zone][0]-embarquement_gate_schedule[date][zone][0]]
        for j in range(1,len(embarquement_gate_schedule[date][zone])):
            occ_zone.append(occ_zone[j-1]+data_gate[date][zone][j]-embarquement_gate_schedule[date][zone][j])
        occ_jour[zone] = occ_zone.copy()
    occ_jour["Gate"] = sum_list(occ_jour)
    for secteur in gate_secteurs:
        occ_jour["Gate : " + secteur] = sum_list({k:v for k,v in occ_jour.items() if k != "Gate" and k.split(" : ")[1].startswith(secteur)})
    occupation_gate_schedule[date] = copy.deepcopy(occ_jour)

for date in data_stand_forecast.keys():
    data_stand_forecast[date]["Stand"] = sum_list(data_stand_forecast[date])

for date in data_stand_schedule.keys():
    data_stand_schedule[date]["Stand"] = sum_list(data_stand_schedule[date])

for date in data_piste_forecast.keys():
    data_piste_forecast[date]["Piste"] = sum_list(data_piste_forecast[date])

for date in data_piste_schedule.keys():
    data_piste_schedule[date]["Piste"] = sum_list(data_piste_schedule[date])

for date in data_surete.keys():
    data_surete[date]["Sûreté"] = sum_list(data_surete[date])

for date in data_checkin.keys():
    data_checkin[date]["Check-in"] = sum_list(data_checkin[date])

for date in data_douane.keys():
    data_douane[date]["Douane"] = sum_list(data_douane[date])

stand_libre_forecast = {}
stand_libre_schedule = {}
for date in data_stand_forecast.keys():
    stand_libre_forecast[date] = {}
    stand_libre_schedule[date] = {}
    for zone in data_stand_forecast[date].keys():
        stand_libre_forecast[date][zone] = list_sub(data_stand_forecast[date][zone],STAND_THRESHOLDS[zone][1])
        stand_libre_schedule[date][zone] = list_sub(data_stand_schedule[date][zone],STAND_THRESHOLDS[zone][1])

def value_to_color(value, var, toggle_rip):
    Thres = Thresholds_perso if toggle_rip == "perso" else Thresholds
    if var in Thres.keys():
        if value <= Thres[var][0]:
            return "lightgrey"
        elif value <= Thres[var][1]:
            return "orange"
        return "red"
    return "lightblue"

def KPI_to_color(KPIs):
    c80 = (KPIs[0] < 0.8) + (KPIs[0] < 0.89)
    c99 = (KPIs[1] < 0.96) + (KPIs[1] < 0.98)
    cv = max(c80,c99)
    if cv == 2:
        return "red"
    if cv == 1:
        return "orange"
    if cv == 0:
        return "lightgrey"
    return "lightblue"

def worst_color(day_col,graphs="Liste"):
    if graphs == "Liste":
        cols = day_col
    else:
        selected_processor = copy.deepcopy(graphs)
        for zone in graph_names.keys():
            all = True
            for processeur in graph_names[zone]:
                if processeur not in graphs:
                    all = False
            if all:
                selected_processor.append(zone)
        cols = [value for key, value in day_col.items() if key in selected_processor]
    if "red" in cols:
        return "red"
    elif "orange" in cols:
        return "orange"
    elif "lightgrey" in cols:
        return "lightgrey"
    return "lightblue"

def comp_color(a,b):
    if a>b:
        return "orange"
    return "lightgrey"

def compute_colors(sx="forecast",rip="reel"):
    colors = {}
    stand_data     = data_stand_forecast if sx == "forecast" else data_stand_schedule
    piste_data     = data_piste_forecast if sx == "forecast" else data_piste_schedule
    gate_occup     = occupation_gate_forecast if sx == "forecast" else occupation_gate_schedule
    if rip == "reel":
        KPI_surete = KPI_surete_reel
        queue_surete = queue_surete_reel
        KPI_douane = KPI_douane_reel
        queue_douane = queue_douane_reel
        KPI_checkin = KPI_checkin_reel
        queue_checkin = queue_checkin_reel
        planning_checkin=  planning_checkin_reel
    elif rip == "ideal":
        KPI_surete = KPI_surete_ideal
        queue_surete = queue_surete_ideal
        KPI_douane = KPI_douane_ideal
        queue_douane = queue_douane_ideal
        KPI_checkin = KPI_checkin_ideal
        queue_checkin = queue_checkin_ideal
        planning_checkin=  planning_checkin_ideal
    elif rip == "perso":
        KPI_surete = KPI_surete_perso
        queue_surete = queue_surete_perso
        KPI_douane = KPI_douane_perso
        queue_douane = queue_douane_perso
        KPI_checkin = KPI_checkin_perso
        queue_checkin = queue_checkin_perso
        planning_checkin=  planning_checkin_perso

    for date in data_surete.keys():
        day_col = {}
        
        # STAND
        lcol = []
        for zone in graph_names["Stand"]:
            col = value_to_color(max(stand_data[date][zone][84:264]), zone, rip)
            day_col[zone] = col
            lcol.append(col)
        lcol.append(value_to_color(max(stand_data[date]["Stand"][84:264]), "Stand", rip))
        day_col["Stand"] = worst_color(lcol)

        # PISTE
        lcol = []
        for zone in graph_names["Piste"]:
            col = value_to_color(max(piste_data[date][zone][::12]), zone, rip)
            day_col[zone] = col
            lcol.append(col)
        lcol.append(value_to_color(max(piste_data[date]["Piste"][::12]), "Piste", rip))
        day_col["Piste"] = worst_color(lcol)

        # SÛRETÉ
        for zone in graph_names["Sûreté"]:
            day_col[zone] = worst_color([
                KPI_to_color(KPI_surete[date][zone]),
                comp_color(max(queue_surete[date][zone]) * LOSsurface["Sûreté"], SurfaceQueue[zone])
            ])
        day_col["Sûreté"] = worst_color(day_col, copy.deepcopy(graph_names["Sûreté"]))

        # CHECK-IN
        for zone in graph_names["Check-in"]:
            day_col[zone] = worst_color([
                KPI_to_color(KPI_checkin[date][zone]),
                comp_color(max(queue_checkin[date][zone]) * LOSsurface["Check-in"],
                           SurfaceQueue["Check-in"] * max(planning_checkin[date][zone]))
            ])
        day_col["Check-in"] = worst_color(day_col, copy.deepcopy(graph_names["Check-in"]))

        # DOUANE
        for zone in graph_names["Douane"]:
            day_col[zone] = worst_color([
                KPI_to_color(KPI_douane[date][zone]),
                comp_color(max(queue_douane[date][zone]) * LOSsurface["Douane"], SurfaceQueue[zone])
            ])
        day_col["Douane"] = worst_color(day_col, copy.deepcopy(graph_names["Douane"]))

        # GATE
        for zone in graph_names["Gate"]:
            day_col[zone] = value_to_color(max(gate_occup[date][zone]), zone, rip)
        day_col["Gate"] = worst_color(day_col, copy.deepcopy(graph_names["Gate"]))

        colors[date] = day_col

    return colors

# Calendar generation
def generate_calendar(graphs, colors):
    calendar_content = []
    current = start_month_date

    french_weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    while current <= end_date:
        year = current.year
        month = current.month
        cal = calendar.Calendar(firstweekday=0)
        days = list(cal.itermonthdates(year, month))

        month_box = html.Div([
            html.H3(f"{FRENCH_MONTHS[month - 1].capitalize()} {year}",
                    style={"textAlign": "center", "marginBottom": "10px", "fontSize": "16px"}),

            html.Div([
                html.Div(
                    french_day,
                    style={
                        "width": "100%",
                        "height": "30px",
                        "lineHeight": "30px",
                        "textAlign": "center",
                        "border": "1px solid #ccc",
                        "fontWeight": "bold",
                        "backgroundColor": "#f0f0f0",
                        "fontSize": "11px",
                        "boxSizing": "border-box"
                    }
                ) for french_day in french_weekdays
            ], style={"display": "grid", "gridTemplateColumns": "repeat(7, minmax(70px, 1fr))", "width": "100%"}),

            html.Div([
                html.Button(
                    str(day.day),
                    n_clicks=0,
                    disabled=not (day.month == month and start_date <= day <= end_date),
                    style={
                        "border": "1px solid #ccc",
                        "width": "100%",
                        "aspectRatio": "3 / 2",
                        "padding": "4px",
                        "textAlign": "left",
                        "verticalAlign": "top",
                        "backgroundColor": (
                            worst_color(colors[str(day)],graphs)
                            if (day.month == month and start_date <= day <= end_date) else "#eee"
                        ),
                        "color": "#000" if day.month == month else "#aaa",
                        "fontSize": "11px",
                        "boxSizing": "border-box",
                        "borderRadius": "0",
                        "cursor": "pointer" if (day.month == month and start_date <= day <= end_date) else "default",
                        "opacity": "1" if (day.month == month and start_date <= day <= end_date) else "0.5",
                    },
                    **({"id": {'type': 'calendar-day', 'date': day.isoformat()}} 
                       if (day.month == month and start_date <= day <= end_date) else {})
                ) for day in days
            ], style={"display": "grid", "gridTemplateColumns": "repeat(7, minmax(70px, 1fr))", "width": "100%"})
        ],  className="month-box",   # on passe sur une classe CSS
            style={
        "margin": "20px",
        "boxSizing": "border-box"
        })

        calendar_content.append(month_box)

        # Next month
        if month == 12:
            current = datetime.date(year + 1, 1, 1)
        else:
            current = datetime.date(year, month + 1, 1)

    return calendar_content

# Graph generation
def generate_graph(values,xname,yname,shapes):
    times = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0,60,5)]
    tickvals = times[::6]
        
    return dcc.Graph(
        figure=go.Figure(
            data=go.Scatter(x=times, y=values, mode='lines', line=dict(color='royalblue', width=2)),
            layout=go.Layout(
                margin=dict(l=30, r=30, t=40, b=30),
                xaxis=dict(title=xname, showgrid=True, gridcolor='#eee', tickangle=45,tickmode="array", tickvals=tickvals, ticktext=tickvals),
                yaxis=dict(title=yname, showgrid=True, gridcolor='#eee'),
                plot_bgcolor='#fafafa',
                paper_bgcolor='#fafafa',
                height=250,
                shapes=shapes
            )
        ),
        config={"displayModeBar": False}
    )

def generate_graph_multiple(values1, values2, xname, yname, shapes, label1, label2):
    times = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0,60,5)]
    tickvals = times[::6]

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=times,
                    y=values1,
                    mode='lines',
                    name=label1,
                    line=dict(color='royalblue', width=2)
                ),
                go.Scatter(
                    x=times,
                    y=values2,
                    mode='lines',
                    name=label2,
                    line=dict(color='green', width=2)
                )
            ],
            layout=go.Layout(
                margin=dict(l=30, r=30, t=40, b=30),
                xaxis=dict(
                    title=xname,
                    showgrid=True,
                    gridcolor='#eee',
                    tickangle=45,
                    tickmode="array",
                    tickvals=tickvals,
                    ticktext=tickvals
                ),
                yaxis=dict(
                    title=yname,
                    showgrid=True,
                    gridcolor='#eee'
                ),
                plot_bgcolor='#fafafa',
                paper_bgcolor='#fafafa',
                height=250,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.15,
                    xanchor="right",
                    x=1
                ),
                shapes=shapes
            )
        ),
        config={"displayModeBar": False}
    )

def generate_thresholds(title, toggle_rip):
    shapes = []
    thresholds = Thresholds_perso[title] if toggle_rip == "perso" else Thresholds[title]
    shapes.append(dict(
        type="line",
        x0="00:00",
        x1="23:55",
        y0=thresholds[0],
        y1=thresholds[0],
        line=dict(color="orange", width=1, dash="dash")
    ))
    shapes.append(dict(
        type="line",
        x0="00:00",
        x1="23:55",
        y0=thresholds[1],
        y1=thresholds[1],
        line=dict(color="red", width=1, dash="dash")
    ))
    return shapes

def generate_threshold(threshold):
    shapes = []
    shapes.append(dict(
        type="line",
        x0="00:00",
        x1="23:55",
        y0=threshold,
        y1=threshold,
        line=dict(color="orange", width=1, dash="dash")
    ))
    return shapes

def generate_kpi_boxes(main, selected_date, title, toggle_rip):
    if main == "Sûreté":
        KPIs = (KPI_surete_reel if toggle_rip == "reel" else KPI_surete_ideal if toggle_rip == "ideal" else KPI_surete_perso)[selected_date][title]
    elif main == "Check-in":
        KPIs = (KPI_checkin_reel if toggle_rip == "reel" else KPI_checkin_ideal if toggle_rip == "ideal" else KPI_checkin_perso)[selected_date][title]
    elif main == "Douane":
        KPIs = (KPI_douane_reel if toggle_rip == "reel" else KPI_douane_ideal if toggle_rip == "ideal" else KPI_douane_perso)[selected_date][title]
    else:
        return None

    seuils = Thresholds_perso[title] if toggle_rip == "perso" else Thresholds[title] 
    texts = [f"% du temps où l'attente est en dessous de {seuils[i]} min" for i in range(2)]
    colors = [KPI_to_color([KPIs[0], 1]),KPI_to_color([1, KPIs[1]])]
    colors = ["green" if color == "lightgrey" else color for color in colors]
    percentages = [f"{int(k * 100)}%" for k in KPIs]

    return html.Div([
        html.Div([
            html.Div(texts[i], style={"fontSize": "14px", "marginBottom": "4px"}),
            html.Div(percentages[i], style={"fontSize": "22px", "fontWeight": "bold"})
        ], style={
            "padding": "12px",
            "marginRight": "10px" if i == 0 else "0px",
            "backgroundColor": colors[i],
            "color": "white",
            "borderRadius": "8px",
            "minWidth": "160px",
            "textAlign": "center"
        }) for i in range(2)
    ], style={"display": "flex", "gap": "12px", "marginBottom": "25px"})

# Layouts
app.layout = html.Div([
    dcc.Store(id="selected-date", data=None),
    dcc.Store(id="selected-layout", data="calendar"),
    dcc.Store(id="selected-graph-section", data=None),
    dcc.Store(id="selected-main", data=None),
    dcc.Store(id="selected-sub", data=None),
    dcc.Store(id='selected-graphs', data=graph_names_list),
    dcc.Store(id='expanded-categories', data=[]),
    dcc.Store(id='show-categories', data=False),
    dcc.Store(id="info-visible", data=False),
    dcc.Store(id="toggle-value", data="forecast"),
    dcc.Store(id="colors", data=compute_colors("forecast")),
    dcc.Store(id="toggle-rip", data="ideal"),
    dcc.Store(id="historique-messages", data=[]),
    html.Div([  # Entête
        html.Img(src="/assets/geneva_airport_logo.png", style={"height": "60px", "marginRight": "20px"}),
        html.H2("Outil DCB - Demand Capacity Balancing", style={"flex": "1", "textAlign": "center", "margin": "0", "fontSize": "28px"}),
        html.Div("Version 1.0", style={"fontSize": "18px", "alignSelf": "center", "marginLeft": "20px"})
    ], style={
        "position": "sticky", "top": "0", "zIndex": "999",
        "backgroundColor": "#f5f5f5",
        "padding": "10px 20px",
        "borderBottom": "2px solid #ccc",
        "display": "flex",
        "alignItems": "center"
    }),
    html.Div([
        html.Div([
            html.Button("+", id='expand-all-categories', n_clicks=0),
            html.Button("Tout", id='select-all', n_clicks=0, style={'margin-right': '5px'}),
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),

        html.Div(id='category-list')
    ], style={'width': '250px', 'display': 'flex', 'flexDirection': 'column'}),
    
    html.Div([
        html.Label("Heure de départ/arrivée :", style={"marginRight": "10px"}),
        dcc.RadioItems(
            id="data-toggle",
            options=[
                {"label": "Expected", "value": "forecast"},
                {"label": "Schedule", "value": "schedule"}
            ],
            value="forecast",
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        )
    ], style={"marginBottom": "20px"}),
    
    html.Div([
        html.Label("Planning à utiliser :", style={"marginRight": "10px"}),
        dcc.RadioItems(
            id="data-toggle-rip",
            options=[
                {"label": "Réel", "value": "reel"},
                {"label": "Idéal", "value": "ideal"},
                {"label": "Personnalisé", "value": "perso"}
            ],
            value="ideal",
            labelStyle={'display': 'inline-block', 'marginRight': '10px'}
        )
    ], style={"marginBottom": "20px"}),

    html.Button(
        "← Retour au calendrier",
        id="reset-day-clicked",
        n_clicks=0,
        style={
            "marginBottom": "20px",
            "padding": "10px 20px",
            "backgroundColor": "#ddd",
            "border": "none",
            "borderRadius": "5px",
            "cursor": "pointer",
            "fontWeight": "bold"
        }
    ),
    
    html.Button(
        "Personnaliser",
        id="personnaliser",
        n_clicks=0,
        style={
            "marginBottom": "20px",
            "padding": "10px 20px",
            "backgroundColor": "#ddd",
            "border": "none",
            "borderRadius": "5px",
            "cursor": "pointer",
            "fontWeight": "bold"
        }
    ),

    html.Div(id="page-content"),
    html.Div(id="dummy-output", style={"display": "none"})
])

def calendar_only_layout(graphs,colors):
    return html.Div([
        html.Div(
            generate_calendar(graphs,colors),
            className="calendar-grid"   # ← on passe sur une classe CSS
        )
    ])

def full_layout(selected_date,graphs,colors):
    if selected_date:
        clicked_datetime = datetime.date.fromisoformat(selected_date)
        title = f"Données Opérationnelles du Jour: {clicked_datetime.day} {FRENCH_MONTHS[clicked_datetime.month - 1]} {clicked_datetime.year}"
    else:
        title = "Données Opérationnelles du Jour"
    return html.Div([
        html.Div([  # Contenu principal
            html.Div(
                generate_calendar(graphs,colors),
                style={"flex": "0 0 450px", "maxWidth": "500px", "padding": "20px", "fontFamily": "Arial, sans-serif", "boxSizing": "border-box"}
            ),
            html.Div([  # Graphes + Zone
                html.Div([
                    html.Div([
                        html.H3(title, style={"margin": 0, "fontSize": "20px", "flex": "1"}),

                        html.Button("i", id="info-button", n_clicks=0, title="Informations",
                            style={
                                "borderRadius": "50%",
                                "width": "26px",
                                "height": "26px",
                                "textAlign": "center",
                                "lineHeight": "26px",
                                "backgroundColor": "#007BFF",
                                "color": "white",
                                "border": "none",
                                "fontWeight": "bold",
                                "cursor": "pointer",
                                "marginLeft": "10px"
                            })
                    ], style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "marginBottom": "10px"
                    }),

                    # Encapsuler ici l'encart d'infos
                    html.Div(id="info-popup", style={
                        "display": "none",  # sera géré par le callback
                        "position": "absolute",
                        "top": "35px",
                        "right": "0px",
                        "width": "300px",
                        "padding": "10px",
                        "backgroundColor": "#f9f9f9",
                        "border": "1px solid #ccc",
                        "borderRadius": "8px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                        "zIndex": "999"
                    })
                ], style={"position": "relative"}),
                html.Div([
                    html.Div([
                        html.H4("Indicateurs DCB", style={"textAlign": "center"}),

                        html.Div([
                            html.Button(
                                label,
                                id={"type": "main-graph-button", "name": label},  # ID dynamique
                                n_clicks=0,
                                style={
                                    "width": "100%",
                                    "padding": "12px",
                                    "marginBottom": "10px",
                                    "backgroundColor": colors[selected_date][label],
                                    "border": "none",
                                    "color": "#000",
                                    "fontWeight": "bold",
                                    "borderRadius": "5px",
                                    "cursor": "pointer"
                                }
                            ) for label in graph_names
                        ]),
                        html.Div(id="sub-buttons-title", style={"fontWeight": "bold", "marginTop": "20px"}),
                        html.Div(id="sub-buttons")
                    ], style={
                        "flex": "0 0 250px",
                        "maxWidth": "250px",
                        "boxSizing": "border-box"
                    }),
                    html.Div(id="graph-display", style={
                        "flex": "1",
                        "paddingLeft": "20px",
                        "boxSizing": "border-box"
                    })
                ], style={
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "flex-start",
                    "gap": "20px",
                    "width": "100%",
                    "boxSizing": "border-box"
                })
            ], style={"flex": "1", "padding": "40px", "boxSizing": "border-box"})
        ], style={"display": "flex", "flexDirection": "row", "height": "100%"})
    ])

COMMON_STYLE = {"display": "flex", "flexDirection": "column", "marginRight": "20px", "marginBottom": "15px"}

def personnaliser_layout():
    return html.Div([
        html.Div([
            # 1. Choix du processeur
            html.Div([
                html.Label("Choisissez un processeur :", style={"marginBottom": "5px"}),
                dcc.Dropdown(
                    id="dropdown-processeur",
                    options=[{"label": k, "value": k} for k in ["Check-in", "Sûreté", "Douane"]],
                    value="Check-in",
                    style={"width": "150px"}
                )
            ], style=COMMON_STYLE),

            # 2. Choix du sous-élément selon le processeur
            html.Div([
                html.Label("Choisissez une zone :", style={"marginBottom": "5px"}),
                dcc.Dropdown(
                    id="dropdown-zone",
                    value=None,
                    style={"width": "200px"}
                )
            ], style=COMMON_STYLE),

            # 3 & 4. Choix des dates
            html.Div([
                html.Label("Date de début :", style={"marginBottom": "5px"}),
                dcc.DatePickerSingle(
                    id="date-debut",
                    min_date_allowed=start_date,
                    max_date_allowed=end_date,
                    date=start_date,
                    display_format="DD.MM.YYYY",
                    first_day_of_week=1
                )
            ], style=COMMON_STYLE),

            html.Div([
                html.Label("Date de fin :", style={"marginBottom": "5px"}),
                dcc.DatePickerSingle(
                    id="date-fin",
                    min_date_allowed=start_date,
                    max_date_allowed=end_date,
                    date=end_date,
                    display_format="DD.MM.YYYY",
                    first_day_of_week=1
                )
            ], style=COMMON_STYLE),

            # 5 & 6. Heure de début (HH & MM)
            html.Div([
                html.Label("Heure de début :", style={"marginBottom": "5px"}),
                html.Div([
                    dcc.Dropdown(id="heure-debut", options=[{"label": h, "value": h} for h in range(0, 24)], value=0, style={"width": "70px", "display": "inline-block", "marginRight": "10px"}),
                    dcc.Dropdown(id="minute-debut", options=[{"label": m, "value": m} for m in range(0, 60, 5)], value=0, style={"width": "70px", "display": "inline-block"})
                ])
            ], style=COMMON_STYLE),

            # 7 & 8. Heure de fin (HH & MM)
            html.Div([
                html.Label("Heure de fin :", style={"marginBottom": "5px"}),
                html.Div([
                    dcc.Dropdown(id="heure-fin", options=[{"label": h, "value": h} for h in range(0, 24)], value=1, style={"width": "70px", "display": "inline-block", "marginRight": "10px"}),
                    dcc.Dropdown(id="minute-fin", options=[{"label": m, "value": m} for m in range(0, 60, 5)], value=0, style={"width": "70px", "display": "inline-block"})
                ])
            ], style=COMMON_STYLE),

            # 9. Valeur à appliquer (champ texte libre)
            html.Div([
                html.Label("Jours de la semaine (1-7):", style={"marginBottom": "5px"}),
                dcc.Input(id="weekday", type="text", value=".......", style={"width": "120px"})
            ], style=COMMON_STYLE),

            # 10. Max planning (sera rempli dynamiquement)
            html.Div([
                html.Label("Nouvelle valeur :", style={"marginBottom": "5px"}),
                dcc.Dropdown(
                    id="valeur",
                    style={"width": "100px"}
                )
            ], style=COMMON_STYLE)
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginBottom": "30px"}),

        html.Button("Appliquer", id="appliquer-personnalisation", n_clicks=0, style={
            "padding": "12px 24px",
            "fontSize": "16px",
            "fontWeight": "bold",
            "backgroundColor": "#007BFF",
            "color": "white",
            "border": "none",
            "borderRadius": "5px",
            "cursor": "pointer"
        }),

        html.Div(id="message-confirmation", style={"marginTop": "20px", "fontSize": "16px"})
    ])



# Callbacks
@app.callback(
    Output("page-content", "children"),
    Input("selected-layout", "data"),
    Input("selected-graphs", "data"),
    Input("colors","data"),
    State("selected-date", "data")
)
def display_page(selected_layout, graphs, colors, selected_date):
    if selected_layout == "full":
        return full_layout(selected_date,graphs,colors)
    elif selected_layout == "personnaliser":
        return personnaliser_layout()
    else:
        return calendar_only_layout(graphs,colors)

@app.callback(
    Output("selected-layout", "data"),
    Output("selected-date", "data"),
    Input({"type": "calendar-day", "date": ALL}, "n_clicks"),
    Input("reset-day-clicked", "n_clicks"),
    Input("personnaliser", "n_clicks"),
    State({"type": "calendar-day", "date": ALL}, "id")
)
def update_day_clicked(n_clicks_list, reset_clicks, perso_clicks, ids):
    triggered_id = ctx.triggered_id
    # Cas 1 : clic sur bouton retour
    if triggered_id == "reset-day-clicked":
        return "calendar", dash.no_update
    
    if triggered_id == "personnaliser":
        return "personnaliser", dash.no_update

    # Cas 2 : clic sur une date du calendrier
    if isinstance(n_clicks_list, list):
        for i, n in enumerate(n_clicks_list):
            if n:  # si ce jour a été cliqué
                return "full", ids[i]["date"]

    # Sinon, ne rien changer
    return dash.no_update, dash.no_update

@app.callback(
    [Output("selected-main", "data"),
     Output("selected-sub", "data"),
     Output("sub-buttons", "children"),
     Output("sub-buttons-title", "children")],
    [Input({"type": "main-graph-button", "name": ALL}, "n_clicks"),
     Input({"type": "sub-graph-button",  "parent": ALL, "name": ALL}, "n_clicks")],
    [State("colors", "data"),
     State("selected-main", "data"),
     State("selected-sub", "data"),
     State("selected-date", "data")],
    prevent_initial_call=True
)
def update_selection_and_show_sub_buttons(nc_main, nc_sub, colors, prev_main, prev_sub, selected_date):
    ctx = callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    # Récupération du bouton déclencheur
    triggered_prop = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if any(nc_main) or any(nc_sub):
        trigger_id = eval(triggered_prop)

        # Clic sur bouton principal
        if isinstance(trigger_id, dict) and trigger_id.get("type") == "main-graph-button":
            sel_main = trigger_id["name"]
            sub_buttons_title = f"{sel_main} :"
            sel_sub  = None  # reset
            sub_buttons = [
                html.Button(
                    label,
                    id={"type": "sub-graph-button", "parent": sel_main, "name": label.split(" : ")[1]},
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "marginBottom": "6px",
                        "backgroundColor": colors[selected_date][label],
                        "border": "1px solid #ccc",
                        "borderRadius": "4px"
                    }
                ) for label in graph_names.get(sel_main, [])
            ]

        # Clic sur sous-bouton → on ne modifie pas la liste des sous-boutons
        elif isinstance(trigger_id, dict) and trigger_id.get("type") == "sub-graph-button":
            sel_main = prev_main
            sel_sub  = trigger_id["name"]
            sub_buttons = dash.no_update
            sub_buttons_title = dash.no_update
    else:
        sel_main    = prev_main
        sel_sub     = prev_sub
        sub_buttons_title = f"{sel_main} :" if sel_main else None
        sub_buttons = [
            html.Button(
                label,
                id={"type": "sub-graph-button", "parent": sel_main, "name": label.split(" : ")[1]},
                style={
                    "width": "100%",
                    "padding": "10px",
                    "marginBottom": "6px",
                    "backgroundColor": colors[selected_date][label],
                    "border": "1px solid #ccc",
                    "borderRadius": "4px"
                }
            ) for label in graph_names.get(sel_main, [])
        ]

    return sel_main, sel_sub, sub_buttons, sub_buttons_title

@app.callback(
    Output('selected-graphs', 'data'),
    Output('expanded-categories', 'data'),
    Output('show-categories', 'data'),
    Input('select-all', 'n_clicks'),
    Input('expand-all-categories', 'n_clicks'),
    Input({'type': 'category-expand', 'index': ALL}, 'n_clicks'),
    Input({'type': 'category-select', 'index': ALL}, 'n_clicks'),
    Input({'type': 'subcat-select', 'index': ALL}, 'n_clicks'),
    State('selected-graphs', 'data'),
    State('expanded-categories', 'data'),
    State('show-categories', 'data')
)
def update_all(select_all_clicks, expand_all_clicks, cat_expands, cat_selects, subcat_selects,
               selected_graphs, expanded_categories, show_categories):
    trigger = ctx.triggered_id

    all_subcats = graph_names_list

    if trigger == 'select-all':
        if set(selected_graphs) == set(all_subcats):
            return [], expanded_categories, show_categories
        else:
            return all_subcats, expanded_categories, show_categories

    elif trigger == 'expand-all-categories':
        return selected_graphs, expanded_categories, not show_categories

    elif isinstance(trigger, dict):
        if trigger['type'] == 'category-expand':
            cat = trigger['index']
            if cat in expanded_categories:
                expanded_categories.remove(cat)
            else:
                expanded_categories.append(cat)
            return selected_graphs, expanded_categories, show_categories

        elif trigger['type'] == 'category-select':
            cat = trigger['index']
            subcats = graph_names[cat]
            
            if all(s in selected_graphs for s in subcats):
                selected_graphs = [s for s in selected_graphs if s not in subcats]
            else:
                selected_graphs = list(set(selected_graphs + subcats))
            return selected_graphs, expanded_categories, show_categories

        elif trigger['type'] == 'subcat-select':
            sub = trigger['index']
            if sub in selected_graphs:
                selected_graphs.remove(sub)
            else:
                selected_graphs.append(sub)
            return selected_graphs, expanded_categories, show_categories

    return selected_graphs, expanded_categories, show_categories

@app.callback(
    Output('category-list', 'children'),
    Input('expanded-categories', 'data'),
    Input('selected-graphs', 'data'),
    Input('show-categories', 'data')
)
def render_categories(expanded_categories, selected_graphs, show_categories):
    if not show_categories:
        return []

    children = []

    for cat, subcats in graph_names.items():
        cat_selected = all(s in selected_graphs for s in subcats)
        text = "+"
        if cat in expanded_categories:
            text = "-"
        row = html.Div([
            html.Button(text, id={'type': 'category-expand', 'index': cat},
                        n_clicks=0, style={'margin-right': '5px'}),
            html.Button(f"{cat} {'✔' if cat_selected else ''}",
                        id={'type': 'category-select', 'index': cat}, n_clicks=0),
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '3px'})

        children.append(row)

        if cat in expanded_categories:
            for sub in subcats:
                sub_selected = sub in selected_graphs
                children.append(html.Div(
                    html.Button(f"{sub} {'✔' if sub_selected else ''}",
                                id={'type': 'subcat-select', 'index': sub}, n_clicks=0),
                    style={'margin-left': '30px', 'margin-bottom': '3px'}
                ))

    return children

@app.callback(
    Output("graph-display", "children"),
    Input("selected-main", "data"),
    Input("selected-sub", "data"),
    Input("toggle-value", "data"),
    Input("toggle-rip", "data"),
    State("selected-date", "data")
)
def update_graph_display(main, sub, toggle, toggle_rip, selected_date):
    if not main or not selected_date:
        return html.Div("Aucun indicateur sélectionné.")

    graph_list = []
    title = f"{main} : {sub}" if sub else main

    if main == "Stand":
        lettre = sub
        if sub:
            lettre += " "
        else:
            lettre = ""
        lettre_heure = "X" if toggle =="forecast" else "S"
        full_title = f"{title} : Nombre de positions avion {lettre}occupées (de 10 minutes avant {lettre_heure}TA à 10 minutes après {lettre_heure}TD)"
        xname = "Heure (HH:MM)"
        yname = f"Nombre de stand {lettre}occupés"
        values = (data_stand_forecast if toggle == "forecast" else data_stand_schedule)[selected_date][title]    
        shapes = generate_thresholds(title, toggle_rip)   
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

        full_title = f"{title} : Nombre de positions avion {lettre}libres"
        xname = "Heure (HH:MM)"
        yname = f"Nombre de stand {lettre}libres"
        values = (stand_libre_forecast if toggle == "forecast" else stand_libre_schedule)[selected_date][title]    
        shapes = [] 
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif main == "Piste":
        if len(title) == 5:
            sens = "de mouvements"
        elif len(title) == 17:
            sens = "de décollages"
        else:
            sens = "d'atterrissages"
        full_title = f"{title} : Nombre {sens} par heure roulante (de H à H+1)"
        xname = "Heure roulante (HH:MM)"
        yname = f"Nombre {sens}"
        values = (data_piste_forecast if toggle == "forecast" else data_piste_schedule)[selected_date][title]    
        shapes = generate_thresholds(title, toggle_rip)   
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif title == "Sûreté":
        full_title = f"{title} : Nombre de passagers arrivants à la sûreté chaque 5 minutes"
        xname = "Heure (HH:MM)"
        yname = "Nombre de passagers"
        values = data_surete[selected_date][title]    
        shapes = [] 
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif main == "Sûreté":
        graph_list.append(generate_kpi_boxes(main,selected_date,title,toggle_rip))

        full_title = f"{title} : Temps d'attente moyen sur la tranche de 30 minutes"
        xname = "Heure (HH:MM)"
        yname = "Temps d'attente (min)"
        values = (attente_moyenne_surete_reel if toggle_rip=="reel" else attente_moyenne_surete_ideal if toggle_rip=="ideal" else attente_moyenne_surete_perso)[selected_date][title]    
        shapes = generate_thresholds(title, toggle_rip)   
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Nombre de passagers dans la file d'attente"
        yname = "Nombre de passagers"
        values = (queue_surete_reel if toggle_rip=="reel" else queue_surete_ideal if toggle_rip=="ideal" else queue_surete_perso)[selected_date][title]    
        shapes = generate_threshold(SurfaceQueue[title]/LOSsurface["Sûreté"])   
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Demande vs capacité en nombre de passagers chaque 5 minutes"
        yname = "Nombre de passagers"
        values1 = data_surete[selected_date][title]
        values2 = (capacite_surete_reel if toggle_rip=="reel" else capacite_surete_ideal if toggle_rip=="ideal" else capacite_surete_perso)[selected_date][title]
        label1 = "Demande"
        label2 = "Capacité"
        shapes = []
        graph = generate_graph_multiple(values1, values2, xname, yname, shapes, label1, label2)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Nombre de lignes ouvertes"
        yname = "Nombre de lignes"
        values = (planning_surete_reel if toggle_rip=="reel" else planning_surete_ideal if toggle_rip=="ideal" else planning_surete_perso)[selected_date][title]
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif title == "Check-in":
        full_title = f"{title} : Nombre de passagers arrivants au check-in chaque 5 minutes"
        xname = "Heure (HH:MM)"
        yname = "Nombre de passagers"
        values = data_checkin[selected_date][title]    
        shapes = []   
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif main == "Check-in":
        graph_list.append(generate_kpi_boxes(main,selected_date,title,toggle_rip))

        full_title = f"{title} : Temps d'attente moyen sur la tranche de 30 minutes"
        xname = "Heure (HH:MM)"
        yname = "Temps d'attente (min)"
        values = (attente_moyenne_checkin_reel if toggle_rip=="reel" else attente_moyenne_checkin_ideal if toggle_rip=="ideal" else attente_moyenne_checkin_perso)[selected_date][title]    
        shapes = generate_thresholds(title, toggle_rip)  
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Nombre de passagers dans la file d'attente"
        yname = "Nombre de passagers"
        values = (queue_checkin_reel if toggle_rip=="reel" else queue_checkin_ideal if toggle_rip=="ideal" else queue_checkin_perso)[selected_date][title]    
        shapes = generate_threshold(SurfaceQueue["Check-in"]/LOSsurface["Check-in"]*max((planning_checkin_reel if toggle_rip=="reel" else planning_checkin_ideal if toggle_rip=="ideal" else planning_checkin_perso)[selected_date][title]))
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Demande vs capacité en nombre de passagers chaque 5 minutes"
        yname = "Nombre de passagers"
        values1 = data_checkin[selected_date][title]
        values2 = (capacite_checkin_reel if toggle_rip=="reel" else capacite_checkin_ideal if toggle_rip=="ideal" else capacite_checkin_perso)[selected_date][title]
        label1 = "Demande"
        label2 = "Capacité"
        shapes = []
        graph = generate_graph_multiple(values1, values2, xname, yname, shapes, label1, label2)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Nombre de lignes ouvertes"
        yname = "Nombre de lignes"
        values = (planning_checkin_reel if toggle_rip=="reel" else planning_checkin_ideal if toggle_rip=="ideal" else planning_checkin_perso)[selected_date][title]
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif title == "Douane":
        full_title = f"{title} : Nombre de passagers arrivants à la douane chaque 5 minutes"
        xname = "Heure (HH:MM)"
        yname = "Nombre de passagers"
        values = data_douane[selected_date][title]    
        shapes = []    
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif main == "Douane":
        graph_list.append(generate_kpi_boxes(main,selected_date,title,toggle_rip))

        full_title = f"{title} : Temps d'attente moyen sur la tranche de 30 minutes"
        xname = "Heure (HH:MM)"
        yname = "Temps d'attente (min)"
        values = (attente_moyenne_douane_reel if toggle_rip=="reel" else attente_moyenne_douane_ideal if toggle_rip=="ideal" else attente_moyenne_douane_perso)[selected_date][title]    
        shapes = generate_thresholds(title, toggle_rip)
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Nombre de passagers dans la file d'attente"
        yname = "Nombre de passagers"
        values = (queue_douane_reel if toggle_rip=="reel" else queue_douane_ideal if toggle_rip=="ideal" else queue_douane_perso)[selected_date][title]    
        shapes = generate_threshold(SurfaceQueue[title]/LOSsurface["Douane"])
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Demande vs capacité en nombre de passagers chaque 5 minutes"
        yname = "Nombre de passagers"
        values1 = data_douane[selected_date][title]
        values2 = (capacite_douane_reel if toggle_rip=="reel" else capacite_douane_ideal if toggle_rip=="ideal" else capacite_douane_perso)[selected_date][title]
        label1 = "Demande"
        label2 = "Capacité"
        shapes = []
        graph = generate_graph_multiple(values1, values2, xname, yname, shapes, label1, label2)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
        
        full_title = f"{title} : Nombre de lignes ouvertes"
        yname = "Nombre de lignes"
        values = (planning_douane_reel if toggle_rip=="reel" else planning_douane_ideal if toggle_rip=="ideal" else planning_douane_perso)[selected_date][title]
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    elif main == "Gate":
        if not sub:
            texte = "dans le terminal 1"
        elif sub in  gate_secteurs:
            texte = "au secteur " + sub
        else:
            texte = "en zone d'embarquement devant les portes " + sub
        full_title = f"{title} : Nombre de passagers présents {texte} au total"
        xname = "Heure (HH:MM)"
        yname = "Nombre de passagers"
        values = (occupation_gate_forecast if toggle == "forecast" else occupation_gate_schedule)[selected_date][title]    
        shapes = generate_thresholds(title, toggle_rip)
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))

    else:
        full_title = f"{title} : Placeholder"
        xname = "Heure (HH:MM)"
        yname = "Placeholder"
        values = [0]*24*12    
        shapes = []  
        graph = generate_graph(values,xname,yname,shapes)
        graph_list.append(html.Div([
            html.H4(full_title, style={"marginBottom": "10px"}),
            graph
        ], style={"marginBottom": "30px"}))
    
    return html.Div(graph_list)

@app.callback(
    Output("info-visible", "data"),
    Input("info-button", "n_clicks"),
    Input("selected-main", "data"),
    Input("selected-sub", "data"),
    Input("selected-date", "data"),
    State("info-visible", "data"),
    prevent_initial_call=True
)
def toggle_or_hide_info(n_clicks, main, sub, date, visible):
    ctx_trigger = ctx.triggered_id

    # Si c'est le bouton info → toggle visible
    if ctx_trigger == "info-button":
        return not visible

    # Si autre chose a changé → masquer
    return False

@app.callback(
    Output("info-popup", "children"),
    Output("info-popup", "style"),
    Input("selected-main", "data"),
    Input("selected-sub", "data"),
    Input("info-visible", "data")
)
def update_info_content(main, sub, visible):
    if not visible:
        return dash.no_update, {"display": "none"}

    # Texte à adapter selon les cas
    if not main:
        text = "Sélectionnez un indicateur pour afficher des informations."
    else:
        title = f"{main} : {sub}" if sub else main
        if title == "Stand":
            text = f"Nombre de stands disponibles:\n\nCode C: Fixe: **{stand_ouv["Cf"]}**, Variable: **{stand_ouv["Cv"]}**\n\nCode D: Fixe: **{stand_ouv["Df"]}**, Variable: **{stand_ouv["Dv"]}**\n\nCode E: Fixe: **{stand_ouv["Ef"]}**, Variable: **{stand_ouv["Ev"]}**\n\nUn buffer de 20 minutes étant en vigueur entre deux avions sur un même stand, il est considéré qu'un avion occupe une position de 10 minutes avant son arrivée à 10 minutes après son départ."

        elif main == "Stand":
            text = f"Nombre de stands disponibles:\n\nCode {sub}: Fixe: **{stand_ouv[sub+"f"]}**, Variable: **{stand_ouv[sub+"v"]}**\n\nUn buffer de 20 minutes étant en vigueur entre deux avions sur un même stand, il est considéré qu'un avion occupe une position de 10 minutes avant son arrivée à 10 minutes après son départ."
            
        elif title == "Piste":
            text = f"Nombre maximum de mouvements SCR autorisés par heure: **{PISTE_THRESHOLDS[title][0]}**"

        elif title == "Piste : Décollage":
            text = f"Nombre maximum de décollages SCR autorisés par heure: **{PISTE_THRESHOLDS[title][0]}**"

        elif title == "Piste : Atterrissage":
            text = f"Nombre maximum d'atterrissages SCR autorisés par heure: **{PISTE_THRESHOLDS[title][0]}**"

        elif title == "Sûreté":
            text = f"Nombre maximum de lignes disponibles à la sûreté internationale: **18**\n\nTemps de traitement à la sûreté internationale: **{int(TEMPS_PROCESS["Sûreté : International"]*60)} secondes**\n\nNombre maximum de lignes disponibles à la sûreté France: **3**\n\nTemps de traitement à la sûreté France: **{int(TEMPS_PROCESS["Sûreté : France"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Sûreté"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Sûreté"][1]} minutes**"

        elif title == "Sûreté : International":
            text = f"Nombre maximum de lignes disponibles à la sûreté internationale: **18**\n\nTemps de traitement à la sûreté internationale: **{int(TEMPS_PROCESS["Sûreté : International"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Sûreté"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Sûreté"][1]} minutes**"

        elif title == "Sûreté : France":
            text = f"Nombre maximum de lignes disponibles à la sûreté France: **3**\n\nTemps de traitement à la sûreté France: **{int(TEMPS_PROCESS["Sûreté : France"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Sûreté"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Sûreté"][1]} minutes**"

        elif title == "Sûreté : TERMINAL 2":
            text = f"Nombre maximum de lignes disponibles à la sûreté France: **4**\n\nTemps de traitement à la sûreté France: **{int(TEMPS_PROCESS["Sûreté : TERMINAL 2"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Sûreté"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Sûreté"][1]} minutes**"

        elif title == "Check-in":
            text = f"Temps de traitement au check-in easy-jet: **{int(TEMPS_PROCESS["Check-in : EASYJET Int"]*60)} secondes**\n\nTemps de traitement aux autres check-in: **{int(TEMPS_PROCESS["Check-in"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Check-in"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Check-in"][1]} minutes**"

        elif title == "Check-in : EASYJET Int":
            text = f"Temps de traitement au check-in easy-jet: **{int(TEMPS_PROCESS["Check-in : EASYJET Int"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Check-in"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Check-in"][1]} minutes**"

        elif main == "Check-in":
            text = f"Temps de traitement au check-in {sub}: **{int(TEMPS_PROCESS["Check-in"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Check-in"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Check-in"][1]} minutes**"

        elif title == "Douane":
            text = f"Nombre maximum de guérites disponibles à la douane de l'aile est: **16 + 5 ABC**\n\nNombre maximum de guérites disponibles à la douane de la trompette: **4**\n\nNombre maximum de guérites disponibles à la douane du satellite 10: **4**\n\nTemps de traitement à la douane: **{int(TEMPS_PROCESS["Douane"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Douane"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Douane"][1]} minutes**"

        elif title == "Douane : Aile est départ":
            text = f"Nombre maximum de guérites disponibles à la douane de l'aile est: **16 + 5 ABC**\n\nTemps de traitement à la douane de l'aile est: **{int(TEMPS_PROCESS["Douane : Aile est départ"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Douane"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Douane"][1]} minutes**"

        elif title == "Douane : Trompette":
            text = f"Nombre maximum de guérites disponibles à la douane de la trompette: **4**\n\nTemps de traitement à la douane de la trompette: **{int(TEMPS_PROCESS["Douane : Trompette"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Douane"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Douane"][1]} minutes**"
            
        elif title == "Douane : Satellite 10":
            text = f"Nombre maximum de guérites disponibles à la douane du satellite 10: **4**\n\nTemps de traitement à la douane du satellite 10: **{int(TEMPS_PROCESS["Douane : Satellite 10"]*60)} secondes**\n\nKPIs: Temps d'attente **89%** du temps en dessous de **{LOSduree["Douane"][0]} minutes** et **98%** du temps en dessous de **{LOSduree["Douane"][1]} minutes**"

        elif title == "Gate":
            text = f"Capacité du terminal 1:\n\nPlaces assises: **{GATE_THRESHOLDS[title][0]}**\n\nNombre de places totales avec les gens debout: **{GATE_THRESHOLDS[title][1]}**\n\nSurface au sol: **{GATE_THRESHOLDS[title][2]} m²**\n\nEn accord avec les level of service IATA, un passagers assis occupe une surface de **1,8 m²**, et un passager debout une surface de **1,2 m²**."

        elif main == "Gate" and sub in gate_secteurs:
            text = f"Capacité du secteur {sub}:\n\nPlaces assises: **{GATE_THRESHOLDS[title][0]}**\n\nNombre de places totales avec les gens debout: **{GATE_THRESHOLDS[title][1]}**\n\nSurface au sol: **{GATE_THRESHOLDS[title][2]} m²**\n\nEn accord avec les level of service IATA, un passagers assis occupe une surface de **1,8 m²**, et un passager debout une surface de **1,2 m²**."

        elif main == "Gate":
            text = f"Capacité de la zone d'embarquement devant les portes {sub}:\n\nPlaces assises: **{GATE_THRESHOLDS[title][0]}**\n\nNombre de places totales avec les gens debout: **{GATE_THRESHOLDS[title][1]}**\n\nSurface au sol: **{GATE_THRESHOLDS[title][2]} m²**\n\nEn accord avec les level of service IATA, un passagers assis occupe une surface de **1,8 m²**, et un passager debout une surface de **1,2 m²**."

        else:
            text = ""

    return dcc.Markdown(text), {"display": "block",
                                "position": "absolute",
                                "top": "50px",
                                "right": "10px",
                                "width": "300px",
                                "padding": "10px",
                                "backgroundColor": "#f9f9f9",
                                "border": "1px solid #ccc",
                                "borderRadius": "8px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.15)",
                                "zIndex": "999"
                                }

@app.callback(
    Output("toggle-value", "data"),
    Input("data-toggle", "value")
)
def update_toggle_value(value):
    return value

@app.callback(
    Output("toggle-rip", "data"),
    Input("data-toggle-rip", "value")
)
def update_toggle_value_rip(value):
    return value

@app.callback(
    Output("colors", "data"),
    Input("toggle-value", "data"),
    Input("toggle-rip", "data")
)
def update_colors(toggle,toggle_rip):
    return compute_colors(toggle,toggle_rip)

@app.callback(
    Output("dropdown-zone", "options"),
    Output("dropdown-zone", "value"),
    Input("dropdown-processeur", "value")
)
def update_zone_dropdown(processeur):
    if not processeur:
        return [], None
    options = [{"label": zone, "value": zone} for zone in graph_names[processeur]]
    return options, options[0]["value"] if options else None

@app.callback(
    Output("valeur", "options"),
    Output("valeur", "value"),
    Input("dropdown-zone", "value")
)
def update_max_planning(zone):
    if not zone:
        return [], None
    max_val = max_planning.get(zone, 20)  # Valeur par défaut de secours
    options = [{"label": val, "value": val} for val in range(0, max_val + 1)]
    return options, options[0]["value"] if options else None

@app.callback(
    Output("data-toggle-rip", "value"),
    Output("historique-messages", "data"),
    Input("appliquer-personnalisation", "n_clicks"),
    Input({"type": "delete-message", "index": ALL}, "n_clicks"),
    State("dropdown-processeur", "value"),
    State("dropdown-zone", "value"),
    State("date-debut", "date"),
    State("date-fin", "date"),
    State("heure-debut", "value"),
    State("minute-debut", "value"),
    State("heure-fin", "value"),
    State("minute-fin", "value"),
    State("weekday", "value"),
    State("valeur", "value"),
    State("historique-messages", "data")
)
def appliquer_modifications(n_clicks, n_suppr, processeur, zone, date_debut, date_fin, heure_debut, minute_debut, heure_fin, minute_fin, weekday, valeur, historique):
    
    triggered = ctx.triggered_id

    if triggered == "appliquer-personnalisation":
        if not all([processeur, zone, date_debut, date_fin]):
            return "perso", historique

        try:
            date1 = datetime.date.fromisoformat(date_debut)
            date2 = datetime.date.fromisoformat(date_fin)
            for d in (date1 + datetime.timedelta(days=i) for i in range((date2 - date1).days + 1)):
                if str(d.isocalendar().weekday) in weekday:
                    update_file_attente(processeur, zone, str(d), heure_debut, minute_debut, heure_fin, minute_fin, valeur)
            message = f"Planning mis à jour pour {zone} du {date1.strftime('%d/%m/%Y')} au {date2.strftime('%d/%m/%Y')} les {jours(weekday)} de {heure_debut}:{minute_debut} à {heure_fin}:{minute_fin} pour la valeur {valeur}."
            return "perso", historique + [{"message": message, "params": {"processeur": processeur, "zone": zone, "date_debut": date_debut, "date_fin": date_fin, "heure_debut": heure_debut, "minute_debut": minute_debut, "heure_fin": heure_fin, "minute_fin": minute_fin, "weekday": weekday}}]
        except Exception as e:
            message = f"❌ Erreur : {str(e)}"
            return "perso", historique + [{"message": message, "params": {"processeur": processeur, "zone": zone, "date_debut": date_debut, "date_fin": date_fin, "heure_debut": heure_debut, "minute_debut": minute_debut, "heure_fin": heure_fin, "minute_fin": minute_fin, "weekday": weekday}}]
        
    elif isinstance(triggered, dict) and triggered.get("type") == "delete-message":
        clicked_index = triggered.get("index")
        if not isinstance(clicked_index, int):
            return "perso", historique

        # messages sont affichés à l’envers, donc il faut inverser l’index
        true_index = len(historique) - 1 - clicked_index
        if 0 <= true_index < len(historique):
            params = historique[true_index]["params"]

            date1 = datetime.date.fromisoformat(params["date_debut"])
            date2 = datetime.date.fromisoformat(params["date_fin"])
            for d in (date1 + datetime.timedelta(days=i) for i in range((date2 - date1).days + 1)):
                if str(d.isocalendar().weekday) in params["weekday"]:
                    update_file_attente(params["processeur"], params["zone"], str(d), params["heure_debut"], params["minute_debut"], params["heure_fin"], params["minute_fin"])
            
            # Appel à ta fonction de réversion ici (à implémenter toi-même)
            # revert_file_attente(**params)

            historique.pop(true_index)

        return "perso", historique

    return dash.no_update, dash.no_update
    
@app.callback(
    Output("message-confirmation", "children"),
    Input("historique-messages", "data"),
    Input("selected-layout", "data")
)
def afficher_historique(messages, layout):
    if layout != "personnaliser":
        raise dash.exceptions.PreventUpdate
    if not messages:
        return ""

    return html.Div([
        html.Div([
            html.Button("❌", id={"type": "delete-message", "index": i}, n_clicks=0,
                        style={"marginLeft": "10px", "color": "red", "border": "none", "background": "none", "cursor": "pointer"}),
            html.Span(msg["message"], style={"flex": "1"})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"})
        for i, msg in enumerate(reversed(messages))
    ])

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='scrollToTop'
    ),
    Output("dummy-output", "children"),
    Input("selected-date", "data"),
    Input("selected-main", "data"),
    Input("selected-sub", "data")
)


# Auto-open browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    port = 8050
    #kill_process_on_port(port)
    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=port, debug=False)