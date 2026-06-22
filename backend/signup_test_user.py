import requests
import json

URL = "https://voicera-backend-production.up.railway.app/api/v1/auth/signup"

signup_data = {
    "company_name": "Test Corp",
    "company_email": "test@example.com",
    "password": "password123",
    "domain": "testcorp.com"
}

try:
    print(f"Attempting signup for {signup_data['company_email']}...")
    response = requests.post(URL, json=signup_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
