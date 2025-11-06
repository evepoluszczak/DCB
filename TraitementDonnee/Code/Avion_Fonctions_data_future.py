import os
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import tqdm

from pathlib import Path

import shutil
import re

def copier_et_renommer_fichiers(dossier_source, dossier_destination):
    """Récupère la planification easyjet dans le dossier pour le PBI et le copie avec un nom adapté dans le dossier du DCB"""
    if not os.path.exists(dossier_destination):
        os.makedirs(dossier_destination)
    
    pattern = re.compile(r'([SW])(\d{2})')
    
    for fichier in os.listdir(dossier_source):
        match = pattern.search(fichier)
        if match:
            lettre, chiffres = match.groups()
            nouveau_nom = f"Planning_EZS_{chiffres}{lettre}{os.path.splitext(fichier)[1]}"
            
            chemin_source = os.path.join(dossier_source, fichier)
            chemin_destination = os.path.join(dossier_destination, nouveau_nom)

            if os.path.isfile(chemin_destination):
                old = os.path.getsize(chemin_destination)
                new = os.path.getsize(chemin_source)
                if new/old > 0.9:
                    shutil.copy(chemin_source, chemin_destination)
                    print(f"Copié : {fichier} -> {nouveau_nom}")
                else:
                    print(f"Le fichier {chemin_source} semble corrompu : sa taille est de {new} bits alors que le fichier précédent avait une taille de {old} bits.")
            else:
                shutil.copy(chemin_source, chemin_destination)
                print(f"Copié : {fichier} -> {nouveau_nom}")

def read_excel_with_unknown_header_index(file):
    # Lire le fichier Excel sans interpréter de ligne comme en-tête
    df_raw = pd.read_excel(file, header=None)

    # Trouver la première ligne non vide
    header_idx = df_raw.notna().any(axis=1).idxmax()

    # Extraire les noms de colonnes
    new_header = df_raw.iloc[header_idx].values

    # Garder les données à partir de la ligne suivante
    df = df_raw.iloc[header_idx + 1:].copy()
    df.columns = new_header
    df.reset_index(drop=True, inplace=True)

    return df


def add_30_minutes(input_time_str):
    input_time = pd.to_datetime(input_time_str, format='%H:%M')
    new_time = input_time + timedelta(minutes=30)
    new_time_str = new_time.dt.strftime('%H:%M')
    return new_time_str

