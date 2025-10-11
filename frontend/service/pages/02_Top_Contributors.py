import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import requests
sys.path.append(str(Path(__file__).resolve().parents[2]))

from service.logger import struct_logger
from service.app import BASE_URL

st.title("🏆 Top Contributeurs")

# --- Sélection du critère ---
criteria = st.selectbox(
    "Choisis un critère de classement :",
    [
        "Nombre de recettes",
        "Note moyenne des recettes",
        "Nombre de commentaires",
    ],
)


