"""
Application DCB - Demand Capacity Balancing
Version Streamlit
"""

import streamlit as st
import calendar
import datetime
import json
import os
import plotly.graph_objs as go
import re
from math import ceil
import copy
import sys

# Configuration de la page
st.set_page_config(
    page_title="Outil DCB - Demand Capacity Balancing",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
post_ops = False  # True pour voir des prévisions faites dans le passé, NE PAS TOUCHER

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
FRENCH_JOURS = ["", "lundis", "mardis", "mercredis", "jeudis", "vendredis", "samedis", "dimanches"]

def jours(weekday):
    j = weekday.replace(".", "")
    nb_j = len(j)
    jstr = ""
    for i in range(nb_j):
        jstr += FRENCH_JOURS[int(j[i])]
        if i == nb_j - 2:
            jstr += " et "
        elif i < nb_j - 2:
            jstr += ", "
    return jstr

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
@st.cache_data
def load_data(name, sous_dossier):
    # Parcourir les fichiers du dossier Actuel
    dossier = os.path.join(DATA_FOLDER, sous_dossier, "Actuel")
    file_name = None
    for fichier in os.listdir(dossier):
        if name in fichier:
            file_name = fichier
            break

    if file_name is None:
        st.error(f"Fichier {name} introuvable dans {dossier}")
        return None, 0

    if sous_dossier in ["Capacite/Aeroport", "LevelOfService", "Capacite/TempsProcess", "Annexe"]:
        dates = 0
    else:
        dates = extract_dates_from_filename(file_name)

    with open(os.path.join(dossier, file_name), 'r', encoding='utf-8') as file:
        return json.load(file), dates

def sum_list(dict_of_list):
    l = len(dict_of_list[list(dict_of_list.keys())[0]])
    s = [0] * l
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
        res.append(liste[i] - base[i])
    return res

def calcul_queue(demande, capacite):
    queue = [0] * len(demande)
    for i in range(len(demande)):
        queue[i] = max(0, demande[i] - capacite[i] + (queue[i - 1] if i > 0 else 0))
    return queue

def calcul_attente(queue, capacite):
    attente = [0] * len(queue)
    for i in range(len(queue)):
        if capacite[i] > 0:
            attente[i] = queue[i] / capacite[i]
        else:
            attente[i] = 0
    return attente

def calcul_attente_moyenne(attente):
    if len(attente) == 0:
        return 0
    return sum(attente) / len(attente)

def calcul_KPI(attente_moyenne, planning, seuil):
    heures_vertes = 0
    heures_jaunes = 0
    heures_rouges = 0
    for i in range(len(planning)):
        if planning[i] > 0:
            if attente_moyenne[i] <= seuil[0]:
                heures_vertes += 1
            elif attente_moyenne[i] <= seuil[1]:
                heures_jaunes += 1
            else:
                heures_rouges += 1
    total = heures_vertes + heures_jaunes + heures_rouges
    if total == 0:
        return [0, 0, 0]
    return [heures_vertes / total, heures_jaunes / total, heures_rouges / total]

def calcul_file_attente(data, planning):
    result = {}
    for processeur in data.keys():
        result[processeur] = {}
        for date in data[processeur].keys():
            demande = data[processeur][date]
            capacite = planning[processeur][date] if processeur in planning and date in planning[processeur] else [0] * len(demande)
            queue = calcul_queue(demande, capacite)
            attente = calcul_attente(queue, capacite)
            attente_moyenne = calcul_attente_moyenne(attente)
            result[processeur][date] = {
                "queue": queue,
                "attente": attente,
                "attente_moyenne": attente_moyenne
            }
    return result

def value_to_color(value, var, toggle_rip):
    if var in ["Piste", "Stand", "Stand : C", "Stand : D", "Stand : E", "Gate", "Gate : A", "Gate : B", "Gate : C", "Gate : D", "Gate : E/F"]:
        if value < Thresholds_dict[toggle_rip][var][0]:
            return "green"
        elif value < Thresholds_dict[toggle_rip][var][1]:
            return "yellow"
        else:
            return "red"
    else:
        if value <= Thresholds_dict[toggle_rip][var][0]:
            return "green"
        elif value <= Thresholds_dict[toggle_rip][var][1]:
            return "yellow"
        else:
            return "red"

def KPI_to_color(KPIs):
    if KPIs[0] >= 0.8:
        return "green"
    elif KPIs[2] <= 0.2:
        return "yellow"
    else:
        return "red"

def worst_color(day_col, graphs="Liste"):
    if graphs == "Liste":
        graphs = st.session_state.selected_graphs
    worst = "green"
    for graph in graphs:
        if graph in day_col:
            color = day_col[graph]
            if color == "red":
                return "red"
            elif color == "yellow":
                worst = "yellow"
    return worst

def comp_color(a, b):
    if a == "red" or b == "red":
        return "red"
    elif a == "yellow" or b == "yellow":
        return "yellow"
    else:
        return "green"

def compute_colors(sx="forecast", rip="ideal"):
    colors = {}

    # Calcul des couleurs pour chaque processeur et chaque date
    planning_dict = {
        "reel": {
            "Sûreté": planning_surete_reel,
            "Check-in": planning_checkin_reel,
            "Douane": planning_douane_reel
        },
        "ideal": {
            "Sûreté": planning_surete_ideal,
            "Check-in": planning_checkin_ideal,
            "Douane": planning_douane_ideal
        },
        "perso": {
            "Sûreté": planning_surete_perso,
            "Check-in": planning_checkin_perso,
            "Douane": planning_douane_perso
        }
    }

    # Pour chaque date
    for date_str in data_surete[list(data_surete.keys())[0]].keys():
        colors[date_str] = {}

        # Sûreté
        for processeur in data_surete.keys():
            if date_str in data_surete[processeur]:
                demande = data_surete[processeur][date_str]
                capacite = planning_dict[rip]["Sûreté"][processeur].get(date_str, [0] * len(demande))
                queue = calcul_queue(demande, capacite)
                attente = calcul_attente(queue, capacite)
                attente_moyenne = calcul_attente_moyenne(attente)
                KPIs = calcul_KPI(attente, capacite, Thresholds_dict[rip][processeur])
                colors[date_str][processeur] = KPI_to_color(KPIs)

        # Check-in
        for processeur in data_checkin.keys():
            if date_str in data_checkin[processeur]:
                demande = data_checkin[processeur][date_str]
                capacite = planning_dict[rip]["Check-in"][processeur].get(date_str, [0] * len(demande))
                queue = calcul_queue(demande, capacite)
                attente = calcul_attente(queue, capacite)
                attente_moyenne = calcul_attente_moyenne(attente)
                KPIs = calcul_KPI(attente, capacite, Thresholds_dict[rip][processeur])
                colors[date_str][processeur] = KPI_to_color(KPIs)

        # Douane
        for processeur in data_douane.keys():
            if date_str in data_douane[processeur]:
                demande = data_douane[processeur][date_str]
                capacite = planning_dict[rip]["Douane"][processeur].get(date_str, [0] * len(demande))
                queue = calcul_queue(demande, capacite)
                attente = calcul_attente(queue, capacite)
                attente_moyenne = calcul_attente_moyenne(attente)
                KPIs = calcul_KPI(attente, capacite, Thresholds_dict[rip][processeur])
                colors[date_str][processeur] = KPI_to_color(KPIs)

        # Piste et Stand
        data_dict = {"forecast": (data_piste_forecast, data_stand_forecast), "schedule": (data_piste_schedule, data_stand_schedule)}
        piste_data, stand_data = data_dict[sx]

        for processeur in piste_data.keys():
            if date_str in piste_data[processeur]:
                max_val = max(piste_data[processeur][date_str])
                colors[date_str][processeur] = value_to_color(max_val, processeur, rip)

        for processeur in stand_data.keys():
            if date_str in stand_data[processeur]:
                max_val = max(stand_data[processeur][date_str])
                colors[date_str][processeur] = value_to_color(max_val, processeur, rip)

        # Gate
        for secteur in gate_secteurs:
            gate_name = f"Gate : {secteur}"
            if date_str in data_gate.get(secteur, {}):
                demande = data_gate[secteur][date_str]
                max_val = max(demande)
                colors[date_str][gate_name] = value_to_color(max_val, gate_name, rip)

    return colors

def generate_calendar(graphs, colors):
    """Génère le HTML du calendrier"""
    # Cette fonction devrait être remplacée par une visualisation Streamlit
    # Pour l'instant, on va créer un affichage simplifié
    return None

def generate_graph(values, xname, yname, shapes):
    """Génère un graphique Plotly"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=values,
        mode='lines',
        name=yname,
        line=dict(color='blue', width=2)
    ))

    # Ajouter les shapes (seuils, etc.)
    if shapes:
        fig.update_layout(shapes=shapes)

    fig.update_layout(
        xaxis_title=xname,
        yaxis_title=yname,
        hovermode='closest',
        height=400
    )

    return fig

def generate_graph_multiple(values1, values2, xname, yname, shapes, label1, label2):
    """Génère un graphique Plotly avec plusieurs séries"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(values1))),
        y=values1,
        mode='lines',
        name=label1,
        line=dict(color='blue', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=list(range(len(values2))),
        y=values2,
        mode='lines',
        name=label2,
        line=dict(color='red', width=2, dash='dash')
    ))

    # Ajouter les shapes (seuils, etc.)
    if shapes:
        fig.update_layout(shapes=shapes)

    fig.update_layout(
        xaxis_title=xname,
        yaxis_title=yname,
        hovermode='closest',
        height=400,
        legend=dict(x=0, y=1)
    )

    return fig