def non_LX_non_EZS(data_flight):

    data_flight = data_flight.loc[data_flight['Linked Flight Call Sign - IATA'] != 'ND'].copy()
    
    # pOUR LES NON ND
    
    data_flight_depart = data_flight.loc[data_flight["Arrival - Departure Code"] == "D"].copy()
    liste_columns_depart = ['Call Sign - IATA', 'Schengen Flight', 'French Sector',
                    'Official IATA Airport Code', 'Local Schedule Time', 'Local Skd Time Grp 60 minutes', 
                    'Pax', 'Bus_OOP+', 'Date', 'Nb Bags Total', 'Linked Flight Call Sign - IATA', 
                    'Night Stop_OOP+','Gate OOP+']
    data_flight_depart = data_flight_depart[liste_columns_depart]
    new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_DEP',
                       'Schengen Flight' : 'Schengen Flight_DEP',
                       'French Sector' : 'French Sector_DEP',
                       'Official IATA Airport Code' : 'Official IATA Airport Code_DEP',
                       'Local Schedule Time' : 'Local Schedule Time_DEP',
                       'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_DEP',
                       'Pax' : 'Pax_DEP', 'Bus_OOP+' : 'Bus_OOP+_DEP', 'Nb Bags Total' : 'Nb Bags Total_DEP',
                       'Linked Flight Call Sign - IATA' : 'Call Sign - IATA_ARR',
                       'Night Stop_OOP+' : 'Night Stop_OOP+_DEP', 'Gate OOP+' : 'Gate_OOP+_DEP'}
    data_flight_depart.rename(columns = new_columns_name, inplace = True)
    data_flight_depart_NS = data_flight_depart.loc[data_flight_depart['Night Stop_OOP+_DEP'] == 'Y']
    data_flight_depart = data_flight_depart.loc[data_flight_depart['Night Stop_OOP+_DEP'] == 'N']

    # ---

    new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_ARR',
                       'Schengen Flight' : 'Schengen Flight_ARR',
                       'French Sector' : 'French Sector_ARR',
                       'Official IATA Airport Code' : 'Official IATA Airport Code_ARR',
                       'Local Schedule Time' : 'Local Schedule Time_ARR',
                       'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_ARR',
                       'Pax' : 'Pax_ARR', 'Bus_OOP+' : 'Bus_OOP+_ARR', 'Nb Bags Total' : 'Nb Bags Total_ARR',
                       'Linked Flight Call Sign - IATA' : 'Call Sign - IATA_DEP',
                       'Night Stop_OOP+' : 'Night Stop_OOP+_ARR', 'Gate OOP+' : 'Gate_OOP+_ARR'}
    data_flight = data_flight.loc[data_flight["Arrival - Departure Code"] == "A"].copy()
    data_flight.rename(columns = new_columns_name, inplace = True)
    data_flight_NS = data_flight.loc[data_flight['Night Stop_OOP+_ARR'] == 'Y']
    data_flight = data_flight.loc[data_flight['Night Stop_OOP+_ARR'] == 'N']
    
    
    # merge jour meme
    data_end = pd.merge(data_flight_depart, data_flight, how = 'outer', on = ['Date', 'Call Sign - IATA_ARR',
                                                              'Call Sign - IATA_DEP'])
    
    data_pb = data_end.loc[(data_end['Official IATA Airport Code_DEP'].isna()) |
                      (data_end['Official IATA Airport Code_ARR'].isna())]

    data_end = data_end.loc[(~data_end['Official IATA Airport Code_DEP'].isna()) &
                          (~data_end['Official IATA Airport Code_ARR'].isna())]

    data_pb = pd.concat([data_pb, 
                         data_end.loc[data_end['Local Schedule Time_ARR'] >= data_end['Local Schedule Time_DEP']]], 
                        ignore_index = True)

    data_end =  data_end.loc[data_end['Local Schedule Time_ARR'] < data_end['Local Schedule Time_DEP']]

    data_end['Date_ARR'] = data_end['Date'].copy()
    data_end['Date_DEP'] = data_end['Date'].copy()
    
    liste_columns_depart = data_flight_depart.columns
    data_flight_depart = data_pb[liste_columns_depart].copy()
    data_flight_depart_NS = pd.concat([data_flight_depart_NS, data_flight_depart], ignore_index = True)
    data_flight_depart_NS = data_flight_depart_NS.drop_duplicates()
    data_flight_depart_NS = data_flight_depart_NS.loc[~data_flight_depart_NS['Local Schedule Time_DEP'].isna()]

    liste_columns_arrivee = data_flight.columns
    data_flight = data_pb[liste_columns_arrivee].copy()
    data_flight_NS = pd.concat([data_flight_NS, data_flight], ignore_index = True)
    data_flight_NS = data_flight_NS.drop_duplicates()
    data_flight_NS = data_flight_NS.loc[~data_flight_NS['Local Schedule Time_ARR'].isna()]

    
    # on merge le jour suivant 
    data_flight_NS['Date_ARR'] = data_flight_NS['Date'].copy()
    data_flight_NS['Date'] = data_flight_NS['Date'] + timedelta(days = 1)
    data_end_NS = pd.merge(data_flight_depart_NS, data_flight_NS, 
                           how = 'outer', on = ['Date', 'Call Sign - IATA_ARR', 'Call Sign - IATA_DEP'])
    data_end_NS['Date_DEP'] = data_end_NS['Date'].copy()

    data_end_NS_pb =  data_end_NS.loc[(data_end_NS['Local Schedule Time_ARR'].isna()) |
                                        (data_end_NS['Local Schedule Time_DEP'].isna())].copy()

    data_end_NS = data_end_NS.loc[(~data_end_NS['Local Schedule Time_ARR'].isna()) &
                                        (~data_end_NS['Local Schedule Time_DEP'].isna())]

    data_end = pd.concat([data_end, data_end_NS], ignore_index = True)

    liste_columns_arrivee = list(liste_columns_arrivee)
    liste_columns_arrivee.append('Date_ARR')

    data_flight_NS = data_end_NS_pb[liste_columns_arrivee].copy()
    data_flight_NS = data_flight_NS.loc[~data_flight_NS['Local Schedule Time_ARR'].isna()]
    data_flight_NS['Date'] = data_flight_NS['Date_ARR'].copy()

    data_flight_depart_NS = data_end_NS_pb[liste_columns_depart].copy()
    data_flight_depart_NS = data_flight_depart_NS.loc[~data_flight_depart_NS['Local Schedule Time_DEP'].isna()]

    


    # On fait du cas par cas : 
    liste_acro =  data_flight_NS['Call Sign - IATA_ARR'].str[:2].drop_duplicates().to_list()
    summ = 0
    for acro in liste_acro :
        d_arr = data_flight_NS[data_flight_NS['Call Sign - IATA_ARR'].str[:2] == acro].copy()

        d_dep = data_flight_depart_NS[data_flight_depart_NS['Call Sign - IATA_DEP'].str[:2] == acro].copy()

        if acro in ['FX', 'LB', 'ET']:
            d_arr['Date'] = d_arr['Date'] + timedelta(days = 2)

        elif acro == 'SR' :
            d_arr['Date'] = d_arr['Date'] + timedelta(days = 3)

        elif acro == 'QY' :
            d_arr.loc[d_arr['Call Sign - IATA_ARR']  == 'QY4894', 'Date'] = d_arr.loc[
                d_arr['Call Sign - IATA_ARR']  == 'QY4894', 'Date'] + timedelta(days = 5)

        for ind in range(len(d_arr)):
            date = d_arr['Date'].iloc[ind]
            cs = d_arr['Call Sign - IATA_ARR'].iloc[ind]

            if len(d_dep.loc[d_dep['Date'] == date]) == 1:
                d_dep.loc[d_dep['Date'] == date, 'Call Sign - IATA_ARR'] = cs

        d_arr.drop(columns = 'Call Sign - IATA_DEP', inplace = True)
        d = pd.merge(d_dep, d_arr, on = ['Date', 'Call Sign - IATA_ARR'] , how = 'inner')
        summ += len(d)


        d['Date_DEP'] = d['Date'].copy()
        data_end = pd.concat([data_end, d], ignore_index = True)
        
    return data_end




