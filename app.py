import streamlit as st
import sqlite3
from datetime import date


st.set_page_config(page_title="Gestionnaire de Candidatures", page_icon="🎯", layout="wide")


# --- Adaptateur SQLite pour les dates (Python 3.12+) ---
def adapt_date(val):
    return val.isoformat()
def convert_date(val):
    return date.fromisoformat(val.decode())
sqlite3.register_adapter(date, lambda x: x.isoformat())
sqlite3.register_converter("DATE", lambda x: date.fromisoformat(x.decode()))



# --- INTERFACE STREAMLIT ---

st.title("🎯 Gestionnaire de Candidatures")

# On vérifie si un message doit être affiché (en mode toast)
if st.session_state.get('message'):
    st.toast(st.session_state.get('message'), icon=st.session_state.get('message_icon'))
    # On vide les variables pour que le message ne revienne pas au prochain clic
    del st.session_state.message
    del st.session_state.message_icon



pages = {
    "Candidatures": [
        st.Page("app_pages/list.py", title="Liste", icon="📋"),
        st.Page("app_pages/add.py", title="Ajouter", icon="➕"),
        st.Page("app_pages/update_delete.py", title="Modifier/Supprimer", icon="⚙️"),
        st.Page("app_pages/archive.py", title="Archives", icon="📦"),
        st.Page("app_pages/search_enterprises.py", title="Recherche d'entreprise", icon="🔎"),
    ],
}

page = st.navigation(pages)
page.run()