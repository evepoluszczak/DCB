"""
Application DCB - Demand Capacity Balancing
Version Streamlit - Safe Loading
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

# Configuration de la page
st.set_page_config(
    page_title="Outil DCB - Demand Capacity Balancing",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
post_ops = False

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_data_folder():
    """Détecte automatiquement le dossier de données disponible"""
    base_path = get_base_path()

    # Chemins locaux uniquement (pas de chemins réseau qui peuvent timeout)
    possible_paths = [
        os.path.join(base_path, "Data Source"),
        os.path.join(base_path, "DataSource"),
        os.path.join(base_path, "data"),
        os.path.join(base_path, "Data"),
    ]

    # Chercher le premier chemin qui existe
    for path in possible_paths:
        try:
            if os.path.exists(path) and os.path.isdir(path):
                return path
        except:
            continue

    return None

# Initialisation différée pour éviter les timeouts
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
    return [liste[i] * coef for i in range(len(liste))]

def list_sub(liste, base):
    return [liste[i] - base[i] for i in range(len(liste))]

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

def calcul_file_attente(data, planning):
    result = {}
    for processeur in data.keys():
        result[processeur] = {}
        for date in data[processeur].keys():
            demande = data[processeur][date]
            capacite = planning[processeur][date] if processeur in planning and date in planning[processeur] else [0] * len(demande)
            queue = calcul_queue(demande, capacite)
            attente = calcul_attente(queue, capacite)
            result[processeur][date] = {
                "queue": queue,
                "attente": attente
            }
    return result

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

            # Vérifier que les seuils existent avant de les utiliser
            if rip in Thresholds_dict and processeur in Thresholds_dict[rip]:
                KPIs = calcul_KPI(attente, capacite, Thresholds_dict[rip][processeur])
                colors[date_str][processeur] = KPI_to_color(KPIs)
            else:
                # Seuil par défaut si non trouvé
                colors[date_str][processeur] = "green"

    return colors

def worst_color(colors_dict):
    if "red" in colors_dict.values():
        return "red"
    elif "yellow" in colors_dict.values():
        return "yellow"
    else:
        return "green"

def value_to_color(value, min_val, max_val):
    if value < min_val:
        return "green"
    elif value < max_val:
        return "yellow"
    else:
        return "red"

def init_session_state():
    if 'selected_graphs' not in st.session_state:
        st.session_state.selected_graphs = []
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_layout' not in st.session_state:
        st.session_state.selected_layout = "calendar"
    if 'toggle_value' not in st.session_state:
        st.session_state.toggle_value = "forecast"
    if 'toggle_rip' not in st.session_state:
        st.session_state.toggle_rip = "reel"
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

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

def generate_graph(data, xaxis_title, yaxis_title, thresholds):
    import plotly.graph_objs as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        name='Données',
        line=dict(color='blue', width=2)
    ))
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode='x unified'
    )
    return fig

def generate_graph_multiple(data1, data2, xaxis_title, yaxis_title, thresholds, name1, name2):
    import plotly.graph_objs as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=data1, mode='lines', name=name1, line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(y=data2, mode='lines', name=name2, line=dict(color='red', width=2)))
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode='x unified'
    )
    return fig

def display_calendar(colors):
    """Affiche le calendrier avec les couleurs"""
    import plotly.graph_objs as go

    current_date = start_month_date

    while current_date <= end_date:
        st.subheader(f"{FRENCH_MONTHS[current_date.month - 1]} {current_date.year}")

        cal = calendar.monthcalendar(current_date.year, current_date.month)

        cols = st.columns(7)
        days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        for i, day in enumerate(days):
            cols[i].markdown(f"**{day}**")

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

def display_details(colors):
    """Affiche les détails d'un jour sélectionné"""
    import plotly.graph_objs as go

    if st.button("← Retour au calendrier"):
        st.session_state.selected_layout = "calendar"
        st.rerun()

    if st.session_state.selected_date is None:
        st.warning("Aucune date sélectionnée")
        return

    date_str = st.session_state.selected_date
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    st.subheader(f"Détails pour le {date.strftime('%d/%m/%Y')}")

    for graph in st.session_state.selected_graphs:
        with st.expander(graph, expanded=True):
            category = None
            for cat, items in graph_names.items():
                if graph in items:
                    category = cat
                    break

            if category == "Piste":
                data_dict = {"forecast": data_piste_forecast, "schedule": data_piste_schedule}
                data = data_dict[st.session_state.toggle_value]

                if graph in data and date_str in data[graph]:
                    values = data[graph][date_str]
                    fig = generate_graph(values, "Heure", "Nombre de mouvements", [])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données disponibles")

            elif category == "Stand":
                data_dict = {"forecast": data_stand_forecast, "schedule": data_stand_schedule}
                data = data_dict[st.session_state.toggle_value]

                if graph in data and date_str in data[graph]:
                    values = data[graph][date_str]
                    fig = generate_graph(values, "Heure", "Nombre de stands occupés", [])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données disponibles")

            elif category in ["Sûreté", "Check-in", "Douane"]:
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

                    fig = generate_graph_multiple(demande, capacite, "Heure", "Nombre de passagers", [], "Demande", "Capacité")
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

            elif category == "Gate":
                secteur = graph.split(" : ")[1] if " : " in graph else None

                if secteur and secteur in data_gate and date_str in data_gate[secteur]:
                    demande = data_gate[secteur][date_str]
                    fig = generate_graph(demande, "Heure", "Nombre de passagers au gate", [])
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

