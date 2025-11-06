import pandas as pd

bus = pd.read_csv("D:/users/bastien.schneuwly/workfolders/documents/Stage_Bastien/DCB_BSHMisiionBus.csv")

bus_interet = bus.iloc[0:len(bus),[0,1,4,5,6,7,8,9,10,11,13,15,16]]
bus_interet = bus_interet[bus_interet["Type Mission"].isin(["Débarquement","Embarquement"])]
bus_interet = bus_interet[-bus_interet['"Initial" - Texte'].isna()]
bus_interet = bus_interet.sort_values(by=["Date Mission","Numéro de mission"]).reset_index(drop=True)

message = bus_interet['"Initial" - Texte'].str.replace(" ","").str.replace("\n",":").str.replace(">",":").str.replace(",",":").str.replace("-",":").str.split(":")

masque = message.str[3]=="MODIF"
message[masque] = message[masque].str[:3]+message[masque].str[4:]

masque = message.str[6]==""
message[masque] = message[masque].str[:6]+message[masque].str[7:]

masque = message.str[7]=="LTA"
masque2 = message.str[8]==""
message[(masque)&(-masque2)] = message[(masque)&(-masque2)].str[:7]+message[(masque)&(-masque2)].str[10:]
message[(masque)&(masque2)] = message[(masque)&(masque2)].str[:7]+message[(masque)&(masque2)].str[9:]

masque = message.str[8]=="DC"
message[masque] = message[masque].str[:8]+message[masque].str[9:]