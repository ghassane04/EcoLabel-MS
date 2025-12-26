# 🔌 WidgetAPI

**API d'intégration pour applications tierces**

## 🎯 Rôle
Fournir un endpoint unique qui orchestre tout le pipeline : Parser → NLP → LCA → Scoring.

## 🔧 Technologies
- Python 3.11
- FastAPI

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification santé |
| `GET` | `/public/product/{id}` | Récupérer un produit scoré |
| `POST` | `/widget/analyze` | Analyse complète d'un produit |

## 📥 Exemple de requête

```bash
curl http://localhost:8005/public/product/1
```

## 🐳 Docker

```bash
docker-compose up -d widget-api
```

## 🗂️ Structure

```
widget-api/
├── app/
│   ├── main.py          # FastAPI app
│   └── ...
├── requirements.txt
└── Dockerfile
```
