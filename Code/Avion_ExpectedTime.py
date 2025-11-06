import pandas as pd
import tqdm 
import numpy as np
from datetime import datetime, timedelta

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
#from sklearn.model_selction import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression

import xgboost as xgb
from xgboost import plot_importance
from pathlib import Path
import os 
import json
import re
import shutil

def first_change(data):
    
    # --------------------------------------------------
    # On modifie certaines données pour avoir une forme convenable
    # --------------------------------------------------

    data["Months"] = data["Local Schedule Time_ARR"].dt.month
    data["Weekday"] = data["Local Schedule Time_ARR"].dt.weekday
    data["Week"] = data["Local Schedule Time_ARR"].dt.isocalendar().week
    data["ZONE"] = "SC"
    """
    On favorise les departs parce que les GCO ils vont donner preference aux departs avant les arrivées.
    """
    data.loc[data['French Sector_DEP']== "Y", "ZONE"] = "FR"
    data.loc[data['Schengen Flight_DEP']== "N", "ZONE"] = "NSC"
    
    data['Night Stop_OOP+'] = 'Y'
    data.loc[data['Date_DEP'] == data['Date_ARR'], 'Night Stop_OOP+'] = 'N'
    data_ns = data.loc[data['Night Stop_OOP+'] == 'N'].copy()
    
    data.sort_values(by = 'Local Schedule Time_ARR', inplace = True)
    data = data.drop_duplicates()
    
    return data, data_ns




def get_matrice_data (data) :
    """
    Fonction qui retourne les dictionaires du presense au sol pour chaque key jour YYYY-MM-DD value 
    presense au sol pour chaque 5 minutes pour toute la journée. Un dictionaire pour schedule et un 
    pour la prediction.
    """
    date_min = max(data["Local Schedule Time_ARR"].min().date(),datetime.now().date())
    date_max = data["Local Schedule Time_DEP"].max().replace(hour=23,minute=59)

    date_range = pd.date_range(date_min, date_max, freq = '5min')

    data_occupation_schedule, data_occupation_pred = {}, {}
    liste_jour1, liste_jour2, k = [0]*288, [0]*288, 0
    current_day = date_range[0].date()
    
    for date in tqdm.tqdm(date_range) :
        
        if current_day is None or date.date() != current_day:
            
            data_occupation_schedule[str(current_day)[:10]] = liste_jour1
            data_occupation_pred[str(current_day)[:10]] = liste_jour2
            liste_jour1, liste_jour2, k = [0]*288, [0]*288, 0
            current_day = date.date()
            
        liste1 = (data["Local Schedule Time_ARR"] < date + pd.Timedelta(minutes=10)) & (data["Local Schedule Time_DEP"] > date - pd.Timedelta(minutes=10))
        liste2 = (data["predictions_ARR"] < date + pd.Timedelta(minutes=10)) & (data["predictions_DEP"] > date - pd.Timedelta(minutes=10))
        
        liste_jour1[k], liste_jour2[k] = int(np.sum(liste1)), int(np.sum(liste2))
        k += 1

    data_occupation_schedule[str(current_day)[:10]] = liste_jour1
    data_occupation_pred[str(current_day)[:10]] = liste_jour2        

    return data_occupation_schedule, data_occupation_pred



