"""
Tests Unitaires pour le microservice LCA-Lite
EcoLabel-MS - Tests avec pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


class TestLCALiteAPI:
    """Tests pour l'API LCA-Lite"""
    
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
    
    def test_lca_calc_valid_input(self):
        """Test du calcul ACV avec des entrées valides"""
        payload = {
            "product_name": "Sauce Tomate Bio",
            "ingredients": [
                {"name": "tomato", "quantity_kg": 0.5},
                {"name": "olive_oil", "quantity_kg": 0.05}
            ],
            "packaging": {"material": "glass", "weight_kg": 0.3},
            "transport": {"distance_km": 200, "mode": "truck"}
        }
        response = self.client.post("/lca/calc", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "total_co2_kg" in data
        assert "total_water_l" in data
        assert "total_energy_mj" in data
        assert data["total_co2_kg"] >= 0
    
    def test_lca_calc_empty_ingredients(self):
        """Test avec une liste d'ingrédients vide"""
        payload = {
            "product_name": "Produit Vide",
            "ingredients": [],
            "packaging": {"material": "plastic", "weight_kg": 0.1},
            "transport": {"distance_km": 100, "mode": "truck"}
        }
        response = self.client.post("/lca/calc", json=payload)
        assert response.status_code == 200
    
    def test_lca_calc_unknown_ingredient(self):
        """Test avec un ingrédient inconnu (doit utiliser l'imputation ML)"""
        payload = {
            "product_name": "Produit Inconnu",
            "ingredients": [
                {"name": "ingredient_totalement_inconnu_xyz123", "quantity_kg": 0.5}
            ],
            "packaging": {"material": "cardboard", "weight_kg": 0.1},
            "transport": {"distance_km": 50, "mode": "truck"}
        }
        response = self.client.post("/lca/calc", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "ml_imputation_used" in data or "total_co2_kg" in data
    
    def test_model_info_endpoint(self):
        """Test du endpoint /lca/model-info"""
        response = self.client.get("/lca/model-info")
        assert response.status_code == 200


class TestEmissionFactors:
    """Tests pour les facteurs d'émission"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_known_ingredients_have_factors(self):
        """Test que les ingrédients connus ont des facteurs d'émission"""
        known_ingredients = ["beef", "chicken", "tomato", "milk", "wheat"]
        
        for ingredient in known_ingredients:
            payload = {
                "product_name": f"Test {ingredient}",
                "ingredients": [{"name": ingredient, "quantity_kg": 1.0}],
                "packaging": {"material": "paper", "weight_kg": 0.05},
                "transport": {"distance_km": 10, "mode": "truck"}
            }
            response = self.client.post("/lca/calc", json=payload)
            assert response.status_code == 200
    
    def test_beef_has_high_impact(self):
        """Test que le boeuf a un impact élevé"""
        payload = {
            "product_name": "Test Boeuf",
            "ingredients": [{"name": "beef", "quantity_kg": 1.0}],
            "packaging": {"material": "plastic", "weight_kg": 0.1},
            "transport": {"distance_km": 100, "mode": "truck"}
        }
        response = self.client.post("/lca/calc", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Le boeuf a généralement un impact > 10 kg CO2/kg
        assert data["total_co2_kg"] > 5


class TestMLImputer:
    """Tests pour le module d'imputation ML"""
    
    def test_estimate_co2_function(self):
        """Test de la fonction d'estimation CO2"""
        try:
            from app.ml_imputer import estimate_co2
            
            # Test avec des caractéristiques typiques
            result = estimate_co2(
                category="vegetable",
                quantity_kg=1.0,
                is_organic=True,
                transport_distance=100
            )
            
            assert result >= 0
        except ImportError:
            pytest.skip("ml_imputer module not available")
    
    def test_load_co2_model(self):
        """Test du chargement du modèle CO2"""
        try:
            from app.ml_imputer import load_co2_model
            model = load_co2_model()
            assert model is not None
        except (ImportError, FileNotFoundError):
            pytest.skip("Model not available")


class TestPackagingImpact:
    """Tests pour l'impact de l'emballage"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    @pytest.mark.parametrize("material,expected_impact", [
        ("paper", "low"),
        ("cardboard", "low"),
        ("glass", "medium"),
        ("plastic", "high"),
        ("aluminum", "high")
    ])
    def test_packaging_material_impact(self, material, expected_impact):
        """Test de l'impact par type d'emballage"""
        payload = {
            "product_name": f"Test {material}",
            "ingredients": [{"name": "tomato", "quantity_kg": 0.1}],
            "packaging": {"material": material, "weight_kg": 0.5},
            "transport": {"distance_km": 50, "mode": "truck"}
        }
        response = self.client.post("/lca/calc", json=payload)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
