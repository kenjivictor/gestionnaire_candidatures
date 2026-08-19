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
- **Conteneurisation :** `Docker` (Isolation de l'environnement et persistance des données)

# 🐳 Conteneurisation avec Docker
L’application est entièrement conteneurisée afin de garantir un environnement reproductible, isolé et simple à déployer.
La conteneurisation permet également de séparer le code Streamlit, la base SQLite et les fichiers générés, tout en assurant une persistance totale des données.

### 🔧 Architecture du conteneur

```
/app/src        → Code Streamlit (monté depuis l’hôte)
/data/db        → Base SQLite persistante (volume Docker)
/data/pdf       → Fichiers PDF générés ou importés (volume Docker)
```

Le dossier `src/` est monté dans le conteneur, ce qui permet un hot reload : toute modification du code est immédiatement prise en compte sans rebuild.

### 📦 Persistance des données
L’application utilise une base SQLite ainsi qu’un dossier dédié aux fichiers générés et importés (PDF).
Pour garantir que ces données ne soient jamais perdues, même lors d’un rebuild ou d’un redémarrage du conteneur, l’architecture Docker repose sur un volume persistant (`db-data`).

| Dossier | Rôle |
| :--- | :--- |
| `/data/db` | Base SQLite |
| `/data/pdf` | Fichiers PDF générés et importés |

Ces deux répertoires sont montés dans un volume Docker, ce qui permet :
- de conserver l’historique complet des candidatures,
- de préserver les fichiers PDF associés,
- de redémarrer ou reconstruire le conteneur sans perte de données.


# 🌟 Points Clés du Projet
- **Conteneurisation Docker :** environnement isolé, reproductible, avec persistance totale des données (base SQLite + PDF)
- **Vectorisation Pandas :** calculs instantanés pour les statuts et relances.
- **Expérience Utilisateur :** Visualisation des PDF intégrée dans l'interface sans dépendances externes.
- **Tableau de bord dynamique :** KPIs mis à jour en temps réel.
- **Robustesse :** Gestion dynamique des chemins de fichiers.
- **Interopérabilité API :** sourcing automatisé via l’API Recherche d’entreprises.
- **Clean Code & maintenabilité :** Fonctions modulaires, commentaires explicites et structure cohérente.


# 📁 Structure du projet

L’application est organisée de manière modulaire afin de séparer clairement la logique métier, l’interface utilisateur, la gestion des données et les outils techniques. Cette structure facilite la maintenance, l’évolution du projet et son déploiement via Docker.

```
├── src/                            → Code source de l’application Streamlit
│   ├── main.py                     → Point d’entrée de l’application
│   ├── app_pages/                  → Pages Streamlit (navigation multi-pages)
│   │   ├── list.py                 → KPIs & Candidatures en cours
│   │   ├── add.py                  → Ajout d'une candidature
│   │   ├── archive.py              → Les candidatures archivées
│   │   ├── search_entreprises.py   → Module de prospection via API
│   │   └── update_delete.py        → Modifier/Supprimer une candidature
│   │
│   ├── data/                → Fichiers CSV pour le remplissage automatique des formulaires
│   │
│   ├── static/              → Polices de thème Streamlit
│   │
│   └── tools/               → Scripts utilitaires
│       ├── create_db.py     → Initialisation de la base SQLite
│       ├── shot.py          → Génération des PDF à partir d'une URL
│       └── utils.py         → Fonctions techniques
│
├── .streamlit/              → Configuration Streamlit (thème, secrets…)
│
├── docker-compose.yml       → Définition des services & volumes Docker
├── Dockerfile               → Construction de l’image de l’application
│
├── .env                     → Variables d’environnement
├── .env-dist                → Modèle de configuration
│
├── pyproject.toml           → Dépendances & configuration du projet
└── uv.lock                  → Verrouillage des versions (uv)
```



# 💻 Installation & lancement

### ⚙️ Configuration initiale
1. Cloner le projet

2. Variables d'environnement
    1. Créer le fichier `.env`
    ```
    cp .env-dist .env
    ```
    2. Mettre à jour les variables d'environnement dans le nouveau fichier


### ▶️ Lancement avec Docker
```
docker compose up
```

L’application est accessible sur le port défini dans `.env`.

### 🔄 Rebuild de l’image
Uniquement nécessaire si :
- le Dockerfile change,
- les dépendances Python évoluent,
- la structure du projet est modifiée.

```
docker compose up --build
```

Les volumes ne sont pas supprimés : la base SQLite reste intacte.

### 🧹 Réinitialisation complète (base + fichiers)
```
docker compose down -v
docker compose up --build
```
⚠️ Cette commande supprime les volumes → la base et les PDF sont effacés.




# 🧠 Difficultés Rencontrées & Solutions

| Difficulté | Solution apportée |
| :--- | :--- |
| **Gestion des chemins** entre les dossiers ``tools/`` et ``db/`` | Utilisation de ``Path(__file__).resolve()`` pour garantir un déploiement sans erreur peu importe l'OS |
| **Affichage des PDF** sans plugin tiers instable | Implémentation d'un **IFrame HTML** avec injection de données en Base64 et paramètres de zoom auto (``#view=FitH``) |
| **Persistance des données** lors des interactions Streamlit | Optimisation du cache et rechargement forcé du fichier ``.env`` (``override=True``) pour une réactivité immédiate |
| **Calcul des relances** complexe sur des dates vides | Utilisation de la **vectorisation Pandas** (``np.where`` et ``.fillna``) pour un calcul de statut instantané |
| **Volume de données limitées** de l'API | Implémentation de filtres côté client (Pandas) et côté serveur (Paramètres de requête API) pour ne récupérer que les entreprises pertinentes en respectant les limites de requêtes imposées par l'API |
| **Lisibilité des résultats** | Transformation du JSON brut en un DataFrame Pandas propre et trié, affiché dynamiquement dans Streamlit |
| **Perte de la base SQLite lors des rebuilds Docker** (volume monté au mauvais emplacement, écrasement du fichier lors du build) | Mise en place d’une structure de volumes persistants : création d’un dossier parent ``/data``, montage du volume sur ce répertoire, déplacement de la base dans ``/data/db``, ajout d’un dossier ``/data/pdf`` pour les fichiers générés, et correction des chemins dans l’application pour garantir une persistance totale |

---

*Projet réalisé par Kenji VICTOR dans le cadre de ma recherche de poste en Data Analysis. N'hésitez pas à me contacter sur [LinkedIn](https://www.linkedin.com/in/kenji-victor/) !*