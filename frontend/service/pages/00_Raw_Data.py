import requests
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from service.logger import struct_logger

st.header("🔌 Raw data")
BASE_URL = "http://mange_ta_main:8000/mange_ta_main"

data_type = st.selectbox("Choisir le dataset", ["recipes", "interations"])

if st.button("Charger le dataset"):
    with st.spinner("Chargement..."):
        url = f"{BASE_URL}/raw-data?data_type={data_type}"
        try:
            response = requests.get(url)
            response.raise_for_status()  
            data = response.json()   
        except requests.exceptions.RequestException as e:
            struct_logger.error(e)
            
        if isinstance(data, str) and "Erreur" in data:
            st.error(data)
        else:
            print(type(data))
            df = pd.DataFrame(data)
            st.write(f"Dataset: {data_type}")
            struct_logger.info(df)
            st.dataframe(df.head(100)) 