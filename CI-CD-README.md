# 🔧 Configuration CI/CD - EcoLabel-MS

## 📋 Vue d'ensemble

Ce projet utilise **SonarQube** pour l'analyse de qualité et **Jenkins** pour l'intégration continue.

## 🚀 Démarrage Rapide

### 1. Lancer SonarQube et Jenkins

```bash
docker-compose -f docker-compose.ci.yml up -d
```

### 2. Accéder aux interfaces

| Service | URL | Credentials par défaut |
|---------|-----|----------------------|
| **SonarQube** | http://localhost:9000 | admin / admin |
| **Jenkins** | http://localhost:8080 | (voir logs) |

### 3. Récupérer le mot de passe Jenkins initial

```bash
docker exec ecolabel-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 📊 SonarQube

### Configuration du projet

Le fichier `sonar-project.properties` configure :
- Sources Python des 6 microservices
- Tests unitaires
- Exclusions (node_modules, __pycache__)
- Rapports de couverture

### Lancer une analyse

```bash
# Avec Docker
docker-compose -f docker-compose.ci.yml run sonar-scanner

# Ou avec sonar-scanner installé localement
sonar-scanner -Dsonar.login=<TOKEN>
```

### Générer les rapports de couverture

```bash
cd scoring
pytest tests/ --cov=app --cov-report=xml:coverage.xml
```

---

## 🔄 Jenkins Pipeline

### Stages du Pipeline

1. **Checkout** : Clone le repository
2. **Build** : Construit les images Docker
3. **Unit Tests** : Exécute les tests en parallèle
4. **SonarQube Analysis** : Analyse de qualité
5. **Quality Gate** : Vérifie les critères qualité
6. **Integration Tests** : Tests end-to-end
7. **Deploy** : Déploiement (branche main uniquement)

### Configurer le pipeline

1. Créer un nouveau Job "Pipeline"
2. Sélectionner "Pipeline script from SCM"
3. Configurer le repo Git
4. Le fichier `Jenkinsfile` sera détecté automatiquement

---

## 🔑 Variables d'environnement

### Jenkins

| Variable | Description |
|----------|-------------|
| `DOCKER_COMPOSE_VERSION` | Version de Docker Compose |
| `SONAR_HOST_URL` | URL du serveur SonarQube |
| `SONAR_PROJECT_KEY` | Clé du projet SonarQube |

### GitHub Actions

| Secret | Description |
|--------|-------------|
| `SONAR_TOKEN` | Token d'authentification SonarQube |
| `SONAR_HOST_URL` | URL du serveur SonarQube |

---

## 📁 Structure des fichiers CI/CD

```
EcoLabel-MS/
├── Jenkinsfile              # Pipeline Jenkins
├── sonar-project.properties # Config SonarQube
├── docker-compose.ci.yml    # Services CI/CD
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions
└── requirements-test.txt    # Dépendances tests
```

---

## ✅ Quality Gates (SonarQube)

| Métrique | Seuil |
|----------|-------|
| Bugs | 0 |
| Vulnérabilités | 0 |
| Code Smells | < 10 |
| Couverture | > 35% |
| Duplication | < 3% |

---

## 🛠️ Commandes utiles

```bash
# Démarrer les services CI
docker-compose -f docker-compose.ci.yml up -d

# Voir les logs
docker-compose -f docker-compose.ci.yml logs -f

# Arrêter les services
docker-compose -f docker-compose.ci.yml down

# Lancer tous les tests
pytest --cov=. --cov-report=xml
```
