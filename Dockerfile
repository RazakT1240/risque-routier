# Image de déploiement « Risque routier » (Dash + gunicorn).
# Les agrégats Parquet (data/processed/) sont versionnés et copiés dans l'image ;
# les données BRUTES restent hors du dépôt (G16).
FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8050 \
    APP_AUTH=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050
# gunicorn sert le serveur Flask exposé par app/app.py (app.server).
# 1 worker + threads : empreinte mémoire maîtrisée (tier gratuit) et cache process cohérent.
CMD ["sh", "-c", "gunicorn app.app:server -b 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120"]
