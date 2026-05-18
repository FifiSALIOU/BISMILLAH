# Guide CI/CD GitLab - RAG Ultra Performant Multimodal API

## 📋 Vue d'ensemble

Ce guide détaille la configuration complète du pipeline CI/CD GitLab pour l'API RAG Ultra Performant Multimodal. Le pipeline supporte trois environnements : développement, staging et production avec des déploiements automatisés et des vérifications de qualité.

## 🏗️ Architecture CI/CD

### Pipeline Stages

1. **Validation** - Vérification des fichiers Docker et du code
2. **Test** - Tests unitaires et d'intégration
3. **Build** - Construction des images Docker
4. **Security** - Analyse de sécurité des conteneurs
5. **Deploy** - Déploiement automatisé
6. **Cleanup** - Nettoyage des ressources

### Environnements

- **Development** : Déploiement automatique sur chaque push vers `develop`
- **Staging** : Déploiement automatique sur chaque push vers `main`
- **Production** : Déploiement manuel avec tags Git

## 🚀 Configuration initiale

### 1. Variables GitLab CI/CD

Configurez les variables suivantes dans GitLab (Settings > CI/CD > Variables) :

#### Variables de base
```bash
# Registry
CI_REGISTRY_IMAGE: registry.gitlab.com/votre-groupe/rag-api

# Déploiement
DEPLOY_HOST_DEV: dev.rag-api.com
DEPLOY_HOST_STAGING: staging.rag-api.com  
DEPLOY_HOST_PROD: rag-api.com
DEPLOY_USER: deploy
SSH_PRIVATE_KEY: [Clé SSH privée en base64]

# Base de données
REDIS_PASSWORD: [Mot de passe Redis sécurisé]
CHROMA_AUTH_TOKEN: [Token d'authentification ChromaDB]
SECRET_KEY: [Clé secrète de l'application]
JWT_SECRET: [Secret JWT]

# Production uniquement
CLICKHOUSE_USER: [Utilisateur ClickHouse]
CLICKHOUSE_PASSWORD: [Mot de passe ClickHouse]
DATABASE_URL: [URL de la base de données]
BACKUP_ENCRYPTION_KEY: [Clé de chiffrement des sauvegardes]

# Services externes
ELASTICSEARCH_URL: [URL Elasticsearch]
ELASTICSEARCH_AUTH_TOKEN: [Token Elasticsearch]
SLACK_WEBHOOK_URL: [URL webhook Slack]
EMAIL_SMTP_SERVER: [Serveur SMTP]
EMAIL_USERNAME: [Nom d'utilisateur email]
EMAIL_PASSWORD: [Mot de passe email]

# Stockage (Production)
S3_BUCKET: [Nom du bucket S3]
S3_REGION: [Région S3]
S3_ACCESS_KEY: [Clé d'accès S3]
S3_SECRET_KEY: [Clé secrète S3]
```

#### Variables de sécurité (Protected + Masked)
- `SSH_PRIVATE_KEY`
- `SECRET_KEY`
- `JWT_SECRET`
- `REDIS_PASSWORD`
- `CHROMA_AUTH_TOKEN`
- `DATABASE_URL`
- `BACKUP_ENCRYPTION_KEY`

### 2. Configuration des runners GitLab

Assurez-vous que vos runners GitLab ont :
- Docker installé et configuré
- Accès au GitLab Container Registry
- Connectivité vers vos serveurs de déploiement

### 3. Préparation des serveurs

#### Serveur de développement
```bash
# Créer l'utilisateur de déploiement
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Créer les répertoires
sudo mkdir -p /opt/rag-api/development
sudo chown -R deploy:deploy /opt/rag-api

# Configurer SSH
sudo -u deploy mkdir -p /home/deploy/.ssh
# Ajouter la clé publique correspondante à SSH_PRIVATE_KEY
```

#### Serveur de staging
```bash
# Même configuration que développement
sudo mkdir -p /opt/rag-api/staging
sudo chown -R deploy:deploy /opt/rag-api
```

#### Serveur de production
```bash
# Configuration renforcée pour la production
sudo mkdir -p /opt/rag-api/production
sudo chown -R deploy:deploy /opt/rag-api

# Configuration des volumes persistants
sudo mkdir -p /opt/rag-api/production/{data,logs,redis,chroma,prometheus,grafana}
sudo chown -R deploy:deploy /opt/rag-api/production
```

## 📁 Structure des fichiers

```
.
├── .gitlab-ci.yml                 # Configuration principale du pipeline
├── .env.ci                        # Variables pour les tests CI
├── .env.staging                   # Variables pour staging
├── .env.prod                      # Variables pour production
├── docker-compose.ci.yml          # Composition pour les tests
├── docker-compose.staging.yml     # Composition pour staging
├── docker-compose.prod.yml        # Composition pour production
├── scripts/
│   ├── deploy.sh                  # Script de déploiement générique
│   └── gitlab-deploy.sh           # Script spécifique GitLab
└── README-CICD.md                 # Ce guide
```

