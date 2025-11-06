import os
import pandas as pd
import numpy as np

from pathlib import Path
import tqdm

import Avion_Fonctions_data_future
import Avion_Fonctions_LX

def Futur(data):
    # Copie les fichiers de planification easyjet dans le bon dossier avec un nom adapté
    dossier_planning_EZS_PBI = "//gva.tld/aig/O/12_EM-DO/4_OOP/17_PBI/01 - Data/02 - Data/Airlines/EasyJet/EasyJet - SSIM/Easyjet_SSIM_xlsx"
    dossier_planning_EZS_DCB = "//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/Planning_EZS"
    Avion_Fonctions_data_future.copier_et_renommer_fichiers(dossier_planning_EZS_PBI,dossier_planning_EZS_DCB)

    # Chargement du fichier
    path = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI")
    data_flight = pd.read_csv(path / "DCB_BSH_futur.csv",low_memory=False)

    data_flight["Gate OOP+"] = data_flight["Gate OOP+"].astype(str)
    data_flight.loc[(data_flight["Gate OOP+"] == "PAV D") & (data_flight["Stand OOP+"].isin(["83","84"])),"Bus OOP+ (Y/N)"] = "N"

    data_flight.fillna({"Expected Pax":0},inplace=True)

    data_flight["Bus_OOP+"] = 0
    data_flight.loc[data_flight["Bus OOP+ (Y/N)"] == "Y", "Bus_OOP+"] = (data_flight.loc[data_flight['Bus OOP+ (Y/N)'] == "Y","Expected Pax"]/70).astype(int) + 1
    data_flight.loc[data_flight["Call Sign - IATA"] == "LX022","Bus_OOP+"] += 1
    data_flight.loc[(data_flight['Bus OOP+ (Y/N)'] == "Y") & (data_flight["Airline IATA Code"].isin(["LX","AC","CA","DL","EK","EY","KU","QR","SV","UA","ET","KQ","ME","LY","MU"])) & (data_flight["Arrival - Departure Code"] == "A"),"Bus_OOP+"] += 1

    data_flight.replace({"Aircraft IATA SubType":{"ND":data_flight["Aircraft Subtype IATA SubType"]}},inplace=True)
    data_flight.drop(columns=["Aircraft Subtype IATA SubType","Bus OOP+ (Y/N)"],inplace=True)

    new_columns_name = {'Stand OOP+' : 'Stand_OOP+', 'Stand Group OOP+' : 'Stand Group_OOP+',
                    'Night Stop OOP+' : 'Night Stop_OOP+', "Aircraft IATA SubType" : "Aircraft Subtype IATA Type",
                    'Expected Pax' : 'Pax', 'Aircraft Subtype Wingspan Code' : 'Wingspan Code'}

    data_flight.rename(columns = new_columns_name, inplace = True)

    data_flight["Date"] = pd.to_datetime(data_flight["Date"])
    data_flight["Local Schedule Time"] = data_flight["Local Schedule Time"].str[11:16]
    data_flight["Season"] = data_flight['Season'].str[:6]

    data_end = Avion_Fonctions_data_future.non_LX_non_EZS(data_flight.copy())

    # On tri ceux qui ne sont pas triés 

    explore_arr = data_end[['Call Sign - IATA_ARR', 'Date_ARR']].copy()
    new_col = {'Date_ARR' : 'Date',
            'Call Sign - IATA_ARR' : 'Call Sign - IATA'}
    explore_arr.rename(columns = new_col, inplace = True)
    explore_arr['Val'] =1


    explore_dep = data_end[['Call Sign - IATA_DEP', 'Date_DEP']].copy()
    new_col = {'Date_DEP' : 'Date',
            'Call Sign - IATA_DEP' : 'Call Sign - IATA'}
    explore_dep.rename(columns = new_col, inplace = True)
    explore_dep['Val1']=1

    data_flight = pd.merge(data_flight, explore_arr, on = ['Date', 'Call Sign - IATA'], how = 'left')
    data_flight = pd.merge(data_flight, explore_dep, on = ['Date', 'Call Sign - IATA'], how = 'left')

    data_flight = data_flight.loc[(data_flight['Val'] != 1) & (data_flight['Val1'] != 1)]
    data_flight.drop(columns = ['Val', 'Val1','Linked Flight Call Sign - IATA'], inplace = True)


    data_flight_LX = data_flight.loc[data_flight['Airline IATA Code'] == 'LX'].copy()
    data_flight_EZS = data_flight.loc[data_flight['Airline IATA Code'].isin(['EZS','EJU','EZY'])].copy()

    data_end = Avion_Fonctions_data_future.for_EZS(data_flight_EZS, data_end)

    #dico_CS, dico_CS_summer, dico_CS_inv, dico_CS_inv_summer, dico_dest, dico_dest_summer, dico_CS_NS, dico_CS_NS_summer, dico_dest_NS, dico_dest_NS_summer, liste_NS, liste_NNS, liste_NS_summer, liste_NNS_summer = Fonctions_data_future.creation_from_histo()

    nouveau_repertoire = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Output")
    os.chdir(nouveau_repertoire)

    data = data.loc[data['Airline IATA Code'] == 'LX']
    liste_columns = ['Date_ARR', 'Date_DEP', 'Call Sign - IATA_ARR', 'Aircraft Subtype IATA Type', 
                        'Official IATA Airport Code_ARR', 'Local Schedule Time_ARR', 'Call Sign - IATA_DEP',
                        'Official IATA Airport Code_DEP', 'Local Schedule Time_DEP', 'Night Stop_ARR', 'Season']
    data = data[liste_columns]
      
    data_summer = data.loc[data['Season'] == 'SUMMER'].copy()
    data_NS_summer = data_summer.loc[data_summer['Night Stop_ARR'] == 'Y'].copy()
    data_NNS_summer = data_summer.loc[data_summer['Night Stop_ARR'] == 'N'].copy()

    data = data.loc[data['Season'] == 'WINTER']

    data_NS = data.loc[data['Night Stop_ARR'] == 'Y'].copy()
    data_NNS = data.loc[data['Night Stop_ARR'] == 'N'].copy()
        
        
        # 1) Pour les non NS -- Dico Call Sign

    dico_CS = {}

    for callsign in tqdm.tqdm(data_NNS['Call Sign - IATA_ARR'].unique()):
        data_local = data_NNS.loc[data_NNS['Call Sign - IATA_ARR'] == callsign].copy()

        if len(data_local)>15:
            dico_CS[callsign] = {}
            for cs in data_local['Call Sign - IATA_DEP'].unique():
                dico_CS[callsign][cs] = np.sum(data_local['Call Sign - IATA_DEP'] == cs)/len(data_local)


    dico_CS_inv = {}

    for callsign in tqdm.tqdm(data_NNS['Call Sign - IATA_DEP'].unique()):
        data_local = data_NNS.loc[data_NNS['Call Sign - IATA_DEP'] == callsign].copy()
        if len(data_local)>10:
            dico_CS_inv[callsign] = {}
            for cs in data_local['Call Sign - IATA_ARR'].unique():
                dico_CS_inv[callsign][cs] = np.sum(data_local['Call Sign - IATA_ARR'] == cs)/len(data_local)


    # 2) Pour les non NS -- Dico Destination et Heure            

    dico_dest = {}

    for dest_arr in tqdm.tqdm(data_NNS['Official IATA Airport Code_ARR'].unique()):
        data_local = data_NNS.loc[data_NNS['Official IATA Airport Code_ARR'] == dest_arr].copy()
        dico_dest[dest_arr] = {}

        for time in data_local['Local Schedule Time_ARR'].unique():
            data_local0 = data_local.loc[data_local['Local Schedule Time_ARR'] == time].copy()

            if len(data_local0)>15:
                dico_dest[dest_arr][time] = {}

                for dest_dep in data_local0['Official IATA Airport Code_DEP'].unique():
                    dico_dest[dest_arr][time][dest_dep] = np.sum(data_local0['Official IATA Airport Code_DEP'] == dest_dep)/len(data_local0)

        # 3) Pour les NS -- Dico Call Sign

    dico_CS_NS = {}

    for callsign in tqdm.tqdm(data_NS['Call Sign - IATA_ARR'].unique()):
        data_local = data_NS.loc[data_NS['Call Sign - IATA_ARR'] == callsign].copy()
        if len(data_local)>6:
            dico_CS_NS[callsign] = {}
            for cs in data_local['Call Sign - IATA_DEP'].unique():
                dico_CS_NS[callsign][cs] = np.sum(data_local['Call Sign - IATA_DEP'] == cs)/len(data_local)


    dico_dest_NS = {}

    for dest_arr in tqdm.tqdm(data_NS['Official IATA Airport Code_ARR'].unique()):
        data_local = data_NS.loc[data_NS['Official IATA Airport Code_ARR'] == dest_arr].copy()

        dico_dest_NS[dest_arr] = {}

        for weekday in data_local['Date_ARR'].dt.weekday.unique():
            data_local0 = data_local.loc[data_local['Date_ARR'].dt.weekday == weekday].copy()

            if len(data_local0)>5:
                dico_dest_NS[dest_arr][weekday] = {}
                for dest_dep in data_local0['Official IATA Airport Code_DEP'].unique():
                    dico_dest_NS[dest_arr][weekday][dest_dep] = np.sum(data_local0['Official IATA Airport Code_DEP'] == dest_dep)/len(data_local0)


        
        
        # 1) Pour les non NS -- Dico Call Sign

    dico_CS_summer = {}

    for callsign in tqdm.tqdm(data_NNS_summer['Call Sign - IATA_ARR'].unique()):
        data_local = data_NNS_summer.loc[data_NNS_summer['Call Sign - IATA_ARR'] == callsign].copy()

        if len(data_local)>15:
            dico_CS_summer[callsign] = {}
            for cs in data_local['Call Sign - IATA_DEP'].unique():
                dico_CS_summer[callsign][cs] = np.sum(data_local['Call Sign - IATA_DEP'] == cs)/len(data_local)

        # Dico pour les CS depart puis arrivee

    dico_CS_inv_summer = {}

    for callsign in tqdm.tqdm(data_NNS_summer['Call Sign - IATA_DEP'].unique()):
        data_local = data_NNS_summer.loc[data_NNS_summer['Call Sign - IATA_DEP'] == callsign].copy()
        if len(data_local)>10:
            dico_CS_inv_summer[callsign] = {}
            for cs in data_local['Call Sign - IATA_ARR'].unique():
                dico_CS_inv_summer[callsign][cs] = np.sum(data_local['Call Sign - IATA_ARR'] == cs)/len(data_local)


        # 2) Pour les non NS -- Dico Destination et Heure            

    dico_dest_summer = {}

    for dest_arr in tqdm.tqdm(data_NNS_summer['Official IATA Airport Code_ARR'].unique()):
        data_local = data_NNS_summer.loc[data_NNS_summer['Official IATA Airport Code_ARR'] == dest_arr].copy()
        dico_dest_summer[dest_arr] = {}

        for time in data_local['Local Schedule Time_ARR'].unique():
            data_local0 = data_local.loc[data_local['Local Schedule Time_ARR'] == time].copy()

            if len(data_local0)>15:
                dico_dest_summer[dest_arr][time] = {}

                for dest_dep in data_local0['Official IATA Airport Code_DEP'].unique():
                    dico_dest_summer[dest_arr][time][dest_dep] = np.sum(data_local0['Official IATA Airport Code_DEP'] == dest_dep)/len(data_local0)

        # 3) Pour les NS -- Dico Call Sign

    dico_CS_NS_summer = {}

    for callsign in tqdm.tqdm(data_NS_summer['Call Sign - IATA_ARR'].unique()):
        data_local = data_NS_summer.loc[data_NS_summer['Call Sign - IATA_ARR'] == callsign].copy()
        if len(data_local)>6:
            dico_CS_NS_summer[callsign] = {}
            for cs in data_local['Call Sign - IATA_DEP'].unique():
                dico_CS_NS_summer[callsign][cs] = np.sum(data_local['Call Sign - IATA_DEP'] == cs)/len(data_local)


    dico_dest_NS_summer = {}

    for dest_arr in tqdm.tqdm(data_NS_summer['Official IATA Airport Code_ARR'].unique()):
        data_local = data_NS_summer.loc[data_NS_summer['Official IATA Airport Code_ARR'] == dest_arr].copy()

        dico_dest_NS_summer[dest_arr] = {}

        for weekday in data_local['Date_ARR'].dt.weekday.unique():
            data_local0 = data_local.loc[data_local['Date_ARR'].dt.weekday == weekday].copy()

            if len(data_local0)>5:
                dico_dest_NS_summer[dest_arr][weekday] = {}
                for dest_dep in data_local0['Official IATA Airport Code_DEP'].unique():
                    dico_dest_NS_summer[dest_arr][weekday][dest_dep] = np.sum(data_local0['Official IATA Airport Code_DEP'] == dest_dep)/len(data_local0)
                        
                        
                        
                        
                        
    liste_NS = np.array(list(data_NS['Call Sign - IATA_DEP']) + list(data_NS['Call Sign - IATA_ARR']))
    liste_NNS = np.array(list(data_NNS['Call Sign - IATA_DEP']) + list(data_NNS['Call Sign - IATA_ARR']))

    liste_NS_summer = np.array(list(data_NS_summer['Call Sign - IATA_DEP']) + list(data_NS_summer['Call Sign - IATA_ARR']))
    liste_NNS_summer = np.array(list(data_NNS_summer['Call Sign - IATA_DEP']) + list(data_NNS_summer['Call Sign - IATA_ARR']))

    saisons_a_prevoir = data_flight_LX["Season"].drop_duplicates().to_list()
    for saison in saisons_a_prevoir:
        data_end_LX = Avion_Fonctions_LX.LX(data_flight_LX, saison, liste_NS, liste_NNS, dico_CS, dico_CS_inv, dico_dest, dico_CS_NS, dico_dest_NS)
        data_end = pd.concat([data_end, data_end_LX], ignore_index = True)

    data_end.drop(columns = ['Date', 'Arrival - Departure Code', 'Night Stop_OOP+_ARR',
                            'Night Stop_OOP+_DEP'], inplace = True)

    data_GCO = data_end.copy()
    data_GCO = data_GCO[['Date_ARR', 'Local Schedule Time_ARR', 'Call Sign - IATA_ARR', 'Date_DEP', 'Local Schedule Time_DEP', 'Call Sign - IATA_DEP', 'method']]

    data_end.drop(columns = ['method'], inplace = True)
    data_end['Night Stop_OOP+'] = 'N'
    data_end.loc[data_end['Date_ARR'] != data_end['Date_DEP'], 'Night Stop_OOP+'] = 'Y'


    nouveau_repertoire = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Output")
    os.chdir(nouveau_repertoire)
    data_end.to_csv('PlanVol_Futur.csv', index=False)
    data_GCO.to_csv('Link_Futur.csv', index = False)

    vol_type = pd.DataFrame(columns = ["Date","Total_DEP","Schengen_DEP","France_DEP","NonSchengen_DEP","Total_ARR","Schengen_ARR","France_ARR","NonSchengen_ARR"]) #dtype={"Date":"str","Total_DEP":"int","Schengen_DEP":"int","France_DEP":"int","NonSchengen_DEP":"int","Total_ARR":"int","Schengen_ARR":"int","France_ARR":"int","NonSchengen_ARR":"int"}
    for date in data_end['Date_DEP'].drop_duplicates():
        data_jour_dep = data_end[data_end["Date_DEP"]==date]
        data_jour_arr = data_end[data_end["Date_ARR"]==date]
        nbSdep = len(data_jour_dep[(data_jour_dep["French Sector_DEP"] == "N") & (data_jour_dep["Schengen Flight_DEP"] == "Y")])
        nbNSdep = len(data_jour_dep[data_jour_dep["Schengen Flight_DEP"] == "N"])
        nbFdep = len(data_jour_dep[data_jour_dep["French Sector_DEP"] == "Y"])
        nbTdep = nbSdep + nbNSdep + nbFdep
        nbSarr = len(data_jour_arr[(data_jour_arr["French Sector_ARR"] == "N") & (data_jour_arr["Schengen Flight_ARR"] == "Y")])
        nbNSarr = len(data_jour_arr[data_jour_arr["Schengen Flight_ARR"] == "N"])
        nbFarr = len(data_jour_arr[data_jour_arr["French Sector_ARR"] == "Y"])
        nbTarr = nbSarr + nbNSarr + nbFarr
        vol_type.loc[len(vol_type)] = [str(date),nbTdep,nbSdep,nbFdep,nbNSdep,nbTarr,nbSarr,nbFarr,nbNSarr]

    min = vol_type.min()
    min["Date"] = "min"
    max = vol_type.max()
    max["Date"] = "max"
    vol_type.loc[len(vol_type)] = min
    vol_type.loc[len(vol_type)] = max
    vol_type.to_csv("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/7_LOUISE/DCB LLA/Creation_Fichiers/vol_type.csv",index=False)

    return data_end
