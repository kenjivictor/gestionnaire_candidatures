import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

# chemin absolu du dossier racine
ROOT_DIR = Path(__file__).resolve().parent.parent

# Charger les variables d'environnement du fichier .env
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path)
DB_FILE_NAME = os.getenv("DB_FILE_NAME", "default.db")

# chemin absolu du fichier de base de données
DB_PATH = ROOT_DIR / "db" / DB_FILE_NAME


def init_db():
    try:
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS candidatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_candidature DATE,
                societe_nom TEXT,
                societe_adresse TEXT,
                societe_tel TEXT,
                societe_mail TEXT,
                societe_contact TEXT,
                type_candidature TEXT,
                canal TEXT,
                titre_poste TEXT,
                type_contrat TEXT,
                lien_offre TEXT,
                pdf_path TEXT,
                date_reponse DATE,
                resultat TEXT,
                suite_a_donner TEXT,
                commentaires TEXT,
                est_archive INTEGER DEFAULT (0)
            )
        ''')
        conn.commit()
        conn.close()
        print(f"✅ Succès : Base de données initialisée ici -> {DB_PATH}")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")

if __name__ == "__main__":
    init_db()
