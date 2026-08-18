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

st.subheader("📋 Résumé")

# Récupération des données pour les calculs des métriques
raw_data = tools.run_query("SELECT resultat FROM candidatures WHERE est_archive = 0", fetch=True)

if isinstance(raw_data, list):
    if len(raw_data) > 0:
        
        df_stats = pd.DataFrame(raw_data, columns=['resultat'])
        total = len(df_stats)
        entretiens = len(df_stats[df_stats['resultat'] == 'Entretien'])
        refus = len(df_stats[df_stats['resultat'] == 'Refus'])
        en_attente = len(df_stats[df_stats['resultat'] == 'En attente'])
        offres = len(df_stats[df_stats['resultat'] == 'Offre'])

        # Affichage des métriques sur une ligne
        col1, col2, col3, col4, col5 = st.columns(5)
        # On considère 'Entretien' ou 'Offre' comme des succès de démarche
        col1.metric("Total Envoyé", total)
        col2.metric("⏳ En attente", en_attente)
        col3.metric("🚀 Entretiens", entretiens, delta=f"{(entretiens/total*100):.1f}%" if total > 0 else "0%")
        col4.metric("✅ Offres", offres, delta=f"{(offres/total*100):.1f}%" if total > 0 else "0%")
        col5.metric("❌ Refus", refus)
        
    else:
        st.info("Aucune donnée disponible.")
elif raw_data == -1:
    st.error("Une erreur est survenue lors de la requête SQL.")


st.divider()


st.subheader("📈 Mes candidatures en cours")



# affichage des candidatures
# data = tools.run_query("SELECT * FROM candidatures WHERE resultat != 'Refus' ORDER BY date_candidature DESC", fetch=True)
data = tools.run_query("SELECT * FROM candidatures WHERE est_archive = 0 ORDER BY date_candidature DESC", fetch=True)

if isinstance(data, list):
    
    
    if len(data) >0:

        df = tools.transform_data_candidature_to_dataframe(data, int(DELAI_RELANCE))


        # -- affichage du message pour les relances
        if df['a_relancer'].sum() >0:
            st.warning(f"⚠️ **Attention :** Tu as **{df['a_relancer'].sum()}** candidature(s) sans réponse depuis plus de **{DELAI_RELANCE} jours**.")
        
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