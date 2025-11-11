"""
Application DCB - Demand Capacity Balancing
Version Streamlit Moderne et Optimisée
Design professionnel pour partage multi-utilisateurs
"""

import streamlit as st
import calendar
import datetime
import json
import os
import re
from math import ceil
import copy
import sys
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import du système de chemins pour lancement local
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TraitementDonnee', 'Code'))
from chemin_dossier import CHEMIN_DATA_SOURCE, CHEMIN_APP_RACINE

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="DCB - Demand Capacity Balancing | Geneva Airport",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# DCB Tool\nDemand Capacity Balancing pour l'Aéroport de Genève"
    }
)

# CSS Personnalisé pour un design moderne et optimisé
st.markdown("""
<style>
    /* Design global moderne avec animation */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Header amélioré avec animation */
    .dcb-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
        color: white;
        animation: slideDown 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }

    .dcb-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite;
    }

    @keyframes slideDown {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    @keyframes shimmer {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-30%, -30%) scale(1.1); }
    }

    .dcb-header h1 {
        color: white;
        font-weight: 700;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }

    .dcb-header p {
        color: #E0E7FF;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
    }

    /* Cards modernes pour métriques avec animations avancées */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #3B82F6;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUp 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }

    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.05));
        transition: width 0.5s ease;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.2);
    }

    .metric-card:hover::after {
        width: 100%;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin: 0;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }

    /* Status indicators */
    .status-green {
        background: #10B981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
    }

    .status-yellow {
        background: #F59E0B;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
    }

    .status-red {
        background: #EF4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
    }

    /* Calendrier moderne */
    .calendar-day {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 2px solid transparent;
    }

    .calendar-day:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-color: #3B82F6;
    }

    /* Sidebar améliorée */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #3B82F6 100%);
    }

    [data-testid="stSidebar"] .element-container {
        color: white;
    }

    /* Boutons modernes avec effets avancés */
    .stButton > button {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }

    /* Tabs modernes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%);
        color: white;
    }

    /* Plotly graphs */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Filtres avancés */
    .filter-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }

    /* Messages d'information */
    .info-box {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Data period badge */
    .data-period {
        background: #F1F5F9;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        color: #475569;
        font-weight: 500;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
post_ops = False

def get_base_path():
    """Retourne le chemin racine de l'application"""
    return str(CHEMIN_APP_RACINE)

def get_data_folder():
    """Retourne le chemin du dossier 'Data Source' en utilisant chemin_dossier.py"""
    return str(CHEMIN_DATA_SOURCE)

# Initialisation différée
ASSETS_FOLDER = None
DATA_FOLDER = None
FRENCH_MONTHS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
FRENCH_JOURS = ["", "lundis", "mardis", "mercredis", "jeudis", "vendredis", "samedis", "dimanches"]

# Variables globales
graph_names = {}
gate_secteurs = []
graph_names_list = []
start_date = None
end_date = None

# ==================== FONCTIONS UTILITAIRES ====================

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

def extract_dates_from_filename(filename):
    dates = re.findall("[0-9]+", filename)
    date_list = []
    for date in dates:
        if len(date) == 8:
            date_list.append(datetime.date(int(date[:4]), int(date[4:6]), int(date[6:8])))
    if len(date_list) != 2:
        raise ValueError(f"Erreur: Impossible d'extraire deux dates du fichier {filename}.")
    return date_list

@st.cache_data
def load_data(name, sous_dossier, data_folder_override=None):
    folder_to_use = data_folder_override if data_folder_override else DATA_FOLDER
    if folder_to_use is None:
        raise FileNotFoundError("Aucun dossier de données trouvé.")

    dossier = os.path.join(folder_to_use, sous_dossier, "Actuel")
    if not os.path.exists(dossier):
        raise FileNotFoundError(f"Le dossier {dossier} n'existe pas.")

    file_name = None
    for fichier in os.listdir(dossier):
        if name in fichier:
            file_name = fichier
            break

    if file_name is None:
        raise FileNotFoundError(f"Fichier contenant '{name}' introuvable dans {dossier}.")

    if sous_dossier in ["Capacite/Aeroport", "LevelOfService", "Capacite/TempsProcess", "Annexe"]:
        dates = 0
    else:
        dates = extract_dates_from_filename(file_name)

    with open(os.path.join(dossier, file_name), 'r', encoding='utf-8') as file:
        return json.load(file), dates

# ==================== FONCTIONS DE CALCUL ====================

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
    return attente

def calcul_attente_moyenne(attente):
    if len(attente) == 0:
        return 0
    return sum(attente) / len(attente)

def calcul_KPI(attente_moyenne, planning, seuil):
    heures_vertes = heures_jaunes = heures_rouges = 0
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

def KPI_to_color(KPI):
    if KPI[2] > 0.1:
        return "red"
    elif KPI[1] > 0.1:
        return "yellow"
    else:
        return "green"

def compute_colors(data, planning, Thresholds_dict, rip):
    colors = {}
    for processeur in data.keys():
        for date_str in data[processeur].keys():
            if date_str not in colors:
                colors[date_str] = {}
            demande = data[processeur][date_str]
            if processeur in planning and date_str in planning[processeur]:
                capacite = planning[processeur][date_str]
            else:
                capacite = [0] * len(demande)

            queue = calcul_queue(demande, capacite)
            attente = calcul_attente(queue, capacite)

            if rip in Thresholds_dict and processeur in Thresholds_dict[rip]:
                KPIs = calcul_KPI(attente, capacite, Thresholds_dict[rip][processeur])
                colors[date_str][processeur] = KPI_to_color(KPIs)
            else:
                colors[date_str][processeur] = "green"
    return colors

def worst_color(colors_dict):
    if "red" in colors_dict.values():
        return "red"
    elif "yellow" in colors_dict.values():
        return "yellow"
    else:
        return "green"

# ==================== SESSION STATE ====================

def init_session_state():
    if 'selected_graphs' not in st.session_state:
        st.session_state.selected_graphs = []
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_layout' not in st.session_state:
        st.session_state.selected_layout = "dashboard"  # dashboard au lieu de calendar
    if 'toggle_value' not in st.session_state:
        st.session_state.toggle_value = "forecast"
    if 'toggle_rip' not in st.session_state:
        st.session_state.toggle_rip = "reel"
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "dashboard"  # dashboard, calendar, analytics
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

# ==================== CHARGEMENT DES DONNÉES ====================

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

    try:
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
    except Exception as e:
        st.error(f"Erreur lors du chargement: {str(e)}")
        return False

# ==================== GÉNÉRATION DE GRAPHIQUES MODERNES ====================

def generate_modern_graph(data, xaxis_title, yaxis_title, title, color="#3B82F6"):
    """Génère un graphique Plotly moderne et stylisé"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=data,
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3, shape='spline'),
        marker=dict(size=6, color=color, line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor=f'rgba(59, 130, 246, 0.1)'
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#1E293B', family='Arial Black')),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        margin=dict(l=50, r=50, t=70, b=50),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E2E8F0',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E2E8F0',
            zeroline=False
        ),
        height=400
    )

    return fig

def generate_comparison_graph(data1, data2, xaxis_title, yaxis_title, title, name1, name2):
    """Génère un graphique de comparaison moderne"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=data1,
        mode='lines+markers',
        name=name1,
        line=dict(color='#3B82F6', width=3, shape='spline'),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        y=data2,
        mode='lines+markers',
        name=name2,
        line=dict(color='#EF4444', width=3, shape='spline', dash='dash'),
        marker=dict(size=6),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#1E293B', family='Arial Black')),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(family='Arial', size=12),
        margin=dict(l=50, r=50, t=70, b=50),
        xaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
        yaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#CBD5E1",
            borderwidth=1
        ),
        height=450
    )

    return fig

