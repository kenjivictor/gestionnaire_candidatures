import pandas as pd
import requests

# Paramètres de recherche
BASE_URL = "https://recherche-entreprises.api.gouv.fr/search"


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




#        **Coordonnées GPS :** {dico['Coordonnées GPS']}  

def get_entreprise_text(dico):
    return f"""
        ### _{dico['Nom']}_   
        **Adresse :** {dico['Adresse']}  
        **SIREN :** {dico['SIREN']} / **NAF :** {dico['NAF']}  
        **Tranche Effectif :** {dico['Tranche Effectif']} / **Catégorie d'entreprise :** {dico['Catégorie d\'entreprise']}  
        **Nature juridique:** {dico['Nature juridique']}  
        **Date de création :** {dico['Date de création']}  
        **Date de fermeture :** {dico['Date de fermeture']}  
        **Convention(s) collective(s) :** {dico['Convention(s) collective(s)']}  
    """

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

