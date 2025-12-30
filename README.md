<h1 align="center">🌿 EcoLabel-MS</h1>

<p align="center">
  <strong>Plateforme de Scoring Environnemental basée sur les Microservices et le Machine Learning</strong>
  <br/>
  <em>Architecture Microservices avec ACV et Intelligence Artificielle</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-teal?logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/XGBoost-ML-orange" alt="XGBoost"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql" alt="PostgreSQL"/>
</p>

<p align="center">
  <a href="#-fonctionnalités">Fonctionnalités</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-utilisation">Utilisation</a> •
  <a href="#-api">API</a> •
  <a href="#-équipe">Équipe</a>
</p>

<p align="center">
  📅 <strong>Dernière mise à jour :</strong> 30 Décembre 2024
</p>

---

## 🎬 Démo Vidéo

<p align="center">
  <a href="https://youtu.be/9TMHXgLH9ig">
    <img src="https://img.youtube.com/vi/9TMHXgLH9ig/maxresdefault.jpg" alt="Démo EcoLabel-MS" width="600"/>
  </a>
</p>

> 🎥 **Cliquez sur l'image** pour voir la démonstration complète sur YouTube.

---

## 📋 À propos

**EcoLabel-MS** est une plateforme intelligente de scoring environnemental conçue pour évaluer l'impact écologique des produits alimentaires. Elle combine l'**Analyse du Cycle de Vie (ACV)**, le **Machine Learning** et une architecture **Microservices** pour fournir un score environnemental simple (A-E) à partir de données complexes.

---

## 🎯 Objectifs

✅ Calculer automatiquement un **score environnemental A-E** pour tout produit alimentaire  
✅ Extraire les données produits via **OCR et NLP** (images, PDF, textes)  
✅ Utiliser le **Machine Learning** pour l'imputation des données manquantes  
✅ Fournir une **traçabilité complète** des calculs (audit)  
✅ Offrir une **API publique** pour l'intégration e-commerce  

---

## ✨ Fonctionnalités

| Module | Description | Technologie |
|--------|-------------|-------------|
| 📄 **ParserProduit** | Extraction OCR et parsing de données produits | Python / FastAPI / Tesseract |
| 🧠 **NLPIngrédients** | Analyse sémantique des ingrédients via NER | Python / Transformers (BERT) |
| 🌍 **LCALite** | Calcul ACV simplifié (CO₂, eau, énergie) | Python / XGBoost Regressor |
| 📊 **Scoring** | Classification environnementale A-E | Python / XGBoost + Random Forest |
| 🔌 **WidgetAPI** | API publique pour intégration | Python / FastAPI |
| 📋 **Provenance** | Traçabilité et audit des calculs | Python / FastAPI |
| 🖥️ **Frontend** | Interface utilisateur moderne | React 18 / TypeScript / Tailwind |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND REACT (3000)                        │
│                   Interface Utilisateur Moderne                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MICROSERVICES                             │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│  Parser  │   NLP    │ LCALite  │ Scoring  │  Widget  │Provenance│
│  :8001   │  :8002   │  :8003   │  :8004   │  :8005   │  :8007   │
│  OCR +   │  BERT    │ XGBoost  │ XGBoost  │   API    │  Audit   │
│ Parsing  │   NER    │Regressor │Classifier│ Publique │   Logs   │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
     │          │          │          │          │          │
     └──────────┴──────────┼──────────┴──────────┴──────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  PostgreSQL  │   │    MinIO     │   │   ML Models  │
│    :5432     │   │    :9000     │   │   (XGBoost)  │
│   Database   │   │   Storage    │   │ RF Classifier│
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 📦 Microservices

| Service | Port | Langage | Framework | ML |
|---------|------|---------|-----------|-----|
| **ParserProduit** | 8001 | Python | FastAPI | - |
| **NLPIngrédients** | 8002 | Python | FastAPI + Transformers | BERT NER |
| **LCALite** | 8003 | Python | FastAPI + Pandas | ✅ XGBoost Regressor |
| **Scoring** | 8004 | Python | FastAPI + Scikit-learn | ✅ XGBoost + Random Forest |
| **WidgetAPI** | 8005 | Python | FastAPI | - |
| **Provenance** | 8007 | Python | FastAPI + SQLAlchemy | - |
| **Frontend** | 3000 | TypeScript | React 18 + Tailwind | - |

---

## 🚀 Installation

### Prérequis

- **Docker 24+** et **Docker Compose 2+**
- **4 GB RAM** minimum (8 GB recommandé)
- **Ports disponibles** : 3000, 5432, 8001-8007, 9000

### Étapes d'installation

#### 1. Cloner le dépôt
```bash
git clone https://github.com/ghassane04/EcoLabel-MS.git
cd EcoLabel-MS
```

