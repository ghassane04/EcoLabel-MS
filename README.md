# 🌿 EcoLabel-MS

**Plateforme de Scoring Environnemental basée sur les Microservices et le Machine Learning**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?logo=fastapi)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)](https://xgboost.ai/)

## 📋 Description

EcoLabel-MS est une plateforme qui calcule le **score environnemental** (A-E) des produits alimentaires en analysant leur composition, emballage et transport. Elle utilise l'**Analyse du Cycle de Vie (ACV)** et le **Machine Learning** pour une classification précise.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend React (3000)                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Microservices                           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Parser   │→ │   NLP    │→ │ LCALite  │→ │ Scoring  │    │
│  │  8001    │  │  8002    │  │  8003    │  │  8004    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       ↓                            ↓            ↓          │
│  ┌──────────┐                 ┌──────────┐                 │
│  │ Widget   │                 │Provenance│                 │
│  │  8005    │                 │  8007    │                 │
│  └──────────┘                 └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│         PostgreSQL (5432)  +  MinIO (9000)                  │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Microservices

| Service | Port | Description | ML |
|---------|------|-------------|-----|
| **ParserProduit** | 8001 | Extraction données produit | - |
| **NLPIngrédients** | 8002 | Analyse sémantique ingrédients | - |
| **LCALite** | 8003 | Calcul ACV (CO₂, eau, énergie) | ✅ XGBoost Regressor |
| **Scoring** | 8004 | Classification A-E | ✅ XGBoost + Random Forest |
| **WidgetAPI** | 8005 | API d'intégration | - |
| **Provenance** | 8007 | Traçabilité et audit | - |

## 🚀 Lancement Rapide

### Prérequis
- Docker & Docker Compose
- 4 GB RAM minimum

### 1. Cloner le projet
```bash
git clone https://github.com/ghassane04/EcoLabel-MS.git
cd EcoLabel-MS
```

### 2. Configurer l'environnement
```bash
cp .env.example .env
# Modifier si nécessaire
```

### 3. Lancer tous les services
```bash
docker-compose up -d
```

### 4. Vérifier le statut
```bash
docker-compose ps
```

### 5. Accéder à l'application
- **Frontend** : http://localhost:3000
- **API Docs** : http://localhost:8004/docs (Scoring)

## 🔧 Commandes Utiles

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f scoring

# Arrêter tous les services
docker-compose down

# Reconstruire un service
docker-compose build scoring
docker-compose up -d scoring

# Accéder au conteneur
docker exec -it ecolabel-scoring bash
```

## 🤖 Machine Learning

### Modèle de Scoring (Classification A-E)

| Algorithme | Accuracy | CV Accuracy |
|------------|----------|-------------|
| Random Forest | **95%** | 93% ± 2% |
| XGBoost | 94% | 92% ± 2% |

**Dataset** : 500 échantillons équilibrés

### Modèle d'Imputation CO₂ (Régression)

| Métrique | Valeur |
|----------|--------|
| R² Score | **0.99** |
| MAE | 0.12 kg |

**Dataset** : 250 échantillons

## 📡 API Endpoints Principaux

### Scoring
```bash
# Calculer un score
curl -X POST http://localhost:8004/score/compute \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Sauce Tomate Bio",
    "total_co2": 1.25,
    "total_water": 48.5,
    "total_energy": 4.2,
    "has_bio_label": 1
  }'
```

### LCALite
```bash
# Calculer l'ACV
curl -X POST http://localhost:8003/lca/calc \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Pizza",
    "ingredients": [{"name": "tomato", "quantity_kg": 0.3}],
    "packaging": {"material": "glass", "weight_kg": 0.2},
    "transport": {"distance_km": 100, "mode": "truck"}
  }'
```

### Provenance
```bash
# Statistiques
curl http://localhost:8007/provenance/stats

# Historique
curl http://localhost:8007/provenance/history/scores
```

## 🗂️ Structure du Projet

```
EcoLabel-MS/
├── docker-compose.yml      # Orchestration Docker
├── .env                    # Variables d'environnement
├── front/                  # Frontend React
├── parser-produit/         # Microservice Parser
├── nlp-ingredients/        # Microservice NLP
├── lca-lite/              # Microservice LCA + ML
│   ├── app/ml_imputer.py  # XGBoost Regressor
│   └── data/              # Dataset CO₂
├── scoring/               # Microservice Scoring + ML
│   ├── app/ml_trainer.py  # XGBoost + Random Forest
│   └── data/              # Dataset 500 échantillons
├── widget-api/            # Microservice Widget
├── provenance/            # Microservice Provenance
└── README.md              # Ce fichier
```

## 🛠️ Technologies

| Catégorie | Technologies |
|-----------|--------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy |
| **Frontend** | React, TypeScript, Tailwind CSS |
| **ML** | Scikit-learn, XGBoost, Pandas, NumPy |
| **Database** | PostgreSQL 15, MinIO |
| **Container** | Docker, Docker Compose |
| **NLP** | Transformers (BERT), HuggingFace |

## 👥 Équipe

- **BOUGERFAOUI Ghassane**
- **BELGUERMAH Mohamed Ali**
- **EL ANANI Souhaib**
- **LABCHIRI Ahmed**

**Institution** : EMSI - École Marocaine des Sciences de l'Ingénieur

## 📄 Licence

MIT License

---

## 🔗 Liens Utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Docker Compose](https://docs.docker.com/compose/)