# Initialisation de l'état de session
def init_session_state():
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_layout' not in st.session_state:
        st.session_state.selected_layout = "calendar"
    if 'selected_main' not in st.session_state:
        st.session_state.selected_main = None
    if 'selected_sub' not in st.session_state:
        st.session_state.selected_sub = None
    if 'toggle_value' not in st.session_state:
        st.session_state.toggle_value = "forecast"
    if 'toggle_rip' not in st.session_state:
        st.session_state.toggle_rip = "ideal"
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

# Chargement des données
@st.cache_resource
def load_all_data():
    global graph_names, gate_secteurs, graph_names_list
    global TEMPS_PROCESS, process_present
    global max_planning, max_plan_ci
    global LOSduree, LOSsurface, SurfaceQueue
    global PISTE_THRESHOLDS, GATE_THRESHOLDS, STAND_THRESHOLDS
    global SURETE_THRESHOLDS, CHECKIN_THRESHOLDS, DOUANE_THRESHOLDS
    global Thresholds, Thresholds_perso, Thresholds_dict
    global data_stand_forecast, dates_in_filename_stand_forecast
    global data_stand_schedule, dates_in_filename_stand_schedule
    global data_piste_forecast, dates_in_filename_piste_forecast
    global data_piste_schedule, dates_in_filename_piste_schedule
    global data_surete, dates_in_filename_surete
    global planning_surete_reel, dates_in_filename_planning_surete_reel
    global planning_surete_ideal, dates_in_filename_planning_surete_ideal
    global data_checkin, dates_in_filename_checkin
    global planning_checkin_reel, dates_in_filename_planning_checkin
    global planning_checkin_ideal
    global data_douane, dates_in_filename_douane
    global planning_douane_reel, dates_in_filename_planning_douane_reel
    global planning_douane_ideal, dates_in_filename_planning_douane_ideal
    global data_gate, dates_in_filename_gate
    global embarquement_gate_forecast, dates_in_filename_embarquement_gate_forecast
    global embarquement_gate_schedule, dates_in_filename_embarquement_gate_schedule
    global planning_checkin_perso, planning_surete_perso, planning_douane_perso
    global start_date, end_date, start_month_date
    global stand_ouv, standTot, standC, standD, standE

    with st.spinner("Chargement des données..."):
        graph_names, _ = load_data("GraphNames", "Annexe")
        gate_secteurs = ["A", "B", "C", "D", "E/F"]
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

        LOSduree, _ = load_data("ValeursCritiquesDuree", "LevelOfService")
        LOSsurface, _ = load_data("ValeursCritiquesSurface", "LevelOfService")
        SurfaceQueue, _ = load_data("CapaciteQueue", "Capacite/Aeroport")
        PISTE_THRESHOLDS, _ = load_data("CapacitePiste", "Capacite/Aeroport")
        GATE_THRESHOLDS, _ = load_data("CapaciteGate", "Capacite/Aeroport")

        stand_ouv, _ = load_data("StandDispo", "Capacite/Aeroport")
        standTot = sum(stand_ouv.values()) + stand_ouv["Dv"] + stand_ouv["Ev"]
        standC = stand_ouv["Cf"] + 2 * stand_ouv["Dv"] + 2 * stand_ouv["Ev"]
        standD = stand_ouv["Df"] + stand_ouv["Dv"]
        standE = stand_ouv["Ef"] + stand_ouv["Ev"]
        STAND_THRESHOLDS = {
            "Stand": [standTot * 0.6, standTot],
            "Stand : C": [standC * 0.6, standC],
            "Stand : D": [standD * 0.8, standD],
            "Stand : E": [standE * 0.6, standE]
        }

        SURETE_THRESHOLDS = {processeur: LOSduree["Sûreté"] for processeur in graph_names["Sûreté"]}
        CHECKIN_THRESHOLDS = {processeur: LOSduree["Check-in"] for processeur in graph_names["Check-in"]}
        DOUANE_THRESHOLDS = {processeur: LOSduree["Douane"] for processeur in graph_names["Douane"]}

        Thresholds = {}
        Thresholds.update(PISTE_THRESHOLDS)
        Thresholds.update(STAND_THRESHOLDS)
        Thresholds.update(SURETE_THRESHOLDS)
        Thresholds.update(CHECKIN_THRESHOLDS)
        Thresholds.update(DOUANE_THRESHOLDS)
        Thresholds.update(GATE_THRESHOLDS)

        Thresholds_perso = copy.deepcopy(Thresholds)
        Thresholds_dict = {"reel": Thresholds, "ideal": Thresholds, "perso": Thresholds_perso}

        data_stand_forecast, dates_in_filename_stand_forecast = load_data("ForecastStandUtilisation", "Demande")
        data_stand_schedule, dates_in_filename_stand_schedule = load_data("ScheduleStandUtilisation", "Demande")
        data_piste_forecast, dates_in_filename_piste_forecast = load_data("ForecastPisteUtilisation", "Demande")
        data_piste_schedule, dates_in_filename_piste_schedule = load_data("SchedulePisteUtilisation", "Demande")
        data_surete, dates_in_filename_surete = load_data("SUPForecastSurete", "Demande")
        planning_surete_reel, dates_in_filename_planning_surete_reel = load_data("PlanningSurete", "Capacite/Planning")
        planning_surete_ideal, dates_in_filename_planning_surete_ideal = load_data("PlanningSureteIdeal", "Capacite/Planning")
        data_checkin, dates_in_filename_checkin = load_data("SUPForecastCheckIn", "Demande")
        planning_checkin_reel, dates_in_filename_planning_checkin = load_data("PlanningCheckIn", "Capacite/Planning")
        data_douane, dates_in_filename_douane = load_data("SUPForecastDouane", "Demande")
        planning_douane_reel, dates_in_filename_planning_douane_reel = load_data("PlanningDouane", "Capacite/Planning")
        planning_douane_ideal, dates_in_filename_planning_douane_ideal = load_data("PlanningDouaneIdeal", "Capacite/Planning")
        data_gate, dates_in_filename_gate = load_data("SUPForecastGate", "Demande")
        embarquement_gate_forecast, dates_in_filename_embarquement_gate_forecast = load_data("ForecastGateEmbarquement", "Demande")
        embarquement_gate_schedule, dates_in_filename_embarquement_gate_schedule = load_data("ScheduleGateEmbarquement", "Demande")

        planning_checkin_ideal = copy.deepcopy(planning_checkin_reel)
        planning_checkin_perso = copy.deepcopy(planning_checkin_reel)
        planning_surete_perso = copy.deepcopy(planning_surete_ideal)
        planning_douane_perso = copy.deepcopy(planning_douane_ideal)

        start_date = dates_in_filename_surete[0]
        end_date = dates_in_filename_surete[1]
        start_month_date = datetime.date(start_date.year, start_date.month, 1)

    return True