def get_matrice_data_wing (data, dic = False) :
    """
    Fonction qui retourne les dictionaires du wingspan pour chaque key jour YYYY-MM-DD value 
    3 list avec wingspans code C,B premiere list, D deuxieme list, E troisieme list au sol pour
    chaque 5 minutes pour toute la journée. Un dictionaire pour schedule et un pour la prediction.
    """
    date_min = max(data["Local Schedule Time_ARR"].min().date(),datetime.now().date())
    date_max = data["Local Schedule Time_DEP"].max().replace(hour=23,minute=59)

    date_range = pd.date_range(date_min, date_max, freq = '5min')

    data_wing_pred, data_wing_schedule = {}, {}

    liste_C1, liste_D1, liste_E1, liste_C2, liste_D2, liste_E2 = [], [], [], [], [], []
    current_day = date_range[0].date()
    
    
    for date in tqdm.tqdm(date_range) :
        
        if current_day is None or date.date() != current_day:
            if dic:
                data_wing_schedule[str(current_day)[:10]] = {"Stand : C" : liste_C1, "Stand : D" : liste_D1, "Stand : E" : liste_E1}
                data_wing_pred[str(current_day)[:10]] = {"Stand : C" : liste_C2, "Stand : D" : liste_D2, "Stand : E" : liste_E2}
            else:
                data_wing_schedule[str(current_day)[:10]] = [liste_C1, liste_D1, liste_E1]
                data_wing_pred[str(current_day)[:10]] = [liste_C2, liste_D2, liste_E2]
            liste_C1, liste_C2, liste_D1, liste_D2, liste_E1, liste_E2 = [], [], [], [], [], []
            
            current_day = date.date()
            
            
        liste1 = (data["Local Schedule Time_ARR"] < date + pd.Timedelta(minutes=10)) & (data["Local Schedule Time_DEP"] > date - pd.Timedelta(minutes=10))
        liste2 = (data["predictions_ARR"] < date + pd.Timedelta(minutes=10)) & (data["predictions_DEP"] > date - pd.Timedelta(minutes=10))
        
        data_local1, data_local2 = data.loc[liste1].copy(), data.loc[liste2].copy()
        
        liste_C1.append(int(np.sum(data_local1["Wingspan Code"].isin(['C', 'B', 'ND', None]))))
        liste_D1.append(int(np.sum(data_local1["Wingspan Code"] == "D")))
        liste_E1.append(int(np.sum(data_local1["Wingspan Code"] == "E")))
        
        liste_C2.append(int(np.sum(data_local2["Wingspan Code"].isin(['C', 'B', 'ND', None]))))
        liste_D2.append(int(np.sum(data_local2["Wingspan Code"] == "D")))
        liste_E2.append(int(np.sum(data_local2["Wingspan Code"] == "E")))
    if dic:
        data_wing_schedule[str(current_day)[:10]] = {"Stand : C" : liste_C1, "Stand : D" : liste_D1, "Stand : E" : liste_E1}
        data_wing_pred[str(current_day)[:10]] = {"Stand : C" : liste_C2, "Stand : D" : liste_D2, "Stand : E" : liste_E2}
    else:
        data_wing_schedule[str(current_day)[:10]] = [liste_C1, liste_D1, liste_E1]
        data_wing_pred[str(current_day)[:10]] = [liste_C2, liste_D2, liste_E2]
    
    return data_wing_pred, data_wing_schedule

def exclude_outliers(group, variable0):

    global liste

    q2 = group[variable0].quantile(0.025)
    q3 = group[variable0].quantile(0.975)

    max_group = max(group[variable0])
    min_group = min(group[variable0])

    if (max_group > 1.3 * q3) :
        liste.append(group[group[variable0] >= q3].index)

    if (min_group < 0.7 * q2) :
        liste.append(group[group[variable0] <= q2].index)
        

def algo(data, data_test_future, n_xgb, n_rf, m_xgb, m_rf, value, variable, eta0 = 0.4):

    global liste
    
    name = data.columns.tolist()
    name.remove(variable)

    name.remove("VID")
    liste_vid = list(data["VID"])
    data.drop('VID', axis=1, inplace=True)
    
    X_train = data[name]
    y_train = data[variable]

    model = DecisionTreeRegressor(min_samples_leaf=max(1,int(0.05 * len(X_train))))

    model.fit(X_train, y_train)

    y_pred_train = model.predict(X_train)

    data["leaf"] = model.apply(X_train)  
    data["y_pred"] = y_pred_train

    
    # Créer un boxplot pour chaque feuille
    liste = []
    data.groupby("leaf").apply(exclude_outliers, variable0 = variable)
    liste = [element for sous_liste in liste for element in sous_liste]

    ind = {"indexes" : list(data.index),
              "indices" : range(len(data.index))}

    liste = [ind["indices"][ind["indexes"].index(element)] for element in liste]

    liste_outlier = [0]*len(data)

    for i in liste :
        liste_outlier[i] = 1

    data["outlier"] = liste_outlier
    data["VID"] = liste_vid
    data = data.loc[data["outlier"]==0]


    data.drop(["leaf", "y_pred", "outlier"], axis=1, inplace=True)

    data.head()

    # Algo

    name = data.columns.tolist()
    name.remove(variable)
    name.remove('VID')

    X_train = data[name]
    y_train = data[variable]


    liste_vid_keep = data_test_future['VID']
    data_test_future = data_test_future.drop(columns = 'VID')


    # Random Forest
    # ---------------------------

    modele_rf = RandomForestRegressor(n_estimators=n_rf, max_depth = m_rf)

    modele_rf.fit(X_train, y_train)
    y_test_predict = modele_rf.predict(data_test_future)


    # XGBoost
    # ---------------------------

    modele_xgb = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=n_xgb, max_depth=m_xgb, eta = eta0)

    modele_xgb.fit(X_train, y_train)
    predictions = modele_xgb.predict(data_test_future)


    # Final 
    # ---------------------------

    pred = y_test_predict*(1 - value) + predictions* value


    
    return data_test_future, pred, liste_vid_keep

