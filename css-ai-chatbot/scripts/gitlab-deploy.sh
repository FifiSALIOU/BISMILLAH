#!/bin/bash

# =============================================================================
# Script de déploiement GitLab CI/CD - RAG Ultra Performant Multimodal API
# Intégration avec les variables GitLab CI/CD et Container Registry
# =============================================================================

set -euo pipefail

# Configuration GitLab CI/CD
GITLAB_REGISTRY="${CI_REGISTRY:-}"
GITLAB_IMAGE="${CI_REGISTRY_IMAGE:-}"
GITLAB_TOKEN="${CI_JOB_TOKEN:-}"
GITLAB_COMMIT="${CI_COMMIT_SHA:-}"
GITLAB_BRANCH="${CI_COMMIT_REF_NAME:-}"
GITLAB_TAG="${CI_COMMIT_TAG:-}"
GITLAB_ENVIRONMENT="${CI_ENVIRONMENT_NAME:-}"

# Configuration du déploiement
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/tmp/gitlab_deploy_${TIMESTAMP}.log"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
DEPLOY_HOST="${DEPLOY_HOST:-}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/rag-api}"
SSH_KEY_PATH="${SSH_PRIVATE_KEY_PATH:-/tmp/deploy_key}"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Fonction de nettoyage
cleanup() {
    local exit_code=$?
    
    # Nettoyer les fichiers temporaires
    if [ -f "$SSH_KEY_PATH" ]; then
        rm -f "$SSH_KEY_PATH"
    fi
    
    if [ $exit_code -ne 0 ]; then
        log "ERROR" "Déploiement GitLab échoué avec le code $exit_code"
        
        # Envoyer une notification d'échec si configuré
        if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
            send_slack_notification "failure" "Déploiement échoué pour $GITLAB_ENVIRONMENT"
        fi
    fi
    
    exit $exit_code
}

trap cleanup EXIT

# Fonction de validation GitLab CI/CD
validate_gitlab_environment() {
    log "INFO" "Validation de l'environnement GitLab CI/CD..."
    
    if [ -z "$GITLAB_REGISTRY" ]; then
        log "ERROR" "Variable CI_REGISTRY non définie"
        exit 1
    fi
    
    if [ -z "$GITLAB_IMAGE" ]; then
        log "ERROR" "Variable CI_REGISTRY_IMAGE non définie"
        exit 1
    fi
    
    if [ -z "$GITLAB_TOKEN" ]; then
        log "ERROR" "Variable CI_JOB_TOKEN non définie"
        exit 1
    fi
    
    if [ -z "$GITLAB_ENVIRONMENT" ]; then
        log "ERROR" "Variable CI_ENVIRONMENT_NAME non définie"
        exit 1
    fi
    
    log "INFO" "Environnement GitLab validé"
    log "INFO" "Registry: $GITLAB_REGISTRY"
    log "INFO" "Image: $GITLAB_IMAGE"
    log "INFO" "Environment: $GITLAB_ENVIRONMENT"
    log "INFO" "Branch: $GITLAB_BRANCH"
    log "INFO" "Commit: ${GITLAB_COMMIT:0:8}"
}

# Fonction de connexion au registre GitLab
login_to_registry() {
    log "INFO" "Connexion au GitLab Container Registry..."
    
    echo "$GITLAB_TOKEN" | docker login -u gitlab-ci-token --password-stdin "$GITLAB_REGISTRY"
    
    if [ $? -eq 0 ]; then
        log "INFO" "Connexion au registre réussie"
    else
        log "ERROR" "Échec de la connexion au registre"
        exit 1
    fi
}

