import streamlit as st
import pandas as pd
import tools.utils as tools
import os
from dotenv import load_dotenv
from pathlib import Path

# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent.parent

# Charger les variables d'environnement du fichier .env
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)
DELAI_RELANCE = os.getenv("DELAI_RELANCE", 15)
DELAI_ARCHIVE = os.getenv("DELAI_ARCHIVE", 35)


st.subheader("📦 Mes candidatures archivées")



# affichage des candidatures
data = tools.run_query("SELECT * FROM candidatures WHERE est_archive = 1 ORDER BY date_candidature DESC", fetch=True)

if isinstance(data, list):
    
    
    if len(data) >0:

        df = tools.transform_data_candidature_to_dataframe(data, int(DELAI_RELANCE))
        
        # -- filtres
        search = st.text_input("Filtrer par société ou poste")
        if search:
            df = df[df['societe_nom'].str.contains(search, case=False) | df['titre_poste'].str.contains(search, case=False)]
        

        # -- affichage des candidatures en colonnes
        nb_cols = 2
        for i in range(0, len(df), nb_cols):
            cols = st.columns(nb_cols) # On crée nb_cols colonnes pour cette ligne
            
            # On remplit chaque colonne du groupe actuel
            for j in range(nb_cols):
                if i + j < len(df):
                    with cols[j]:
                        tools.display_candidature(df.iloc[i+j], int(DELAI_ARCHIVE))
    
    else:
        st.info("Aucune donnée disponible.")
    
elif data == -1:
    st.error("Une erreur est survenue lors de la requête SQL.")