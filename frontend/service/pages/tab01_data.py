from pathlib import Path

import pandas as pd
import requests
import streamlit as st

try:
    from ..app import BASE_URL
    from ..logger import struct_logger
    from ..components.sidebar import render_sidebar
except ImportError:  # pragma: no cover
    import sys

    ROOT_PATH = Path(__file__).resolve().parents[2]
    if str(ROOT_PATH) not in sys.path:
        sys.path.append(str(ROOT_PATH))

    COMPONENTS_DIR = Path(__file__).resolve().parents[1] / "components"
    if str(COMPONENTS_DIR) not in sys.path:
        sys.path.append(str(COMPONENTS_DIR))

    from app import BASE_URL  # type: ignore
    from logger import struct_logger  # type: ignore
    from sidebar import render_sidebar  # type: ignore

render_sidebar()
st.header("🔌 Données")

data_type = st.selectbox("Choisir le dataset", ["recipes", "interactions"])

if st.button("Charger le dataset"):
    with st.spinner("Chargement..."):
        url = f"{BASE_URL}/load-data?data_type={data_type}"
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
