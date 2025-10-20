from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def get_data_dir() -> Path:
    """
    Détermine le répertoire racine des données.
    Priorité:
    1) Variable d'env DATA_DIR
    2) Dossier EDA/Data à la racine du repo (défaut utile)
    3) Dossier local streamlit_app/data (fallback)
    """
    # 1) ENV
    env = os.getenv("DATA_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_dir():
            return p

    # 2) EDA/Data (repo root/EDA/Data)
    # __file__ = .../frontend/service/streamlit_app/src/io_loader.py
    repo_root = Path(__file__).resolve().parents[4]  # remonte jusqu'à la racine du repo
    eda_data = repo_root / "EDA" / "Data"
    if eda_data.is_dir():
        return eda_data

    # 3) fallback local
    local = Path(__file__).resolve().parents[2] / "data"
    return local


@st.cache_data(show_spinner=False)
def load_interactions() -> pd.DataFrame:
    data_dir = get_data_dir()
    path = data_dir / "RAW_interactions.csv"
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_recipes() -> pd.DataFrame:
    data_dir = get_data_dir()
    path = data_dir / "RAW_recipes.csv"
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    return pd.read_csv(path)
