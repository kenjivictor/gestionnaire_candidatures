import streamlit as st
import sqlite3
import pandas as pd
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from streamlit_option_menu import option_menu
import tools.utils as tools
import tools.streamlit_widgets as st_widgets
from pathlib import Path
from dotenv import load_dotenv
import uuid
import base64

# --- CONFIGURATION DES VARIABLES ---

# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent

# Charger les variables d'environnement du fichier .env
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)
DB_FILE_NAME = os.getenv("DB_FILE_NAME", "default.db")
DELAI_RELANCE = os.getenv("DELAI_RELANCE", 15)
DELAI_ARCHIVE = os.getenv("DELAI_ARCHIVE", 40)

# charger les données initiales (pour les formulaires)
ETAT_ADMINISTRATIF = {"Active" : "A", "Cessée": "C"}
NAF_CODES = tools.get_codes_naf()
TRANCHES_EFFECTIF = tools.get_tranches_effectif()
DEPARTEMENTS = tools.get_departements()
CODES_POSTAUX = tools.get_codes_postaux()

# autres variables
PDF_FOLDER_PATH = ROOT_DIR / "offres_pdf"

# --- Adaptateur SQLite pour les dates (Python 3.12+) ---
def adapt_date(val):
    return val.isoformat()
def convert_date(val):
    return date.fromisoformat(val.decode())
sqlite3.register_adapter(date, lambda x: x.isoformat())
sqlite3.register_converter("DATE", lambda x: date.fromisoformat(x.decode()))

# fonction qui sauvegarde une page web
def save_pdf_from_url(url, filename):
    """Lance shot.py en tant que processus indépendant pour éviter les conflits asyncio."""
    if not url: return None
    
    
    output_path = os.path.abspath(os.path.join(PDF_FOLDER_PATH, f"{filename}.pdf"))

    try:
        # On appelle shot.py avec l'URL et le chemin de sortie
        # On utilise sys.executable pour être sûr d'utiliser le bon environnement Python
        result = subprocess.run(
            [sys.executable, "tools/shot.py", url, output_path],
            capture_output=True,
            text=True
        )

        if "Success" in result.stdout:
            return output_path
        else:
            st.warning(f"Erreur lors de la capture : {result.stdout} {result.stderr}")
            return None
    except Exception as e:
        st.warning(f"Impossible de générer le PDF (mais la candidature est enregistrée) : {e}")
        return None

# fonction qui exécute une requete SQL et si c'est un SELECT, retourne le résultat sous forme de liste de dictionnaires
def run_query(query, params=(), fetch=False):
    try:
        # chemin absolu du fichier de base de données
        db_path = ROOT_DIR / "db" / DB_FILE_NAME
        
        # Ajout de detect_types pour que SQLite reconnaisse nos dates
        with sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row # Cette ligne permet d'accéder aux colonnes par leur nom (ex: row['societe_nom'])
            cursor = conn.cursor()

            # Conversion explicite des dates en string pour éviter le warning si l'adaptateur échoue
            clean_params = tuple(p.isoformat() if isinstance(p, date) else p for p in params)

            cursor.execute(query, clean_params)
            conn.commit()
            if fetch:
                # On convertit les sqlite3.Row en dict standard
                return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erreur SQLite: {e}")
        return -1
    return None

# fonction qui donne une couleur en fonction du statut de la candidature
def color_result(val):
    if val == 'Refus': return 'background-color: #ffcccc' # Rouge clair
    if val == 'Entretien': return 'background-color: #ccffcc' # Vert clair
    if val == 'Offre': return 'background-color: #ffff99' # Jaune/Or
    return ''


# fonction qui affiche un fichier PDF dans une fenetre modale
@st.dialog("Visualisation du document", width="large")
def display_pdf(file_path):
    
    # teste l'existance du fichier
    if not os.path.exists(file_path):
        st.error("Le fichier est introuvable sur le disque.")
        return
    
    # Lecture du fichier et encodage en base64
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Création de l'objet HTML (Iframe)
    pdf_display = f'''
            <div style="height: 80vh; width: 100%; overflow: hidden;">
                <iframe 
                    src="data:application/pdf;base64,{base64_pdf}#view=FitH" 
                    width="100%" 
                    height="100%" 
                    type="application/pdf"
                    style="border:none;"
                ></iframe>
            </div>
                '''
    
    # Affichage dans Streamlit
    st.markdown(pdf_display, unsafe_allow_html=True)


# --- INTERFACE STREAMLIT ---


st.set_page_config(page_title="Job Tracker", page_icon="🎯", layout="wide")
st.title("🎯 Gestionnaire de Candidatures")

