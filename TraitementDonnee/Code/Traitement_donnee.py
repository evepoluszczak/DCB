from Avion_LinkHisto import Historique
from Avion_LinkFutur import Futur
from Avion_ExpectedTime import Delai
from Avion_Mouvements import Mouvements
from Pax_Embarquement import Embarquement
from Pax_ApplicationSUP import ApplicationSUP
from Pax_PlanningIdealDouane import PlanningIdealDouane
from Pax_PlanningIdealSurete import PlanningIdealSurete
from Pax_SUPjson import SUPjson
from PBI_CalculPowerBI import CalculPBI
from Pax_PlaningSurete import PlanningSurete
from time import time
import os
from datetime import datetime

a = time()

os.chdir("//gva.tld/aig/O/12_EM-DO/4_OOP/10_PERSONAL_FOLDERS/8_BASTIEN/DCB_Standalone_App/TraitementDonnee/Data/Input/WEBI")
for file in os.listdir():
    date = datetime.fromtimestamp(os.path.getmtime(file)).date()
    if date != datetime.now().date():
        print(f"L'export WEBI {file} n'a pas fonctionné aujourd'hui. La version utilisée sera celle du {date}.")

print("Traitement de la donnée historique")
data_histo, conv_MTOW, conv_airline = Historique()

print("Traitement de la donnée future")
data_futur = Futur(data_histo)

print("Calcul des retards")
data_predi = Delai(conv_MTOW,conv_airline,data_histo,data_futur)

print("Calcul du nombre de mouvements par heure roulante")
Mouvements(data_predi)

print("Calcul des embarquements par tranche de 5 minutes")
Embarquement(data_predi)

print("Application des show-up profiles aux vols")
DCB_xlsx, PlanningCI_xlsx = ApplicationSUP()

print("Transformation du planning sûreté au format DCB app python")
PlanningSurete("csv")

print("Calcul du planning idéal à la douane")
PlanningIdealDouane(DCB_xlsx)

print("Calcul du planning idéal à la sûreté")
PlanningIdealSurete(DCB_xlsx)

print("Transformation de la donnée au format DCB app python")
SUPjson(DCB_xlsx, PlanningCI_xlsx)

print("Transformation de la donnée au format DCB PowerBI")
CalculPBI()

print("Fini!")

b=time()
t=b-a
print(f"Temps de process total : {int(t/60)} minutes et {int(t%60)} secondes!")