def generate_date_range(row):
    return pd.date_range(start=row['Eff Dt'], end=row['Dis Dt'], freq='D')


def for_EZS (data_flight_EZS, data_end) :
    
    # ------------------------------1
    # Traitement du fichier EZS
    # ------------------------------
    nouveau_repertoire = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Planning_EZS")
    os.chdir(nouveau_repertoire)
    files = os.listdir()
    
    planning_EZS = read_excel_with_unknown_header_index(files[-2])
    planning_EZS.replace(to_replace=" ", value=pd.NA,inplace=True)
    planning_EZS.dropna(how='all',inplace=True)
    planning_EZS0 = read_excel_with_unknown_header_index(files[-1])
    planning_EZS0.replace(to_replace=" ", value=pd.NA,inplace=True)
    planning_EZS0.dropna(how='all',inplace=True)
    planning_EZS = pd.concat([planning_EZS, planning_EZS0], ignore_index = True)
    
    planning_EZS = planning_EZS.loc[~planning_EZS['Eff Dt'].isna()]

    planning_EZS['Eff Dt'] = pd.to_datetime(planning_EZS['Eff Dt'].copy(), format='%Y-%m-%d')
    planning_EZS['Dis Dt'] = pd.to_datetime(planning_EZS['Dis Dt'].copy(), format='%Y-%m-%d')
    planning_EZS = planning_EZS.dropna(subset=['Eff Dt', 'Dis Dt'])
    
    planning_EZS = planning_EZS.loc[(planning_EZS['Arvl Sta'] == 'GVA')]
    planning_EZS['DateRange'] = planning_EZS.apply(generate_date_range, axis=1)

    planning_EZS['Days'] = planning_EZS['Frequency'].apply(lambda x: [i for i, c in enumerate(str(x)) if c.isdigit()])
    planning_EZS = planning_EZS.explode('DateRange').explode('Days')
    planning_EZS = planning_EZS[planning_EZS['DateRange'].dt.dayofweek == planning_EZS['Days'].astype(int)]

    planning_EZS = planning_EZS[['flight no', 'Onward flts', 'DateRange']]
    planning_EZS.columns = ['Call Sign - IATA_ARR','Call Sign - IATA_DEP','Date']
    planning_EZS['Call Sign - IATA_ARR'] = [k[:3]+k[4:] for k in planning_EZS['Call Sign - IATA_ARR']]
    planning_EZS['Call Sign - IATA_DEP'] = [str(k)[:3]+str(k)[5:] for k in planning_EZS['Call Sign - IATA_DEP']]
    # ------------------------------
    # ARR/DEP
    # ------------------------------
    
    data_flight_depart_EZS = data_flight_EZS.loc[data_flight_EZS["Arrival - Departure Code"] == "D"].copy()
    liste_columns_depart_EZS = ['Call Sign - IATA', 'Schengen Flight', 'French Sector',
                     'Official IATA Airport Code', 'Local Schedule Time', 'Local Skd Time Grp 60 minutes', 
                            'Pax', 'Bus_OOP+', 'Date', 'Nb Bags Total', 'Night Stop_OOP+', 'Gate OOP+']
    data_flight_depart_EZS = data_flight_depart_EZS[liste_columns_depart_EZS]
    new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_DEP',
                       'Schengen Flight' : 'Schengen Flight_DEP',
                       'French Sector' : 'French Sector_DEP',
                       'Official IATA Airport Code' : 'Official IATA Airport Code_DEP',
                       'Local Schedule Time' : 'Local Schedule Time_DEP',
                       'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_DEP',
                       'Pax' : 'Pax_DEP', 'Bus_OOP+' : 'Bus_OOP+_DEP', 'Nb Bags Total' : 'Nb Bags Total_DEP',
                       'Night Stop_OOP+' : 'Night Stop_OOP+_DEP', 'Gate OOP+' : 'Gate_OOP+_DEP'} 
    data_flight_depart_EZS.rename(columns = new_columns_name, inplace = True)
    data_flight_depart_EZS['VID_DEP'] = range(len(data_flight_depart_EZS))



    new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_ARR',
                       'Schengen Flight' : 'Schengen Flight_ARR',
                       'French Sector' : 'French Sector_ARR',
                       'Official IATA Airport Code' : 'Official IATA Airport Code_ARR',
                       'Local Schedule Time' : 'Local Schedule Time_ARR',
                       'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_ARR',
                       'Pax' : 'Pax_ARR', 'Bus_OOP+' : 'Bus_OOP+_ARR', 'Nb Bags Total' : 'Nb Bags Total_ARR',
                       'Night Stop_OOP+' : 'Night Stop_OOP+_ARR', 'Gate OOP+' : 'Gate_OOP+_ARR'}
    data_flight_arrivee_EZS = data_flight_EZS.loc[data_flight_EZS["Arrival - Departure Code"] == "A"].copy()
    data_flight_arrivee_EZS.rename(columns = new_columns_name, inplace = True)
    data_flight_arrivee_EZS['VID_ARR'] = range(len(data_flight_arrivee_EZS))
    
    # ------------------------------
    # On merge le jour même
    # ------------------------------
    
    data_flight_arrivee_EZS = pd.merge(data_flight_arrivee_EZS, planning_EZS, 
                                       on = ['Call Sign - IATA_ARR', 'Date'], how = 'left')
    data_flight_depart_EZS = pd.merge(data_flight_depart_EZS, planning_EZS, 
                                      on = ['Call Sign - IATA_DEP', 'Date'], how = 'left')

    test = pd.merge(data_flight_arrivee_EZS, data_flight_depart_EZS, 
                    on = ['Call Sign - IATA_ARR', 'Call Sign - IATA_DEP', 'Date'], how = 'inner')
    test = test.loc[test['Local Schedule Time_DEP']  >= add_30_minutes(test['Local Schedule Time_ARR'])]
    test["Date_DEP"] = test["Date"]

    data_flight_depart_EZS = data_flight_depart_EZS.loc[~data_flight_depart_EZS['VID_DEP'].isin(test['VID_DEP'].to_list())]
    data_flight_arrivee_EZS = data_flight_arrivee_EZS.loc[~data_flight_arrivee_EZS['VID_ARR'].isin(test['VID_ARR'].to_list())]
    print(len(test))

    # ------------------------------
    # On merge le jour suivant
    # ------------------------------
    
    data_flight_depart_EZS.drop(columns = ['Call Sign - IATA_ARR'], inplace=True)
    data_flight_depart_EZS['Date_DEP'] = data_flight_depart_EZS['Date'].copy()
    data_flight_depart_EZS['Date'] = data_flight_depart_EZS['Date'] - timedelta(days = 1)

    data_flight_depart_EZS = pd.merge(data_flight_depart_EZS, planning_EZS, 
                                      on = ['Call Sign - IATA_DEP', 'Date'], how = 'left')
    test2 = pd.merge(data_flight_arrivee_EZS, data_flight_depart_EZS, 
                     on = ['Call Sign - IATA_ARR', 'Call Sign - IATA_DEP', 'Date'], how = 'inner')

    data_flight_depart_EZS = data_flight_depart_EZS[~data_flight_depart_EZS['VID_DEP'].isin(test2['VID_DEP'].to_list())]

    data_flight_arrivee_EZS = data_flight_arrivee_EZS[~data_flight_arrivee_EZS['VID_ARR'].isin(test2['VID_ARR'].to_list())]

    # ------------------------------
    # On merge le jour encore suivant
    # ------------------------------
    
    data_flight_depart_EZS.drop(columns = ['Call Sign - IATA_ARR'], inplace=True)
    data_flight_depart_EZS['Date'] = data_flight_depart_EZS['Date'] - timedelta(days = 1)

    data_flight_depart_EZS = pd.merge(data_flight_depart_EZS, planning_EZS, 
                                      on = ['Call Sign - IATA_DEP', 'Date'], how = 'left')
    test3 = pd.merge(data_flight_arrivee_EZS, data_flight_depart_EZS, 
                     on = ['Call Sign - IATA_ARR', 'Call Sign - IATA_DEP', 'Date'], how = 'inner')

    data_flight_depart_EZS = data_flight_depart_EZS[~data_flight_depart_EZS['VID_DEP'].isin(test3['VID_DEP'].to_list())]

    data_flight_arrivee_EZS = data_flight_arrivee_EZS[~data_flight_arrivee_EZS['VID_ARR'].isin(test3['VID_ARR'].to_list())]

    # On supp les incohérences
    date =  max(data_flight_depart_EZS['Date'])
    data_flight_arrivee_EZS = data_flight_arrivee_EZS.loc[data_flight_arrivee_EZS['Date'] <= date]

    date =  min(data_flight_arrivee_EZS['Date'])
    data_flight_depart_EZS = data_flight_depart_EZS.loc[data_flight_depart_EZS['Date'] >= date]


    # ------------------------------
    # On fait du cas par cas
    # ------------------------------

    for date in tqdm.tqdm(data_flight_arrivee_EZS['Date'].unique()):
        date = pd.to_datetime(str(date)[:10])
        data_local_depart = data_flight_depart_EZS.loc[
            data_flight_depart_EZS['Date_DEP'] == date + timedelta(days = 1)].copy()
        data_local_arrivee = data_flight_arrivee_EZS.loc[data_flight_arrivee_EZS['Date'] == date].copy()

        if len(data_local_depart) == len(data_local_arrivee):

            for ind in range(len(data_local_depart)):

                csa = data_local_arrivee['Call Sign - IATA_ARR'].iloc[ind]
                csd = data_local_depart['Call Sign - IATA_DEP'].iloc[ind]

                data_flight_depart_EZS.loc[(data_flight_depart_EZS['Date_DEP'] == date + timedelta(days = 1))
                                          & (data_flight_depart_EZS['Call Sign - IATA_DEP'] == csd), 
                                          'Call Sign - IATA_ARR'] = csa

                data_flight_arrivee_EZS.loc[(data_flight_arrivee_EZS['Date'] == date) &
                                          (data_flight_arrivee_EZS['Call Sign - IATA_ARR'] == csa),
                                          'Call Sign - IATA_DEP'] = csd

    data_flight_depart_EZS['Date'] = data_flight_depart_EZS['Date_DEP'] - timedelta(days = 1)
    test4 = pd.merge(data_flight_arrivee_EZS, data_flight_depart_EZS, 
                     on = ['Call Sign - IATA_ARR', 'Call Sign - IATA_DEP', 'Date'], how = 'inner')
    
    data_flight_depart_EZS = data_flight_depart_EZS[~data_flight_depart_EZS['VID_DEP'].isin(test4['VID_DEP'].to_list())]

    data_flight_arrivee_EZS = data_flight_arrivee_EZS[~data_flight_arrivee_EZS['VID_ARR'].isin(test4['VID_ARR'].to_list())]

    # De meme avec les NS

    data_flight_depart_EZS['Call Sign - IATA_ARR'] = ''
    summ = 0

    for ind in tqdm.tqdm(range(len(data_flight_arrivee_EZS))) :

        date = data_flight_arrivee_EZS['Date'].iloc[ind]
        csa = data_flight_arrivee_EZS['Call Sign - IATA_ARR'].iloc[ind]


        d = data_flight_depart_EZS.loc[(data_flight_depart_EZS['Date_DEP'] == (date + timedelta(days = 1)))
                                          & (data_flight_depart_EZS['Call Sign - IATA_ARR'] == '')]

        if len(d) > 0:
            summ += 1
            csd = d['Call Sign - IATA_DEP'].iloc[0]

            data_flight_depart_EZS.loc[(data_flight_depart_EZS['Date_DEP'] == (date + timedelta(days = 1)))
                                          & (data_flight_depart_EZS['Call Sign - IATA_DEP'] == csd),
                                      'Call Sign - IATA_ARR'] = csa

            data_flight_arrivee_EZS.loc[(data_flight_arrivee_EZS['Date'] == date)
                                       & (data_flight_arrivee_EZS['Call Sign - IATA_ARR'] == csa),
                                       'Call Sign - IATA_DEP'] = csd

    data_flight_depart_EZS['Date'] = data_flight_depart_EZS['Date_DEP'] - timedelta(days = 1)
    test5 = pd.merge(data_flight_arrivee_EZS, data_flight_depart_EZS, 
                     on = ['Call Sign - IATA_ARR', 'Call Sign - IATA_DEP', 'Date'], how = 'inner')

    data_flight_depart_EZS = data_flight_depart_EZS[~data_flight_depart_EZS['VID_DEP'].isin(test5['VID_DEP'].to_list())]

    data_flight_arrivee_EZS = data_flight_arrivee_EZS[~data_flight_arrivee_EZS['VID_ARR'].isin(test5['VID_ARR'].to_list())]
    
    # ------------------------------
    # On merge tout 
    # ------------------------------

    test = pd.concat([test, test2, test3, test4, test5], ignore_index=True)
    test['Date_ARR'] = test['Date']
    test.drop(columns = ['VID_ARR', 'VID_DEP'], inplace = True)
    data_end = pd.concat([data_end, test], ignore_index = True)
    
    return data_end
