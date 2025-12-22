import requests
import json

url = "http://localhost:8002/nlp/extract"

def test_nlp():
    print(f"Testing NLP API at {url}...")
    
    text = "Produced by Nestle in France using organic tomatoes."
    payload = {"text": text}
    
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
    test_nlp()
