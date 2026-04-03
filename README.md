
# Présentation du projet

Depuis ma reconvertion en Data Analyst, j'ai découvert pas mal de notions telles que le langage Python, possibilité de publier une application via Streamlit, les librairies d'analyse de données comme Pandas et bien d'autres.

Une fois ma certification en poche, je me suis lancée dans la recherche d'offres d'emplois. J'ai commencé à recevoir des réponses et au bout d'un moment, je ne savais plus où j'avais postulé, et quelles entreprises il fallait que je relance.

Il me fallait un outil qui me permette de référencer mes candidatures, les classer et avoir une analyse qui me donne des infos à l'instant T.

J'ai donc créé une application entièrement codée en Python, qui me permette d'avoir un suivi en temps réel de mes candidatures.

# Fonctionnalités

- Liste des candidatures et filtrage
- Ajout de candidature et capture de l'offre en PDF, si c'est une réponse à une offre
- Modification/Suppression de candidature
- Recherche d'entreprise grâce à l'[API Recherche d'entreprises](https://recherche-entreprises.api.gouv.fr)

# Installation

## Structure de la Base de Données (SQLite)

Lancer la commande `python tools/create_db.py` une seule fois pour créer la base de données `candidatures.db`


## L'application Streamlit 
Lancer la commande `streamlit run app.py`


# Configuration

1. Copier le fichier `.env-dist` vers `.env`
2. Mettre à jour les variables d'environnement dans le nouveau fichier