# Fonction de détermination du tag d'image
determine_image_tag() {
    local image_tag=""
    
    if [ -n "$GITLAB_TAG" ]; then
        # Déploiement depuis un tag Git
        image_tag="$GITLAB_TAG"
        log "INFO" "Utilisation du tag Git: $image_tag"
    elif [ "$GITLAB_BRANCH" = "main" ] || [ "$GITLAB_BRANCH" = "master" ]; then
        # Déploiement depuis la branche principale
        image_tag="latest"
        log "INFO" "Utilisation du tag latest pour la branche principale"
    else
        # Déploiement depuis une branche de développement
        image_tag="${GITLAB_BRANCH}-${GITLAB_COMMIT:0:8}"
        log "INFO" "Utilisation du tag de branche: $image_tag"
    fi
    
    echo "$image_tag"
}

# Fonction de configuration SSH
setup_ssh() {
    if [ -z "$DEPLOY_HOST" ]; then
        log "INFO" "Déploiement local, SSH non requis"
        return 0
    fi
    
    log "INFO" "Configuration SSH pour le déploiement distant..."
    
    # Créer la clé SSH depuis la variable d'environnement
    if [ -n "${SSH_PRIVATE_KEY:-}" ]; then
        echo "$SSH_PRIVATE_KEY" | base64 -d > "$SSH_KEY_PATH"
        chmod 600 "$SSH_KEY_PATH"
        log "INFO" "Clé SSH configurée"
    else
        log "ERROR" "Variable SSH_PRIVATE_KEY non définie pour le déploiement distant"
        exit 1
    fi
    
    # Ajouter l'hôte aux known_hosts
    ssh-keyscan -H "$DEPLOY_HOST" >> ~/.ssh/known_hosts 2>/dev/null || true
}

# Fonction de déploiement local
deploy_local() {
    local image_tag="$1"
    local full_image="${GITLAB_IMAGE}:${image_tag}"
    
    log "INFO" "Déploiement local avec l'image: $full_image"
    
    # Tirer l'image depuis le registre
    docker pull "$full_image"
    
    # Déterminer le fichier Docker Compose
    local compose_file=""
    case "$GITLAB_ENVIRONMENT" in
        "development")
            compose_file="docker-compose.yml"
            ;;
        "staging")
            compose_file="docker-compose.staging.yml"
            ;;
        "production")
            compose_file="docker-compose.prod.yml"
            ;;
        *)
            log "ERROR" "Environnement non supporté: $GITLAB_ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Arrêter les services existants
    docker-compose -f "$compose_file" down --remove-orphans || true
    
    # Démarrer avec la nouvelle image
    export IMAGE_TAG="$image_tag"
    export REGISTRY_URL="$GITLAB_IMAGE"
    docker-compose -f "$compose_file" up -d
    
    # Vérifier la santé des services
    local timeout=300
    local interval=10
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if docker-compose -f "$compose_file" ps | grep -q "Up (healthy)"; then
            log "INFO" "Services déployés et en bonne santé"
            return 0
        fi
        
        log "DEBUG" "Attente de la santé des services... ($elapsed/$timeout secondes)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    log "ERROR" "Timeout atteint pour la vérification de santé"
    return 1
}

# Fonction de déploiement distant
deploy_remote() {
    local image_tag="$1"
    local full_image="${GITLAB_IMAGE}:${image_tag}"
    
    log "INFO" "Déploiement distant sur $DEPLOY_HOST avec l'image: $full_image"
    
    # Créer le script de déploiement distant
    local remote_script="/tmp/remote_deploy_${TIMESTAMP}.sh"
    cat > "$remote_script" << EOF
#!/bin/bash
set -euo pipefail

# Connexion au registre GitLab
echo "$GITLAB_TOKEN" | docker login -u gitlab-ci-token --password-stdin "$GITLAB_REGISTRY"

# Aller dans le répertoire de déploiement
cd "$DEPLOY_PATH"

# Tirer la nouvelle image
docker pull "$full_image"

# Déterminer le fichier Docker Compose
case "$GITLAB_ENVIRONMENT" in
    "development")
        COMPOSE_FILE="docker-compose.yml"
        ;;
    "staging")
        COMPOSE_FILE="docker-compose.staging.yml"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.prod.yml"
        ;;