def generate_heatmap_graph(data_dict, title):
    """Génère une heatmap moderne pour visualiser les tendances"""
    # Préparer les données pour la heatmap
    dates = sorted(list(data_dict.keys()))
    hours = list(range(24))

    z_data = []
    for date in dates:
        if date in data_dict and len(list(data_dict[date].values())) > 0:
            first_key = list(data_dict[date].keys())[0]
            z_data.append(data_dict[date][first_key])
        else:
            z_data.append([0] * 24)

    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=hours,
        y=dates,
        colorscale='Blues',
        hoverongaps=False,
        colorbar=dict(title="Valeur")
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Heure de la journée",
        yaxis_title="Date",
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

# ==================== VUES DE L'APPLICATION ====================

def display_welcome():
    """Écran d'accueil pour nouveaux utilisateurs"""

    st.markdown('''
    <div class="dcb-header">
        <h1>✈️ Bienvenue sur DCB Tool</h1>
        <p>Demand Capacity Balancing - Geneva Airport</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        ### 👋 Première visite ?

        Cette application vous permet d'analyser et de visualiser les données de **Demand Capacity Balancing**
        pour l'aéroport de Genève.

        #### 🎯 Fonctionnalités principales

        - **📊 Dashboard** : Vue d'ensemble avec KPIs et métriques clés
        - **📅 Calendrier** : Visualisation mensuelle des performances
        - **🛫 Opérations** : Analyse détaillée des mouvements de piste et stands
        - **👥 Passagers** : Suivi des flux passagers et files d'attente
        - **📈 Analytique** : Tendances et statistiques avancées

        #### 🚀 Pour commencer

        1. Utilisez la **sidebar** (à gauche) pour naviguer
        2. Sélectionnez votre **mode de vue** (Dashboard, Calendrier, Détails)
        3. Choisissez le **type de données** (Forecast ou Schedule)
        4. Explorez les **processeurs** qui vous intéressent

        #### 💡 Codes couleur

        - 🟢 **Vert** : Conditions excellentes (< 5 min d'attente)
        - 🟡 **Jaune** : Conditions acceptables (5-10 min)
        - 🔴 **Rouge** : Conditions critiques (> 10 min)

        ---

        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("🚀 Démarrer l'exploration", key="start_exploration", use_container_width=True):
                st.session_state.show_welcome = False
                st.session_state.first_visit = False
                st.rerun()

        with col_b:
            if st.button("📚 Voir le Dashboard", key="go_dashboard", use_container_width=True):
                st.session_state.show_welcome = False
                st.session_state.selected_layout = "dashboard"
                st.rerun()

        st.markdown("---")

        with st.expander("ℹ️ Aide et support"):
            st.markdown("""
            **Besoin d'aide ?**

            - Consultez la **documentation** dans les fichiers README
            - Utilisez la **page Administration** pour gérer vos données
            - Les **tooltips** vous guident à travers l'interface

            **Raccourcis clavier** (Streamlit) :
            - `Ctrl + R` : Actualiser l'application
            - `Ctrl + K` : Ouvrir la recherche
            """)

def display_dashboard():
    """Dashboard principal avec KPIs et visualisations clés"""

    st.markdown('<div class="dcb-header"><h1>✈️ Dashboard DCB</h1><p>Demand Capacity Balancing - Geneva Airport</p></div>', unsafe_allow_html=True)

    # Période de données
    st.markdown(f'<div class="data-period">📅 Période: {start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)

    # KPIs globaux en haut
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">✓</div>
            <div class="metric-label">Statut Système</div>
            <div class="status-green">Opérationnel</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        total_days = (end_date - start_date).days + 1
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_days}</div>
            <div class="metric-label">Jours de données</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        total_processeurs = len(graph_names_list)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_processeurs}</div>
            <div class="metric-label">Processeurs actifs</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">98%</div>
            <div class="metric-label">Disponibilité</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Onglets pour différentes vues
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "🛫 Opérations", "👥 Passagers", "📈 Analytique"])

    with tab1:
        st.subheader("Vue d'ensemble des opérations")

        col1, col2 = st.columns(2)

        with col1:
            # Graphique Stand
            if "Stand" in data_stand_forecast:
                sample_date = list(data_stand_forecast["Stand"].keys())[0]
                stand_data = data_stand_forecast["Stand"][sample_date]
                fig = generate_modern_graph(
                    stand_data,
                    "Heure",
                    "Stands occupés",
                    "Occupation des Stands"
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Graphique Piste
            if "Piste" in data_piste_forecast:
                sample_date = list(data_piste_forecast["Piste"].keys())[0]
                piste_data = data_piste_forecast["Piste"][sample_date]
                fig = generate_modern_graph(
                    piste_data,
                    "Heure",
                    "Mouvements",
                    "Mouvements de piste",
                    "#10B981"
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Détails des opérations aéroportuaires")

        # Sélection de date
        selected_date = st.date_input(
            "Sélectionner une date",
            value=start_date,
            min_value=start_date,
            max_value=end_date
        )

        date_str = selected_date.strftime("%Y-%m-%d")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🛫 Piste")
            if "Piste" in data_piste_forecast and date_str in data_piste_forecast["Piste"]:
                piste_data = data_piste_forecast["Piste"][date_str]
                fig = generate_modern_graph(
                    piste_data,
                    "Heure",
                    "Mouvements/heure",
                    f"Mouvements Piste - {selected_date.strftime('%d/%m/%Y')}"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Métriques
                st.metric("Max mouvements/h", max(piste_data))
                st.metric("Moyenne", f"{sum(piste_data)/len(piste_data):.1f}")
            else:
                st.info("Pas de données disponibles pour cette date")

        with col2:
            st.markdown("### 🅿️ Stands")
            if "Stand" in data_stand_forecast and date_str in data_stand_forecast["Stand"]:
                stand_data = data_stand_forecast["Stand"][date_str]
                fig = generate_modern_graph(
                    stand_data,
                    "Heure",
                    "Stands occupés",
                    f"Occupation Stands - {selected_date.strftime('%d/%m/%Y')}",
                    "#F59E0B"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Métriques
                st.metric("Max stands occupés", max(stand_data))
                st.metric("Taux d'occupation", f"{(max(stand_data)/standTot)*100:.1f}%")

    with tab3:
        st.subheader("Flux passagers et capacités")

        selected_process = st.selectbox(
            "Sélectionner un processeur",
            graph_names_list,
            index=0
        )

        # Trouver la catégorie
        category = None
        for cat, items in graph_names.items():
            if selected_process in items:
                category = cat
                break

        if category in ["Sûreté", "Check-in", "Douane"]:
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

            processeur = selected_process.split(" : ")[0] if " : " in selected_process else selected_process

            # Sélection de date
            selected_date = st.date_input(
                "Date d'analyse",
                value=start_date,
                min_value=start_date,
                max_value=end_date,
                key="passenger_date"
            )
            date_str = selected_date.strftime("%Y-%m-%d")

            if processeur in data and date_str in data[processeur]:
                demande = data[processeur][date_str]
                capacite = planning[processeur].get(date_str, [0] * len(demande))

                # Graphique comparaison
                fig = generate_comparison_graph(
                    demande,
                    capacite,
                    "Heure",
                    "Passagers",
                    f"{selected_process} - {selected_date.strftime('%d/%m/%Y')}",
                    "Demande",
                    "Capacité"
                )
                st.plotly_chart(fig, use_container_width=True)

                # KPIs
                queue = calcul_queue(demande, capacite)
                attente = calcul_attente(queue, capacite)
                attente_moyenne = calcul_attente_moyenne(attente)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("File max", f"{max(queue):.0f} pax")
                with col2:
                    st.metric("Attente max", f"{max(attente):.1f} min")
                with col3:
                    st.metric("Attente moy", f"{attente_moyenne:.1f} min")
                with col4:
                    # Status basé sur l'attente moyenne
                    if attente_moyenne <= 5:
                        st.markdown('<div class="status-green">Excellent</div>', unsafe_allow_html=True)
                    elif attente_moyenne <= 10:
                        st.markdown('<div class="status-yellow">Correct</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="status-red">Critique</div>', unsafe_allow_html=True)
            else:
                st.info("Pas de données disponibles pour ce processeur à cette date")

    with tab4:
        st.subheader("Analyse et tendances")

        st.markdown("### 📈 Tendances hebdomadaires")

        # Calculer les tendances sur la période
        if st.session_state.toggle_rip == "reel":
            planning = planning_surete_reel
        elif st.session_state.toggle_rip == "ideal":
            planning = planning_surete_ideal
        else:
            planning = planning_surete_perso

        colors = compute_colors(data_surete, planning, Thresholds_dict, st.session_state.toggle_rip)

        # Compter les jours par couleur
        status_counts = {"green": 0, "yellow": 0, "red": 0}
        for date_str, day_colors in colors.items():
            color = worst_color(day_colors)
            status_counts[color] += 1

        # Graphique en camembert
        fig = go.Figure(data=[go.Pie(
            labels=['Excellent', 'Acceptable', 'Critique'],
            values=[status_counts['green'], status_counts['yellow'], status_counts['red']],
            hole=.4,
            marker_colors=['#10B981', '#F59E0B', '#EF4444']
        )])

        fig.update_layout(
            title="Distribution des jours par statut de performance",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Statistiques
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #10B981;">
                <div class="metric-value" style="color: #10B981;">{status_counts['green']}</div>
                <div class="metric-label">Jours Excellents</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #F59E0B;">
                <div class="metric-value" style="color: #F59E0B;">{status_counts['yellow']}</div>
                <div class="metric-label">Jours Acceptables</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #EF4444;">
                <div class="metric-value" style="color: #EF4444;">{status_counts['red']}</div>
                <div class="metric-label">Jours Critiques</div>
            </div>
            """, unsafe_allow_html=True)

def display_calendar():
    """Affiche le calendrier avec les couleurs de statut"""

    st.markdown('<div class="dcb-header"><h1>📅 Calendrier DCB</h1><p>Vue calendrier des performances</p></div>', unsafe_allow_html=True)

    # Calculer les couleurs
    if st.session_state.toggle_rip == "reel":
        planning = planning_surete_reel
    elif st.session_state.toggle_rip == "ideal":
        planning = planning_surete_ideal
    else:
        planning = planning_surete_perso

    colors = compute_colors(data_surete, planning, Thresholds_dict, st.session_state.toggle_rip)

    current_date = start_month_date

    while current_date <= end_date:
        st.subheader(f"{FRENCH_MONTHS[current_date.month - 1]} {current_date.year}")

        cal = calendar.monthcalendar(current_date.year, current_date.month)

        # En-têtes
        cols = st.columns(7)
        days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        for i, day in enumerate(days):
            cols[i].markdown(f"**{day}**")

        # Jours
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown("")
                else:
                    date = datetime.date(current_date.year, current_date.month, day)
                    if start_date <= date <= end_date:
                        date_str = date.strftime("%Y-%m-%d")

                        if date_str in colors:
                            day_color = worst_color(colors[date_str])
                            color_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[day_color]
                        else:
                            color_emoji = "⚪"

                        if cols[i].button(f"{day} {color_emoji}", key=f"day_{date_str}"):
                            st.session_state.selected_date = date_str
                            st.session_state.selected_layout = "details"
                            st.rerun()
                    else:
                        cols[i].markdown(f"{day}")

        if current_date.month == 12:
            current_date = datetime.date(current_date.year + 1, 1, 1)
        else:
            current_date = datetime.date(current_date.year, current_date.month + 1, 1)

        st.markdown("---")

def display_details():
    """Affiche les détails d'un jour sélectionné"""

    if st.button("← Retour"):
        st.session_state.selected_layout = "dashboard"
        st.rerun()

    if st.session_state.selected_date is None:
        st.warning("Aucune date sélectionnée")
        return

    date_str = st.session_state.selected_date
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    st.markdown(f'<div class="dcb-header"><h1>📊 Détails du {date.strftime("%d/%m/%Y")}</h1></div>', unsafe_allow_html=True)

    # Afficher les graphiques pour chaque processeur sélectionné
    for graph in st.session_state.selected_graphs:
        with st.expander(f"📈 {graph}", expanded=True):
            category = None
            for cat, items in graph_names.items():
                if graph in items:
                    category = cat
                    break

            if category in ["Sûreté", "Check-in", "Douane"]:
                data_dict = {"Sûreté": data_surete, "Check-in": data_checkin, "Douane": data_douane}
                planning_dict = {
                    "Sûreté": {"reel": planning_surete_reel, "ideal": planning_surete_ideal, "perso": planning_surete_perso},
                    "Check-in": {"reel": planning_checkin_reel, "ideal": planning_checkin_ideal, "perso": planning_checkin_perso},
                    "Douane": {"reel": planning_douane_reel, "ideal": planning_douane_ideal, "perso": planning_douane_perso}
                }

                data = data_dict[category]
                planning = planning_dict[category][st.session_state.toggle_rip]

                processeur = graph.split(" : ")[0] if " : " in graph else graph

                if processeur in data and date_str in data[processeur]:
                    demande = data[processeur][date_str]
                    capacite = planning[processeur].get(date_str, [0] * len(demande))

                    fig = generate_comparison_graph(
                        demande, capacite,
                        "Heure", "Passagers",
                        graph,
                        "Demande", "Capacité"
                    )
                    st.plotly_chart(fig, use_container_width=True)

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

# ==================== MAIN ====================

def main():
    global DATA_FOLDER, ASSETS_FOLDER

    if DATA_FOLDER is None:
        DATA_FOLDER = get_data_folder()
    if ASSETS_FOLDER is None:
        ASSETS_FOLDER = os.path.join(get_base_path(), 'assets')

    init_session_state()

    # Vérification des données
    if DATA_FOLDER is None:
        st.error("❌ Aucun dossier de données trouvé!")
        st.markdown("""
        ### Configuration requise

        L'application ne trouve pas le dossier contenant les données DCB.

        **Utilisez la page Administration pour :**
        1. Uploader les données (fichiers JSON ou fichiers WEBI)
        2. Exécuter le traitement des données

        **Répertoire actuel :** `{}`
        """.format(get_base_path()))
        return

    # Chargement des données
    if not st.session_state.data_loaded:
        try:
            with st.spinner("🔄 Chargement des données en cours..."):
                success = load_all_data()
                if success:
                    st.session_state.data_loaded = True
                    st.rerun()
                else:
                    st.error("❌ Le chargement des données a échoué.")
                    return
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
            st.info(f"📁 Dossier de données détecté : `{DATA_FOLDER}`")
            return

    if len(graph_names_list) == 0:
        st.error("❌ Les données n'ont pas été chargées correctement.")
        return

    # ==================== SIDEBAR MODERNE ====================

    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # Mode de vue
        view_mode = st.radio(
            "Vue",
            ["📊 Dashboard", "📅 Calendrier", "📋 Détails"],
            index=["dashboard", "calendar", "details"].index(st.session_state.selected_layout)
        )

        if view_mode == "📊 Dashboard":
            st.session_state.selected_layout = "dashboard"
        elif view_mode == "📅 Calendrier":
            st.session_state.selected_layout = "calendar"
        else:
            st.session_state.selected_layout = "details"

        st.markdown("---")

        # Type de données
        toggle_option = st.radio(
            "Type de données",
            ["🔮 Forecast", "📋 Schedule"],
            index=0 if st.session_state.toggle_value == "forecast" else 1
        )
        st.session_state.toggle_value = "forecast" if toggle_option == "🔮 Forecast" else "schedule"

        # Type de planning
        toggle_rip_option = st.radio(
            "Type de planning",
            ["📊 Réel", "⭐ Idéal", "✏️ Personnalisé"],
            index=["reel", "ideal", "perso"].index(st.session_state.toggle_rip)
        )
        st.session_state.toggle_rip = {"📊 Réel": "reel", "⭐ Idéal": "ideal", "✏️ Personnalisé": "perso"}[toggle_rip_option]

        st.markdown("---")

        # Sélection des processeurs
        st.markdown("### 🎯 Processeurs sélectionnés")

        if st.button("🗑️ Tout désélectionner"):
            st.session_state.selected_graphs = []
            st.rerun()

        for category, items in graph_names.items():
            with st.expander(f"{category} ({len(items)})"):
                for item in items:
                    is_selected = item in st.session_state.selected_graphs
                    if st.checkbox(item, key=f"check_{item}", value=is_selected):
                        if item not in st.session_state.selected_graphs:
                            st.session_state.selected_graphs.append(item)
                    else:
                        if item in st.session_state.selected_graphs:
                            st.session_state.selected_graphs.remove(item)

    # ==================== CONTENU PRINCIPAL ====================

    # Afficher l'écran d'accueil pour les nouveaux utilisateurs
    if st.session_state.show_welcome and st.session_state.first_visit:
        display_welcome()
    elif st.session_state.selected_layout == "dashboard":
        display_dashboard()
    elif st.session_state.selected_layout == "calendar":
        display_calendar()
    elif st.session_state.selected_layout == "details":
        display_details()

    # Bouton pour réafficher l'écran d'accueil
    with st.sidebar:
        st.markdown("---")
        if st.button("ℹ️ Aide & Guide", use_container_width=True):
            st.session_state.show_welcome = True
            st.rerun()

if __name__ == "__main__":
    main()
