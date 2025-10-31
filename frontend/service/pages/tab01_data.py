import pandas as pd
import streamlit as st
from logger import struct_logger

try:
    from ..components.sidebar import render_sidebar
    from ..src.http_client import BackendAPIError, fetch_backend_json
except ImportError:  # pragma: no cover - fallback for standalone execution
    from components.sidebar import render_sidebar
    try:  # pragma: no cover - streamlit run context
        from src.http_client import BackendAPIError, fetch_backend_json
    except ImportError:  # pragma: no cover - fallback when src is package under service
        from service.src.http_client import BackendAPIError, fetch_backend_json


def render_data_page() -> None:
    """Render the data exploration page."""

    render_sidebar()
    st.header("🔌 Visualisation et export des donnée")
    st.markdown(
        """
        Cet espace vous permet de sélectionner le dataset de votre choix puis de le charger en un clic.
        Une fois affichées, les données peuvent être :

        - ✅ Visualisées directement dans l’interface pour une exploration rapide  
        - ✅ Téléchargées afin de réaliser vos propres analyses, traitements ou archivages

        Que vous souhaitiez consulter quelques entrées ou travailler en profondeur, cette section offre une expérience simple, flexible et accessible, adaptée à tous les besoins data.
        """
    )

    data_type = st.selectbox("Choisir le dataset", ["recipes", "interactions"])

    if not callable(getattr(st, "button", None)):
        return

    def _render_load_error(exc: Exception) -> None:
        struct_logger.error(
            "dataset_load_failed",
            data_type=data_type,
            error=str(exc),
            endpoint=getattr(exc, "endpoint", None),
        )
        error_fn = getattr(st, "error", None)
        if callable(error_fn):
            details = getattr(exc, "details", str(exc))
            error_fn(f"Impossible de charger le dataset : {details}")

    if st.button("Charger le dataset"):
        with st.spinner("Chargement..."):
            try:
                payload = fetch_backend_json(
                    "load-data",
                    params={"data_type": data_type, "limit": 5_000},
                    ttl=30,
                )
            except BackendAPIError as exc:
                _render_load_error(exc)
                return
            except Exception as exc:  # pragma: no cover - defensive fallback
                _render_load_error(exc)
                return

            struct_logger.info("dataset_loaded", data_type=data_type, rows=len(payload))
            df = pd.DataFrame(payload)
            st.dataframe(df, use_container_width=True)


if __name__ == "__main__":  # pragma: no cover - executed when run via `streamlit run`
    render_data_page()
