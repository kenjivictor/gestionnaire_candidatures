import streamlit as st
import tools.utils as tools


# --- FONCTION DE PAGINATION DYNAMIQUE ---
def afficher_pagination(total_pages):
    curr_p = st.session_state.current_page
    
    # 1. Barre de navigation principale (Conteneur horizontal)
    st.write("---")
    
    # ÉTAPE 1 : Créer 3 colonnes pour le centrage global
    # [1, 3, 1] signifie que la colonne centrale est 3x plus large que les bords
    _, center_col, _ = st.columns([1, 9, 1])
    
    with center_col:
        # ÉTAPE 2 : Dans la colonne centrale, on crée nos sous-colonnes pour les boutons
        # On calcule le nombre de boutons (Premier, Précédent, 9 numéros, Suivant, Dernier)
        # On peut en avoir jusqu'à 13 au total.
        cols = st.columns([1] * 13)

        col_idx = 0

        # --- BOUTON PREMIER & PRÉCÉDENT ---
        with cols[col_idx]:
            if st.button("«", help="Première page", disabled=(curr_p == 1)):
                changer_page(1)
        col_idx += 1
        
        with cols[col_idx]:
            if st.button("‹", help="Précédente", disabled=(curr_p == 1)):
                changer_page(curr_p - 1)
        col_idx += 1

        # --- CALCUL DES PAGES ENVIRONNANTES (-4, +4) ---
        # On veut afficher au max 9 numéros (4 avant, la courante, 4 après)
        start_p = max(1, curr_p - 4)
        end_p = min(total_pages, curr_p + 4)

        # Ajustement si on est au début ou à la fin pour toujours avoir 7 boutons si possible
        if curr_p <= 4:
            end_p = min(total_pages, 9)
        if curr_p > total_pages - 4:
            start_p = max(1, total_pages - 8)

        # --- BOUTONS NUMÉRIQUES ---
        for p in range(start_p, end_p + 1):
            with cols[col_idx]:
                btn_type = "primary" if p == curr_p else "secondary"
                if st.button(f"{p}", key=f"p_{p}", type=btn_type):
                    changer_page(p)
            col_idx += 1

        # On se cale sur les deux dernières colonnes pour Suivant/Dernier
        col_idx = 11

        # --- BOUTON SUIVANT & DERNIER ---
        with cols[col_idx]:
            if st.button("›", help="Suivante", disabled=(curr_p == total_pages)):
                changer_page(curr_p + 1)
        col_idx += 1
        
        with cols[col_idx]:
            if st.button("»", help="Dernière page", disabled=(curr_p == total_pages)):
                changer_page(total_pages)

def changer_page(num):
    st.session_state.current_page = num
    with st.spinner(f"Chargement page {num}..."):
        st.session_state.search_results = tools.fetch_entreprises(
            st.session_state.search_params, 
            page=num
        )
    st.rerun()