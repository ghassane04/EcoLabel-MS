"""
Tests Unitaires pour le microservice Parser-Produit
EcoLabel-MS - Tests avec pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


class TestParserProduitAPI:
    """Tests pour l'API Parser-Produit"""
    
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
    
    def test_parse_text_valid_input(self):
        """Test du parsing avec un texte valide"""
        payload = {
            "text": "Pizza Margherita - Ingrédients: tomates, fromage mozzarella, basilic, huile d'olive"
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "product_name" in data or "ingredients" in data
    
    def test_parse_text_with_brand(self):
        """Test du parsing avec marque"""
        payload = {
            "text": "Sauce Tomate Bio - Marque Carrefour - 500g - Ingrédients: tomates bio 95%, sel, sucre"
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "product_name" in data or "parsed" in data
    
    def test_parse_empty_text(self):
        """Test avec un texte vide"""
        payload = {"text": ""}
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code in [200, 400, 422]
    
    def test_parse_complex_product_label(self):
        """Test avec une étiquette produit complexe"""
        payload = {
            "text": """
            Yaourt Nature Bio
            Marque: Danone
            Poids net: 125g x 4
            
            INGRÉDIENTS: Lait entier* 96%, ferments lactiques.
            *Issus de l'agriculture biologique
            
            Valeurs nutritionnelles pour 100g:
            - Énergie: 65 kcal
            - Matières grasses: 3.5g
            - Glucides: 4.0g
            - Protéines: 4.2g
            
            À conserver entre 2°C et 6°C
            Fabriqué en France
            """
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200


class TestOCRParsing:
    """Tests pour le parsing OCR"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_parse_handles_ocr_errors(self):
        """Test que le parser gère les erreurs OCR courantes"""
        payload = {
            "text": "Sauce T0mate Bi0 - Ingr3dients: tomat3s, hu1le d'oliv3"
        }
        response = self.client.post("/product/parse", json=payload)
        # Le parser doit accepter le texte même avec des erreurs OCR
        assert response.status_code == 200
    
    def test_parse_handles_mixed_case(self):
        """Test avec majuscules/minuscules mélangées"""
        payload = {
            "text": "SAUCE TOMATE BIO - ingrédients: TOMATES, Huile D'OLIVE, Sel"
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200


class TestProductExtraction:
    """Tests pour l'extraction des informations produit"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_extract_product_name(self):
        """Test de l'extraction du nom du produit"""
        payload = {
            "text": "Biscuits au Chocolat Noir - Prince de LU - 300g"
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200
        data = response.json()
        if "product_name" in data:
            assert len(data["product_name"]) > 0
    
    def test_extract_ingredients_list(self):
        """Test de l'extraction de la liste d'ingrédients"""
        payload = {
            "text": "Ingrédients: farine de blé, sucre, huile de palme, cacao maigre 4%, sel"
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200
        data = response.json()
        if "ingredients" in data:
            assert isinstance(data["ingredients"], list)
    
    def test_extract_packaging_info(self):
        """Test de l'extraction des infos d'emballage"""
        payload = {
            "text": "Conditionné sous atmosphère protectrice. Emballage recyclable. Pot en verre 350g."
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200


class TestDatabaseOperations:
    """Tests pour les opérations de base de données"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_parse_and_save(self):
        """Test du parsing avec sauvegarde en BDD"""
        payload = {
            "text": "Confiture de Fraises Bio - 350g - Ingrédients: fraises bio 60%, sucre bio, pectine"
        }
        response = self.client.post("/product/parse", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Vérifie qu'un ID est retourné (indiquant une sauvegarde)
        if "id" in data:
            assert data["id"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
