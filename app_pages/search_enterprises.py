import streamlit as st
import tools.utils as tools
import tools.streamlit_widgets as st_widgets

# charger les données initiales (pour les formulaires)
ETAT_ADMINISTRATIF = {"Active" : "A", "Cessée": "C"}
NAF_CODES = tools.get_codes_naf()
TRANCHES_EFFECTIF = tools.get_tranches_effectif()
DEPARTEMENTS = tools.get_departements()
CODES_POSTAUX = tools.get_codes_postaux()


st.subheader("🔎 Recherche d'entreprises")

# --- INITIALISATION DU STATE ---
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "search_params" not in st.session_state:
    st.session_state.search_params = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# Création du formulaire
with st.form("search_entreprise_form"):

    # Définition des 4 champs de sélection multiple
    champ_1 = st.radio("Etat administratif", options=ETAT_ADMINISTRATIF)
    champ_2 = st.multiselect("Activité principale", options=NAF_CODES, help="Vous pouvez sélectionner plusieurs éléments")
    champ_3 = st.multiselect("Effectifs salariés", options=TRANCHES_EFFECTIF, help="Vous pouvez sélectionner plusieurs éléments")
    champ_4 = st.multiselect("Départements", options=DEPARTEMENTS, help="Vous pouvez sélectionner plusieurs éléments")
    champ_5 = st.multiselect("Codes Postaux", options=CODES_POSTAUX, help="Vous pouvez sélectionner plusieurs éléments")

    # Bouton de soumission du formulaire
    submitted = st.form_submit_button("Lancer la recherche", type="primary")



# Logique de traitement après clic sur le bouton
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
    
# AFFICHAGE DES RÉSULTATS (Persistant grâce au session_state)
if st.session_state.search_results:
    res = st.session_state.search_results
    results_list = res['results']
    
    st.divider()
    st.info(f"📍 {res['total_results']} entreprises trouvées (Page {st.session_state.current_page} sur {res['total_pages']})")

    # --- Affichage des fiches entreprises
    nb_cols = 3
    # On parcourt la liste par groupes de nb_cols
    for i in range(0, len(results_list), nb_cols):
        cols = st.columns(nb_cols) # On crée les colonnes pour cette ligne
        
        # On remplit chaque colonne du groupe actuel
        for j in range(nb_cols):
            if i + j < len(results_list):
                with cols[j]:
                    # On affiche la fiche dans une "Card" (st.container avec bordure)
                    with st.container(border=True):
                        # On réduit un peu la taille du texte pour que ça rentre bien en colonnes
                        st.markdown(f"**{results_list[i+j]['Nom']}**")
                        st.write(f"📍 {results_list[i+j]['Adresse']}")
                        st.caption(f"SIREN: {results_list[i+j]['SIREN']} / NAF: {results_list[i+j]['NAF']}")
                        
                        # Bouton optionnel pour voir le détail complet
                        with st.expander("Détails"):
                            st.info(tools.get_entreprise_details(results_list[i+j]))

    # --- PAGINATION ---
    if res["total_pages"] > 1:
        st_widgets.afficher_pagination(res["total_pages"])