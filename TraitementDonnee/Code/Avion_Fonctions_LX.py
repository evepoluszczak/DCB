import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tqdm


def add_30_minutes(input_time_str):
    input_time = datetime.strptime(input_time_str, '%H:%M')
    new_time = input_time + timedelta(minutes=30)
    new_time_str = new_time.strftime('%H:%M')
    return new_time_str

def minus_30_minutes(input_time_str):
    input_time = datetime.strptime(input_time_str, '%H:%M')
    new_time = input_time - timedelta(minutes=30)
    new_time_str = new_time.strftime('%H:%M')
    return new_time_str

def minus_40_minutes(input_time_str):
    input_time = datetime.strptime(input_time_str, '%H:%M')
    new_time = input_time - timedelta(minutes=40)
    new_time_str = new_time.strftime('%H:%M')
    return new_time_str

def add_90_minutes(input_time_str):
    input_time = datetime.strptime(input_time_str, '%H:%M')
    new_time = input_time + timedelta(minutes=90)
    new_time_str = new_time.strftime('%H:%M')
    return new_time_str

    
def get_maxi (dico):
    maxi = -1
    for key in dico.keys():
        if dico[key]>maxi:
            key_return = key
            maxi = dico[key]
    return key_return

def recherche_max (matrice):
    cs_arr_max, cs_dep_max, maxi = 0, 0, -1
    
    for cs_arr in matrice.keys():
        for cs_dep in matrice[cs_arr].keys():
            if matrice[cs_arr][cs_dep] > maxi :
                cs_arr_max = cs_arr
                cs_dep_max = cs_dep
                maxi = matrice[cs_arr][cs_dep]
    return cs_arr_max, cs_dep_max


