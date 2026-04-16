import streamlit as st
from datetime import date
import uuid
import tools.utils as tools
from pathlib import Path


# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent.parent
PDF_FOLDER_PATH = ROOT_DIR / "offres_pdf"


st.subheader("➕ Nouvelle Candidature")
with st.form("form_add"):
    col1, col2 = st.columns(2)
    with col1:
        d_cand = st.date_input("Date candidature", date.today(), format="DD/MM/YYYY")
        nom = st.text_input("Société")
        adresse = st.text_input("Adresse")
        contact = st.text_input("Personne à contacter")
        mail = st.text_input("Email contact")
    with col2:
        titre = st.text_input("Titre du poste")
        contrat = st.selectbox("Contrat", ["CDI", "CDD", "Alternance", "Stage", "Interim"])
        type_c = st.selectbox("Type", ["Réponse à une offre", "Candidature spontanée"])
        canal = st.text_input("Canal (ex: HelloWork, Mail...)")
        lien = st.text_input("Lien de l'offre")

    comm = st.text_area("Commentaires")
    submit = st.form_submit_button("💾 Enregistrer", type="primary")

if submit:
    pdf_file = None
    if lien:
        with st.spinner("Capture du PDF de l'offre..."):
            safe_name = f"{d_cand}_{nom}_{str(uuid.uuid4())[:8]}".replace(" ", "_")
            pdf_file = tools.save_pdf_from_url(lien, safe_name, PDF_FOLDER_PATH)

    query = '''
            INSERT INTO candidatures (date_candidature, societe_nom, societe_adresse, type_candidature,
            titre_poste, canal, type_contrat, lien_offre, pdf_path, societe_mail, commentaires, resultat, societe_contact)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            '''
    result = tools.run_query(query, (d_cand, nom, adresse, type_c, titre, canal, contrat, lien, pdf_file, mail, comm, 'En attente',contact))
    
    if result != -1:
        st.session_state.message = "Candidature ajoutée !"
        st.session_state.message_icon = "✅"
        st.rerun()
    else:
        st.session_state.message = "Une erreur s'est produite"
        st.session_state.message_icon = "❌"