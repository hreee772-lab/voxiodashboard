import requests
import json

BASE_URL = "https://voicera-backend-production.up.railway.app/api/v1"
FILE_PATH = "Geniffy_Clean.txt"

print("Step 1: Logging in...")
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "test@example.com", "password": "password123"},
    timeout=30
)

if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.text}")
    exit(1)

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("\nStep 2: Uploading Cleaned KB...")
with open(FILE_PATH, "rb") as f:
    upload_resp = requests.post(
        f"{BASE_URL}/kb/upload",
        headers=headers,
        files={"file": ("Geniffy_Clean.txt", f, "text/plain")},
        timeout=120
    )

print(f"Status: {upload_resp.status_code}")
print(upload_resp.text)