def LX(data_flight_LX, season, liste_NS, liste_NNS, dico_CS, dico_CS_inv, dico_dest, dico_CS_NS, dico_dest_NS):
    data_flight_LX = data_flight_LX[data_flight_LX['Season'] == season]

    data_flight_depart_LX = data_flight_LX.loc[data_flight_LX["Arrival - Departure Code"] == "D"].copy()
    liste_columns_depart_LX = ['Call Sign - IATA', 'Schengen Flight', 'French Sector',
                    'Official IATA Airport Code', 'Local Schedule Time', 'Local Skd Time Grp 60 minutes', 
                    'Pax', 'Bus_OOP+', 'Date', 'Nb Bags Total', 'Night Stop_OOP+', 'Gate OOP+',
                    'Aircraft Subtype IATA Type']
    data_flight_depart_LX = data_flight_depart_LX[liste_columns_depart_LX]
    new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_DEP',
                       'Schengen Flight' : 'Schengen Flight_DEP',
                       'French Sector' : 'French Sector_DEP',
                       'Official IATA Airport Code' : 'Official IATA Airport Code_DEP',
                       'Local Schedule Time' : 'Local Schedule Time_DEP',
                       'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_DEP',
                       'Pax' : 'Pax_DEP', 'Bus_OOP+' : 'Bus_OOP+_DEP', 'Nb Bags Total' : 'Nb Bags Total_DEP',
                       'Night Stop_OOP+' : 'Night Stop_OOP+_DEP', 'Gate OOP+' : 'Gate_OOP+_DEP'}
    data_flight_depart_LX.rename(columns = new_columns_name, inplace = True)
    data_flight_depart_LX['Call Sign - IATA_ARR'] = 'ND'
    data_flight_depart_LX_NS = data_flight_depart_LX.loc[data_flight_depart_LX['Night Stop_OOP+_DEP'] == 'Y']
    data_flight_depart_LX = data_flight_depart_LX.loc[data_flight_depart_LX['Night Stop_OOP+_DEP'] == 'N']


    new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_ARR',
                       'Schengen Flight' : 'Schengen Flight_ARR',
                       'French Sector' : 'French Sector_ARR',
                       'Official IATA Airport Code' : 'Official IATA Airport Code_ARR',
                       'Local Schedule Time' : 'Local Schedule Time_ARR',
                       'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_ARR',
                       'Pax' : 'Pax_ARR', 'Bus_OOP+' : 'Bus_OOP+_ARR', 'Nb Bags Total' : 'Nb Bags Total_ARR',
                       'Night Stop_OOP+' : 'Night Stop_OOP+_ARR', 'Gate OOP+' : 'Gate_OOP+_ARR'}
    data_flight_arrivee_LX = data_flight_LX.loc[data_flight_LX["Arrival - Departure Code"] == "A"].copy()
    data_flight_arrivee_LX['Call Sign - IATA_DEP'] = 'ND'
    data_flight_arrivee_LX.rename(columns = new_columns_name, inplace = True)
    data_flight_arrivee_LX_NS = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Night Stop_OOP+_ARR'] == 'Y']
    data_flight_arrivee_LX = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Night Stop_OOP+_ARR'] == 'N']
    
    # ----------------------------
    # On refait les NS
    # ----------------------------
             
             
    for date in tqdm.tqdm(data_flight_arrivee_LX['Date'].unique()):
        data_local_arrivee = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Date'] == date].copy()
        data_local_depart = data_flight_depart_LX.loc[data_flight_depart_LX['Date'] == date].copy()


        for aircraft in data_local_arrivee['Aircraft Subtype IATA Type'].unique() :

            if len(data_local_depart.loc[data_local_depart['Aircraft Subtype IATA Type'] == aircraft]) == 0 :
                        data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Date'] == date) &
                                       (data_flight_arrivee_LX['Aircraft Subtype IATA Type'] == aircraft), 
                                       'Night Stop_OOP+_ARR'] = 'Y'

            else : 
                heure_arr_min = add_30_minutes(data_local_arrivee.loc[
                    data_local_arrivee['Aircraft Subtype IATA Type'] == aircraft, 'Local Schedule Time_ARR'].min())
                heure_dep_max = minus_30_minutes(data_local_depart.loc[
                    data_local_depart['Aircraft Subtype IATA Type'] == aircraft, 'Local Schedule Time_DEP'].max())

                data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Date'] == date) &
                                           (data_flight_arrivee_LX['Aircraft Subtype IATA Type'] == aircraft)
                                           & (data_flight_arrivee_LX['Local Schedule Time_ARR'] > heure_dep_max), 
                                           'Night Stop_OOP+_ARR'] = 'Y'

                data_flight_depart_LX.loc[(data_flight_depart_LX['Date'] == date) &
                                           (data_flight_depart_LX['Aircraft Subtype IATA Type'] == aircraft)
                                           & (data_flight_depart_LX['Local Schedule Time_DEP'] < heure_arr_min), 
                                          'Night Stop_OOP+_DEP'] = 'Y'


    data_flight_arrivee_LX_NS = pd.concat([data_flight_arrivee_LX_NS, data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Night Stop_OOP+_ARR'] == 'Y']],
                                         ignore_index = True)
    data_flight_arrivee_LX = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Night Stop_OOP+_ARR'] != 'Y']

    data_flight_depart_LX_NS = pd.concat([data_flight_depart_LX_NS, data_flight_depart_LX.loc[data_flight_depart_LX['Night Stop_OOP+_DEP'] == 'Y']],
                                        ignore_index = True)
    data_flight_depart_LX = data_flight_depart_LX.loc[data_flight_depart_LX['Night Stop_OOP+_DEP'] != 'Y']


    for cs in data_flight_depart_LX['Call Sign - IATA_DEP'].unique():
        data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_DEP'] == cs,
                                    'Nbr NS'] = np.sum(liste_NS == cs)
        data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_DEP'] == cs,
                                    'Nbr NNS'] = np.sum(liste_NNS == cs)  

    for cs in data_flight_arrivee_LX_NS['Call Sign - IATA_ARR'].unique():
        data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_ARR'] == cs,
                                    'Nbr NS'] = np.sum(liste_NS == cs)
        data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_ARR'] == cs,
                                    'Nbr NNS'] = np.sum(liste_NNS == cs)  

    data_flight_depart_LX['Nbr'] = data_flight_depart_LX['Nbr NS'] + data_flight_depart_LX['Nbr NNS']
    data_flight_depart_LX['Nbr NS'] = data_flight_depart_LX['Nbr NS'] / data_flight_depart_LX['Nbr']
    data_flight_depart_LX['Nbr NNS'] = data_flight_depart_LX['Nbr NNS'] / data_flight_depart_LX['Nbr']

    data_flight_arrivee_LX['Nbr'] = data_flight_arrivee_LX['Nbr NS'] + data_flight_arrivee_LX['Nbr NNS']
    data_flight_arrivee_LX['Nbr NS'] = data_flight_arrivee_LX['Nbr NS'] /data_flight_arrivee_LX['Nbr'] 
    data_flight_arrivee_LX['Nbr NNS'] = data_flight_arrivee_LX['Nbr NNS'] / data_flight_arrivee_LX['Nbr'] 


    data_flight_depart_LX['Night Stop_OOP+_DEP'] = 'N'
    data_flight_depart_LX.loc[data_flight_depart_LX['Nbr NS'] >= 0.6, 'Night Stop_OOP+_DEP'] = 'Y'
    data_flight_depart_LX.loc[(data_flight_depart_LX['Nbr NS'] < 0.6) &
                                 (data_flight_depart_LX['Nbr NS'] > 0.4),'Night Stop_OOP+_DEP'] = 'ND'

    data_flight_arrivee_LX['Night Stop_OOP+_ARR'] = 'N'
    data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Nbr NS'] >= 0.6, 'Night Stop_OOP+_ARR'] = 'Y'
    data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Nbr NS'] < 0.6) &
                                 (data_flight_arrivee_LX['Nbr NS'] > 0.4), 'Night Stop_OOP+_ARR'] = 'ND'




    data_flight_arrivee_LX_NS = pd.concat([data_flight_arrivee_LX_NS, 
                                           data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Night Stop_OOP+_ARR'] == 'Y']],
                                         ignore_index = True)
    data_flight_arrivee_LX = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Night Stop_OOP+_ARR'] != 'Y']

    data_flight_depart_LX_NS = pd.concat([data_flight_depart_LX_NS, 
                                           data_flight_depart_LX.loc[data_flight_depart_LX['Night Stop_OOP+_DEP'] == 'Y']],
                                        ignore_index = True)
    data_flight_depart_LX = data_flight_depart_LX.loc[data_flight_depart_LX['Night Stop_OOP+_DEP'] != 'Y']


    data_flight_depart_LX.drop(columns = ['Nbr', 'Nbr NS', 'Nbr NNS'], inplace = True)
    data_flight_arrivee_LX.drop(columns = ['Nbr', 'Nbr NS', 'Nbr NNS'], inplace = True)
    data_flight_depart_LX_NS.drop(columns = ['Nbr', 'Nbr NS', 'Nbr NNS'], inplace = True)
    data_flight_arrivee_LX_NS.drop(columns = ['Nbr', 'Nbr NS', 'Nbr NNS'], inplace = True)
             
             
    

             
             
             
             
    # --------------------------
    # Etape Call Sign
    # --------------------------
             
             

    for ind in tqdm.tqdm(range(len(data_flight_arrivee_LX))):
        cs = data_flight_arrivee_LX['Call Sign - IATA_ARR'].iloc[ind]
        air = data_flight_arrivee_LX['Aircraft Subtype IATA Type'].iloc[ind]
        date = data_flight_arrivee_LX['Date'].iloc[ind]

        if cs in dico_CS.keys():
            for csd in dico_CS[cs].keys():
                if dico_CS[cs][csd]>0.5:

                    if len(data_flight_depart_LX.loc[(data_flight_depart_LX['Call Sign - IATA_DEP'] == csd) & 
                                   (data_flight_depart_LX['Aircraft Subtype IATA Type'] == air) &
                                                     (data_flight_depart_LX['Date'] == date)]) > 0 :

                        data_flight_depart_LX.loc[(data_flight_depart_LX['Call Sign - IATA_DEP'] == csd) & 
                                  (data_flight_depart_LX['Aircraft Subtype IATA Type'] == air) &
                                 (data_flight_depart_LX['Date'] == date), 'Call Sign - IATA_ARR'] = cs

                        data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Call Sign - IATA_ARR'] == cs) & 
                                       (data_flight_arrivee_LX['Aircraft Subtype IATA Type'] == air) &
                                 (data_flight_arrivee_LX['Date'] == date), 'Call Sign - IATA_DEP'] = csd


    # On remove celles qui sont matchées : 
    data_flight_depart_LX_done = data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_ARR']!= 'ND']
    data_flight_depart_LX = data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_ARR']== 'ND']

    data_flight_arrivee_LX_done= data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_DEP']!='ND']
    data_flight_arrivee_LX = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_DEP'] == 'ND']

    data_end_LX = pd.merge(data_flight_arrivee_LX_done, data_flight_depart_LX_done, how = 'inner', 
                            on = ['Date', 'Call Sign - IATA_DEP', 
                                  'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX['Date_DEP'] = data_end_LX['Date'].copy()
    data_end_LX['Date_ARR'] = data_end_LX['Date'].copy()
    data_end_LX.drop(columns = ['Date'], inplace = True)
    data_end_LX['method'] = 'Call Sign'
    
    print('Etape CS : ', len(data_end_LX))
             
             


    for ind in tqdm.tqdm(range(len(data_flight_depart_LX))):
        csd = data_flight_depart_LX['Call Sign - IATA_DEP'].iloc[ind]
        air = data_flight_depart_LX['Aircraft Subtype IATA Type'].iloc[ind]
        date = data_flight_depart_LX['Date'].iloc[ind]

        if csd in dico_CS_inv.keys():
            for csa in dico_CS_inv[csd].keys():
                if dico_CS_inv[csd][csa]>0.5:

                    if len(data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Call Sign - IATA_ARR'] == csa) & 
                                   (data_flight_arrivee_LX['Aircraft Subtype IATA Type'] == air) &
                                    (data_flight_arrivee_LX['Date'] == date)]) > 0 :

                        data_flight_depart_LX.loc[(data_flight_depart_LX['Call Sign - IATA_DEP'] == csd) & 
                                    (data_flight_depart_LX['Aircraft Subtype IATA Type'] == air) &
                                    (data_flight_depart_LX['Date'] == date), 'Call Sign - IATA_ARR'] = csa

                        data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Call Sign - IATA_ARR'] == csa) & 
                                    (data_flight_arrivee_LX['Aircraft Subtype IATA Type'] == air) &
                                    (data_flight_arrivee_LX['Date'] == date), 'Call Sign - IATA_DEP'] = csd


    # On remove celles qui sont matchées : 
    data_flight_depart_LX_done = data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_ARR']!= 'ND']
    data_flight_depart_LX = data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_ARR']== 'ND']

    data_flight_arrivee_LX_done = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_DEP'] != 'ND']
    data_flight_arrivee_LX = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_DEP'] == 'ND']

    data_end_LX0 = pd.merge(data_flight_arrivee_LX_done, data_flight_depart_LX_done, how = 'inner', 
                 on = ['Date', 'Call Sign - IATA_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX0['Date_DEP'] = data_end_LX0['Date'].copy()
    data_end_LX0['Date_ARR'] = data_end_LX0['Date'].copy()
    data_end_LX0.drop(columns = ['Date'], inplace = True)
    data_end_LX0['method'] = 'Call Sign inv'
    data_end_LX = pd.concat([data_end_LX, data_end_LX0], ignore_index = True)
             
    print('Etape CS inv : ', len(data_end_LX0))        

    # Pour les NS 

    for ind in tqdm.tqdm(range(len(data_flight_arrivee_LX_NS))):
        cs = data_flight_arrivee_LX_NS['Call Sign - IATA_ARR'].iloc[ind]
        air = data_flight_arrivee_LX_NS['Aircraft Subtype IATA Type'].iloc[ind]
        date = data_flight_arrivee_LX_NS['Date'].iloc[ind]

        if cs in dico_CS_NS.keys():
            for csd in dico_CS_NS[cs].keys():
                if dico_CS_NS[cs][csd]>0.5:

                    if len(data_flight_depart_LX_NS.loc[(data_flight_depart_LX_NS['Call Sign - IATA_DEP'] == csd) & (data_flight_depart_LX_NS['Aircraft Subtype IATA Type'] == air) & (data_flight_depart_LX_NS['Date'] == date + timedelta(days=1))])== 1 :

                        data_flight_depart_LX_NS.loc[(data_flight_depart_LX_NS['Call Sign - IATA_DEP'] == csd) & (data_flight_depart_LX_NS['Aircraft Subtype IATA Type'] == air) &(data_flight_depart_LX_NS['Date'] == date + timedelta(days=1)), 'Call Sign - IATA_ARR'] = cs

                        data_flight_arrivee_LX_NS.loc[(data_flight_arrivee_LX_NS['Call Sign - IATA_ARR'] == cs) & (data_flight_arrivee_LX_NS['Aircraft Subtype IATA Type'] == air) &(data_flight_arrivee_LX_NS['Date'] == date), 'Call Sign - IATA_DEP'] = csd

    # On remove celles qui sont matchées : 
    data_flight_depart_LX_done = data_flight_depart_LX_NS.loc[data_flight_depart_LX_NS['Call Sign - IATA_ARR'] !='ND']
    data_flight_depart_LX_NS = data_flight_depart_LX_NS.loc[data_flight_depart_LX_NS['Call Sign - IATA_ARR'] =='ND']

    data_flight_arrivee_LX_done = data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Call Sign - IATA_DEP']!='ND']
    data_flight_arrivee_LX_NS = data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Call Sign - IATA_DEP']=='ND']

    data_flight_depart_LX_done['Date_DEP'] = data_flight_depart_LX_done['Date'].copy()
    data_flight_arrivee_LX_done['Date_ARR'] = data_flight_arrivee_LX_done['Date'].copy()
    data_flight_arrivee_LX_done['Date'] = data_flight_arrivee_LX_done['Date'] + timedelta(days = 1)

    data_end_LX0 = pd.merge(data_flight_arrivee_LX_done, data_flight_depart_LX_done, how = 'inner',
               on = ['Date', 'Call Sign - IATA_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX0.drop(columns = ['Date'], inplace = True)
    data_end_LX0['method'] = 'Call Sign'
    data_end_LX = pd.concat([data_end_LX, data_end_LX0], ignore_index = True)
             
             
    print('Etape CS NS : ', len(data_end_LX0))    
             
             
    # --------------------------
    # Etape Destinations
    # --------------------------
             
             


    for ind in range(len(data_flight_arrivee_LX_NS)):
        date_arr = data_flight_arrivee_LX_NS['Date'].iloc[ind]
        aircraft = data_flight_arrivee_LX_NS['Aircraft Subtype IATA Type'].iloc[ind]
        date_dep = date_arr + timedelta(days = 1)
        csa = data_flight_arrivee_LX_NS['Call Sign - IATA_ARR'].iloc[ind]
        weekday = date_arr.weekday()

        dest_arr = data_flight_arrivee_LX_NS['Official IATA Airport Code_ARR'].iloc[ind]

        if dest_arr in dico_dest_NS.keys():
            if weekday in dico_dest_NS[dest_arr].keys():
                dest_dep = get_maxi(dico_dest_NS[dest_arr][weekday])

                data_local = data_flight_depart_LX_NS.loc[(data_flight_depart_LX_NS['Date'] == date_dep) &
                           (data_flight_depart_LX_NS['Official IATA Airport Code_DEP'] == dest_dep) &
                                        (data_flight_depart_LX_NS['Call Sign - IATA_ARR'] == 'ND') &
                                  (data_flight_depart_LX_NS['Aircraft Subtype IATA Type'] == aircraft)]
                
                if dico_dest_NS[dest_arr][weekday][dest_dep] >= 0.4 :
                    if len(data_local)>0:
                        csd = data_local['Call Sign - IATA_DEP'].iloc[0]
                        data_flight_arrivee_LX_NS.loc[(data_flight_arrivee_LX_NS['Date'] == date_arr) &
                                                     (data_flight_arrivee_LX_NS['Call Sign - IATA_ARR'] == csa), 
                                                      'Call Sign - IATA_DEP'] = csd 

                        data_flight_depart_LX_NS.loc[(data_flight_depart_LX_NS['Date'] == date_dep) &
                                                    (data_flight_depart_LX_NS['Call Sign - IATA_DEP'] == csd), 
                                                     'Call Sign - IATA_ARR'] = csa

    # On remove celles qui sont matchées : 
    data_flight_depart_LX_NS_done = data_flight_depart_LX_NS.loc[data_flight_depart_LX_NS['Call Sign - IATA_ARR'] !='ND']
    data_flight_depart_LX_NS = data_flight_depart_LX_NS.loc[data_flight_depart_LX_NS['Call Sign - IATA_ARR'] =='ND']

    data_flight_arrivee_LX_NS_done = data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Call Sign - IATA_DEP']!='ND']
    data_flight_arrivee_LX_NS = data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Call Sign - IATA_DEP']=='ND']

    data_flight_depart_LX_NS_done['Date_DEP'] = data_flight_depart_LX_NS_done['Date'].copy()
    data_flight_arrivee_LX_NS_done['Date_ARR'] = data_flight_arrivee_LX_NS_done['Date'].copy()
    data_flight_arrivee_LX_NS_done['Date'] = data_flight_arrivee_LX_NS_done['Date'] + timedelta(days = 1)

    data_end_LX0 = pd.merge(data_flight_arrivee_LX_NS_done, data_flight_depart_LX_NS_done, how = 'inner', on = ['Date', 'Call Sign - IATA_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX0.drop(columns = ['Date'], inplace = True)
    data_end_LX0['method'] = 'Destinations NS'
    data_end_LX = pd.concat([data_end_LX, data_end_LX0], ignore_index = True)

             
             
    print('Etape Desti NS : ', len(data_end_LX0))     
             
             
    # --------------------------
    # Only logic depart
    # --------------------------


    for date in tqdm.tqdm(data_flight_arrivee_LX['Date'].unique()):
        for aircraft_type in data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Date'] == date, 
                                                        'Aircraft Subtype IATA Type'].unique():

            data_arrivee_local = data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Date'] == date) &
                               (data_flight_arrivee_LX['Aircraft Subtype IATA Type'] == aircraft_type)]
            
            data_depart_local = data_flight_depart_LX[(data_flight_depart_LX['Date'] == date) &
                                 (data_flight_depart_LX['Aircraft Subtype IATA Type'] == aircraft_type)]

            n_arrivee = len(data_arrivee_local)

            for ind in range(n_arrivee):
                data_depart_local = data_depart_local[data_depart_local['Call Sign - IATA_ARR'] == 'ND']

                liste_pos = np.array(data_depart_local['Local Schedule Time_DEP'])
                time = data_arrivee_local['Local Schedule Time_ARR'].iloc[ind]
                csa = data_arrivee_local['Call Sign - IATA_ARR'].iloc[ind]
                time_sup = add_90_minutes(time)
                time_inf = add_30_minutes(time)

                liste_pos = liste_pos[liste_pos <= time_sup]
                liste_pos = liste_pos[liste_pos >= time_inf]

                if len(liste_pos) == 1:
                    csd = data_depart_local.loc[data_depart_local['Local Schedule Time_DEP'] == liste_pos[0], 
                                                         'Call Sign - IATA_DEP'].iloc[0]


                    data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Date'] == date) &
                                              (data_flight_arrivee_LX['Call Sign - IATA_ARR'] == csa), 
                                              'Call Sign - IATA_DEP'] = csd

                    data_flight_depart_LX.loc[(data_flight_depart_LX['Date'] == date) &
                                                    (data_flight_depart_LX['Call Sign - IATA_DEP'] == csd), 
                                              'Call Sign - IATA_ARR'] = csa


    # On remove celles qui sont matchés : 
    data_flight_depart_LX_done = data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_ARR']!= 'ND']
    data_flight_depart_LX = data_flight_depart_LX.loc[data_flight_depart_LX['Call Sign - IATA_ARR'] == 'ND']

    data_flight_arrivee_LX_done = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_DEP']!= 'ND']
    data_flight_arrivee_LX = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Call Sign - IATA_DEP'] == 'ND']

    data_end_LX0 = pd.merge(data_flight_arrivee_LX_done, data_flight_depart_LX_done, how = 'inner', on = ['Date', 'Call Sign - IATA_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX0['Date_DEP'] = data_end_LX0['Date'].copy()
    data_end_LX0['Date_ARR'] = data_end_LX0['Date'].copy()
    data_end_LX0.drop(columns = ['Date'], inplace = True)
    data_end_LX0['method'] = 'Only depart logic'
    data_end_LX = pd.concat([data_end_LX, data_end_LX0], ignore_index = True)
             
             
             
    print('Etape Depart Logic : ', len(data_end_LX0))    
             
             
             
                          
    # --------------------------
    # Last Choice
    # --------------------------             

    # --------------------------------------------------

    for date in data_flight_depart_LX["Date"].unique():
        data_local_arrivee = data_flight_arrivee_LX.loc[data_flight_arrivee_LX['Date'] == date].copy()
        data_local_depart = data_flight_depart_LX.loc[data_flight_depart_LX['Date'] == date].copy()

        for aircraft in data_local_arrivee['Aircraft Subtype IATA Type'].unique():

            nbr_NS_dep = 0

            data_local_arrivee_aircraft = data_local_arrivee.loc[data_local_arrivee['Aircraft Subtype IATA Type'] == aircraft].copy()

            data_local_depart_aircraft = data_local_depart.loc[data_local_depart['Aircraft Subtype IATA Type'] == aircraft].copy()

            data_local_depart_aircraft.sort_values(by='Local Schedule Time_DEP', inplace = True)

            for ind in range(len(data_local_depart_aircraft)):

                time0 = data_local_depart_aircraft['Local Schedule Time_DEP'].iloc[ind]
                time = minus_40_minutes(time0)
                csd = data_local_depart_aircraft['Call Sign - IATA_DEP'].iloc[ind]

                nbr = np.sum(data_local_arrivee_aircraft['Local Schedule Time_ARR'] <= time)

                nbr_NS_dep = max(nbr_NS_dep, ind+1-nbr)

            data_local_arrivee_aircraft.sort_values(by='Local Schedule Time_ARR', inplace = True)

            k = 0
            ind = 0

            while k < nbr_NS_dep : 

                csd = data_local_depart_aircraft['Call Sign - IATA_DEP'].iloc[ind]
                ind = ind + 1

                if len(data_local_depart_aircraft.loc[(data_local_depart_aircraft['Call Sign - IATA_DEP'] == csd) &
                                                    (data_local_depart_aircraft['Call Sign - IATA_ARR'] == 'ND')]) == 1 :
                        k = k + 1

                        data_flight_depart_LX.loc[(data_flight_depart_LX['Date'] == date) & 
                                                     (data_flight_depart_LX['Call Sign - IATA_DEP'] == csd) &
                                                    (data_flight_depart_LX['Call Sign - IATA_ARR'] == 'ND') &
                                         (data_flight_depart_LX['Aircraft Subtype IATA Type'] == aircraft),
                                                     'Night Stop_OOP+_DEP'] = 'Y'


            data_local_depart00 = data_local_depart_aircraft.loc[(data_local_depart_aircraft['Night Stop_OOP+_DEP'] != 'Y') &
                           (data_local_depart_aircraft['Call Sign - IATA_ARR'] == 'ND')].copy()

            data_local_arrivee00 = data_local_arrivee_aircraft.loc[data_local_arrivee_aircraft['Call Sign - IATA_DEP'] == 'ND'].copy()

            data_local_depart00.sort_values(by='Local Schedule Time_DEP', inplace = True)
            data_local_arrivee00.sort_values(by='Local Schedule Time_ARR', inplace = True)

            for ind in range(len(data_local_depart00['Call Sign - IATA_DEP']))  :

                if (ind < len(data_local_arrivee00)):
                    csd = data_local_depart00['Call Sign - IATA_DEP'].iloc[ind]
                    csa = data_local_arrivee00['Call Sign - IATA_ARR'].iloc[ind]
                    hour1 = data_local_arrivee00['Local Schedule Time_ARR'].iloc[ind]
                    hour2 = data_local_depart00['Local Schedule Time_DEP'].iloc[ind]


                    #if hour1 >= hour2 : 
                        #print('il y a un problème !')

                    data_flight_depart_LX.loc[(data_flight_depart_LX['Date'] == date) &
                                                (data_flight_depart_LX['Call Sign - IATA_DEP'] == csd),
                                                 'Call Sign - IATA_ARR'] = csa

                    data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Date'] == date) &
                                                (data_flight_arrivee_LX['Call Sign - IATA_ARR'] == csa),
                                                 'Call Sign - IATA_DEP'] = csd


    data_flight_arrivee_LX_done = data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Call Sign - IATA_DEP'] != 'ND') & (data_flight_arrivee_LX['Night Stop_OOP+_ARR'] != 'Y')]

    data_flight_depart_LX_done = data_flight_depart_LX.loc[(data_flight_depart_LX['Call Sign - IATA_ARR'] != 'ND') & (data_flight_depart_LX['Night Stop_OOP+_DEP'] != 'Y')]

    data_flight_arrivee_LX_NS = pd.concat([data_flight_arrivee_LX_NS, data_flight_arrivee_LX.loc[(data_flight_arrivee_LX['Call Sign - IATA_DEP'] == 'ND') |(data_flight_arrivee_LX['Night Stop_OOP+_ARR'] == 'Y')]])

    data_flight_depart_LX_NS = pd.concat([data_flight_depart_LX_NS, data_flight_depart_LX.loc[(data_flight_depart_LX['Call Sign - IATA_ARR'] == 'ND') | (data_flight_depart_LX['Night Stop_OOP+_DEP'] == 'Y')]])


    data_end_LX0 = pd.merge(data_flight_arrivee_LX_done, data_flight_depart_LX_done, how = 'inner', on = ['Date', 'Call Sign - IATA_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX0['Date_DEP'] = data_end_LX0['Date'].copy()
    data_end_LX0['Date_ARR'] = data_end_LX0['Date'].copy()
    data_end_LX0.drop(columns = ['Date'], inplace = True)
    data_end_LX0['method'] = 'Last choice'
    data_end_LX = pd.concat([data_end_LX, data_end_LX0], ignore_index = True)



    print('Etape Last Choice : ', len(data_end_LX0))    



                          
    # --------------------------
    # Last Choice NS
    # --------------------------   

    data_flight_depart_LX_NS['Call Sign - IATA_ARR'] = 'ND'
    data_flight_arrivee_LX_NS['Call Sign - IATA_DEP'] = 'ND'

    for date in  data_flight_arrivee_LX_NS['Date'].unique() :
        for aircraft in data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Date'] == date, 'Aircraft Subtype IATA Type'].unique():

            data_local_arr = data_flight_arrivee_LX_NS.loc[(data_flight_arrivee_LX_NS['Date'] == date) &
                      (data_flight_arrivee_LX_NS['Aircraft Subtype IATA Type'] == aircraft)].copy()
            
            data_local_dep = data_flight_depart_LX_NS.loc[(data_flight_depart_LX_NS['Date'] == date + timedelta(days = 1)) &
                                                         (data_flight_depart_LX_NS['Aircraft Subtype IATA Type'] == aircraft)].copy()

            n = min(len(data_local_arr), len(data_local_dep))
            matrice = {}

            for cs_arr in data_local_arr['Call Sign - IATA_ARR'].unique():
                matrice[cs_arr] ={}
                for cs_dep in data_local_dep['Call Sign - IATA_DEP'].unique():
                    matrice[cs_arr][cs_dep] = 0
                    if cs_arr in dico_CS_NS.keys():
                        if cs_dep in dico_CS_NS[cs_arr].keys():
                            matrice[cs_arr][cs_dep] = dico_CS_NS[cs_arr][cs_dep]


            for _ in range(n):
                cs_arr_max, cs_dep_max = recherche_max(matrice)

                del matrice[cs_arr_max]
                for c1 in matrice.keys(): 
                    del matrice[c1][cs_dep_max]


                data_flight_arrivee_LX_NS.loc[(data_flight_arrivee_LX_NS['Date'] == date)&
                                             (data_flight_arrivee_LX_NS['Aircraft Subtype IATA Type'] == aircraft)&
                                             (data_flight_arrivee_LX_NS['Call Sign - IATA_ARR'] == cs_arr_max),
                                             'Call Sign - IATA_DEP'] = cs_dep_max

                data_flight_depart_LX_NS.loc[(data_flight_depart_LX_NS['Date'] == date + timedelta(days = 1))&
                                             (data_flight_depart_LX_NS['Aircraft Subtype IATA Type'] == aircraft)&
                                             (data_flight_depart_LX_NS['Call Sign - IATA_DEP'] == cs_dep_max),
                                             'Call Sign - IATA_ARR'] = cs_arr_max



    data_flight_depart_LX_NS_done = data_flight_depart_LX_NS.loc[data_flight_depart_LX_NS['Call Sign - IATA_ARR'] !='ND']
    data_flight_depart_LX_NS = data_flight_depart_LX_NS.loc[data_flight_depart_LX_NS['Call Sign - IATA_ARR'] =='ND']

    data_flight_arrivee_LX_NS_done = data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Call Sign - IATA_DEP']!='ND']
    data_flight_arrivee_LX_NS = data_flight_arrivee_LX_NS.loc[data_flight_arrivee_LX_NS['Call Sign - IATA_DEP']=='ND']
             
             
    data_flight_depart_LX_NS_done['Date_DEP'] = data_flight_depart_LX_NS_done['Date'].copy()
    data_flight_arrivee_LX_NS_done['Date_ARR'] = data_flight_arrivee_LX_NS_done['Date'].copy()
    data_flight_arrivee_LX_NS_done['Date'] = data_flight_arrivee_LX_NS_done['Date'] + timedelta(days = 1)

    data_end_LX0 = pd.merge(data_flight_arrivee_LX_NS_done, data_flight_depart_LX_NS_done, how = 'inner',
           on = ['Date', 'Call Sign - IATA_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type'])

    data_end_LX0.drop(columns = ['Date'], inplace = True)
    data_end_LX0['method'] = 'Last choice NS'
    data_end_LX = pd.concat([data_end_LX, data_end_LX0], ignore_index = True)
             
    print('Etape Last Choice NS : ', len(data_end_LX0))    
             
    return data_end_LX