esac

# Arrêter les services existants
docker-compose -f "\$COMPOSE_FILE" down --remove-orphans || true

# Démarrer avec la nouvelle image
export IMAGE_TAG="$image_tag"
export REGISTRY_URL="$GITLAB_IMAGE"
docker-compose -f "\$COMPOSE_FILE" up -d

# Vérifier la santé des services
timeout=300
interval=10
elapsed=0

while [ \$elapsed -lt \$timeout ]; do
    if docker-compose -f "\$COMPOSE_FILE" ps | grep -q "Up (healthy)"; then
        echo "Services déployés et en bonne santé"
        exit 0
    fi
    
    echo "Attente de la santé des services... (\$elapsed/\$timeout secondes)"
    sleep \$interval
    elapsed=\$((elapsed + interval))
done

echo "Timeout atteint pour la vérification de santé"
exit 1
EOF
    
    # Copier et exécuter le script sur le serveur distant
    scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$remote_script" "${DEPLOY_USER}@${DEPLOY_HOST}:/tmp/"
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "${DEPLOY_USER}@${DEPLOY_HOST}" "chmod +x /tmp/$(basename $remote_script) && /tmp/$(basename $remote_script)"
    
    # Nettoyer le script distant
    ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "${DEPLOY_USER}@${DEPLOY_HOST}" "rm -f /tmp/$(basename $remote_script)"
    rm -f "$remote_script"
}

# Fonction de notification Slack
send_slack_notification() {
    local status="$1"
    local message="$2"
    
    if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
        return 0
    fi
    
    local color=""
    local emoji=""
    
    case "$status" in
        "success")
            color="good"
            emoji=":white_check_mark:"
            ;;
        "failure")
            color="danger"
            emoji=":x:"
            ;;
        "warning")
            color="warning"
            emoji=":warning:"
            ;;
    esac
    
    local payload=$(cat << EOF
{
    "attachments": [
        {
            "color": "$color",
            "fields": [
                {
                    "title": "Déploiement RAG API",
                    "value": "$emoji $message",
                    "short": false
                },
                {
                    "title": "Environnement",
                    "value": "$GITLAB_ENVIRONMENT",
                    "short": true
                },
                {
                    "title": "Branche",
                    "value": "$GITLAB_BRANCH",
                    "short": true
                },
                {
                    "title": "Commit",
                    "value": "${GITLAB_COMMIT:0:8}",
                    "short": true
                }
            ]
        }
    ]
}
EOF
    )
    
    curl -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK_URL" || true
}

# Fonction de post-déploiement
post_deployment_tasks() {
    log "INFO" "Tâches post-déploiement..."
    
    # Nettoyer les images Docker non utilisées
    docker image prune -f || true
    
    # Envoyer une notification de succès
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        send_slack_notification "success" "Déploiement réussi pour $GITLAB_ENVIRONMENT"
    fi
    
    # Créer un artifact avec les logs de déploiement
    if [ -n "${CI_PROJECT_DIR:-}" ]; then
        cp "$LOG_FILE" "${CI_PROJECT_DIR}/deployment.log" || true
    fi
    
    log "INFO" "Déploiement GitLab terminé avec succès!"
}

# Fonction principale
main() {
    log "INFO" "Début du déploiement GitLab CI/CD"
    
    validate_gitlab_environment
    login_to_registry
    
    local image_tag=$(determine_image_tag)
    log "INFO" "Tag d'image déterminé: $image_tag"
    
    setup_ssh
    
    if [ -n "$DEPLOY_HOST" ]; then
        deploy_remote "$image_tag"
    else
        deploy_local "$image_tag"
    fi
    
    post_deployment_tasks
    
    log "INFO" "Script de déploiement GitLab terminé"
}

# Exécuter le script principal
main "$@"