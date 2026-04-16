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
BASE_URL = "https://recherche-entreprises.api.gouv.fr/search"
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



TRANCHES_EFFECTIF = get_tranches_effectif()
FORMES_JURIDIQUES = get_formes_juridique()




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
        response = requests.get(BASE_URL, params=params, timeout=10, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        

        for item in results:
            
            
            all_results.append({
                "SIREN": item.get("siren"),
                "Nom": item.get("nom_complet"),
                "Adresse": item.get("siege").get("adresse"),
                "NAF": item.get("activite_principale"),
                "Tranche Effectif": find_element_key_dico(item.get("tranche_effectif_salarie"), TRANCHES_EFFECTIF),
                "Coordonnées GPS": item.get("siege").get("coordonnees"),
                "Nature juridique": FORMES_JURIDIQUES.get(int(item.get("nature_juridique")[0])),
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






# def get_entreprise_text(dico):
#     return f"""
#         ### _{dico['Nom']}_   
#         **Adresse :** {dico['Adresse']}  
#         **SIREN :** {dico['SIREN']} / **NAF :** {dico['NAF']}  
#         **Tranche Effectif :** {dico['Tranche Effectif']} / **Catégorie d'entreprise :** {dico['Catégorie d\'entreprise']}  
#         **Nature juridique:** {dico['Nature juridique']}  
#         **Date de création :** {dico['Date de création']}  
#         **Date de fermeture :** {dico['Date de fermeture']}  
#         **Convention(s) collective(s) :** {dico['Convention(s) collective(s)']}  
#     """

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
    # chemin absolu du fichier de base de données
    db_path = ROOT_DIR / "db" / DB_FILE_NAME
    try:
        
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

# fonction qui donne une couleur en fonction du statut de la candidature
def color_result(val):
    if val == 'En attente': return "ℹ️", "blue"
    if val == 'Entretien': return "☑️", "violet"
    if val == 'Offre': return "✅", "green"
    if val == 'Refus': return "❌", "red"
    return "ℹ️", "blue"