#### 2. Configurer l'environnement
```bash
cp .env.example .env
# Modifier .env selon vos besoins
```

#### 3. Lancer tous les services
```bash
docker-compose up -d
```

#### 4. Vérifier le statut
```bash
docker-compose ps
```

#### 5. Accéder à l'application

| Service | URL |
|---------|-----|
| 🌐 **Interface Web** | http://localhost:3000 |
| 📡 **API Scoring** | http://localhost:8004/docs |
| 📊 **API LCA** | http://localhost:8003/docs |
| 🗄️ **MinIO Console** | http://localhost:9001 |

---

## 💻 Utilisation

### Interface Web

| Page | Description |
|------|-------------|
| **Dashboard** | Vue d'ensemble des statistiques |
| **ParserProduit** | Upload et parsing de documents |
| **NLPIngrédients** | Analyse des ingrédients |
| **LCALite** | Calcul d'impact environnemental |
| **Scoring** | Génération du score A-E |
| **Provenance** | Historique et traçabilité |

### Exemple de Scoring

**Entrée :**
```json
{
  "product_name": "Sauce Tomate Bio",
  "total_co2": 0.5,
  "total_water": 20.0,
  "total_energy": 1.5,
  "has_bio_label": 1,
  "packaging_type": "glass"
}
```

**Sortie :**
```json
{
  "product_name": "Sauce Tomate Bio",
  "score_letter": "A",
  "score_numerical": 92.5,
  "confidence": 0.95,
  "model_used": "RandomForest"
}
```

---

## 📡 API

### Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/product/parse` | Parser un produit (OCR/texte) |
| `POST` | `/nlp/extract` | Extraire les entités NLP |
| `POST` | `/lca/calc` | Calculer l'ACV |
| `POST` | `/score/compute` | Calculer le score A-E |
| `GET` | `/provenance/stats` | Statistiques globales |
| `GET` | `/health` | Health check |

### Exemple d'appel API

```bash
curl -X POST http://localhost:8004/score/compute \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Pizza Margherita",
    "total_co2": 2.5,
    "total_water": 80,
    "total_energy": 5.0,
    "packaging_type": "cardboard",
    "transport_km": 200
  }'
```

---

## 🤖 Machine Learning

### Modèle de Classification (Score A-E)

| Algorithme | Accuracy | CV Accuracy | F1-Score |
|------------|----------|-------------|----------|
| **Random Forest** | **100%** | 97.5% ± 5% | 1.00 |
| **XGBoost** | 100% | 95% ± 6% | 1.00 |
| Logistic Regression | 90% | 70% ± 10% | 0.89 |

**Dataset :** 464 échantillons équilibrés (A-E)

### Modèle de Régression CO₂

| Métrique | Valeur |
|----------|--------|
| **R² Score** | 0.998 |
| **MAE** | 0.089 kg CO₂ |
| **RMSE** | 0.14 kg CO₂ |

**Dataset :** 241 échantillons

### Feature Importance

| Feature | Importance |
|---------|------------|
| `energy_mj` | 22.5% |
| `transport_km` | 20.0% |
| `co2_kg` | 19.6% |
| `water_l` | 19.3% |
| `packaging_weight_kg` | 7.4% |

---

## 🧪 Tests

### Lancer les tests

```bash
# Tests unitaires Python
cd scoring
pytest tests/ -v --cov=app

# Tests d'intégration
pytest tests/test_integration.py -v

# Tests de performance (JMeter)
jmeter -n -t jmeter/ecolabel-load-test.jmx -l results.jtl

# Tous les tests
pytest --cov=. --cov-report=html
```

### Couverture de Code

| Composant | Couverture |
|-----------|------------|
| Backend Python | 35% |
| Frontend React | 10% |
| **Objectif** | 80% |

---

## 📁 Structure du Projet

```
EcoLabel-MS/
├── 📂 parser-produit/         # Microservice Parser (OCR)
├── 📂 nlp-ingredients/        # Microservice NLP (BERT NER)
├── 📂 lca-lite/               # Microservice ACV (XGBoost)
│   ├── app/ml_imputer.py      # 🤖 XGBoost Regressor
│   └── data/co2_training.csv  # Dataset CO₂
├── 📂 scoring/                # Microservice Scoring (ML)
│   ├── app/ml_trainer.py      # 🤖 XGBoost + Random Forest
│   └── data/training_dataset.csv
├── 📂 widget-api/             # API publique
├── 📂 provenance/             # Traçabilité et audit
├── 📂 front/                  # Frontend React
├── 📂 tests/                  # Tests d'intégration
├── 📂 jmeter/                 # Tests de performance
├── 📂 docs/                   # Documentation
├── 📂 .github/workflows/      # CI/CD GitHub Actions
├── 📄 docker-compose.yml      # Orchestration Docker
├── 📄 docker-compose.ci.yml   # SonarQube + Jenkins
├── 📄 Jenkinsfile             # Pipeline CI/CD
├── 📄 sonar-project.properties
└── 📄 README.md
```