## 🔄 Workflow de déploiement

### Développement
1. Push vers la branche `develop`
2. Pipeline automatique : validation → tests → build → déploiement
3. Déploiement automatique sur l'environnement de développement

### Staging
1. Push vers la branche `main`
2. Pipeline automatique : validation → tests → build → sécurité → déploiement
3. Déploiement automatique sur l'environnement de staging

### Production
1. Création d'un tag Git (ex: `v1.2.3`)
2. Pipeline automatique : validation → tests → build → sécurité
3. **Déploiement manuel** requis via l'interface GitLab
4. Possibilité de rollback automatique

## 🛠️ Commandes utiles

### Déploiement manuel local
```bash
# Développement
./scripts/deploy.sh -e development -t latest

# Staging
./scripts/deploy.sh -e staging -t v1.2.3

# Production
./scripts/deploy.sh -e production -t v1.2.3 -r registry.gitlab.com/user/project
```

### Vérification des services
```bash
# Statut des conteneurs
docker-compose -f docker-compose.prod.yml ps

# Logs des services
docker-compose -f docker-compose.prod.yml logs -f rag-api

# Santé des services
curl -f http://localhost:8000/health
```

### Sauvegarde manuelle
```bash
# Exécuter une sauvegarde
./scripts/backup.sh production

# Lister les sauvegardes
ls -la /backups/
```

## 🔍 Monitoring et observabilité

### Métriques disponibles
- **Prometheus** : `http://localhost:9090`
- **Grafana** : `http://localhost:3000`
- **Logs** : Centralisés via Loki (production)

### Dashboards Grafana
- Performance de l'API
- Utilisation des ressources
- Métriques de base de données
- Alertes système

### Health checks
- API : `GET /health`
- Redis : `redis-cli ping`
- ChromaDB : `GET /api/v1/heartbeat`

## 🚨 Gestion des erreurs

### Rollback automatique
Le pipeline inclut un rollback automatique en cas d'échec du déploiement :
1. Détection d'échec du health check
2. Arrêt des nouveaux services
3. Restauration depuis la dernière sauvegarde
4. Redémarrage des services précédents

### Rollback manuel
```bash
# Via GitLab UI
# Aller dans Deployments > Environments > [Environment] > Rollback

# Via script local
./scripts/deploy.sh -e production -t previous-working-tag
```

### Debugging
```bash
# Logs détaillés du pipeline
# Disponibles dans GitLab CI/CD > Jobs

# Logs des conteneurs
docker-compose logs --tail=100 rag-api

# Connexion au conteneur
docker exec -it rag-api-production bash
```

## 🔐 Sécurité

### Bonnes pratiques implémentées
- Scan de sécurité des images avec Trivy
- Scan des secrets avec Trufflehog
- Variables sensibles masquées et protégées
- Authentification par clés SSH
- Chiffrement des sauvegardes
- HTTPS obligatoire en production

### Mise à jour des secrets
1. Mettre à jour les variables dans GitLab
2. Redéployer l'environnement concerné
3. Vérifier la connectivité des services

## 📊 Métriques de performance

### Objectifs SLA
- **Disponibilité** : 99.9%
- **Temps de réponse** : < 200ms (95e percentile)
- **Temps de déploiement** : < 10 minutes
- **Temps de rollback** : < 5 minutes

### Surveillance
- Alertes automatiques via Prometheus
- Notifications Slack en cas d'incident
- Monitoring continu des ressources

## 🆘 Support et dépannage

### Contacts
- **Équipe DevOps** : devops@rag-api.com
- **Équipe Développement** : dev@rag-api.com
- **Urgences** : +33 X XX XX XX XX

### Ressources
- [Documentation GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

### FAQ

**Q: Le déploiement échoue avec une erreur de connexion SSH**
R: Vérifiez que la variable `SSH_PRIVATE_KEY` est correctement configurée et que l'utilisateur `deploy` existe sur le serveur cible.

**Q: Les tests d'intégration échouent**
R: Vérifiez que tous les services (Redis, ChromaDB) sont démarrés et accessibles dans l'environnement CI.

**Q: Comment ajouter un nouvel environnement ?**
R: 1) Créer un nouveau fichier `.env.{env}`, 2) Ajouter un job de déploiement dans `.gitlab-ci.yml`, 3) Configurer les variables GitLab correspondantes.

---

*Ce guide est maintenu par l'équipe DevOps. Dernière mise à jour : $(date +"%Y-%m-%d")*