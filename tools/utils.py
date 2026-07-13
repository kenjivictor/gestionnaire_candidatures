import pandas as pd
import requests
import os
import subprocess
import sys
import streamlit as st
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import base64

# Paramètres de recherche
BASE_API_URL = "https://recherche-entreprises.api.gouv.fr/search"
# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent.parent

# Charger les variables d'environnement du fichier .env
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)
DB_FILE_NAME = os.getenv("DB_FILE_NAME", "default.db")



def get_codes_naf():
    all_results = {}

    try:
        df = pd.read_csv('data/naf_clean_niv2.csv', sep=';')
        df['NAFs'] = df['NAFs'].apply(lambda x: eval(x))
        # Libellé devient l'index, on sélectionne les codes, puis conversion en dictionnaire
        all_results = df.set_index('Libellé')['NAFs'].to_dict()
    except:
        print('Erreur de récupération des Codes NAF')

    return all_results

def get_tranches_effectif():
    all_results = {}

    try:
        df = pd.read_csv('data/effectifs.csv', sep=';')
        df['Codes'] = df['Codes'].apply(lambda x: eval(x))
        # Libellé devient l'index, on sélectionne les codes, puis conversion en dictionnaire
        all_results = df.set_index('Libellé')['Codes'].to_dict()
    except:
        print('Erreur de récupération des Effectifs')

    return all_results



def get_departements():
    all_results = {}

    try:
        df = pd.read_csv('data/codes_departement.csv', sep=';')
        # Libellé devient l'index, on sélectionne les codes, puis conversion en dictionnaire
        all_results = df.set_index('Nom_Departement')['Code_Departement'].to_dict()
    except:
        print('Erreur de récupération des Départements')

    return all_results

def get_codes_postaux():
    all_results = {}

    try:
        df = pd.read_csv('data/codes_postaux.csv', sep=';', dtype='str')
        # Libellé devient l'index, on sélectionne les codes, puis conversion en dictionnaire
        all_results = df.set_index('Commune')['Code_postal'].to_dict()
    except:
        print('Erreur de récupération des Codes Postaux')

    return all_results


def get_formes_juridique():
    all_results = {}

    try:
        df = pd.read_csv('data/formes_juridiques.csv', sep=';')
        # Libellé devient l'index, on sélectionne les codes, puis conversion en dictionnaire
        all_results = df.set_index('Code')['Libellé'].to_dict()
    except:
        print('Erreur de récupération des formes juridiques')

    return all_results



#TRANCHES_EFFECTIF = get_tranches_effectif()
#FORMES_JURIDIQUES = get_formes_juridique()




# permet de trouver la clef correspondante à un élément dans un dictionnaire
# exemple : trouver la tranche d'effectif dans le dictionnaire retourné par get_tranches_effectif()
def find_element_key_dico(element, dico):
    resultat = None
    for clef, codes in dico.items():
        if element in codes:
            resultat = clef
            break
    return resultat


def format_field(listes, dico):
    # On récupère la valeur, on ignore si None, et on convertit en str
    items = []
    for liste in listes:
        for item in liste:
            items += eval(str(dico.get(item)))
    return ",".join(items)

