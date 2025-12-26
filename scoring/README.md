# 📊 Scoring ML

**Service de classification environnementale avec Machine Learning**

## 🎯 Rôle
Attribution d'un score environnemental A-E aux produits en utilisant XGBoost et Random Forest.

## 🔧 Technologies
- Python 3.11
- FastAPI
- **XGBoost** (Classification)
- **Scikit-learn** (Random Forest)
- Pandas, NumPy
- Joblib

## 🤖 Machine Learning

### Modèles de Classification

| Modèle | Accuracy | CV Accuracy |
|--------|----------|-------------|
| **Random Forest** | 95% | 93% ± 2% |
| **XGBoost** | 94% | 92% ± 2% |

### Dataset
- **Taille** : 500 échantillons
- **Distribution** : 100 par grade (A, B, C, D, E)
- **Features** : 10 variables

### Features utilisées
1. `co2_kg` - Émissions CO₂
2. `water_l` - Consommation eau
3. `energy_mj` - Énergie
4. `packaging_weight_kg` - Poids emballage
5. `transport_km` - Distance transport
6. `has_bio_label` - Label bio
7. `has_recyclable` - Recyclable
8. `has_local_label` - Local
9. `packaging_type` - Type emballage
10. `category` - Catégorie produit

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification santé + modèle |
| `POST` | `/score/compute` | Calcul du score |
| `GET` | `/score/model-info` | Métriques ML |
| `POST` | `/score/train` | Réentraîner le modèle |

## 📥 Exemple de requête

```bash
curl -X POST http://localhost:8004/score/compute \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Sauce Tomate Bio",
    "total_co2": 1.25,
    "total_water": 48.5,
    "total_energy": 4.2,
    "packaging_type": "glass",
    "transport_km": 200,
    "has_bio_label": 1
  }'
```

## 📤 Exemple de réponse

```json
{
  "product_name": "Sauce Tomate Bio",
  "score_numerical": 85.5,
  "score_letter": "A",
  "confidence_level": 0.92,
  "model_used": "RandomForest",
  "probabilities": {
    "A": 0.92, "B": 0.05, "C": 0.02, "D": 0.01, "E": 0.00
  }
}
```

## 🐳 Docker

```bash
docker-compose up -d scoring
```

## 🗂️ Structure

```
scoring/
├── app/
│   ├── main.py          # FastAPI app
│   ├── ml_trainer.py    # 🤖 XGBoost + Random Forest
│   ├── database.py      
│   └── models.py        
├── data/
│   └── training_dataset.csv  # 500 échantillons
├── models/
│   ├── scoring_model.pkl     # Modèle sauvegardé
│   └── training_metrics.json # Métriques
├── requirements.txt
└── Dockerfile
```

## 📈 Génération Matrice de Confusion

```bash
python generate_confusion_matrix.py
```

Génère : `confusion_matrix.png`, `confusion_matrix_normalized.png`
