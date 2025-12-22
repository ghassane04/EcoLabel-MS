import requests
import json
import datetime

url = "http://localhost:8006/provenance/log"

def test_provenance():
    print(f"Testing Provenance API at {url}...")
    
    # Simulate data that would come from Scoring service after a calculation
    payload = {
        "score_id": 12345,
        "product_name": "Tomato Sauce",
        "calculation_date": datetime.datetime.now().isoformat(),
        "emissions_model_version": "v1.2",
        "dataset_hash": "a1b2c3d4e5f6",
        "parameters": {
            "w_co2": 0.5,
            "w_water": 0.25,
            "w_energy": 0.25
        }
    }
    
    try:
        # 1. Log Provenance
        print("Logging provenance...")
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success Log!")
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Failed Log:", response.status_code, response.text)

        # 2. Retrieve Provenance
        print("\nRetrieving provenance...")
        getUrl = "http://localhost:8006/provenance/12345"
        response = requests.get(getUrl)
        if response.status_code == 200:
             print("Success Retrieve!")
             print("Response:", json.dumps(response.json(), indent=2))
        else:
             print("Failed Retrieve:", response.status_code, response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_provenance()
