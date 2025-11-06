import os
import pandas as pd
from datetime import datetime

from pathlib import Path


'''
But de ce fichier : 
Prendre les fichiers de Bruno mis à jour automatiquement (ici 2023 et 2022) puis les modifier pour obtenir un unique fichier avec ces colonnes : 

['Date', 'Call Sign - IATA_ARR', 'Aircraft Registration',
       'Aircraft Subtype IATA Type', 'Wingspan Code', 'MTOW', 'Flight Service Type',
       'Schengen Flight_ARR', 'French Sector_ARR', 'Airline IATA Code',
       'Official IATA Airport Code_ARR', 'Local Schedule Time_ARR',
       'Local Skd Time 60 minutes_ARR', 'Local Actual Time_ARR', 'VID', 'Pax_ARR',
       'Local Pax', 'Bus_OOP+_ARR', 'Capacity', 'Call Sign - IATA_DEP',
       'Schengen Flight_DEP', 'French Sector_DEP',
       'Official IATA Airport Code_DEP', 'Local Schedule Time_DEP',
       'Local Skd Time 60 minutes_DEP', 'Local Actual Time_DEP', 'Pax_DEP',
       'Bus_OOP+_DEP', 'Date_ARR', 'Night Stop_ARR', 'Local TOBT Time']
'''

