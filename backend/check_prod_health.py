import requests

URL = "https://voicera-backend-production.up.railway.app/health"

try:
    response = requests.get(URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
