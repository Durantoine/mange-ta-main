import streamlit as st
import requests


st.title("Mange ta main ma gueule")


BASE_URL = "http://mange_ta_main:8000/mange_ta_main/"

st.image("images/mouette.jpg", caption="")

def appeler_api():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status() 
        return response.text.strip()  
    except requests.exceptions.RequestException as e:
        return f"Erreur : {str(e)}"

if st.button("Comment tu t'appelles ?"):
    with st.spinner("Chargement..."):
        reponse = appeler_api()
        if "Erreur" in reponse:
            st.error(reponse)
        else:
            st.write(f"{reponse}")