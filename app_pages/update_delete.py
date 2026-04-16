
import streamlit as st
import tools.utils as tools
from datetime import date
import os
from pathlib import Path
import uuid

# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent.parent
PDF_FOLDER_PATH = ROOT_DIR / "offres_pdf"


st.subheader("🛠️ Suivi, mise à jour et suppression de dossier")

# 1. On récupère la liste pour la sélection
items = tools.run_query("SELECT id, societe_nom, titre_poste, date_candidature FROM candidatures ORDER BY date_candidature DESC", fetch=True)

if isinstance(items, list):
    if len(items) >0:
        # On ajoute une option vide au début pour que rien ne soit sélectionné par défaut
        options = [None] + items

        choice_item = st.selectbox(
            "Sélectionner une candidature",
            options,
            format_func=lambda x: f"{x['date_candidature']} - {x['societe_nom']} - {x['titre_poste']}" if x else "Choisir dans la liste...",
            key="select_suivi" # Ajout d'une clé stable
        )

        if choice_item:

            id_sel = choice_item['id']

            # 2. RÉCUPÉRATION DES DONNÉES ACTUELLES pour pré-remplir les champs
            current_data = tools.run_query("SELECT * FROM candidatures WHERE id=?", (id_sel,), fetch=True)

            if isinstance(current_data, list) and len(current_data) >0:
                
                st.subheader("⚙️ Suivi & Mise à jour du dossier")
                
                # On récupère les colonnes pour mapper facilement (comme un dictionnaire)
                d = current_data[0]


                with st.form("update_date_reponse"):
                    col1, col2 = st.columns(2)
                    with col1:

                        # Gestion de la date de réponse
                        try:
                            d_rep_val = d['date_reponse'] if d['date_reponse'] else date.today()
                        except:
                            d_rep_val = date.today()
                        date_reponse = st.date_input("Date de réponse", d_rep_val, format="DD/MM/YYYY")


                        if st.form_submit_button("💾 Enregistrer la date de retour", type="primary"):
                            tools.run_query("""
                                UPDATE candidatures SET
                                    date_reponse=?
                                WHERE id=?
                                """, (date_reponse, id_sel))
                            st.session_state.message = "Mise à jour effectuée !"
                            st.session_state.message_icon = "✅"
                            st.rerun()

                with st.form("update_form"):
                    col1, col2 = st.columns(2)
                    with col1:

                        # Gestion du résultat
                        res_options = ["En attente", "Entretien", "Refus", "Offre"]
                        current_res = d['resultat']
                        res_index = res_options.index(current_res) if current_res in res_options else 0
                        res = st.selectbox("Résultat", res_options, index=res_index)

                        suite = st.text_input("Suite à donner", value=d['suite_a_donner'] or "")
                        comms = st.text_area("Commentaires", value=d['commentaires'] or "")
                    with col2:
                        contact = st.text_input("Personne à contacter", value=d['societe_contact'] or "")
                        adresse = st.text_input("Adresse postale", value=d['societe_adresse'] or "")
                        mail = st.text_input("Mail", value=d['societe_mail'] or "")
                        tel = st.text_input("Tel", value=d['societe_tel'] or "")

                    if st.form_submit_button("💾 Mettre à jour les informations", type="primary"):
                        tools.run_query("""
                            UPDATE candidatures SET
                                resultat=?, suite_a_donner=?, commentaires=?, societe_contact=?, societe_adresse=?,
                                societe_mail=?, societe_tel=?
                            WHERE id=?
                            """, (res, suite, comms, contact, adresse, mail, tel, id_sel))
                        st.session_state.message = "Mise à jour effectuée !"
                        st.session_state.message_icon = "✅"
                        st.rerun()

                with st.expander("**Mise à jour en profondeur**"):
                    
                    @st.dialog("Confirmation de mise à jour")
                    def confirm_update_dialog(query="", query_params=[], update_pdf=False, pdf_params={}):
                        st.warning(f"Valider les changement pour **{d['societe_nom']} - {d['titre_poste']}** ?")
                        c1, c2 = st.columns(2)
                        if c1.button("Oui, mettre à jour", type="primary", width="stretch"):
                            
                            if update_pdf:
                                with st.spinner("Capture du PDF de l'offre..."):
                                    # si un fichier existe déjà, on le supprime
                                    if pdf_params['old_pdf_path'] and os.path.exists(pdf_params['old_pdf_path']):
                                        os.remove(pdf_params['old_pdf_path'])
                                    safe_name = f"{pdf_params['date_candidature']}_{pdf_params['nom']}_{str(uuid.uuid4())[:8]}".replace(" ", "_")
                                    pdf_file = tools.save_pdf_from_url(lien, safe_name, PDF_FOLDER_PATH)
                                    query_params.insert(-1, pdf_file)
                            
                            tools.run_query(query, query_params)
                            st.session_state.message = "Mise à jour effectuée !"
                            st.session_state.message_icon = "✅"
                            st.rerun()
                        if c2.button("Annuler", width="stretch"):
                            st.rerun()
                    
                    with st.form("update_date_candidature"):
                        col1, col2 = st.columns(2)
                        with col1:
                            try:
                                d_can_val = d['date_candidature']
                            except:
                                d_can_val = date.today()
                            date_candidature = st.date_input("Date de candidature", d_can_val, format="DD/MM/YYYY")

                            if st.form_submit_button("💾 Enregistrer la date de candidature", type="primary"):
                                confirm_update_dialog("""
                                    UPDATE candidatures SET
                                        date_candidature=?
                                    WHERE id=?
                                    """, [date_candidature, id_sel])

                    with st.form("update_other_candidature"):
                        col1, col2 = st.columns(2)
                        with col1:

                            nom = st.text_input("Société", value=d['societe_nom'] or "")
                            titre = st.text_input("Titre du poste", value=d['titre_poste'] or "")
                            # Gestion du Contrat
                            contrat_options = ["CDI", "CDD", "Alternance", "Stage"]
                            contrat_index = contrat_options.index(d['type_contrat']) if d['type_contrat'] in contrat_options else 0
                            contrat = st.selectbox("Contrat", contrat_options, index=contrat_index)
                        with col2:

                            # Gestion du Type de candidature
                            type_c_options = ["Réponse à une offre", "Candidature spontanée"]
                            type_c_index = type_c_options.index(d['type_candidature']) if d['type_candidature'] in type_c_options else 0
                            type_c = st.selectbox("Type de candidature", type_c_options, index=type_c_index)

                            canal = st.text_input("Canal (ex: HelloWork)", value=d['canal'] or "")


                        if st.form_submit_button("💾 Enregistrer les informations", type="primary"):
                            confirm_update_dialog("""
                                UPDATE candidatures SET
                                societe_nom=?, type_candidature=?, titre_poste=?, canal=?, type_contrat=?
                                WHERE id=?
                                """, [nom, type_c, titre, canal, contrat, id_sel])
                    
                    if d["type_candidature"] == "Réponse à une offre":
                        with st.form("update_lien"):
                            lien = st.text_input("Lien de l'offre", value=d['lien_offre'] or "")
                            if st.form_submit_button("💾 Enregistrer la capture", type="primary"):
                                if lien :
                                    
                                    confirm_update_dialog("""
                                        UPDATE candidatures SET
                                        lien_offre=?, pdf_path=?
                                        WHERE id=?
                                        """, [lien, id_sel], update_pdf=True, pdf_params={'old_pdf_path':d['pdf_path'],'date_candidature':date_candidature, 'nom':nom})


                st.divider()
                
                st.subheader("🗑️ Suppression du dossier")
                
                with st.container(border=True):
                    st.write("⚠️ Cette action est irréversible. Le fichier associé sera également effacé du disque, le cas échéant.")
                    
                    if st.button("🗑️ Supprimer cette candidature", type="primary"):
                        # On utilise une variable temporaire en session pour la popup
                        st.session_state.confirm_delete = True

                if st.session_state.get('confirm_delete'):
                    @st.dialog("Confirmation de suppression")
                    def confirm_dialog():
                        st.warning(f"Supprimer définitivement la candidature chez **{d['societe_nom']}** ?")
                        c1, c2 = st.columns(2)
                        if c1.button("Oui, supprimer", type="primary", width="stretch"):
                            try:
                                # suppression du fichier
                                if d['pdf_path'] and os.path.exists(d['pdf_path']):
                                    os.remove(d['pdf_path'])
                                    print(f"✅ Fichier supprimé : {d['pdf_path']}")
                                # suppression dans la base de données
                                tools.run_query("DELETE FROM candidatures WHERE id=?", (id_sel,))
                                st.session_state.message = f"Supression de la candidature chez **{d['societe_nom']}** !"
                                st.session_state.message_icon = "✅"
                            except Exception as e:
                                st.session_state.message = f"Erreur de supression de la candidature chez **{d['societe_nom']}** !"
                                st.session_state.message_icon = "❌"
                                print(f"Erreur lors de la suppression : {e}")
                            st.session_state.confirm_delete = False
                            st.rerun()
                        if c2.button("Annuler", width="stretch"):
                            st.session_state.confirm_delete = False
                            st.rerun()
                    confirm_dialog()

        else:
            st.info("Sélectionnez une candidature ci-dessus pour afficher ses détails.")
    else:
        st.info("Aucune donnée disponible.")
elif items == -1:
    st.error("Une erreur est survenue lors de la requête SQL.")