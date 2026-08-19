FROM python:3.12-slim-bookworm
# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# chemin interne container
WORKDIR /app

# install dependances uv
COPY pyproject.toml uv.lock /app/
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked 

# affichage des logs en temps réel dans docker
ENV PYTHONUNBUFFERED=1

# copier le code source de l'hôte vers container et recrer arborescence dans container
COPY src/ ./src/


# créer les dossiers persistants
RUN mkdir -p /data/db
RUN mkdir -p /data/files
#COPY db/ /data/db/
#COPY offres_pdf/ /data/files/offres_pdf

# lancer le script de création de la base de données
RUN python src/tools/create_db.py