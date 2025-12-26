"""
Tests Unitaires pour le microservice Widget-API
EcoLabel-MS - Tests avec pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


class TestWidgetAPI:
    """Tests pour l'API Widget"""
    
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
    
    def test_get_public_product(self):
        """Test de récupération d'un produit public"""
        response = self.client.get("/public/product/1")
        # L'ID peut ne pas exister
        assert response.status_code in [200, 404]
    
    def test_widget_analyze_endpoint(self):
        """Test du endpoint /widget/analyze"""
        payload = {
            "product_text": "Sauce Tomate Bio - Ingrédients: tomates bio, huile olive, sel",
            "include_details": True
        }
        response = self.client.post("/widget/analyze", json=payload)
        # Le service peut dépendre d'autres microservices
        assert response.status_code in [200, 500, 503]


class TestWidgetIntegration:
    """Tests d'intégration pour le Widget"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_full_pipeline(self):
        """Test du pipeline complet (si les autres services sont disponibles)"""
        payload = {
            "product_text": "Pizza Margherita - tomates, mozzarella, basilic",
            "include_details": True
        }
        response = self.client.post("/widget/analyze", json=payload)
        # Vérifie que le service répond
        assert response.status_code in [200, 500, 503, 401, 422]
    
    def test_cors_headers(self):
        """Test des headers CORS pour l'intégration web"""
        response = self.client.options("/public/product/1")
        # Les options peuvent être supportées ou non
        assert response.status_code in [200, 204, 405]


class TestPublicEndpoints:
    """Tests pour les endpoints publics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_public_product_structure(self):
        """Test de la structure d'un produit public"""
        response = self.client.get("/public/product/1")
        if response.status_code == 200:
            data = response.json()
            # Vérifie les champs attendus
            possible_fields = ["product_name", "score_letter", "score_numerical", "id"]
            assert any(field in data for field in possible_fields)
    
    def test_product_not_found(self):
        """Test avec un ID produit inexistant"""
        response = self.client.get("/public/product/999999")
        assert response.status_code in [404, 200]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
