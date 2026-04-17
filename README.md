# 📖 Présentation du projet
![Python](https://img.shields.io/badge/python-3.12+-blue.svg) ![Streamlit](https://img.shields.io/badge/streamlit-1.55-red.svg)

Fraîchement certifiée **Data Analyst** 🎓, j'ai rapidement été confrontée à un défi de taille : gérer efficacement un volume croissant de candidatures. Entre les relances à effectuer, les entretiens à préparer et le suivi des réponses, j'ai ressenti le besoin d'un outil centralisé et intelligent.

   *🚀 L'objectif : transformer un processus administratif fastidieux en un flux de données exploitable.*

Pour répondre à ce besoin, j'ai conçu et développé une application de suivi en temps réel sous **Python** et **Streamlit**. 

Ce projet m'a permis de mettre en pratique des compétences clés :
- **Data Management :** Manipulation et structuration des données avec Pandas.
- **Automatisation :** Création d'alertes intelligentes pour les relances.
- **Dataviz :** Mise en place d'un tableau de bord décisionnel pour piloter ma recherche à l'instant T.

# 📷 Aperçu de l'application
*Les données présentes dans l'aperçu sont des données de test*
![Aperçu de l'application](animation_candidatures.gif)

# ⚙️ Fonctionnalités principales

📁 **Gestion du cycle de vie des candidatures**
- **Suivi centralisé :** Enregistrement complet des opportunités (Société, Contact, Lien de l'offre, Type de contrat).
- **Stockage intelligent :** Archivage et visualisation directe des fichiers PDF (capture de l'offre en PDF via l'URL) grâce à un lecteur intégré.
- **Logique de relance :** Calcul dynamique du statut "À relancer" basé sur des seuils temporels personnalisables.

🔍 **Module de Sourcing & Prospection (via API)**
- **Recherche en temps réel :** Connexion directe à l'[API Recherche d'entreprises](https://recherche-entreprises.api.gouv.fr) pour identifier de nouvelles cibles.
- **Filtres multicritères :** Ciblage précis par domaine d'activité (code NAF), par tranche d'effectifs et secteurs géographiques (département, ville).
- **Prospection Data-Driven :** Génération instantanée d'une liste d'entreprises correspondant à la recherche dans une zone géographique donnée.

📊 **Pilotage & Analyse**
- **Tableau de bord :** Indicateurs clés (KPIs) mis à jour à l'instant T pour piloter l'effort de recherche.
- **Pagination fluide :** Navigation optimisée dans le catalogue de candidatures pour une expérience utilisateur fluide.


# 🛠️ Stack Technique

- **Langage :** `Python 3.12+` 
- **Gestion de paquets :** `uv` (Performance et isolation) 
- **Analyse de données :** `Pandas` (Manipulation de DataFrames) 
- **Interface Utilisateur :** `Streamlit` (Dashboard interactif) 
- **Base de données :** `SQLite3` (Stockage relationnel local) 
- **Environnement :** `python-dotenv` (Gestion sécurisée des variables d'environnement) 
- **API Externes :** [API Recherche d'entreprises](https://recherche-entreprises.api.gouv.fr) (Récupération de métadonnées légales)
- **Requêtes HTTP :** `Requests` (Gestion des appels API et des codes de statut)



# 🌟 Points Clés du Projet
- **Intelligence Métier :** Calcul automatique des délais de relance et priorisation des dossiers.
- **Expérience Utilisateur :** Visualisation des PDF intégrée directement dans l'interface via encodage Base64.
- **Robustesse :** Gestion dynamique des chemins de fichiers (système agnostique) avec pathlib.
- **Clean Code :** Fonctions modulaires, commentaires explicites et séparation de la logique DB / UI.
- **Interopérabilité :** Connexion à des services tiers via API REST pour automatiser l'enrichissement des fiches entreprises.



# 🧠 Difficultés Rencontrées & Solutions

| Difficulté | Solution apportée |
| :--- | :--- |
| **Gestion des chemins** entre les dossiers ``tools/`` et ``db/`` | Utilisation de ``Path(__file__).resolve()`` pour garantir un déploiement sans erreur peu importe l'OS |
| **Affichage des PDF** sans plugin tiers instable | Implémentation d'un **IFrame HTML** avec injection de données en Base64 et paramètres de zoom auto (``#view=FitH``) |
| **Persistance des données** lors des interactions Streamlit | Optimisation du cache et rechargement forcé du fichier ``.env`` (``override=True``) pour une réactivité immédiate |
| **Calcul des relances** complexe sur des dates vides | Utilisation de la **vectorisation Pandas** (``np.where`` et ``.fillna``) pour un calcul de statut instantané |
| **Volume de données limitées** de l'API | Implémentation de filtres côté client (Pandas) et côté serveur (Paramètres de requête API) pour ne récupérer que les entreprises pertinentes en respectant les limites de requêtes imposées par l'API |
| **Lisibilité des résultats** | Transformation du JSON brut en un DataFrame Pandas propre et trié, affiché dynamiquement dans Streamlit |


# 💻 Installation & lancement

1. Cloner le projet

2. Installer les dépendances : `uv sync`

3. Configuration
    1. Copier le fichier `.env-dist` vers `.env`
    2. Mettre à jour les variables d'environnement dans le nouveau fichier

4. Structure de la Base de Données (SQLite)
Lancer la commande `python tools/create_db.py` une seule fois pour créer la base de données

5. L'application Streamlit 
Lancer la commande `streamlit run app.py`

---

*Projet réalisé par Kenji VICTOR dans le cadre de ma recherche de poste en Data Analysis. N'hésitez pas à me contacter sur [LinkedIn](https://www.linkedin.com/in/kenji-victor/) !*