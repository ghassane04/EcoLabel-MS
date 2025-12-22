import requests
import json

url = "http://localhost:8004/score/compute"

def test_scoring():
    print(f"Testing Scoring API at {url}...")
    
    # Input from previous LCA step ideally
    payload = {
        "product_name": "Tomato Sauce",
        "total_co2": 1.4,        # kg CO2
        "total_water": 36.5,     # L water
        "total_energy": 8.9      # MJ energy
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
    test_scoring()