---

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `POSTGRES_DB` | Nom de la base de données | `ecolabel` |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `ecolabel_user` |
| `POSTGRES_PASSWORD` | Mot de passe | `ecolabel_pass` |
| `MINIO_ROOT_USER` | Utilisateur MinIO | `minioadmin` |
| `MINIO_ROOT_PASSWORD` | Mot de passe MinIO | `minioadmin` |

---

## 🔄 CI/CD

### Pipeline Jenkins (8 Stages)

| Stage | Description |
|-------|-------------|
| 1. Checkout | Clone du repository |
| 2. Build | Construction des images Docker |
| 3. Unit Tests | Tests unitaires (parallèle) |
| 4. SonarQube | Analyse qualité du code |
| 5. Quality Gate | Vérification des critères |
| 6. Integration Tests | Tests end-to-end |
| 7. JMeter | Tests de performance |
| 8. Deploy | Déploiement (branche main) |

### GitHub Actions

| Workflow | Déclencheur | Actions |
|----------|-------------|---------|
| `ci-cd.yml` | Push main/develop | Build, tests, SonarQube |

---

## 📊 Métriques de Performance

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| Temps de réponse moyen | < 500ms | ✅ 200ms |
| Throughput | > 50 req/s | ✅ 80 req/s |
| Taux d'erreur | < 1% | ✅ 0% |
| Disponibilité | > 99% | ✅ 99.5% |

---

## 🛡️ Qualité du Code (SonarQube)

| Métrique | Backend | Frontend |
|----------|---------|----------|
| Quality Gate | ✅ Passé | ✅ Passé |
| Fiabilité | A (0 bugs) | A (0 bugs) |
| Sécurité | A (0 vulnérabilités) | A |
| Maintenabilité | A | A |
| Duplication | 1.5% | 2.0% |

---

## 📈 Dataset

### Scoring Dataset

| Attribut | Valeur |
|----------|--------|
| Nombre d'échantillons | 464 |
| Features | 10 |
| Classes | 5 (A, B, C, D, E) |
| Distribution | Équilibrée |

### CO₂ Training Dataset

| Attribut | Valeur |
|----------|--------|
| Nombre d'échantillons | 241 |
| Features | 8 |
| Plage CO₂ | 0.18 - 10.25 kg |

---

## ⚠️ Limites & Perspectives

### Limites Actuelles

| Limite | Impact | Amélioration |
|--------|--------|--------------|
| Dataset synthétique | 100% accuracy non réaliste | Collecte de données réelles |
| OCR basique | Qualité variable | Améliorer preprocessing |
| NER généraliste | Détection imparfaite | Fine-tuning sur corpus alimentaire |

### Perspectives d'Évolution

**Court terme (3-6 mois)**
- 📈 Enrichissement du dataset avec données réelles
- 🔧 Fine-tuning du modèle NER
- 📱 Application mobile

**Moyen terme (6-12 mois)**
- ☸️ Orchestration Kubernetes
- 🌐 Support multilingue
- 🔗 Intégration API Open Food Facts

**Long terme (1-2 ans)**
- 🏭 Extension au secteur textile/cosmétique
- 🇪🇺 Certification affichage environnemental (ADEME)
- 📊 Dashboard analytics avancé

---

## 👥 Équipe

<table>
  <tr>
    <td align="center"><strong>BOUGERFAOUI Ghassane</strong></td>
    <td align="center"><strong>BELGUERMAH Mohamed Ali</strong></td>
    <td align="center"><strong>LABCHIRI Ahmed</strong></td>
    <td align="center"><strong>EL ANANI Souhaib</strong></td>
  </tr>
</table>

**🏫 École Marocaine des Sciences de l'Ingénieur (EMSI)**  
📆 Année académique **2024-2025**

---

## 🔗 Liens Utiles

- 📖 [Documentation FastAPI](https://fastapi.tiangolo.com/)
- 🤖 [XGBoost Documentation](https://xgboost.readthedocs.io/)
- 🐳 [Docker Compose](https://docs.docker.com/compose/)
- 🌿 [AGRIBALYSE Database](https://agribalyse.ademe.fr/)
- 🏷️ [Affichage Environnemental (ADEME)](https://affichage-environnemental.ademe.fr/)

---

## 📝 Licence

Ce projet est développé dans un cadre académique.  
**MIT License** - Tous droits réservés © 2024

---

<p align="center">
  <strong>🌿 EcoLabel-MS - Pour une consommation responsable 🌍</strong>
</p>
