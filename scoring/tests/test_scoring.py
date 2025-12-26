"""
Tests Unitaires pour le microservice Scoring
EcoLabel-MS - Tests avec pytest
"""

import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


class TestScoringAPI:
    """Tests pour l'API Scoring"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test client"""
        from app.main import app
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test du endpoint /health"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data
    
    def test_compute_score_valid_input(self):
        """Test du calcul de score avec des entrées valides"""
        payload = {
            "product_name": "Sauce Tomate Bio",
            "total_co2": 0.5,
            "total_water": 20.0,
            "total_energy": 1.5,
            "packaging_type": "glass",
            "packaging_weight_kg": 0.1,
            "transport_km": 50,
            "has_bio_label": 1,
            "has_recyclable": 1,
            "has_local_label": 1,
            "category": "sauce"
        }
        response = self.client.post("/score/compute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "score_letter" in data
        assert data["score_letter"] in ["A", "B", "C", "D", "E"]
        assert "score_numerical" in data
        assert "confidence" in data
    
    def test_compute_score_high_impact(self):
        """Test du score pour un produit à fort impact (D ou E)"""
        payload = {
            "product_name": "Viande Boeuf Import",
            "total_co2": 12.0,
            "total_water": 700.0,
            "total_energy": 60.0,
            "packaging_type": "plastic",
            "packaging_weight_kg": 0.5,
            "transport_km": 2000,
            "has_bio_label": 0,
            "has_recyclable": 0,
            "has_local_label": 0,
            "category": "meat"
        }
        response = self.client.post("/score/compute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["score_letter"] in ["D", "E"]
    
    def test_compute_score_low_impact(self):
        """Test du score pour un produit à faible impact (A ou B)"""
        payload = {
            "product_name": "Salade Bio Locale",
            "total_co2": 0.3,
            "total_water": 15.0,
            "total_energy": 0.8,
            "packaging_type": "paper",
            "packaging_weight_kg": 0.02,
            "transport_km": 20,
            "has_bio_label": 1,
            "has_recyclable": 1,
            "has_local_label": 1,
            "category": "salad"
        }
        response = self.client.post("/score/compute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["score_letter"] in ["A", "B"]
    
    def test_compute_score_missing_fields(self):
        """Test avec des champs manquants (doit utiliser les valeurs par défaut)"""
        payload = {
            "product_name": "Produit Test",
            "total_co2": 2.0,
            "total_water": 50.0,
            "total_energy": 5.0
        }
        response = self.client.post("/score/compute", json=payload)
        assert response.status_code == 200
    
    def test_model_info_endpoint(self):
        """Test du endpoint /score/model-info"""
        response = self.client.get("/score/model-info")
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data or "message" in data


class TestMLTrainer:
    """Tests pour le module ML Trainer"""
    
    def test_load_and_prepare_data(self):
        """Test du chargement des données"""
        from app.ml_trainer import load_and_prepare_data
        X, y, label_encoder, pkg_encoder, cat_encoder, features = load_and_prepare_data()
        
        assert X is not None
        assert len(X) > 0
        assert len(y) == len(X)
        assert len(features) == 10
    
    def test_predict_function(self):
        """Test de la fonction de prédiction"""
        from app.ml_trainer import predict
        
        result = predict(
            co2_kg=1.0,
            water_l=40.0,
            energy_mj=2.5,
            packaging_type="glass",
            packaging_weight_kg=0.1,
            transport_km=100,
            has_bio_label=1,
            has_recyclable=1,
            has_local_label=0,
            category="sauce"
        )
        
        assert "grade" in result
        assert result["grade"] in ["A", "B", "C", "D", "E"]
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
        assert "probabilities" in result
    
    def test_label_encoder_classes(self):
        """Test des classes du label encoder"""
        from app.ml_trainer import load_and_prepare_data
        _, _, label_encoder, _, _, _ = load_and_prepare_data()
        
        expected_classes = ["A", "B", "C", "D", "E"]
        assert list(label_encoder.classes_) == expected_classes


class TestScoringGrades:
    """Tests pour la logique de scoring"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    @pytest.mark.parametrize("co2,expected_grades", [
        (0.3, ["A", "B"]),
        (2.0, ["B", "C"]),
        (5.0, ["C", "D"]),
        (8.0, ["D", "E"]),
        (15.0, ["E"])
    ])
    def test_score_by_co2_range(self, co2, expected_grades):
        """Test des scores par plage de CO2"""
        payload = {
            "product_name": f"Test CO2 {co2}",
            "total_co2": co2,
            "total_water": co2 * 30,
            "total_energy": co2 * 2,
            "packaging_type": "plastic",
            "transport_km": co2 * 50
        }
        response = self.client.post("/score/compute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["score_letter"] in expected_grades


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
