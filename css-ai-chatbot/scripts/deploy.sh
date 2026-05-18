#!/bin/bash

# =============================================================================
# Script de déploiement automatisé - RAG Ultra Performant Multimodal API
# Supporte les environnements: development, staging, production
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/tmp/deploy_${TIMESTAMP}.log"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
ENVIRONMENT=""
IMAGE_TAG=""
REGISTRY_URL="${CI_REGISTRY_IMAGE:-}"
COMPOSE_FILE=""
ENV_FILE=""
BACKUP_ENABLED="true"
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_ON_FAILURE="true"

# Fonction de logging
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} ${timestamp} - $message" | tee -a "$LOG_FILE"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message" | tee -a "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${timestamp} - $message" | tee -a "$LOG_FILE"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} ${timestamp} - $message" | tee -a "$LOG_FILE"
            ;;
    esac
}

# Fonction d'aide
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV    Environnement de déploiement (development|staging|production)
    -t, --tag TAG           Tag de l'image Docker à déployer
    -r, --registry URL      URL du registre Docker (optionnel)
    -b, --no-backup         Désactiver la sauvegarde avant déploiement
    -n, --no-rollback       Désactiver le rollback automatique en cas d'échec
    -h, --help              Afficher cette aide

Exemples:
    $0 -e development -t latest
    $0 -e staging -t v1.2.3
    $0 -e production -t v1.2.3 -r registry.gitlab.com/user/project
EOF
}

# Fonction de nettoyage en cas d'erreur
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log "ERROR" "Déploiement échoué avec le code $exit_code"
        if [ "$ROLLBACK_ON_FAILURE" = "true" ] && [ -n "$ENVIRONMENT" ]; then
            log "INFO" "Tentative de rollback..."
            rollback_deployment
        fi
    fi
    exit $exit_code
}

# Configuration du trap pour le nettoyage
trap cleanup EXIT

# Fonction de validation des prérequis
validate_prerequisites() {
    log "INFO" "Validation des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log "ERROR" "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier les paramètres obligatoires
    if [ -z "$ENVIRONMENT" ]; then
        log "ERROR" "L'environnement doit être spécifié"
        show_help
        exit 1
    fi
    
    if [ -z "$IMAGE_TAG" ]; then
        log "ERROR" "Le tag de l'image doit être spécifié"
        show_help
        exit 1
    fi
    
    log "INFO" "Prérequis validés"
}

# Fonction de configuration de l'environnement
configure_environment() {
    log "INFO" "Configuration de l'environnement: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        "development")
            COMPOSE_FILE="docker-compose.yml"
            ENV_FILE=".env.dev"
            ;;
        "staging")
            COMPOSE_FILE="docker-compose.staging.yml"
            ENV_FILE=".env.staging"
            ;;
        "production")
            COMPOSE_FILE="docker-compose.prod.yml"
            ENV_FILE=".env.prod"
            ;;
        *)
            log "ERROR" "Environnement non supporté: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Vérifier l'existence des fichiers
    if [ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]; then
        log "ERROR" "Fichier Docker Compose non trouvé: $COMPOSE_FILE"
        exit 1
    fi
    
    log "INFO" "Configuration terminée"
}

# Fonction de sauvegarde
backup_data() {
    if [ "$BACKUP_ENABLED" = "false" ]; then
        log "INFO" "Sauvegarde désactivée"
        return 0
    fi
    
    log "INFO" "Création de la sauvegarde..."
    
    # Créer le répertoire de sauvegarde
    local backup_dir="/backups/${ENVIRONMENT}_${TIMESTAMP}"
    mkdir -p "$backup_dir"
    
    # Sauvegarder les volumes Docker
    if docker volume ls | grep -q "${ENVIRONMENT}_"; then
        log "INFO" "Sauvegarde des volumes Docker..."
        docker run --rm \
            -v "${ENVIRONMENT}_redis_data:/source/redis:ro" \
            -v "${ENVIRONMENT}_chroma_data:/source/chroma:ro" \
            -v "$backup_dir:/backup" \
            alpine:latest \
            sh -c "tar czf /backup/volumes_${TIMESTAMP}.tar.gz -C /source ."
    fi
    
    # Sauvegarder la configuration
    cp "$PROJECT_ROOT/$COMPOSE_FILE" "$backup_dir/"
    if [ -f "$PROJECT_ROOT/$ENV_FILE" ]; then
        cp "$PROJECT_ROOT/$ENV_FILE" "$backup_dir/"
    fi
    
    log "INFO" "Sauvegarde créée dans: $backup_dir"
}

