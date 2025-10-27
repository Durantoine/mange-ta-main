import pandas as pd
import requests
import streamlit as st
from components.sidebar import render_sidebar
from domain import BASE_URL
from logger import struct_logger

render_sidebar()
st.header("🔌 Données")

data_type = st.selectbox("Choisir le dataset", ["recipes", "interactions"])

if st.button("Charger le dataset"):
    with st.spinner("Chargement..."):
        url = f"{BASE_URL}/mange_ta_main/load-data?data_type={data_type}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            struct_logger.error(e)

        else:
            print(type(data))
            df = pd.DataFrame(data)
            struct_logger.info(df)
            st.dataframe(df.head(100))