def main():
    global DATA_FOLDER, ASSETS_FOLDER

    # Initialiser les chemins
    if DATA_FOLDER is None:
        DATA_FOLDER = get_data_folder()
    if ASSETS_FOLDER is None:
        ASSETS_FOLDER = os.path.join(get_base_path(), 'assets')

    init_session_state()

    # Vérification de l'existence du dossier de données
    if DATA_FOLDER is None:
        st.error("❌ Aucun dossier de données trouvé!")
        st.markdown("""
        ### Configuration requise

        L'application ne trouve pas le dossier contenant les données DCB.

        **Options :**

        1. **Pour le développement local :** Créez un dossier nommé `Data Source` dans le répertoire de l'application

        2. **Pour Streamlit Cloud :** Utilisez la page Administration pour uploader les données ou exécuter le traitement

        3. **Générer les données localement :**
           ```bash
           cd TraitementDonnee/Code
           python Traitement_donnee.py
           ```

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
                else:
                    st.error("❌ Le chargement des données a échoué.")
                    return
        except FileNotFoundError as e:
            st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
            st.info(f"📁 Dossier de données détecté : `{DATA_FOLDER}`")
            st.markdown("""
            ### Vérifications à faire :

            1. Le dossier existe-t-il vraiment ?
            2. La structure des sous-dossiers est-elle correcte ?
            3. Les fichiers JSON ont-ils été générés par `Traitement_donnee.py` ?

            Consultez le README_STREAMLIT.md pour plus de détails.
            """)
            return
        except Exception as e:
            st.error(f"❌ Erreur inattendue : {str(e)}")
            st.exception(e)
            return

    # Vérifier que graph_names_list a bien été initialisé
    if len(graph_names_list) == 0:
        st.error("❌ Les données n'ont pas été chargées correctement (graph_names_list est vide).")
        st.markdown(f"""
        ### Debug Info
        - DATA_FOLDER: `{DATA_FOLDER}`
        - graph_names keys: `{list(graph_names.keys()) if graph_names else 'empty'}`
        - graph_names_list length: `{len(graph_names_list)}`

        Essayez d'aller sur la page Administration pour uploader de nouvelles données.
        """)
        return

    # Interface principale
    st.title("Outil DCB - Demand Capacity Balancing")

    # Sidebar pour la sélection
    with st.sidebar:
        st.header("Configuration")

        # Toggle Forecast/Schedule
        toggle_option = st.radio(
            "Type de données:",
            ["Forecast", "Schedule"],
            index=0 if st.session_state.toggle_value == "forecast" else 1
        )
        st.session_state.toggle_value = "forecast" if toggle_option == "Forecast" else "schedule"

        # Toggle Réel/Idéal/Perso
        toggle_rip_option = st.radio(
            "Type de planning:",
            ["Réel", "Idéal", "Personnalisé"],
            index=["reel", "ideal", "perso"].index(st.session_state.toggle_rip)
        )
        st.session_state.toggle_rip = {"Réel": "reel", "Idéal": "ideal", "Personnalisé": "perso"}[toggle_rip_option]

        st.markdown("---")

        # Sélection des processeurs
        st.subheader("Sélection des processeurs")

        for category, items in graph_names.items():
            with st.expander(f"{category} ({len(items)})"):
                for item in items:
                    if st.checkbox(item, key=f"check_{item}", value=item in st.session_state.selected_graphs):
                        if item not in st.session_state.selected_graphs:
                            st.session_state.selected_graphs.append(item)
                    else:
                        if item in st.session_state.selected_graphs:
                            st.session_state.selected_graphs.remove(item)

        if st.button("Tout désélectionner"):
            st.session_state.selected_graphs = []
            st.rerun()

    # Calculer les couleurs
    if st.session_state.toggle_rip == "reel":
        planning = planning_surete_reel
    elif st.session_state.toggle_rip == "ideal":
        planning = planning_surete_ideal
    else:
        planning = planning_surete_perso

    colors = compute_colors(data_surete, planning, Thresholds_dict, st.session_state.toggle_rip)

    # Affichage selon le layout sélectionné
    if st.session_state.selected_layout == "calendar":
        display_calendar(colors)
    elif st.session_state.selected_layout == "details":
        display_details(colors)
    elif st.session_state.selected_layout == "personnalisation":
        display_personnalisation()

if __name__ == "__main__":
    main()
