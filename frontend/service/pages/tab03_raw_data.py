import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[2]))

from service.app import BASE_URL
from service.logger import struct_logger

st.header("🔌 Raw data")

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