# On vérifie si un message doit être affiché (en mode toast)
if st.session_state.get('message'):
    st.toast(st.session_state.get('message'), icon=st.session_state.get('message_icon'))
    # On vide les variables pour que le message ne revienne pas au prochain clic
    del st.session_state.message
    del st.session_state.message_icon


with st.sidebar:
    menu_selected = option_menu(
        menu_title="Navigation",  # Titre du menu
        options=["Liste", "Ajouter", "Modifier/Supprimer", "Recherche d'entreprise"],  # Options
        icons=["list-task", "plus-circle", "gear", "search"],  # Icônes (Bootstrap icons)
        menu_icon="speedometer2",  # Icône du titre
        default_index=0,  # Sélection par défaut
        styles={
            #"container": {"padding": "5!important", "background-color": "#fafafa"},
            #"icon": {"color": "orange", "font-size": "20px"},
            #"nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link": {"--hover-color": "#1A1C2455"},
            #"nav-link-selected": {"background-color": "#02ab21"},
        }
    )
    st.divider()
    st.info("Conseil : Capturez l'offre dès l'ajout pour garder une trace du descriptif.")

if menu_selected == "Ajouter":
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
                pdf_file = save_pdf_from_url(lien, safe_name)

        query = '''
                INSERT INTO candidatures (date_candidature, societe_nom, societe_adresse, type_candidature,
                titre_poste, canal, type_contrat, lien_offre, pdf_path, societe_mail, commentaires, resultat, societe_contact)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                '''
        result = run_query(query, (d_cand, nom, adresse, type_c, titre, canal, contrat, lien, pdf_file, mail, comm, 'En attente',contact))
        
        if result != -1:
            st.session_state.message = "Candidature ajoutée !"
            st.session_state.message_icon = "✅"
            st.rerun()
        else:
            st.session_state.message = "Une erreur s'est produite"
            st.session_state.message_icon = "❌"

elif menu_selected == "Liste":
    st.subheader("📋 Résumé")

    # Récupération des données pour les calculs des métriques
    raw_data = run_query("SELECT resultat FROM candidatures", fetch=True)

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
    data = run_query("SELECT * FROM candidatures WHERE resultat != 'Refus' ORDER BY date_candidature DESC", fetch=True)
    
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
            df['a_relancer'] = (df['date_ref'] < seuil_relance).astype(int)

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
                                
                                if candidature['id'] in ids_alert:
                                    text_color = ":yellow"
                                    text_color_back = ":yellow-background"
                                    text_icon = "⚠️"
                                else :
                                    text_color = ":blue"
                                    text_color_back = ":blue-background"
                                    text_icon = "ℹ️"
                                
                                is_alert = df[(df['id'] == candidature['id']) & (df['a_relancer'] ==1)]['jours_attente']
                                if len(is_alert)>0:
                                    text_jours = f"{text_color}[{text_color_back}[**" + str(is_alert.iloc[0]) + " jour(s)**]]"
                                else:
                                    text_jours = ""
                                
                                st.markdown(f"{text_color}[{text_color_back}[**{text_icon} {candidature['societe_nom']} - {candidature['titre_poste']} - {candidature['type_contrat']}**]]")
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
                                    st.write(f"""
                                            **Adresse :** {candidature['societe_adresse']}  
                                            **Mail :** {candidature['societe_mail']}  
                                            **Tel :** {candidature['societe_tel']}  
                                            **Personne contact :** {candidature['societe_contact']}  
                                            **Lien original :** {candidature['lien_offre']}
                                            """)
                                    
                                    pdf_path = candidature['pdf_path']
                                        # On vérifie que le fichier existe avant d'essayer de l'afficher
                                    if pdf_path and os.path.exists(pdf_path):
                                        if st.button("Voir le PDF", key=f"btn_pdf_{i+j}"):
                                            display_pdf(pdf_path)
        
        else:
            st.info("Aucune donnée disponible.")
        
    elif data == -1:
        st.error("Une erreur est survenue lors de la requête SQL.")


