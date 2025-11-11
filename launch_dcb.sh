#!/bin/bash

# ==============================================
# Script de lancement DCB App
# Version Linux/Mac
# ==============================================

echo "╔═══════════════════════════════════════════╗"
echo "║    DCB Tool - Lancement de l'application  ║"
echo "║    Demand Capacity Balancing              ║"
echo "║    Geneva Airport                         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_step() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

# Vérifier Python
print_step "Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé ou n'est pas dans le PATH"
    echo "Veuillez installer Python 3 depuis https://www.python.org/"
    exit 1
fi
print_success "Python 3 trouvé : $(python3 --version)"

# Vérifier si on est dans le bon dossier
if [ ! -f "DCB_app_streamlit.py" ]; then
    print_error "Le fichier DCB_app_streamlit.py n'a pas été trouvé"
    print_warning "Assurez-vous d'exécuter ce script depuis le dossier racine du projet"
    exit 1
fi

# Vérifier si Streamlit est installé
print_step "Vérification de Streamlit..."
if ! python3 -c "import streamlit" &> /dev/null; then
    print_warning "Streamlit n'est pas installé"
    print_step "Installation des dépendances..."

    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_success "Dépendances installées avec succès"
        else
            print_error "Échec de l'installation des dépendances"
            exit 1
        fi
    else
        print_error "Fichier requirements.txt introuvable"
        exit 1
    fi
else
    print_success "Streamlit est déjà installé"
fi

# Vérifier le dossier de données
print_step "Vérification des données..."
if [ -d "Data Source" ] || [ -d "DataSource" ]; then
    print_success "Dossier de données trouvé"
else
    print_warning "Dossier 'Data Source' non trouvé"
    echo "L'application va démarrer, mais vous devrez uploader des données via l'interface d'administration"
fi

echo ""
print_success "✓ Tous les prérequis sont satisfaits"
echo ""
print_step "Lancement de l'application DCB..."
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  L'application va s'ouvrir dans votre navigateur${NC}"
echo -e "${GREEN}  URL par défaut : http://localhost:8501${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Pour arrêter l'application, appuyez sur Ctrl+C"
echo ""

# Lancer Streamlit
streamlit run DCB_app_streamlit.py --server.headless=true

# Si Streamlit se termine
print_step "Application fermée"
