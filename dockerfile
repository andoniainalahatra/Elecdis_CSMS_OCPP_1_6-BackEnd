
# Utilisation d'une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration et les dépendances
COPY requirements.txt requirements.txt
COPY .env ./

# Installer les dépendances et nettoyer les fichiers temporaires pour minimiser la taille de l'image
RUN pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Copier le code source et les fichiers de configuration d'Alembic
COPY . .
COPY alembic.ini alembic/

# Exposer le port de l'application
EXPOSE 8080

# Démarrer l'application
CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8080"]
