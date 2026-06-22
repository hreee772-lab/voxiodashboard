import requests
import json
import os

BASE_URL = "https://voicera-backend-production.up.railway.app/api/v1"
FILE_PATH = r"C:\Users\LENOVO\Downloads\geniffy_kb.txt"
CLIENT_ID = "70d0188f-ef36-4c79-b0b6-b215e767d859"

# ── Step 1: Login ──────────────────────────────────────────────────────────────
print("Step 1: Logging in...")
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "test@example.com", "password": "password123"},
    timeout=30
)
print(f"  Status: {login_resp.status_code}")

if login_resp.status_code != 200:
    print(f"  ERROR: Login failed!\n  Body: {login_resp.text}")
    exit(1)

login_data = login_resp.json()
access_token = login_data.get("access_token")

if not access_token:
    print(f"  ERROR: No access_token in response!\n  Body: {json.dumps(login_data, indent=2)}")
    exit(1)

print(f"  Login successful. Token: {access_token[:30]}...")
print(f"  Client ID: {CLIENT_ID}")

# ── Step 2: Upload File to knowledge base ─────────────────────────────────────
print(f"\nStep 2: Uploading {os.path.basename(FILE_PATH)} to knowledge base...")
headers = {"Authorization": f"Bearer {access_token}"}

# Determine MIME type based on extension
ext = os.path.splitext(FILE_PATH)[1].lower()
mime_type = "application/pdf" if ext == ".pdf" else "text/plain"

with open(FILE_PATH, "rb") as f:
    upload_resp = requests.post(
        f"{BASE_URL}/kb/upload",
        headers=headers,
        files={"file": (os.path.basename(FILE_PATH), f, mime_type)},
        data={"client_id": CLIENT_ID},
        timeout=120
    )

print(f"  Status: {upload_resp.status_code}")
print("\n--- Full Upload Response ---")
try:
    print(json.dumps(upload_resp.json(), indent=2))
except Exception:
    print(upload_resp.text)
