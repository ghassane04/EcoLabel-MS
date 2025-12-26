# 📄 ParserProduit

**Service d'extraction de données produit**

## 🎯 Rôle
Extraction des données structurées à partir de textes bruts, images ou fichiers PDF de produits alimentaires.

## 🔧 Technologies
- Python 3.11
- FastAPI
- BeautifulSoup4
- Tesseract OCR
- SQLAlchemy

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification santé du service |
| `POST` | `/product/parse` | Parse un texte/fichier produit |

## 📥 Exemple de requête

```bash
curl -X POST http://localhost:8001/product/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Pizza Margherita - Ingrédients: tomates, fromage, basilic"}'
```

## 📤 Exemple de réponse

```json
{
  "product_name": "Pizza Margherita",
  "ingredients": ["tomates", "fromage", "basilic"],
  "packaging": null,
  "brand": null
}
```

## 🐳 Docker

```bash
docker-compose up -d parser-produit
```

## 🗂️ Structure

```
parser-produit/
├── app/
│   ├── main.py          # FastAPI app
│   ├── database.py      # Connexion DB
│   └── models.py        # Modèles SQLAlchemy
├── requirements.txt
└── Dockerfile
```