# fonction qui recherche les entreprises dans l'API en fonction des paramètres fournis
def fetch_entreprises(data: dict, page:int =1)-> dict: 
    retour = {
        'results': [],
        'total_results' :0,
        'total_pages' :0
    }
    all_results = []

    # Filtre le dictionnaire pour ne garder que les clés dont la valeur n'est pas ""
    params = {k: v for k, v in data.items() if v != ""}

    print(f"Début de la recherche...")
    params['per_page'] = 24
    params['page'] = page

    try:
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
                }
        response = requests.get(BASE_API_URL, params=params, timeout=10, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        

        for item in results:
            
            
            all_results.append({
                "SIREN": item.get("siren"),
                "Nom": item.get("nom_complet"),
                "Adresse": item.get("siege").get("adresse"),
                "NAF": item.get("activite_principale"),
                "Tranche Effectif": find_element_key_dico(item.get("tranche_effectif_salarie"), get_tranches_effectif()),
                "Coordonnées GPS": item.get("siege").get("coordonnees"),
                "Nature juridique": get_formes_juridique().get(int(item.get("nature_juridique")[0])),
                "Date de création" : item.get("siege").get("date_creation"),
                "Date de fermeture" : item.get("siege").get("date_fermeture"),
                "Catégorie d'entreprise" : item.get("categorie_entreprise"),
                "Convention(s) collective(s)": item.get("complements").get("liste_idcc"),
            })
        
        retour['results'] = all_results
        retour['total_results'] = data.get("total_results")
        retour['total_pages'] = data.get("total_pages")
    except Exception as e:
        print(f"Erreur lors de la requête : {e}")

    return retour





# fonction qui affiche les détails d'une entreprise (vue concernée : recherche d'netreprises)
def get_entreprise_details(dico):
    
    
    retour = f"""
        **Tranche Effectif :** {dico['Tranche Effectif']}  
        **Catégorie d'entreprise :** {dico['Catégorie d\'entreprise']}  
        **Nature juridique:** {dico['Nature juridique']}  
        **Date de création :** {dico['Date de création']}  
        """
    
    if dico['Date de fermeture'] is not None:
        retour += f"**Date de fermeture :** {dico['Date de fermeture']}  "
    #    **Coordonnées GPS :** {dico['Coordonnées GPS']}  
    
    
    url = "https://code.travail.gouv.fr/convention-collective/"
    conventions = dico['Convention(s) collective(s)']
    liens_conv = []
    if conventions is not None:
        for c in conventions:
            liens_conv.append(f"[{c}]({url + c})")
    
        retour += f"**Convention(s) collective(s) :** {" - ".join(liens_conv)}  "
        
    return retour

# fonction qui réalise toutes les transformation nécessaires sur le résultat obtenu de la requete SQL sur les candidatures
# et retourne le résultat sous forme de dataframe pandas
def transform_data_candidature_to_dataframe(data, delai_relance):
    # Transformation des données en DataFrame pour manipulation facile
    df = pd.DataFrame(data)

    # -- calcul de nouvelles colonnes

    # Conversion de la colonne date (qui est en texte/ISO dans SQLite) en objet datetime
    # errors='coerce' => Si la cellule est vide dans SQLite, Pandas créera un NaT (Not a Time)
    df['date_candidature'] = pd.to_datetime(df['date_candidature'], format="Y-m-d")
    df['date_reponse'] = pd.to_datetime(df['date_reponse'], format="Y-m-d", errors='coerce')

    # Calcul du délai de relance (aujourd'hui - nb jours)
    seuil_relance = datetime.now() - timedelta(days=delai_relance)
    
    # date de référence à prendre en compte selon s'il y a déjà eu un retour ou non
    df['date_ref'] = df['date_reponse'].fillna(df['date_candidature'])
    
    # calcul des candidatures à relancer
    df['a_relancer'] = ((df['date_ref'] < seuil_relance) & (df['resultat'] == 'En attente') & (df['est_archive'] == 0)).astype(int)

    # Calcule du nombre de jours d'attente (si 'En attente' => nbjours, sinon 0)
    # Calcul de la différence pour toutes les lignes, puis création de la nouvelle colonne
    diff_jours = (datetime.now() - df['date_candidature']).dt.days
    df['jours_attente'] = diff_jours.where((df['resultat'] == 'En attente') & (df['est_archive'] == 0), 0)
    
    return df


#fonction qui affiche une candidature sous forme de carte (les vues concernées : liste et archives)
def display_candidature(candidature, delai_archive):
    # On affiche la fiche dans une "Card" (st.container avec bordure)
    with st.container(border=True):
        text_icon, text_color = color_result(candidature[['resultat','a_relancer','est_archive']])
        
        
        text_etat = f":{text_color}[:{text_color}-background[**" + str(candidature['resultat']) + "**]]"
        text_jours = ""
        text_archive = ""
        
        if candidature['a_relancer'] :
            text_jours = f":{text_color}[:{text_color}-background[**" + str(candidature['jours_attente']) + " jour(s)**]]"
        
        if candidature['est_archive'] :
            
            text_jours = f":grey[:grey-background[**📦 Archivé**]]"
        
        
        st.markdown(f":{text_color}[:{text_color}-background[**{text_icon} {candidature['societe_nom']} - {candidature['titre_poste']} - {candidature['type_contrat']}**]]")
        st.caption(f"""
                Candidature envoyée le **{datetime.strftime(candidature['date_candidature'], '%d/%m/%Y')}** en **'{candidature['type_candidature']}'**  
                Canal d'envoi : {candidature['canal']}
                """)
        st.write(f"""**Etat :** {text_etat} depuis le {datetime.strftime(candidature['date_ref'], '%d/%m/%Y')} {text_jours}""")
        if candidature['est_archive'] :
            if st.button("→ Désarchiver", key=f"btn_desarchive_{candidature['id']}"):
                confirm_archivage_dialog(int(candidature['id']), candidature['societe_nom'], archive=False)
        else:
            if int(candidature['jours_attente']) >= delai_archive or candidature['resultat'] == "Refus":
                if st.button("→ Archiver", key=f"btn_archive_{candidature['id']}"):
                    confirm_archivage_dialog(int(candidature['id']), candidature['societe_nom'])
        st.write(f"**Commentaires :** {candidature['commentaires']}")
        
        # Bouton pour voir le détail complet
        with st.expander("Détails"):
            cols_detail = st.columns(2)
            with cols_detail[0]:
                st.markdown(f"""
                        **Adresse :** {candidature['societe_adresse']}  
                        **Mail :** {candidature['societe_mail']}  
                        **Tel :** {candidature['societe_tel']}  
                        **Personne contact :** {candidature['societe_contact']}  
                        """)
            with cols_detail[1]:
                st.markdown(f"**Lien original :** [Suivre le lien]({candidature['lien_offre']})")
                pdf_path = candidature['pdf_path']
                    # On vérifie que le fichier existe avant d'essayer de l'afficher
                if pdf_path and os.path.exists(pdf_path):
                    if st.button("Voir le PDF", key=f"btn_pdf_{candidature['id']}"):
                        display_pdf(pdf_path)

# fonction qui sauvegarde une page web
def save_pdf_from_url(url, filename, pdf_folder_path):
    """Lance shot.py en tant que processus indépendant pour éviter les conflits asyncio."""
    if not url: return None
    
    
    output_path = os.path.abspath(os.path.join(pdf_folder_path, f"{filename}.pdf"))

    try:
        # On appelle shot.py avec l'URL et le chemin de sortie
        # On utilise sys.executable pour être sûr d'utiliser le bon environnement Python
        result = subprocess.run(
            [sys.executable, "tools/shot.py", url, output_path],
            capture_output=True,
            text=True
        )
        
        # --- afficher les logs du script ---
        print("=== LOGS shot.py ===")
        print(result.stdout)
        print(result.stderr)
        print("====================")
        
        # --- on vérifie le code retour ---
        if result.returncode == 0:
            print(f"✅ Capture PDF réussie : {output_path}")
            return output_path
        else:
            print(f"❌ Capture PDF échouée : {result.stdout} {result.stderr}")
            return None
        
    except Exception as e:
        st.warning(f"Impossible de générer le PDF (mais la candidature est enregistrée) : {e}")
        print(f"❌ Exception lors de la capture : {e}")
        return None

# fonction qui exécute une requete SQL et si c'est un SELECT, retourne le résultat sous forme de liste de dictionnaires
def run_query(query, params=(), fetch=False):
    import numpy as np
    # chemin absolu du fichier de base de données
    db_path = ROOT_DIR / "db" / DB_FILE_NAME
    
    # fonction interne qui convertit les types Pandas/NumPy/Python en types compatibles SQLite
    def normalize_param(p):
        
        # NumPy → Python natif
        if isinstance(p, (np.integer)):
            return int(p)
        if isinstance(p, (np.floating, np.float64)):
            return float(p)
        if isinstance(p, (np.bool_)):
            return bool(p)

        # Dates → ISO string
        if isinstance(p, (date, datetime)):
            return p.isoformat()

        # None, str, int, float → OK
        return p
    
    # fonction interne qui affiche la requete SQL
    def trace_callback(stmt):
        print("SQL exécuté :", stmt)
    
    try:
        # Ajout de detect_types pour que SQLite reconnaisse nos dates
        with sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            # conn.set_trace_callback(trace_callback) # pour afficher la requete exécutée
            conn.row_factory = sqlite3.Row # Cette ligne permet d'accéder aux colonnes par leur nom (ex: row['societe_nom'])
            cursor = conn.cursor()

            # Toujours convertir params en tuple
            if not isinstance(params, (tuple, list)):
                params = (params,)

            # Conversion explicite des dates en string pour éviter le warning si l'adaptateur échoue
            clean_params = tuple(normalize_param(p) for p in params)

            cursor.execute(query, clean_params)
            conn.commit()
            if fetch:
                # On convertit les sqlite3.Row en dict standard
                return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erreur SQLite ({db_path}): {e}")
        return -1
    return None

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


#fonction qui affiche une modale de confirmation
@st.dialog("Confirmation archivage")
def confirm_archivage_dialog(id, societe, archive=True):
    
    if archive == True:
        txt_title = "Archiver"
        txt_button = "archiver"
        est_archive = 1
        txt_message = "archivée"
    else:
        txt_title = "Désarchiver"
        txt_button = "désarchiver"
        est_archive = 0
        txt_message = "désarchivée"
    
    st.warning(f"{txt_title} la candidature chez **{societe}** ?")
    c1, c2 = st.columns(2)
    if c1.button(f"Oui, {txt_button}", type="primary", width="stretch"):
        try:
            # suppression dans la base de données
            run_query(f"UPDATE candidatures SET est_archive = {est_archive} WHERE id=?", (id,))
            st.session_state.message = f"Candidature chez **{societe}** {txt_message} !"
            st.session_state.message_icon = "✅"
        except Exception as e:
            st.session_state.message = f"Erreur : candidature chez **{societe}** non {txt_message} !"
            st.session_state.message_icon = "❌"
            print(f"Erreur lors de l'archivage : {e}")
        st.rerun()
    if c2.button("Annuler", width="stretch"):
        st.rerun()

# fonction qui donne une couleur en fonction du statut de la candidature
def color_result(val):
    if val['a_relancer'] == 1: return "⚠️", "yellow"
    if val['resultat'] == 'Entretien': return "☑️", "violet"
    if val['resultat'] == 'Offre': return "✅", "green"
    if val['resultat'] == 'Refus': return "❌", "red"
    if val['resultat'] == 'En attente': return "ℹ️", "blue"
    if val['est_archive'] == 1: return "📦", "grey"
    return "ℹ️", "blue"


