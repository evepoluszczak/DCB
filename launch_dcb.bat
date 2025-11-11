@echo off
REM ==============================================
REM Script de lancement DCB App
REM Version Windows
REM ==============================================

title DCB Tool - Lancement

echo ================================================
echo    DCB Tool - Lancement de l'application
echo    Demand Capacity Balancing
echo    Geneva Airport
echo ================================================
echo.

REM Vérifier Python
echo [INFO] Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python trouve

REM Vérifier si on est dans le bon dossier
if not exist "DCB_app_streamlit.py" (
    echo [ERREUR] Le fichier DCB_app_streamlit.py n'a pas ete trouve
    echo Assurez-vous d'executer ce script depuis le dossier racine du projet
    pause
    exit /b 1
)

REM Vérifier Streamlit
echo [INFO] Verification de Streamlit...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] Streamlit n'est pas installe
    echo [INFO] Installation des dependances...

    if exist "requirements.txt" (
        python -m pip install -r requirements.txt
        if %errorlevel% equ 0 (
            echo [OK] Dependances installees avec succes
        ) else (
            echo [ERREUR] Echec de l'installation des dependances
            pause
            exit /b 1
        )
    ) else (
        echo [ERREUR] Fichier requirements.txt introuvable
        pause
        exit /b 1
    )
) else (
    echo [OK] Streamlit est deja installe
)

REM Vérifier les données
echo [INFO] Verification des donnees...
if exist "Data Source\" (
    echo [OK] Dossier de donnees trouve
) else if exist "DataSource\" (
    echo [OK] Dossier de donnees trouve
) else (
    echo [ATTENTION] Dossier 'Data Source' non trouve
    echo L'application va demarrer, mais vous devrez uploader des donnees
    echo via l'interface d'administration
)

echo.
echo [OK] Tous les prerequis sont satisfaits
echo.
echo [INFO] Lancement de l'application DCB...
echo.
echo ================================================
echo   L'application va s'ouvrir dans votre navigateur
echo   URL par defaut : http://localhost:8501
echo ================================================
echo.
echo Pour arreter l'application, appuyez sur Ctrl+C
echo.

REM Lancer Streamlit
streamlit run DCB_app_streamlit.py --server.headless=true

REM Si Streamlit se termine
echo.
echo [INFO] Application fermee
pause
