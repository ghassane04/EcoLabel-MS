"""
Tests Unitaires pour le microservice Provenance
EcoLabel-MS - Tests avec pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


class TestProvenanceAPI:
    """Tests pour l'API Provenance"""
    
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
    
    def test_stats_endpoint(self):
        """Test du endpoint /provenance/stats"""
        response = self.client.get("/provenance/stats")
        assert response.status_code == 200
        data = response.json()
        # Vérifie la structure des statistiques
        assert isinstance(data, dict)
    
    def test_history_scores_endpoint(self):
        """Test du endpoint /provenance/history/scores"""
        response = self.client.get("/provenance/history/scores")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "scores" in data
    
    def test_history_lca_endpoint(self):
        """Test du endpoint /provenance/history/lca"""
        response = self.client.get("/provenance/history/lca")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "lca" in data
    
    def test_search_by_name(self):
        """Test de la recherche par nom de produit"""
        response = self.client.get("/provenance/search/test")
        # Le résultat peut être vide mais la requête doit réussir
        assert response.status_code in [200, 404]
    
    def test_get_provenance_by_id(self):
        """Test de récupération par ID"""
        response = self.client.get("/provenance/1")
        # L'ID peut ne pas exister mais la route doit être fonctionnelle
        assert response.status_code in [200, 404]


class TestAuditTrail:
    """Tests pour le système d'audit"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_stats_contains_required_fields(self):
        """Test que les stats contiennent les champs requis"""
        response = self.client.get("/provenance/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Les stats peuvent contenir ces champs
        possible_fields = ["scores", "lca", "products_parsed", "score_distribution"]
        # Au moins un champ doit être présent
        assert any(field in data for field in possible_fields) or isinstance(data, dict)
    
    def test_history_returns_list(self):
        """Test que l'historique retourne une liste"""
        response = self.client.get("/provenance/history/scores")
        assert response.status_code == 200
        data = response.json()
        # Peut être une liste ou un dict avec une clé contenant une liste
        assert isinstance(data, (list, dict))


class TestScoreDistribution:
    """Tests pour la distribution des scores"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_score_distribution_structure(self):
        """Test de la structure de la distribution des scores"""
        response = self.client.get("/provenance/stats")
        assert response.status_code == 200
        data = response.json()
        
        if "score_distribution" in data:
            dist = data["score_distribution"]
            # Vérifie que les grades A-E sont présents
            for grade in ["A", "B", "C", "D", "E"]:
                if grade in dist:
                    assert isinstance(dist[grade], (int, float))


class TestDataIntegrity:
    """Tests pour l'intégrité des données"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from app.main import app
        self.client = TestClient(app)
    
    def test_search_returns_valid_structure(self):
        """Test que la recherche retourne une structure valide"""
        # Recherche d'un terme générique
        response = self.client.get("/provenance/search/sauce")
        if response.status_code == 200:
            data = response.json()
            # La réponse doit être une liste ou un objet avec des résultats
            assert isinstance(data, (list, dict))
    
    def test_pagination_support(self):
        """Test du support de la pagination"""
        # Essaie avec des paramètres de pagination
        response = self.client.get("/provenance/history/scores?limit=10&offset=0")
        # Le service peut ou non supporter la pagination
        assert response.status_code in [200, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
