import streamlit as st
import pandas as pd
import tools.utils as tools
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pathlib import Path

# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent.parent

# Charger les variables d'environnement du fichier .env
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)
DELAI_RELANCE = os.getenv("DELAI_RELANCE", 15)

st.subheader("📋 Résumé")

# Récupération des données pour les calculs des métriques
raw_data = tools.run_query("SELECT resultat FROM candidatures", fetch=True)

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
data = tools.run_query("SELECT * FROM candidatures ORDER BY date_candidature DESC", fetch=True)

if isinstance(data, list):
    
    
    if len(data) >0:

        # Transformation des données en DataFrame pour manipulation facile
        df = pd.DataFrame(data)

        # -- calcul de nouvelles colonnes

        # Conversion de la colonne date (qui est en texte/ISO dans SQLite) en objet datetime
        # errors='coerce' => Si la cellule est vide dans SQLite, Pandas créera un NaT (Not a Time)
        df['date_candidature'] = pd.to_datetime(df['date_candidature'], format="Y-m-d")
        df['date_reponse'] = pd.to_datetime(df['date_reponse'], format="Y-m-d", errors='coerce')

        # Calcul du délai de relance (aujourd'hui - nb jours)
        seuil_relance = datetime.now() - timedelta(days=float(DELAI_RELANCE))
        
        # date de référence à prendre en compte selon s'il y a déjà eu un retour ou non
        df['date_ref'] = df['date_reponse'].fillna(df['date_candidature'])
        
        # calcul des candidatures à relancer
        df['a_relancer'] = ((df['date_ref'] < seuil_relance) & (df['resultat'] == 'En attente')).astype(int)

        # Calcule du nombre de jours d'attente (si 'En attente' => nbjours, sinon 0)
        # Calcul de la différence pour toutes les lignes, puis création de la nouvelle colonne
        diff_jours = (datetime.now() - df['date_candidature']).dt.days
        df['jours_attente'] = diff_jours.where(df['resultat'] == 'En attente', 0)
        ids_alert = df[df['a_relancer'] == 1]['id'].to_list()


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
                        
                        candidature = df.iloc[i+j]
                        
                        # On affiche la fiche dans une "Card" (st.container avec bordure)
                        with st.container(border=True):
                            
                            text_icon, text_color = tools.color_result(candidature['resultat'])
                            
                            if candidature['id'] in ids_alert:
                                text_color = "yellow"
                                text_icon = "⚠️"
                            
                            is_alert = df[(df['id'] == candidature['id']) & (df['a_relancer'] ==1)]['jours_attente']
                            if len(is_alert)>0:
                                text_jours = f":{text_color}[:{text_color}-background[**" + str(is_alert.iloc[0]) + " jour(s)**]]"
                            else:
                                text_jours = ""
                            
                            st.markdown(f":{text_color}[:{text_color}-background[**{text_icon} {candidature['societe_nom']} - {candidature['titre_poste']} - {candidature['type_contrat']}**]]")
                            st.caption(f"""
                                    Candidature envoyée le **{datetime.strftime(candidature['date_candidature'], '%d/%m/%Y')}** en **'{candidature['type_candidature']}'**  
                                    Canal d'envoi : {candidature['canal']}
                                    """)
                            st.write(f"""
                                    **Etat :** {candidature['resultat']} depuis le {datetime.strftime(candidature['date_ref'], '%d/%m/%Y')} {text_jours}  
                                    **Suite à donner :** {candidature['suite_a_donner']}
                                    """)
                            st.write(f"**Commentaires :** {candidature['commentaires']}")
                            
                            # Bouton pour voir le détail complet
                            with st.expander("Détails"):
                                st.markdown(f"""
                                        **Adresse :** {candidature['societe_adresse']}  
                                        **Mail :** {candidature['societe_mail']}  
                                        **Tel :** {candidature['societe_tel']}  
                                        **Personne contact :** {candidature['societe_contact']}  
                                        **Lien original :** [Suivre le lien]({candidature['lien_offre']})
                                        """)
                                
                                pdf_path = candidature['pdf_path']
                                    # On vérifie que le fichier existe avant d'essayer de l'afficher
                                if pdf_path and os.path.exists(pdf_path):
                                    if st.button("Voir le PDF", key=f"btn_pdf_{i+j}"):
                                        tools.display_pdf(pdf_path)
    
    else:
        st.info("Aucune donnée disponible.")
    
elif data == -1:
    st.error("Une erreur est survenue lors de la requête SQL.")