def deplacer_fichier(nom_cible, super_dossier, sous_dossier = None):
    # Obtenir le chemin absolu des dossiers
    chemin_actuel = os.path.join(super_dossier, 'Actuel')
    chemin_historique = os.path.join(super_dossier, 'Historique')
    if sous_dossier:
        chemin_historique = os.path.join(chemin_historique,sous_dossier)

    # Expression régulière : date + nom + date-date.json
    pattern = re.compile(rf'^(\d{{12}}){re.escape(nom_cible)}(\d{{8}}-\d{{8}})\.json$')

    # Parcourir les fichiers du dossier Actuel
    for fichier in os.listdir(chemin_actuel):
        if pattern.match(fichier):
            source = os.path.join(chemin_actuel, fichier)
            destination = os.path.join(chemin_historique, fichier)
            shutil.move(source, destination)
            print(f"Fichier déplacé : {fichier}")
            return

    print(f"Aucun fichier correspondant à '{nom_cible}' trouvé dans '{chemin_actuel}'.")

def Delai(conversion, conversion_airline, data, data_future):

    # --------------------------------------
    # Infos about distance 
    # --------------------------------------
    distance = pd.read_csv("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Autre/Distance.csv")
    conversion_aero = pd.read_excel("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Autre/Conversion_aero.xlsx")

    distance = distance.loc[distance["DEST"]=="GVA"]

    distance = dict(zip(distance['ORIGIN'], distance['DISTANCE IN MILES']))
    conversion_aero = dict(zip(conversion_aero['Official ICAO Airport Code'], conversion_aero['Official IATA Airport Code']))

    correspondance = {"AJA" : 526,
                    "ATH" : 6861,
                    "AYT" : 2291,
                    "BDS" : 5383,
                    "DJE" : 175,
                    "DME" : 2430,
                    "GVA" : 0,
                    "HER" : 4855,
                    "HRG" : 3226,
                    "KGS" : 2031,
                    "KLX" : 1666,
                    "LCY" : 734,
                    "LED" : 2190,
                    "OLB" : 7846,
                    "OSL" : 1588,
                    "PDL" : 2772,
                    "SKG" : 1502,
                    "ZAG" : 772,
                    "ZTH" : 1541,
                    "ACE" : 343.92,
                    "ADB" : 1938.56,
                    "AGA" : 2221.46,
                    "AHO" : 648.28,
                    "AOI" : 641.68,
                    "AQJ" : 3112.9,
                    "BEG" : 1116.6,
                    "BIA" : 474.94,
                    "BIO" : 787.25,
                    "SUF" : 745.5,
                    "CAG" : 814.15,
                    "CHQ" : 1922.47,
                    "CLY" : 515.99,
                    "ERF" : 636.9,
                    "FNI" : 306.45,
                    "FSC" : 578.45,
                    "FUE" : 2639.27,
                    "LCG" : 1188.81,
                    "LIL" : 538.7,
                    "LPA" : 2774.33,
                    "LRH" : 562.18,
                    "NBE" : 1187.19,
                    "NTE" : 597.63,
                    "PUY" : 197.87,
                    "QLA" : 3791.97,
                    "RNS" : 370.32,
                    "SCQ" : 1208.52,
                    "SKP" : 1325.63,
                    "RBA" : 1745.22,
                    "EPL" : 232.23,
                    "ALG" : 1088.18,
                    "BEY" : 2837.2,
                    "SAW" : 1955.57,
                    "MRU" : 1644.96,
                    "ASR" : 2534.94,
                    "TUN" : 1099.38}

    # --------------------------------------
    # Traitements de données
    # --------------------------------------

    # On redéfinit le data future avec les bonnes dates souhaitées
    data["Aircraft Subtype IATA Type"] = data["Aircraft Subtype IATA Type"].astype(str)
    data_future["Aircraft Subtype IATA Type"] = data_future["Aircraft Subtype IATA Type"].astype(str)
    data_future['VID'] = [-1 * k for k in range(1,len(data_future)+1)]

    # Préparation du data Future --> Pour l'output

    data_future = data_future.loc[(~data_future['Local Schedule Time_ARR'].isna())&(~data_future['Local Schedule Time_DEP'].isna())]
    data_future['Local Schedule Time_ARR'] = pd.to_timedelta(data_future['Local Schedule Time_ARR'] + ':00') + data_future['Date_ARR']
    data_future['Local Schedule Time_DEP'] = pd.to_timedelta(data_future['Local Schedule Time_DEP'] + ':00') + data_future['Date_DEP']

    # -----------------------------
    # Traitement pour l'algorithme
    # -----------------------------

    # 1) Les temps
    # -----------------------------

    data.dropna(subset=['Local Schedule Time_DEP'], inplace=True)
    data.dropna(subset=['Local Schedule Time_ARR'], inplace=True)

    data[['Local TOBT Time', 'Local Actual Time_DEP', 'Local Actual Time_ARR']] = data[['Local TOBT Time', 'Local Actual Time_DEP', 'Local Actual Time_ARR']].fillna('00:00')
    data[['Local TOBT Time', 'Local Actual Time_DEP', 'Local Actual Time_ARR']] = data[['Local TOBT Time', 'Local Actual Time_DEP', 'Local Actual Time_ARR']].replace('ND', '00:00')

    data["Local Schedule Time_DEP"] = pd.to_timedelta(data["Local Schedule Time_DEP"] + ":00") + data["Date_DEP"]
    data["Local Schedule Time_ARR"] = pd.to_timedelta(data["Local Schedule Time_ARR"] + ":00") + data["Date_ARR"]
    data["Local Actual Time_DEP"] = pd.to_timedelta(data["Local Actual Time_DEP"] + ":00") + data["Date_DEP"]
    data["Local Actual Time_ARR"] = pd.to_timedelta(data["Local Actual Time_ARR"] + ":00") + data["Date_ARR"]
    data["Local TOBT Time"] = pd.to_timedelta(data["Local TOBT Time"] + ":00") + data["Date_DEP"]

    data = data.sort_values(by='Local Actual Time_ARR')



    # 2) Les destinations
    # -----------------------------

    data["Official IATA Airport Code_DEP"] = data["Official IATA Airport Code_DEP"].replace(conversion_aero)
    data["Official IATA Airport Code_DEP"] = data["Official IATA Airport Code_DEP"].replace(distance)
    data["Official IATA Airport Code_DEP"] = data["Official IATA Airport Code_DEP"].replace(correspondance)

    data["Official IATA Airport Code_ARR"] = data["Official IATA Airport Code_ARR"].replace(conversion_aero)
    data["Official IATA Airport Code_ARR"] = data["Official IATA Airport Code_ARR"].replace(distance)
    data["Official IATA Airport Code_ARR"] = data["Official IATA Airport Code_ARR"].replace(correspondance)

    data = data.loc[data['Official IATA Airport Code_ARR'] != '22*']
    data = data.loc[data['Official IATA Airport Code_DEP'] != '22*'] 

    data.loc[data["Official IATA Airport Code_DEP"].astype(str).str.isalpha(), "Official IATA Airport Code_DEP"] = 500
    data.loc[data["Official IATA Airport Code_ARR"].astype(str).str.isalpha(), "Official IATA Airport Code_ARR"] = 500

    data["Official IATA Airport Code_ARR"] = data["Official IATA Airport Code_ARR"].astype(int)
    data["Official IATA Airport Code_DEP"] = data["Official IATA Airport Code_DEP"].astype(int)

    data_future["Official IATA Airport Code_DEP"] = data_future["Official IATA Airport Code_DEP"].replace(conversion_aero)
    data_future["Official IATA Airport Code_DEP"] = data_future["Official IATA Airport Code_DEP"].replace(distance)
    data_future["Official IATA Airport Code_DEP"] = data_future["Official IATA Airport Code_DEP"].replace(correspondance)

    data_future["Official IATA Airport Code_ARR"] = data_future["Official IATA Airport Code_ARR"].replace(conversion_aero)
    data_future["Official IATA Airport Code_ARR"] = data_future["Official IATA Airport Code_ARR"].replace(distance)
    data_future["Official IATA Airport Code_ARR"] = data_future["Official IATA Airport Code_ARR"].replace(correspondance)

    data_future = data_future.loc[data_future['Official IATA Airport Code_ARR'] != '22*']
    data_future = data_future.loc[data_future['Official IATA Airport Code_DEP'] != '22*'] 

    data_future.loc[data_future["Official IATA Airport Code_DEP"].astype(str).str.isalpha(), "Official IATA Airport Code_DEP"] = 500
    data_future.loc[data_future["Official IATA Airport Code_ARR"].astype(str).str.isalpha(), "Official IATA Airport Code_ARR"] = 500

    data_future["Official IATA Airport Code_ARR"] = data_future["Official IATA Airport Code_ARR"].astype(int)
    data_future["Official IATA Airport Code_DEP"] = data_future["Official IATA Airport Code_DEP"].astype(int)


    # 4) Pour les PAX
    # -----------------------------

    data["Pax_DEP"] = data["Pax_DEP"].fillna(0)
    data["Pax_ARR"] = data["Pax_ARR"].fillna(0)
    data["Capacity"] = data["Capacity"].replace("ND",0)

    data["LF_depart"] = data["Pax_DEP"] / data["Capacity"] * 100
    data.loc[data["Capacity"] == 0,"LF_depart"] = 0

    data["LF_arrivee"] = data["Pax_ARR"] / data["Capacity"] * 100
    data.loc[data["Capacity"] == 0,"LF_arrivee"] = 0

    data_future["Pax_DEP"] = data_future["Pax_DEP"].fillna(0)
    data_future["Pax_ARR"] = data_future["Pax_ARR"].fillna(0)
    data_future["Capacity"] = data_future["Capacity"].replace("ND",0)

    data_future["LF_depart"] = data_future["Pax_DEP"] / data_future["Capacity"] * 100
    data_future.loc[data_future["Capacity"] == 0,"LF_depart"] = 0

    data_future["LF_arrivee"] = data_future["Pax_ARR"] / data_future["Capacity"] * 100
    data_future.loc[data_future["Capacity"] == 0,"LF_arrivee"] = 0

    # 5) CREATION ETT, STT, TT, A_Delay, ...
    # ---------------------------------------

    data["STT"] =  data["Local Schedule Time_DEP"] - data["Local Schedule Time_ARR"]
    data["TT"] = data["Local Actual Time_DEP"] - data["Local Actual Time_ARR"] #data["Local TOBT Time"] - data["Local Actual Time_ARR"]
    data["A_Delay"] = data["Local Actual Time_ARR"] - data["Local Schedule Time_ARR"]

    data['STT'] = data['STT'].dt.total_seconds() / 60
    data['TT'] = data['TT'].dt.total_seconds() / 60
    data["A_Delay"] = data["A_Delay"].dt.total_seconds() / 60

    data['WeekDay'] = data['Date_DEP'].dt.dayofweek
    data['Months'] = data['Date_DEP'].dt.month
    data["Hour"] = data["Local Schedule Time_DEP"].dt.hour

    data_future["STT"] =  data_future["Local Schedule Time_DEP"] - data_future["Local Schedule Time_ARR"]

    data_future['STT'] = data_future['STT'].dt.total_seconds() / 60

    data_future['WeekDay'] = data_future['Date_DEP'].dt.dayofweek
    data_future['Months'] = data_future['Date_DEP'].dt.month
    data_future["Hour"] = data_future["Local Schedule Time_DEP"].dt.hour

    # 6) Congestion
    # ---------------------------------------

    liste = []

    for time_arrival in tqdm.tqdm(data["Local Schedule Time_ARR"]) :
        borne_inf = time_arrival - timedelta(minutes = 30)
        borne_sup = time_arrival + timedelta(minutes = 30)
        liste.append(np.sum((data["Local Schedule Time_ARR"] < borne_sup) 
                            & (data["Local Schedule Time_ARR"] > borne_inf)))
        
    data["Congestion"] = liste

    liste = []

    for time_arrival in tqdm.tqdm(data_future["Local Schedule Time_ARR"]) :
        borne_inf = time_arrival - timedelta(minutes = 30)
        borne_sup = time_arrival + timedelta(minutes = 30)
        liste.append(np.sum((data_future["Local Schedule Time_ARR"] < borne_sup) 
                            & (data_future["Local Schedule Time_ARR"] > borne_inf)))
        
    data_future["Congestion"] = liste

    # 7) MTOW
    # ---------------------------------------

    data_future["MTOW"] = 0

    for airline in tqdm.tqdm(data_future["Airline IATA Code"].unique()) :
        data_future_local = data_future.loc[data_future["Airline IATA Code"] == airline].copy()
        
        for aircraft in data_future_local["Aircraft Subtype IATA Type"].unique():

            data_future_conversion = conversion.loc[(conversion["Airline IATA Code"] == airline) & (conversion["Aircraft Subtype IATA Type"] == aircraft)]
            if len(data_future_conversion) == 0 :
                #print("Il manque le MTOW de l'avion " + aircraft + " de l'airline " + airline)
                data_future_conversion = conversion[conversion["Aircraft Subtype IATA Type"] == aircraft]
                if len(data_future_conversion) != 0:
                    mtow = int(round(data_future_conversion["MTOW"].mean(),0))
                else:
                    if aircraft == "75C":
                        mtow = 93
                    elif aircraft == "AT4":
                        mtow = 17
            else : 
                mtow = data_future_conversion["MTOW"].iloc[0]
            data_future.loc[(data_future["Airline IATA Code"] == airline) & (data_future["Aircraft Subtype IATA Type"] == aircraft), "MTOW"] = mtow

                
    # 8) Airline
    # ---------------------------------------

    data = pd.merge(data, conversion_airline, on = ['Airline IATA Code'], how = 'left')
    data['Airline IATA Code'] = data['count'].copy()
    data.drop(columns = ['count'], inplace = True)
    data.loc[data['Airline IATA Code'].isna(),"Airline IATA Code"] = 0

    data["Airline IATA Code"] = data["Airline IATA Code"].astype(int)

    data_future = pd.merge(data_future, conversion_airline, on = ['Airline IATA Code'], how = 'left')
    data_future['Airline IATA Code'] = data_future['count'].copy()
    data_future.drop(columns = ['count'], inplace = True)
    data_future.loc[data_future['Airline IATA Code'].isna(),"Airline IATA Code"] = 0

    data_future["Airline IATA Code"] = data_future["Airline IATA Code"].astype(int)

    # 9) Pour le Subtype
    # ---------------------------------------

    label_encoder_aircraft = LabelEncoder()
    label_encoder_aircraft.fit(data["Aircraft Subtype IATA Type"].to_list()+data_future["Aircraft Subtype IATA Type"].to_list())
    data["Aircraft Subtype IATA Type"] = label_encoder_aircraft.transform(data["Aircraft Subtype IATA Type"])
    data_future["Aircraft Subtype IATA Type"] = label_encoder_aircraft.transform(data_future["Aircraft Subtype IATA Type"])


    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------
    # Temps au sol
    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------

    saisons_a_prevoir = data_future["Season"].drop_duplicates().to_list()

    data_original = data.copy()

    data = data[data["Retard non GA_DEP"] == 0]

    data = data[(data["TT"] >= 30) & (data["TT"] <= 130)]
    data = data[(data["A_Delay"] >= -30) & (data["A_Delay"] <= 50)]

    liste_columns = ["TT", "WeekDay", "Months", "Hour", "STT", 
                "Official IATA Airport Code_DEP", "Official IATA Airport Code_ARR", 'Airline IATA Code',
                "LF_depart", "LF_arrivee", "Aircraft Subtype IATA Type", 
                'VID', 'MTOW', 'Season']

    data = data[liste_columns] 
    data_test_future = data_future[liste_columns[1:]]
    data_test_future1 = pd.DataFrame(columns=['VID','pred_tt'])
    for saison in saisons_a_prevoir:
        data_saison = data.loc[data['Season'] == saison].copy()

        data_test_future_saison = data_test_future.loc[data_test_future['Season'] == saison].copy()

        data_saison.drop(columns =['Season'], inplace = True)

        data_test_future_saison.drop(columns =['Season'], inplace = True)

        data_test_future_saison = data_test_future_saison[(data_test_future_saison["STT"] <= 130) & (data_test_future_saison["STT"] >= 30)]


        data_test_future_saison = data_test_future_saison.loc[~data_test_future_saison['LF_depart'].isna()]
        data_test_future_saison = data_test_future_saison.loc[~data_test_future_saison['LF_arrivee'].isna()]

        # ---------

        data_test_future0, pred, liste_vid_keep = algo(data_saison, data_test_future_saison, 110, 75, 3, 10, 0.7, 'TT')

        data_test_future0['pred_tt'] = pred
        data_test_future0['VID'] = liste_vid_keep
        data_test_future0 = data_test_future0[['VID', 'pred_tt']]

        data_test_future1 = pd.concat([data_test_future1, data_test_future0], ignore_index = True)

    data_future = pd.merge(data_future, data_test_future1, on = 'VID', how = 'left')



    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------
    # Retards
    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------
    data = data_original.copy()

    data = data[(data["A_Delay"] >= -90) & (data["A_Delay"] <= 120)]

    label_encoder_cs = LabelEncoder()
    label_encoder_cs.fit(data["Call Sign - IATA_ARR"].to_list()+data_future["Call Sign - IATA_ARR"].to_list())
    data["Call Sign - IATA_ARR"] = label_encoder_cs.transform(data["Call Sign - IATA_ARR"])

    label_encoder_schengen = LabelEncoder()
    label_encoder_schengen.fit(data["Schengen Flight_ARR"].to_list()+data_future["Schengen Flight_ARR"].to_list())
    data["Schengen Flight_ARR"] = label_encoder_schengen.transform(data["Schengen Flight_ARR"])

    label_encoder_french = LabelEncoder()
    label_encoder_french.fit(data["French Sector_ARR"].to_list()+data_future["French Sector_ARR"].to_list())
    data["French Sector_ARR"] = label_encoder_french.transform(data["French Sector_ARR"])

    liste_columns = ['A_Delay', 'Call Sign - IATA_ARR', 'Schengen Flight_ARR', 'French Sector_ARR',
                    'Airline IATA Code', 'Official IATA Airport Code_ARR', 
                'VID', 'WeekDay', 'Months', 'Hour', 'Congestion', 'MTOW',
                    'LF_arrivee', 'Season']

    data = data[liste_columns]
    data_test_future = data_future[liste_columns[1:]]
    data_test_future["Call Sign - IATA_ARR"] = label_encoder_cs.transform(data_test_future["Call Sign - IATA_ARR"])
    data_test_future["Schengen Flight_ARR"] = label_encoder_schengen.transform(data_test_future["Schengen Flight_ARR"])
    data_test_future["French Sector_ARR"] = label_encoder_french.transform(data_test_future["French Sector_ARR"])
    data_test_future1 = pd.DataFrame(columns=['VID', 'pred_delay'])
    for saison in saisons_a_prevoir:
        data_saison = data.loc[data['Season'] == saison].copy()

        data_test_future_saison = data_test_future.loc[data_test_future['Season'] == saison].copy()
        data_test_future_saison = data_test_future_saison.loc[data_test_future_saison['LF_arrivee'].isna() == False]

        data_saison.drop(columns =['Season'], inplace = True)

        data_test_future_saison.drop(columns =['Season'], inplace = True)

        data_test_future0, pred, liste_vid_keep = algo(data_saison, data_test_future_saison, 100, 110, 3, 9, 0.8, 'A_Delay')
        data_test_future0['pred_delay'] = pred
        data_test_future0['VID'] = liste_vid_keep
        data_test_future0 = data_test_future0[['VID', 'pred_delay']]
        print(32)
        print(data_test_future0)
        data_test_future1 = pd.concat([data_test_future1, data_test_future0], ignore_index = True)
    data_future = pd.merge(data_future, data_test_future1, on = 'VID', how = 'left')


    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------
    # Final
    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------
    """
    Prediction arrival = schedule arrival time + pred_delay
    Prediction depart = Prediction arrival + pred_tt
    """
    data_future["Aircraft Subtype IATA Type"] = label_encoder_aircraft.inverse_transform(data_future["Aircraft Subtype IATA Type"])
    data_future.loc[~data_future["pred_tt"].isna(), 'pred_tt'] = data_future.loc[~data_future["pred_tt"].isna(), 'pred_tt'].apply(lambda x: timedelta(minutes=int(x)))
    data_future.loc[~data_future["pred_delay"].isna(), 'pred_delay'] = data_future.loc[~data_future["pred_delay"].isna(), 'pred_delay'].apply(lambda x: timedelta(minutes=int(x)))
    data_future.loc[data_future["pred_tt"].isna(), 'pred_tt'] = timedelta(minutes = 0)
    data_future.loc[data_future["pred_delay"].isna(), 'pred_delay'] = timedelta(minutes = 0)

    data_future['predictions_ARR'] = data_future['Local Schedule Time_ARR'] + data_future['pred_delay']

    data_future.loc[data_future['pred_tt'] != timedelta(minutes = 0), 'predictions_DEP'] = data_future.loc[data_future['pred_tt'] != timedelta(minutes = 0), 'predictions_ARR'] + data_future.loc[data_future['pred_tt'] != timedelta(minutes = 0), 'pred_tt']
    data_future.loc[data_future['pred_tt'] == timedelta(minutes = 0), 'predictions_DEP'] = data_future.loc[data_future['pred_tt'] == timedelta(minutes = 0), 'Local Schedule Time_DEP']

    data, data_ns = first_change(data_future)
    data.to_csv('//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Output/Expected_Time.csv', index=False)

    data_occupation_schedule, data_occupation_pred = get_matrice_data(data)
    data_wing_pred, data_wing_schedule = get_matrice_data_wing(data_ns)

    nouveau_repertoire = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/7_LOUISE/DCB LLA/Creation_Fichiers")
    os.chdir(nouveau_repertoire)

    with open("data_occupation_schedule.json", "w") as f:
        json.dump(data_occupation_schedule, f)

    with open("data_occupation_pred.json", "w") as f:
        json.dump(data_occupation_pred, f)

    with open("data_wing_schedule.json", "w") as f:
        json.dump(data_wing_schedule, f)

    with open("data_wing_pred.json", "w") as f:
        json.dump(data_wing_pred, f)

    BSH_wing_pred, BSH_wing_schedule = get_matrice_data_wing(data,True)
    dates = list(BSH_wing_pred.keys())
    mnt = datetime.now().strftime(format="%Y%m%d%H%M")
    first_date = dates[0].replace("-","")
    last_date = dates[len(dates)-1].replace("-","")
    fn = "ForecastStandUtilisation"
    sn = "ScheduleStandUtilisation"
    forecast_name = mnt + fn + first_date + "-" + last_date + ".json"
    schedule_name = mnt + sn + first_date + "-" + last_date + ".json"

    # Exemple d'utilisation
    super_dossier = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/Data Source/Demande"
    deplacer_fichier(fn,super_dossier,"Stand/Forecast")
    deplacer_fichier(sn,super_dossier,"Stand/Schedule")

    with open(os.path.join(super_dossier,"Actuel",forecast_name),"w") as f:
        json.dump(BSH_wing_pred,f)
    with open(os.path.join(super_dossier,"Actuel",schedule_name),"w") as f:
        json.dump(BSH_wing_schedule,f)

    return data