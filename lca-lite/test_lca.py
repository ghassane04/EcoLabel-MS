import requests
import json

url = "http://localhost:8003/lca/calc"

def test_lca():
    print(f"Testing LCA API at {url}...")
    
    payload = {
        "product_name": "Tomato Sauce",
        "ingredients": [
            {"name": "tomato", "quantity_kg": 0.5},
            {"name": "sugar", "quantity_kg": 0.05}
        ],
        "packaging": {
            "material": "glass",
            "weight_kg": 0.3
        },
        "transport": {
            "distance_km": 150,
            "mode": "truck"
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success!")
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Failed:", response.status_code, response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_lca()