def Historique():
       # ----------------------------------
       # 1- Chargement du data Live flight
       # ----------------------------------

       print("I am loading the realized flights")
       YEAR = datetime.now().year

       path = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI")
       data_flight = pd.read_csv(path / "DCB_BSH_link.csv",low_memory=False)
       data_flight["Date"] = pd.to_datetime(data_flight["Date"])
       data_flight["Local Schedule Time"] = data_flight["Local Schedule Time"].str[11:16]
       data_flight["Local TOBT Time"] = data_flight["Local TOBT Time"].str[11:16]
       data_flight["Local Actual Time"] = data_flight["Local Actual Time"].str[11:16]

       # 1-1- Traitements de l'ensemble

       data_flight["Pax"] = data_flight["Local Pax"] + data_flight["Connecting Pax"]
       data_flight.drop(columns=["Connecting Pax","Transit Pax"],inplace=True)

       data_flight.replace({"Aircraft IATA SubType":{"ND":data_flight["Aircraft Subtype IATA SubType"]}},inplace=True)
       data_flight.drop(columns="Aircraft Subtype IATA SubType",inplace=True)
       data_flight.rename(columns={"Aircraft IATA SubType":"Aircraft Subtype IATA Type"},inplace=True)

       data_flight["Retard non GA_DEP"] = 0
       data_flight.fillna({"Delay 1 Sum":0,"Delay 2 Sum":0,"Delay 3 Sum":0,"Delay 4 Sum":0},inplace=True)
       data_flight.loc[data_flight["IR 1 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Retard non GA_DEP"] += data_flight.loc[data_flight["IR 1 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Delay 1 Sum"]
       data_flight.loc[data_flight["IR 2 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Retard non GA_DEP"] += data_flight.loc[data_flight["IR 2 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Delay 2 Sum"]
       data_flight.loc[data_flight["IR 3 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Retard non GA_DEP"] += data_flight.loc[data_flight["IR 3 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Delay 3 Sum"]
       data_flight.loc[data_flight["IR 4 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Retard non GA_DEP"] += data_flight.loc[data_flight["IR 4 Code"].isin(["70","71","72","73","74","75","76","77","78","80","81","82","83","84"]),"Delay 4 Sum"]
       data_flight.drop(columns=["Delay 1 Sum","IR 1 Code","Delay 2 Sum","IR 2 Code","Delay 3 Sum","IR 3 Code","Delay 4 Sum","IR 4 Code"],inplace=True)
       # 1-2- Regrouper les arrivees et les departs par VID

       data_flight_depart = data_flight.loc[data_flight["Arrival - Departure Code"] == "D"].copy()

       liste_columns_depart = ['Call Sign - IATA', 'Schengen Flight', 'French Sector',
                     'Official IATA Airport Code', 'Local Schedule Time', 'Local Skd Time Grp 60 minutes', 
                            'Local Actual Time',
                     'VID', 'Local Pax', 'Pax', 'Nb bus', 'Date', 'Nb Bags Total', 'Night Stop', 'Local TOBT Time', "Retard non GA_DEP"]

       data_flight_depart = data_flight_depart[liste_columns_depart]

       new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_DEP',
                     'Schengen Flight' : 'Schengen Flight_DEP',
                     'French Sector' : 'French Sector_DEP',
                     'Official IATA Airport Code' : 'Official IATA Airport Code_DEP',
                     'Local Schedule Time' : 'Local Schedule Time_DEP',
                     'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_DEP',
                     'Local Actual Time' : 'Local Actual Time_DEP',
                     'Pax' : 'Pax_DEP', 'Nb bus' : 'Bus_OOP+_DEP',
                     'Date' : 'Date_DEP', 'Nb Bags Total' : 'Nb Bags Total_DEP',
                     'Local Pax' : 'Local Pax_DEP', 'Night Stop' : 'Night Stop_DEP'}

       data_flight_depart.rename(columns = new_columns_name, inplace = True)

       # ---

       new_columns_name = {'Call Sign - IATA' : 'Call Sign - IATA_ARR',
                     'Schengen Flight' : 'Schengen Flight_ARR',
                     'French Sector' : 'French Sector_ARR',
                     'Official IATA Airport Code' : 'Official IATA Airport Code_ARR',
                     'Local Schedule Time' : 'Local Schedule Time_ARR',
                     'Local Skd Time Grp 60 minutes' : 'Local Skd Time 60 minutes_ARR',
                     'Local Actual Time' : 'Local Actual Time_ARR',
                     'Pax' : 'Pax_ARR', 'Nb bus' : 'Bus_OOP+_ARR',
                     'Date' : 'Date_ARR', 'Nb Bags Total' : 'Nb Bags Total_ARR',
                     'Local Pax' : 'Local Pax_ARR', 'Night Stop' : 'Night Stop_ARR',
                     'Stand OOP+' : 'Stand_OOP+', 'Stand Group OOP+' : 'Stand Group_OOP+',
                     'Night Stop OOP+' : 'Night Stop_OOP+',
                     'Maximum Take Off Weight' : 'MTOW',
                     'Aircraft Subtype Wingspan Code' : 'Wingspan Code'}

       data_flight = data_flight.loc[data_flight["Arrival - Departure Code"] == "A"].copy()
       Conversion_airline = data_flight.loc[data_flight["Date"].dt.year == YEAR-1 ,"Airline IATA Code"].value_counts()
       data_flight.drop(columns = ['Arrival - Departure Code', 'Local TOBT Time','Retard non GA_DEP'], inplace=True)
       data_flight.rename(columns = new_columns_name, inplace = True)

       # ---

       data_flight = pd.merge(data_flight, data_flight_depart, on = "VID")

       # ----------------------------------
       # 3) Chargement du data Set Final
       # ----------------------------------

       print("finiiiiiiiiiii !!!!!")

       print('Nombre de vols qui manque la valeur TOBT : ', len(data_flight.loc[data_flight['Local TOBT Time'].isna()]), '.',sep='')
       print('Sur : ', len(data_flight), ' valeurs totales.',sep='')

       #nouveau_repertoire = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/7_LOUISE/DCB LLA/Creation_Fichiers")
       #os.chdir(nouveau_repertoire)

       data_flight.loc[data_flight['Local TOBT Time'].isna(), 'Local TOBT Time'] = data_flight.loc[data_flight['Local TOBT Time'].isna(), 'Local Actual Time_DEP']
                            
       data_flight['Season'] = data_flight['Season'].str[:6]

       conversion_MTOW = data_flight[["Airline IATA Code", "Aircraft Subtype IATA Type", "MTOW"]]
       conversion_MTOW = conversion_MTOW[conversion_MTOW['MTOW'] != 0]

       # 2-4. Grouper par les colonnes, calculer la moyenne de MTOW, puis arrondir
       conversion_MTOW = conversion_MTOW.groupby(['Airline IATA Code', 'Aircraft Subtype IATA Type'])['MTOW'].mean().round().astype(int).reset_index()

       nouveau_repertoire = Path("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Output")
       os.chdir(nouveau_repertoire)
       data_flight.to_csv('PlanVol_Historique.csv', index=False)
       conversion_MTOW.to_csv("Conversion_MTOW.csv", index=False)
       Conversion_airline.to_csv("Conversion_airline.csv")
       return data_flight, conversion_MTOW, Conversion_airline
