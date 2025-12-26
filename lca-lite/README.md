# 🌍 LCALite

**Service de calcul d'Analyse du Cycle de Vie (ACV)**

## 🎯 Rôle
Calcul de l'impact environnemental (CO₂, eau, énergie) des produits avec imputation ML pour les données manquantes.

## 🔧 Technologies
- Python 3.11
- FastAPI
- Pandas
- **XGBoost** (Régression CO₂)
- Scikit-learn
- SQLAlchemy
- MinIO (stockage rapports)

## 🤖 Machine Learning

### XGBoost Regressor (Imputation CO₂)
- **But** : Estimer les émissions CO₂ quand l'ingrédient est inconnu
- **Dataset** : 250 échantillons
- **Performance** : R² = 0.99, MAE = 0.12 kg

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification santé |
| `POST` | `/lca/calc` | Calcul ACV complet |
| `GET` | `/lca/model-info` | Infos modèle ML |
| `POST` | `/lca/train-imputer` | Réentraîner le modèle |

## 📥 Exemple de requête

```bash
curl -X POST http://localhost:8003/lca/calc \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Sauce Tomate Bio",
    "ingredients": [
      {"name": "tomates_bio_italiennes", "quantity_kg": 0.5},
      {"name": "basilic_frais", "quantity_kg": 0.02}
    ],
    "packaging": {"material": "glass", "weight_kg": 0.3},
    "transport": {"distance_km": 200, "mode": "truck"}
  }'
```

## 📤 Exemple de réponse

```json
{
  "product_name": "Sauce Tomate Bio",
  "total_co2_kg": 1.25,
  "total_water_l": 48.5,
  "total_energy_mj": 4.2,
  "ml_imputation_used": false,
  "breakdown": {...}
}
```

## 🐳 Docker

```bash
docker-compose up -d lca-lite
```

## 🗂️ Structure

```
lca-lite/
├── app/
│   ├── main.py          # FastAPI app
│   ├── ml_imputer.py    # 🤖 XGBoost Regressor
│   ├── database.py      
│   └── models.py        
├── data/
│   ├── co2_training.csv # Dataset entraînement
│   └── co2_imputer.pkl  # Modèle sauvegardé
├── requirements.txt
└── Dockerfile
```
