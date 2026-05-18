# =============================================================================
# Dockerfile - CSS RAG API Ultra Performant Multimodal
# Version: 2005.0.3
# Description: Image Docker optimisée pour l'API RAG multimodale
# =============================================================================

# =============================================================================
# ÉTAPE 1: IMAGE DE BASE ET DÉPENDANCES SYSTÈME
# =============================================================================
FROM python:3.12-slim AS base

# Métadonnées de l'image
LABEL maintainer="CSS RAG Team"
LABEL version="2005.0.3"
LABEL description="API RAG Ultra Performant Multimodal avec support Telegram"

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Outils de base
    curl \
    wget \
    git \
    # Dépendances pour OpenCV et traitement d'images
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    # Dépendances pour Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    # Dépendances pour compilation Python
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# ÉTAPE 2: INSTALLATION DES DÉPENDANCES PYTHON
# =============================================================================
FROM base AS dependencies

# Mise à jour de pip et installation des outils de build
RUN pip install --upgrade pip setuptools wheel

# Copie du fichier requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Installation des dépendances Python avec optimisations
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# =============================================================================
# ÉTAPE 3: IMAGE FINALE OPTIMISÉE
# =============================================================================
FROM dependencies AS final

# Création d'un utilisateur non-root pour la sécurité
RUN groupadd -r cssrag && useradd -r -g cssrag -s /bin/bash cssrag

# Création des répertoires de travail
WORKDIR /app

# Création des répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /app/logs \
             /app/data \
             /app/uploads \
             /app/multimodal-documents \
             /app/for-analysis/questions-answered \
             /app/for-analysis/request-logs \
             /home/cssrag/.cache \
             /home/cssrag/.cache/huggingface \
             /home/cssrag/.cache/torch \
    && chown -R cssrag:cssrag /app \
    && chown -R cssrag:cssrag /home/cssrag

# Copie de l'application
COPY --chown=cssrag:cssrag app/ /app/app/
COPY --chown=cssrag:cssrag telegram_advanced.py /app/

# Copie du fichier .env s'il existe (optionnel)
COPY --chown=cssrag:cssrag .env* /app/

# Copie des scripts utilitaires (optionnel)
COPY --chown=cssrag:cssrag tests_scripts/ /app/tests_scripts/

# Variables d'environnement pour l'application
ENV PYTHONPATH=/app \
    APP_ENV=production \
    LOG_LEVEL=INFO \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    # Configuration du cache Hugging Face
    HF_HOME=/home/cssrag/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/cssrag/.cache/huggingface \
    TORCH_HOME=/home/cssrag/.cache/torch \
    # Désactivation des modèles multimodaux par défaut pour économiser la mémoire
    DISABLE_MULTIMODAL_MODELS=true \
    # Configuration FastAPI
    HOST=0.0.0.0 \
    PORT=8000 \
    # Configuration Telegram (optionnel)
    AUTO_START_TELEGRAM_BOT=false \
    CSS_API_URL=http://localhost:8000

# Exposition du port
EXPOSE 8000

# Changement vers l'utilisateur non-root
USER cssrag

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Point d'entrée par défaut
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# =============================================================================
# INSTRUCTIONS D'UTILISATION
# =============================================================================
# 
# Construction de l'image:
# docker build -t csshub/chatbot-backend:latest .
#
# Exécution avec Redis externe:
# docker run -d \
#   --name chatbot-backend \
#   -p 8000:8000 \
#   -e REDIS_HOST=your-redis-host \
#   -e REDIS_PASSWORD=your-redis-password \
#   -v $(pwd)/data:/app/data \
#   -v $(pwd)/logs:/app/logs \
#   csshub/chatbot-backend:latest
#
# Exécution avec variables d'environnement personnalisées:
# docker run -d \
#   --name chatbot-backend \
#   -p 8000:8000 \
#   --env-file .env \
#   -v $(pwd)/data:/app/data \
#   -v $(pwd)/logs:/app/logs \
#   csshub/chatbot-backend:latest
#
# =============================================================================