# Interface principale
def main():
    init_session_state()

    # Chargement des données
    if not st.session_state.data_loaded:
        st.session_state.data_loaded = load_all_data()

    # En-tête
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        # Logo (si disponible)
        logo_path = os.path.join(ASSETS_FOLDER, "geneva_airport_logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
    with col2:
        st.title("Outil DCB - Demand Capacity Balancing")
    with col3:
        st.markdown("### Version 2.0")

    st.markdown("---")

    # Sidebar avec les options
    with st.sidebar:
        st.header("Options")

        # Sélection des graphes
        st.subheader("Sélection des processeurs")
        if 'selected_graphs' not in st.session_state:
            st.session_state.selected_graphs = graph_names_list

        # Bouton "Tout sélectionner"
        if st.button("Tout sélectionner"):
            st.session_state.selected_graphs = graph_names_list

        # Affichage par catégorie
        for category, items in graph_names.items():
            with st.expander(category, expanded=False):
                for item in items:
                    selected = st.checkbox(
                        item,
                        value=item in st.session_state.selected_graphs,
                        key=f"checkbox_{item}"
                    )
                    if selected and item not in st.session_state.selected_graphs:
                        st.session_state.selected_graphs.append(item)
                    elif not selected and item in st.session_state.selected_graphs:
                        st.session_state.selected_graphs.remove(item)

        st.markdown("---")

        # Options de visualisation
        st.subheader("Options de visualisation")

        toggle_value = st.radio(
            "Heure de départ/arrivée :",
            ["forecast", "schedule"],
            format_func=lambda x: "Expected" if x == "forecast" else "Schedule",
            key="toggle_radio"
        )
        st.session_state.toggle_value = toggle_value

        toggle_rip = st.radio(
            "Planning à utiliser :",
            ["ideal", "reel", "perso"],
            format_func=lambda x: {"ideal": "Idéal", "reel": "Réel", "perso": "Personnalisé"}[x],
            key="toggle_rip_radio"
        )
        st.session_state.toggle_rip = toggle_rip

    # Calcul des couleurs
    colors = compute_colors(st.session_state.toggle_value, st.session_state.toggle_rip)

    # Navigation
    if st.session_state.selected_layout == "calendar":
        display_calendar(colors)
    elif st.session_state.selected_layout == "details":
        display_details(colors)
    elif st.session_state.selected_layout == "personnaliser":
        display_personnalisation()

def display_calendar(colors):
    """Affiche la vue calendrier"""
    st.subheader(f"Période: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")

    # Bouton pour personnaliser
    if st.button("Personnaliser les plannings"):
        st.session_state.selected_layout = "personnaliser"
        st.rerun()

    # Affichage du calendrier
    current_date = start_date

    # Parcourir les mois
    while current_date <= end_date:
        st.markdown(f"### {FRENCH_MONTHS[current_date.month - 1]} {current_date.year}")

        # Créer le calendrier du mois
        cal = calendar.monthcalendar(current_date.year, current_date.month)

        # En-têtes des jours
        cols = st.columns(7)
        days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        for i, day in enumerate(days):
            cols[i].markdown(f"**{day}**")

        # Affichage des jours
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown("")
                else:
                    date = datetime.date(current_date.year, current_date.month, day)
                    if start_date <= date <= end_date:
                        date_str = date.strftime("%Y-%m-%d")

                        # Calculer la couleur du jour
                        if date_str in colors:
                            day_color = worst_color(colors[date_str])
                            color_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[day_color]
                        else:
                            color_emoji = "⚪"

                        # Bouton pour voir les détails
                        if cols[i].button(f"{day} {color_emoji}", key=f"day_{date_str}"):
                            st.session_state.selected_date = date_str
                            st.session_state.selected_layout = "details"
                            st.rerun()
                    else:
                        cols[i].markdown(f"{day}")

        # Passer au mois suivant
        if current_date.month == 12:
            current_date = datetime.date(current_date.year + 1, 1, 1)
        else:
            current_date = datetime.date(current_date.year, current_date.month + 1, 1)

        st.markdown("---")

def display_details(colors):
    """Affiche les détails d'un jour sélectionné"""
    if st.button("← Retour au calendrier"):
        st.session_state.selected_layout = "calendar"
        st.rerun()

    if st.session_state.selected_date is None:
        st.warning("Aucune date sélectionnée")
        return

    date_str = st.session_state.selected_date
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    st.subheader(f"Détails pour le {date.strftime('%d/%m/%Y')}")

    # Afficher les graphiques pour chaque processeur sélectionné
    for graph in st.session_state.selected_graphs:
        with st.expander(graph, expanded=True):
            # Déterminer le type de processeur
            category = None
            for cat, items in graph_names.items():
                if graph in items:
                    category = cat
                    break

            if category == "Piste":
                # Graphique piste
                data_dict = {
                    "forecast": data_piste_forecast,
                    "schedule": data_piste_schedule
                }
                data = data_dict[st.session_state.toggle_value]

                if graph in data and date_str in data[graph]:
                    values = data[graph][date_str]
                    fig = generate_graph(
                        values,
                        "Heure",
                        "Nombre de mouvements",
                        []
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données disponibles")

            elif category == "Stand":
                # Graphique stand
                data_dict = {
                    "forecast": data_stand_forecast,
                    "schedule": data_stand_schedule
                }
                data = data_dict[st.session_state.toggle_value]

                if graph in data and date_str in data[graph]:
                    values = data[graph][date_str]
                    fig = generate_graph(
                        values,
                        "Heure",
                        "Nombre de stands occupés",
                        []
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données disponibles")

            elif category in ["Sûreté", "Check-in", "Douane"]:
                # Graphique avec demande et capacité
                data_dict = {
                    "Sûreté": data_surete,
                    "Check-in": data_checkin,
                    "Douane": data_douane
                }
                planning_dict = {
                    "Sûreté": {
                        "reel": planning_surete_reel,
                        "ideal": planning_surete_ideal,
                        "perso": planning_surete_perso
                    },
                    "Check-in": {
                        "reel": planning_checkin_reel,
                        "ideal": planning_checkin_ideal,
                        "perso": planning_checkin_perso
                    },
                    "Douane": {
                        "reel": planning_douane_reel,
                        "ideal": planning_douane_ideal,
                        "perso": planning_douane_perso
                    }
                }

                data = data_dict[category]
                planning = planning_dict[category][st.session_state.toggle_rip]

                processeur = graph.split(" : ")[0] if " : " in graph else graph

                if processeur in data and date_str in data[processeur]:
                    demande = data[processeur][date_str]
                    capacite = planning[processeur].get(date_str, [0] * len(demande))

                    fig = generate_graph_multiple(
                        demande,
                        capacite,
                        "Heure",
                        "Nombre de passagers",
                        [],
                        "Demande",
                        "Capacité"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Calculer les KPIs
                    queue = calcul_queue(demande, capacite)
                    attente = calcul_attente(queue, capacite)
                    attente_moyenne = calcul_attente_moyenne(attente)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("File d'attente max", f"{max(queue):.0f} pax")
                    with col2:
                        st.metric("Attente max", f"{max(attente):.1f} min")
                    with col3:
                        st.metric("Attente moyenne", f"{attente_moyenne:.1f} min")
                else:
                    st.info("Pas de données disponibles")

            elif category == "Gate":
                # Graphique gate
                secteur = graph.split(" : ")[1] if " : " in graph else None

                if secteur and secteur in data_gate and date_str in data_gate[secteur]:
                    demande = data_gate[secteur][date_str]

                    fig = generate_graph(
                        demande,
                        "Heure",
                        "Nombre de passagers au gate",
                        []
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données disponibles")

def display_personnalisation():
    """Affiche l'interface de personnalisation des plannings"""
    if st.button("← Retour au calendrier"):
        st.session_state.selected_layout = "calendar"
        st.rerun()

    st.subheader("Personnalisation des plannings")

    st.info("Fonctionnalité de personnalisation en cours de développement")

    # TODO: Implémenter l'interface de personnalisation
    # avec les formulaires pour modifier les plannings

if __name__ == "__main__":
    main()
