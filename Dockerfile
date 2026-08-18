FROM python:3.12-slim-bookworm
# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# chemin interne container
WORKDIR /app

# install dependances uv
COPY pyproject.toml uv.lock /app/
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked 

#affichage des logs en temps réel dans docker
ENV PYTHONUNBUFFERED=1

# copier le code source de l'ordinateur vers container et recrer arborescence dans container
COPY src/ ./src/


#copier la base de données
RUN mkdir -p /data/db
COPY db/ /data/db/

#copier les fichiers
RUN mkdir -p /data/offres_pdf
COPY offres_pdf/ /data/offres_pdf/
