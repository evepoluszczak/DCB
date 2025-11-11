#!/usr/bin/env python3
"""
Analyse tous les fichiers Python dans TraitementDonnee/Code/
et liste ceux qui utilisent encore des chemins en dur
"""

import os
import re
from pathlib import Path

# Chemin vers le dossier Code
code_dir = Path("/home/user/DCB/TraitementDonnee/Code")

# Pattern pour détecter les chemins en dur
pattern_aero = r'//gva\.tld/aig/O/12_EM-DO/.*?["\']'
pattern_maison = r'/Users/bastien/Documents/.*?["\']'

print("=" * 80)
print("ANALYSE DES CHEMINS EN DUR DANS LES MODULES DE TRAITEMENT")
print("=" * 80)
print()

# Dictionnaire pour stocker les résultats
files_with_hardcoded_paths = {}

# Parcourir tous les fichiers .py
for py_file in sorted(code_dir.glob("*.py")):
    if py_file.name == "chemin_dossier.py":
        continue  # On skip ce fichier car c'est normal qu'il ait des chemins commentés

    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # Chercher les chemins en dur
    hardcoded_lines = []

    for i, line in enumerate(lines, 1):
        # Ignorer les lignes commentées
        if line.strip().startswith('#'):
            continue

        # Chercher les patterns
        if re.search(pattern_aero, line) or re.search(pattern_maison, line):
            hardcoded_lines.append((i, line.strip()))

    if hardcoded_lines:
        files_with_hardcoded_paths[py_file.name] = hardcoded_lines

# Afficher les résultats
if files_with_hardcoded_paths:
    print(f"❌ {len(files_with_hardcoded_paths)} fichiers utilisent des chemins en dur:\n")

    for filename, lines in files_with_hardcoded_paths.items():
        print(f"📄 {filename}")
        print(f"   {len(lines)} occurrence(s):")
        for line_num, line_content in lines:
            # Tronquer si trop long
            if len(line_content) > 100:
                line_content = line_content[:97] + "..."
            print(f"      Ligne {line_num:3d} : {line_content}")
        print()
else:
    print("✅ Aucun fichier n'utilise de chemins en dur!")

print("=" * 80)
print("RECOMMANDATIONS")
print("=" * 80)
print("""
Pour migrer vers le système de chemins dynamiques (chemin_dossier.py),
chaque module devrait :

1. Importer les chemins nécessaires :
   from chemin_dossier import CHEMIN_INPUT, CHEMIN_OUTPUT, CHEMIN_DATA_SOURCE, etc.

2. Remplacer les chemins en dur par les variables correspondantes :
   - "//gva.tld/.../DCB_Standalone_App/TraitementDonnee/Data/Input"
     → str(CHEMIN_INPUT)

   - "//gva.tld/.../DCB_Standalone_App/TraitementDonnee/Data/Output"
     → str(CHEMIN_OUTPUT)

   - "//gva.tld/.../DCB_Standalone_App/Data Source"
     → str(CHEMIN_DATA_SOURCE)

3. Utiliser pathlib.Path pour construire les chemins :
   fichier = CHEMIN_INPUT / "Autre" / "mon_fichier.csv"

   Au lieu de :
   fichier = dossier + "/" + "mon_fichier.csv"

Avantages :
- ✅ Portable (fonctionne depuis n'importe quel emplacement)
- ✅ Compatible multi-OS (Windows, Linux, macOS)
- ✅ Centralisé (un seul endroit pour gérer les chemins)
- ✅ Sûr (pathlib gère automatiquement les séparateurs)
""")
print("=" * 80)

# Créer un fichier de rapport
rapport_path = Path("/home/user/DCB/rapport_chemins_en_dur.txt")
with open(rapport_path, 'w', encoding='utf-8') as f:
    f.write("RAPPORT D'ANALYSE DES CHEMINS EN DUR\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Nombre de fichiers avec chemins en dur : {len(files_with_hardcoded_paths)}\n\n")

    for filename, lines in files_with_hardcoded_paths.items():
        f.write(f"Fichier : {filename}\n")
        f.write(f"Occurrences : {len(lines)}\n")
        for line_num, line_content in lines:
            f.write(f"  Ligne {line_num} : {line_content}\n")
        f.write("\n")

print(f"\n📄 Rapport détaillé sauvegardé dans : {rapport_path}")
