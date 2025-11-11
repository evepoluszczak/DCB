#!/usr/bin/env python3
"""
Script de test pour vérifier que les chemins locaux fonctionnent correctement
"""

import sys
import os

# Ajouter le chemin pour importer chemin_dossier
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TraitementDonnee', 'Code'))

print("=" * 60)
print("TEST DES CHEMINS LOCAUX - DCB APPLICATION")
print("=" * 60)

try:
    from chemin_dossier import (
        CHEMIN_APP_RACINE,
        CHEMIN_DATA_SOURCE,
        DOSSIER_DATA,
        CHEMIN_INPUT,
        CHEMIN_OUTPUT,
        DOSSIER_TRAITEMENT
    )

    print("\n✅ Import du module chemin_dossier réussi!\n")

    # Afficher tous les chemins
    print("CHEMINS CONFIGURÉS:")
    print("-" * 60)
    print(f"  📁 CHEMIN_APP_RACINE    : {CHEMIN_APP_RACINE}")
    print(f"  📊 CHEMIN_DATA_SOURCE   : {CHEMIN_DATA_SOURCE}")
    print(f"  🔧 DOSSIER_TRAITEMENT   : {DOSSIER_TRAITEMENT}")
    print(f"  💾 DOSSIER_DATA         : {DOSSIER_DATA}")
    print(f"  📥 CHEMIN_INPUT         : {CHEMIN_INPUT}")
    print(f"  📤 CHEMIN_OUTPUT        : {CHEMIN_OUTPUT}")

    # Vérifier l'existence des dossiers
    print("\n" + "=" * 60)
    print("VÉRIFICATION DES DOSSIERS:")
    print("-" * 60)

    chemins = {
        "CHEMIN_APP_RACINE": CHEMIN_APP_RACINE,
        "CHEMIN_DATA_SOURCE": CHEMIN_DATA_SOURCE,
        "DOSSIER_TRAITEMENT": DOSSIER_TRAITEMENT,
        "DOSSIER_DATA": DOSSIER_DATA,
        "CHEMIN_INPUT": CHEMIN_INPUT,
        "CHEMIN_OUTPUT": CHEMIN_OUTPUT,
    }

    all_exist = True
    for nom, chemin in chemins.items():
        existe = chemin.exists()
        status = "✅" if existe else "❌"
        print(f"  {status} {nom:22s} : {existe}")
        if not existe:
            all_exist = False

    # Vérifier le contenu de Data Source
    print("\n" + "=" * 60)
    print("CONTENU DE 'DATA SOURCE':")
    print("-" * 60)

    if CHEMIN_DATA_SOURCE.exists():
        subdirs = sorted([d.name for d in CHEMIN_DATA_SOURCE.iterdir() if d.is_dir()])
        for subdir in subdirs:
            actuel_path = CHEMIN_DATA_SOURCE / subdir / "Actuel"
            if actuel_path.exists():
                json_files = list(actuel_path.glob("*.json"))
                print(f"  📂 {subdir:20s} : {len(json_files)} fichiers JSON")
            else:
                print(f"  📂 {subdir:20s} : ⚠️ Dossier 'Actuel' manquant")
    else:
        print("  ❌ Le dossier 'Data Source' n'existe pas!")
        all_exist = False

    # Résultat final
    print("\n" + "=" * 60)
    if all_exist:
        print("✅ TOUS LES CHEMINS SONT VALIDES!")
        print("✅ L'application peut être lancée en local avec:")
        print("   streamlit run DCB_app_streamlit.py")
    else:
        print("❌ ERREUR: Certains dossiers sont manquants")
        print("⚠️  Vérifiez la structure de votre projet")
    print("=" * 60)

except ImportError as e:
    print(f"\n❌ ERREUR D'IMPORT: {e}")
    print("\n⚠️  Vérifiez que le fichier chemin_dossier.py existe dans:")
    print(f"   {os.path.join(os.path.dirname(__file__), 'TraitementDonnee', 'Code')}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    sys.exit(1)
