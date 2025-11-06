"""
Version minimale de test pour identifier le problème de chargement
"""

import streamlit as st

st.set_page_config(
    page_title="Test DCB",
    page_icon="✈️",
    layout="wide"
)

st.title("Test - Application DCB")
st.success("✅ L'application se charge correctement!")

st.write("Si vous voyez ce message, l'application Streamlit fonctionne.")
st.write("Le problème vient donc du code dans DCB_app_streamlit.py")
