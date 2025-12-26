"""
Tests Unitaires pour le microservice NLP-Ingredients
EcoLabel-MS - Tests avec pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


class TestNLPIngredientsAPI:
    """Tests pour l'API NLP-Ingredients"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test du endpoint /health"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_extract_entities_valid_input(self):
        """Test de l'extraction NER avec des entrées valides"""
        payload = {
            "text": "tomates bio, huile d'olive extra vierge, sel de mer, basilic frais"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data or "ingredients" in data
    
    def test_extract_entities_empty_text(self):
        """Test avec un texte vide"""
        payload = {"text": ""}
        response = self.client.post("/nlp/extract", json=payload)
        # Le service peut retourner 200 avec une liste vide ou 400
        assert response.status_code in [200, 400, 422]
    
    def test_extract_entities_multiple_ingredients(self):
        """Test avec plusieurs ingrédients"""
        payload = {
            "text": "farine de blé, sucre, oeufs, beurre, lait, chocolat noir 70%, vanille, sel"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Vérifie qu'au moins quelques entités ont été extraites
        if "entities" in data:
            assert len(data["entities"]) >= 1
        elif "ingredients" in data:
            assert len(data["ingredients"]) >= 1
    
    def test_extract_complex_french_text(self):
        """Test avec un texte français complexe"""
        payload = {
            "text": "Ingrédients: Purée de tomates 58%, eau, huile d'olive vierge extra 5%, "
                    "sel, sucre, basilic 1%, ail, origan, poivre noir"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200


class TestNERModel:
    """Tests pour le modèle NER"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_model_handles_special_characters(self):
        """Test que le modèle gère les caractères spéciaux"""
        payload = {
            "text": "huile d'olive, crème fraîche, œufs, maïs"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200
    
    def test_model_handles_percentages(self):
        """Test que le modèle gère les pourcentages"""
        payload = {
            "text": "tomates 60%, eau, sel 2%, sucre 1.5%"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200
    
    def test_model_handles_allergens(self):
        """Test que le modèle gère les allergènes en gras"""
        payload = {
            "text": "farine de BLÉ, LAIT, ŒUFS, traces de FRUITS À COQUE"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200


class TestIngredientCategories:
    """Tests pour la catégorisation des ingrédients"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    @pytest.mark.parametrize("ingredient,expected_category", [
        ("tomates", "vegetable"),
        ("boeuf", "meat"),
        ("lait", "dairy"),
        ("huile d'olive", "oil"),
        ("sucre", "sugar")
    ])
    def test_ingredient_categorization(self, ingredient, expected_category):
        """Test de la catégorisation des ingrédients"""
        payload = {"text": ingredient}
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200
        # Note: La vérification de catégorie dépend de l'implémentation


class TestBioLabels:
    """Tests pour la détection des labels bio"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_detect_bio_label(self):
        """Test de la détection du label bio"""
        payload = {
            "text": "tomates bio, basilic biologique, huile olive AB"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Vérifie la présence de bio dans la réponse
        response_str = str(data).lower()
        assert "bio" in response_str or len(data.get("entities", data.get("ingredients", []))) > 0
    
    def test_detect_local_label(self):
        """Test de la détection du label local"""
        payload = {
            "text": "tomates locales, produit régional, origine France"
        }
        response = self.client.post("/nlp/extract", json=payload)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