elif menu_selected == "Modifier/Supprimer":
    
    st.subheader("🛠️ Suivi, mise à jour et suppression de dossier")

    # 1. On récupère la liste pour la sélection
    items = run_query("SELECT id, societe_nom, titre_poste, date_candidature FROM candidatures ORDER BY date_candidature DESC", fetch=True)

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
                current_data = run_query("SELECT * FROM candidatures WHERE id=?", (id_sel,), fetch=True)

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
                                run_query("""
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
                            run_query("""
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
                        def confirm_update_dialog(query, params):
                            st.warning(f"Valider les changement pour **{d['societe_nom']} - {d['titre_poste']}** ?")
                            c1, c2 = st.columns(2)
                            if c1.button("Oui, mettre à jour", type="primary", width="stretch"):
                                run_query(query, params)
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
                                        """, (date_candidature, id_sel))

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
                                #lien = st.text_input("Lien de l'offre")


                            if st.form_submit_button("💾 Enregistrer les informations", type="primary"):
                                confirm_update_dialog("""
                                    UPDATE candidatures SET
                                    societe_nom=?, type_candidature=?, titre_poste=?, canal=?, type_contrat=?
                                    WHERE id=?
                                    """, (nom, type_c, titre, canal, contrat, id_sel))


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
                                    run_query("DELETE FROM candidatures WHERE id=?", (id_sel,))
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


elif menu_selected == "Recherche d'entreprise":
    st.subheader("🔎 Recherche d'entreprises")
    
    # --- INITIALISATION DU STATE ---
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "search_params" not in st.session_state:
        st.session_state.search_params = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # 1. Création du formulaire
    with st.form("search_entreprise_form"):

        # Définition des 4 champs de sélection multiple
        # Tu peux remplacer les listes ['Option A', ...] par tes propres sources de données
        champ_1 = st.radio("Etat administratif", options=ETAT_ADMINISTRATIF)
        champ_2 = st.multiselect("Activité principale", options=NAF_CODES, help="Vous pouvez éslectionnez plusieurs éléments")
        champ_3 = st.multiselect("Effectifs salariés", options=TRANCHES_EFFECTIF, help="Vous pouvez éslectionnez plusieurs éléments")
        champ_4 = st.multiselect("Départements", options=DEPARTEMENTS, help="Vous pouvez éslectionnez plusieurs éléments")
        champ_5 = st.multiselect("Codes Postaux", options=CODES_POSTAUX, help="Vous pouvez éslectionnez plusieurs éléments")

        # Bouton de soumission du formulaire
        submitted = st.form_submit_button("Lancer la recherche", type="primary")

    

    # 3. Logique de traitement après clic sur le bouton
    if submitted:
        st.divider()
        st.subheader("Résultats")

        # Récupération des données
        data = {
            "etat_administratif": ETAT_ADMINISTRATIF.get(champ_1),
            "activite_principale": tools.format_field([champ_2], NAF_CODES),
            "tranche_effectif_salarie": tools.format_field([champ_3], TRANCHES_EFFECTIF),
            "departement": ','.join([str(DEPARTEMENTS.get(val)) for val in champ_4]),
            "code_postal": ','.join([str(CODES_POSTAUX.get(val)) for val in champ_5])
        }

        # Vérification si des données ont été saisies
        if any(data.values()):
            
            st.session_state.search_params = data
            st.session_state.current_page = 1 # Reset à la page 1
            with st.spinner("Recherche en cours..."):
                st.session_state.search_results = tools.fetch_entreprises(data, page=1)

        else:
            st.warning("Veuillez remplir au moins un critère.")
        
    # 3. AFFICHAGE DES RÉSULTATS (Persistant grâce au session_state)
    if st.session_state.search_results:
        res = st.session_state.search_results
        results_list = res['results']
        
        st.divider()
        st.info(f"📍 {res['total_results']} entreprises trouvées (Page {st.session_state.current_page} sur {res['total_pages']})")

        # Affichage des fiches entreprises
                
        # On parcourt la liste par groupes de 4
        for i in range(0, len(results_list), 4):
            cols = st.columns(4) # On crée 4 colonnes pour cette ligne
            
            # On remplit chaque colonne du groupe actuel
            for j in range(4):
                if i + j < len(results_list):
                    with cols[j]:
                        # On affiche la fiche dans une "Card" (st.container avec bordure)
                        with st.container(border=True):
                            # On réduit un peu la taille du texte pour que ça rentre bien en colonnes
                            st.markdown(f"**{results_list[i+j]['Nom']}**")
                            st.write(f"📍 {results_list[i+j]['Adresse']}")
                            st.caption(f"SIREN: {results_list[i+j]['SIREN']} / NAF: {results_list[i+j]['NAF']}")
                            
                            # Bouton optionnel pour voir le détail complet
                            #if st.button("Détails", key=f"btn_{results_list[i+j]['SIREN']}"):
                            with st.expander("Détails"):
                                st.info(tools.get_entreprise_details(results_list[i+j]))

        # --- PAGINATION USER-FRIENDLY ---
        if res["total_pages"] > 1:
            st_widgets.afficher_pagination(res["total_pages"])