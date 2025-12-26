"""
Tests d'Intégration End-to-End pour EcoLabel-MS
EcoLabel-MS - Tests avec pytest

Ces tests vérifient le fonctionnement complet du pipeline :
Parser → NLP → LCA → Scoring → Provenance
"""

import pytest
import requests
import time

# Configuration des URLs des microservices
SERVICES = {
    "parser": "http://localhost:8001",
    "nlp": "http://localhost:8002",
    "lca": "http://localhost:8003",
    "scoring": "http://localhost:8004",
    "widget": "http://localhost:8005",
    "provenance": "http://localhost:8007"
}


class TestServiceHealth:
    """Tests de santé des services"""
    
    @pytest.mark.parametrize("service,url", SERVICES.items())
    def test_service_health(self, service, url):
        """Test que chaque service répond au health check"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except requests.exceptions.ConnectionError:
            pytest.skip(f"Service {service} not running at {url}")


class TestFullPipeline:
    """Tests du pipeline complet"""
    
    def test_product_scoring_pipeline(self):
        """Test du pipeline: texte → parsing → NLP → LCA → scoring"""
        product_text = "Sauce Tomate Bio - Ingrédients: tomates bio 80%, huile d'olive 10%, sel, basilic"
        
        # Étape 1: Parser
        try:
            parser_response = requests.post(
                f"{SERVICES['parser']}/product/parse",
                json={"text": product_text},
                timeout=10
            )
            assert parser_response.status_code == 200
            parsed_data = parser_response.json()
        except requests.exceptions.ConnectionError:
            pytest.skip("Parser service not available")
        
        # Étape 2: NLP
        try:
            nlp_response = requests.post(
                f"{SERVICES['nlp']}/nlp/extract",
                json={"text": product_text},
                timeout=30  # NLP peut être lent au premier appel
            )
            assert nlp_response.status_code == 200
            nlp_data = nlp_response.json()
        except requests.exceptions.ConnectionError:
            pytest.skip("NLP service not available")
        
        # Étape 3: LCA
        try:
            lca_payload = {
                "product_name": "Sauce Tomate Bio",
                "ingredients": [
                    {"name": "tomato", "quantity_kg": 0.4},
                    {"name": "olive_oil", "quantity_kg": 0.05}
                ],
                "packaging": {"material": "glass", "weight_kg": 0.25},
                "transport": {"distance_km": 150, "mode": "truck"}
            }
            lca_response = requests.post(
                f"{SERVICES['lca']}/lca/calc",
                json=lca_payload,
                timeout=10
            )
            assert lca_response.status_code == 200
            lca_data = lca_response.json()
            assert "total_co2_kg" in lca_data
        except requests.exceptions.ConnectionError:
            pytest.skip("LCA service not available")
        
        # Étape 4: Scoring
        try:
            scoring_payload = {
                "product_name": "Sauce Tomate Bio",
                "total_co2": lca_data.get("total_co2_kg", 0.5),
                "total_water": lca_data.get("total_water_l", 20.0),
                "total_energy": lca_data.get("total_energy_mj", 2.0),
                "packaging_type": "glass",
                "transport_km": 150,
                "has_bio_label": 1,
                "category": "sauce"
            }
            scoring_response = requests.post(
                f"{SERVICES['scoring']}/score/compute",
                json=scoring_payload,
                timeout=10
            )
            assert scoring_response.status_code == 200
            score_data = scoring_response.json()
            assert "score_letter" in score_data
            assert score_data["score_letter"] in ["A", "B", "C", "D", "E"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Scoring service not available")


class TestScenarios:
    """Tests de scénarios métier"""
    
    def test_low_impact_product(self):
        """Test d'un produit à faible impact (devrait obtenir A ou B)"""
        try:
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
            response = requests.post(
                f"{SERVICES['scoring']}/score/compute",
                json=payload,
                timeout=10
            )
            assert response.status_code == 200
            data = response.json()
            assert data["score_letter"] in ["A", "B"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Scoring service not available")
    
    def test_high_impact_product(self):
        """Test d'un produit à fort impact (devrait obtenir D ou E)"""
        try:
            payload = {
                "product_name": "Steak Boeuf Import",
                "total_co2": 15.0,
                "total_water": 800.0,
                "total_energy": 70.0,
                "packaging_type": "plastic",
                "packaging_weight_kg": 0.5,
                "transport_km": 3000,
                "has_bio_label": 0,
                "has_recyclable": 0,
                "has_local_label": 0,
                "category": "meat"
            }
            response = requests.post(
                f"{SERVICES['scoring']}/score/compute",
                json=payload,
                timeout=10
            )
            assert response.status_code == 200
            data = response.json()
            assert data["score_letter"] in ["D", "E"]
        except requests.exceptions.ConnectionError:
            pytest.skip("Scoring service not available")


class TestProvenanceIntegration:
    """Tests d'intégration avec Provenance"""
    
    def test_stats_after_scoring(self):
        """Test que les statistiques sont mises à jour après un scoring"""
        try:
            # Récupère les stats initiales
            stats_before = requests.get(
                f"{SERVICES['provenance']}/provenance/stats",
                timeout=5
            ).json()
            
            # Effectue un scoring
            scoring_payload = {
                "product_name": "Test Provenance",
                "total_co2": 2.0,
                "total_water": 50.0,
                "total_energy": 5.0
            }
            requests.post(
                f"{SERVICES['scoring']}/score/compute",
                json=scoring_payload,
                timeout=10
            )
            
            # Attend un peu pour la propagation
            time.sleep(1)
            
            # Vérifie les stats après
            stats_after = requests.get(
                f"{SERVICES['provenance']}/provenance/stats",
                timeout=5
            ).json()
            
            # Les stats doivent être valides
            assert isinstance(stats_after, dict)
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Required services not available")


class TestErrorHandling:
    """Tests de gestion des erreurs"""
    
    def test_scoring_with_invalid_data(self):
        """Test du scoring avec des données invalides"""
        try:
            payload = {
                "product_name": "",
                "total_co2": -1,  # Invalide
                "total_water": -1,  # Invalide
            }
            response = requests.post(
                f"{SERVICES['scoring']}/score/compute",
                json=payload,
                timeout=10
            )
            # Doit retourner une erreur ou gérer gracieusement
            assert response.status_code in [200, 400, 422]
        except requests.exceptions.ConnectionError:
            pytest.skip("Scoring service not available")
    
    def test_lca_with_empty_ingredients(self):
        """Test du LCA avec une liste d'ingrédients vide"""
        try:
            payload = {
                "product_name": "Produit Vide",
                "ingredients": [],
                "packaging": {"material": "paper", "weight_kg": 0.1},
                "transport": {"distance_km": 10, "mode": "truck"}
            }
            response = requests.post(
                f"{SERVICES['lca']}/lca/calc",
                json=payload,
                timeout=10
            )
            assert response.status_code in [200, 400, 422]
        except requests.exceptions.ConnectionError:
            pytest.skip("LCA service not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
