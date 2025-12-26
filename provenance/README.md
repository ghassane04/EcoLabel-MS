# 📋 Provenance

**Service de traçabilité et d'audit**

## 🎯 Rôle
Assurer la traçabilité des calculs, historique des scores, et audit pour reproductibilité.

## 🔧 Technologies
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification santé |
| `GET` | `/provenance/{id}` | Audit par ID score |
| `GET` | `/provenance/search/{name}` | Recherche par nom |
| `GET` | `/provenance/history/scores` | Historique scores |
| `GET` | `/provenance/history/lca` | Historique LCA |
| `GET` | `/provenance/stats` | Statistiques globales |

## 📥 Exemple de requête

```bash
# Audit par ID
curl http://localhost:8007/provenance/1

# Recherche par nom
curl http://localhost:8007/provenance/search/pizza

# Statistiques
curl http://localhost:8007/provenance/stats
```

## 📤 Exemple de réponse (Stats)

```json
{
  "scores": {"count": 25, "avg_score": 65.3},
  "score_distribution": {"A": 5, "B": 8, "C": 7, "D": 4, "E": 1},
  "lca": {"count": 20, "avg_co2": 3.5},
  "products_parsed": 30,
  "emission_factors": 35
}
```

## 🐳 Docker

```bash
docker-compose up -d provenance
```

## 🗂️ Structure

```
provenance/
├── app/
│   ├── main.py          # FastAPI app + requêtes DB
│   └── ...
├── requirements.txt
└── Dockerfile
```
