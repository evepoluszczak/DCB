#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les imports de Traitement_donnee.py fonctionnent
"""

import sys
import os

# Ajouter le chemin pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TraitementDonnee', 'Code'))

print("=" * 60)
print("TEST DES IMPORTS - TRAITEMENT_DONNEE.PY")
print("=" * 60)
print()

# Liste des modules à tester
modules = [
    ("chemin_dossier", ["CHEMIN_INPUT", "CHEMIN_OUTPUT"]),
    ("Avion_LinkHisto", ["Historique"]),
    ("Avion_LinkFutur", ["Futur"]),
    ("Avion_ExpectedTime", ["Delai"]),
    ("Avion_Mouvements", ["Mouvements"]),
    ("Pax_Embarquement", ["Embarquement"]),
    ("Pax_ApplicationSUP", ["ApplicationSUP"]),
    ("Pax_PlanningIdealDouane", ["PlanningIdealDouane"]),
    ("Pax_PlanningIdealSurete", ["PlanningIdealSurete"]),
    ("Pax_SUPjson", ["SUPjson"]),
    ("PBI_CalculPowerBI", ["CalculPBI"]),
    ("Pax_PlanningSurete", ["PlanningSurete"]),
]

success_count = 0
fail_count = 0
errors = []

for module_name, functions in modules:
    try:
        module = __import__(module_name, fromlist=functions)

        # Vérifier que les fonctions/variables existent
        missing = []
        for func in functions:
            if not hasattr(module, func):
                missing.append(func)

        if missing:
            print(f"⚠️  {module_name:30s} : importé mais manque {missing}")
            fail_count += 1
            errors.append(f"{module_name} : manque {missing}")
        else:
            print(f"✅ {module_name:30s} : OK")
            success_count += 1

    except ImportError as e:
        print(f"❌ {module_name:30s} : ERREUR - {e}")
        fail_count += 1
        errors.append(f"{module_name} : {e}")
    except Exception as e:
        print(f"⚠️  {module_name:30s} : ERREUR - {e}")
        fail_count += 1
        errors.append(f"{module_name} : {e}")

# Vérifier que CHEMIN_INPUT et CHEMIN_OUTPUT pointent vers les bons dossiers
print()
print("=" * 60)
print("VÉRIFICATION DES CHEMINS")
print("=" * 60)

try:
    from chemin_dossier import CHEMIN_INPUT, CHEMIN_OUTPUT
    print(f"✅ CHEMIN_INPUT  : {CHEMIN_INPUT}")
    print(f"   → Existe : {CHEMIN_INPUT.exists()}")
    print(f"✅ CHEMIN_OUTPUT : {CHEMIN_OUTPUT}")
    print(f"   → Existe : {CHEMIN_OUTPUT.exists()}")

    # Vérifier WEBI
    webi_path = CHEMIN_INPUT / "WEBI"
    print(f"\n📁 Dossier WEBI   : {webi_path}")
    print(f"   → Existe : {webi_path.exists()}")

except Exception as e:
    print(f"❌ Erreur lors de la vérification des chemins : {e}")
    fail_count += 1

# Résumé
print()
print("=" * 60)
print("RÉSUMÉ")
print("=" * 60)
print(f"✅ Imports réussis : {success_count}")
print(f"❌ Imports échoués : {fail_count}")

if errors:
    print("\n⚠️  ERREURS DÉTECTÉES :")
    for error in errors:
        print(f"   - {error}")
else:
    print("\n🎉 Tous les imports fonctionnent correctement !")

print("=" * 60)

if fail_count > 0:
    print("\n⚠️  NOTE : Certains modules peuvent nécessiter des fichiers de données")
    print("   pour s'importer correctement. Les erreurs ci-dessus peuvent être")
    print("   normales si les données d'entrée ne sont pas présentes.")

sys.exit(0 if fail_count == 0 else 1)