# Fonction de déploiement
deploy() {
    log "INFO" "Début du déploiement..."
    
    cd "$PROJECT_ROOT"
    
    # Arrêter les services existants
    log "INFO" "Arrêt des services existants..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
    
    # Nettoyer les images non utilisées
    log "INFO" "Nettoyage des images non utilisées..."
    docker image prune -f || true
    
    # Tirer les nouvelles images
    if [ -n "$REGISTRY_URL" ]; then
        log "INFO" "Récupération de l'image depuis le registre..."
        docker pull "${REGISTRY_URL}:${IMAGE_TAG}"
    fi
    
    # Démarrer les services
    log "INFO" "Démarrage des services..."
    export IMAGE_TAG="$IMAGE_TAG"
    export REGISTRY_URL="$REGISTRY_URL"
    
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log "INFO" "Services démarrés"
}

# Fonction de vérification de santé
health_check() {
    log "INFO" "Vérification de la santé des services..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local interval=10
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up (healthy)"; then
            log "INFO" "Services en bonne santé"
            return 0
        fi
        
        log "DEBUG" "Attente de la santé des services... ($elapsed/$timeout secondes)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    log "ERROR" "Timeout atteint pour la vérification de santé"
    return 1
}

# Fonction de rollback
rollback_deployment() {
    log "WARN" "Rollback du déploiement..."
    
    # Arrêter les services défaillants
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true
    
    # Restaurer depuis la sauvegarde si disponible
    local latest_backup=$(find /backups -name "${ENVIRONMENT}_*" -type d | sort -r | head -n 2 | tail -n 1)
    if [ -n "$latest_backup" ] && [ -d "$latest_backup" ]; then
        log "INFO" "Restauration depuis: $latest_backup"
        
        # Restaurer les volumes
        if [ -f "$latest_backup/volumes_*.tar.gz" ]; then
            docker run --rm \
                -v "${ENVIRONMENT}_redis_data:/target/redis" \
                -v "${ENVIRONMENT}_chroma_data:/target/chroma" \
                -v "$latest_backup:/backup:ro" \
                alpine:latest \
                sh -c "cd /target && tar xzf /backup/volumes_*.tar.gz"
        fi
        
        # Redémarrer avec la configuration précédente
        docker-compose -f "$COMPOSE_FILE" up -d
        
        log "INFO" "Rollback terminé"
    else
        log "WARN" "Aucune sauvegarde trouvée pour le rollback"
    fi
}

# Fonction de post-déploiement
post_deployment() {
    log "INFO" "Tâches post-déploiement..."
    
    # Afficher le statut des services
    log "INFO" "Statut des services:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Afficher les logs récents
    log "INFO" "Logs récents:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
    
    # Nettoyer les anciennes sauvegardes (garder les 5 dernières)
    if [ -d "/backups" ]; then
        find /backups -name "${ENVIRONMENT}_*" -type d | sort -r | tail -n +6 | xargs rm -rf || true
    fi
    
    log "INFO" "Déploiement terminé avec succès!"
}

# Fonction principale
main() {
    log "INFO" "Début du script de déploiement"
    log "INFO" "Environnement: $ENVIRONMENT, Tag: $IMAGE_TAG"
    
    validate_prerequisites
    configure_environment
    backup_data
    deploy
    health_check
    post_deployment
    
    log "INFO" "Script de déploiement terminé"
}

# Parsing des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY_URL="$2"
            shift 2
            ;;
        -b|--no-backup)
            BACKUP_ENABLED="false"
            shift
            ;;
        -n|--no-rollback)
            ROLLBACK_ON_FAILURE="false"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log "ERROR" "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Exécuter le script principal
main