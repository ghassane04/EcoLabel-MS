# 🧠 NLPIngrédients

**Service d'analyse sémantique des ingrédients**

## 🎯 Rôle
Analyse NLP des listes d'ingrédients pour identification, normalisation et classification.

## 🔧 Technologies
- Python 3.11
- FastAPI
- HuggingFace Transformers
- BERT Multilingual NER (`Davlan/bert-base-multilingual-cased-ner-hrl`)

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification santé |
| `POST` | `/nlp/extract` | Extraction des ingrédients |

## 📥 Exemple de requête

```bash
curl -X POST http://localhost:8002/nlp/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "tomates bio, huile d olive extra vierge, sel de mer, basilic frais"}'
```

## 📤 Exemple de réponse

```json
{
  "ingredients": [
    {"name": "tomates", "category": "vegetable", "is_bio": true},
    {"name": "huile d'olive", "category": "oil", "is_bio": false},
    {"name": "sel", "category": "condiment", "is_bio": false},
    {"name": "basilic", "category": "herb", "is_bio": false}
  ],
  "count": 4
}
```

## 🐳 Docker

```bash
docker-compose up -d nlp-ingredients
```

## 🗂️ Structure

```
nlp-ingredients/
├── app/
│   ├── main.py          # FastAPI app
│   ├── database.py      
│   └── models.py        
├── requirements.txt
└── Dockerfile
```
