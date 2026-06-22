import requests
import json

BASE_URL = "https://voicera-backend-production.up.railway.app/api/v1"

# Login to get token
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "test@example.com", "password": "password123"},
    timeout=30
)
login_data = login_resp.json()
access_token = login_data.get("access_token")
client_id = login_data.get("user", {}).get("client_id")

# Test a question that SHOULD be answerable from the chunks we saw
print("\n--- Sending chat for 'Who are Geniffy's sub-processors?' ---")
session_resp = requests.post(
    f"{BASE_URL}/sessions/start",
    json={
        "client_id": client_id,
        "user_email": "test@example.com",
        "user_name": "Test User",
        "channel": "chat"
    },
    timeout=30
)
session_id = session_resp.json().get("session_id")

r = requests.post(
    f"{BASE_URL}/chat/message",
    headers={"Authorization": f"Bearer {access_token}"},
    json={
        "session_id": session_id,
        "client_id": client_id,
        "message": "Who are Geniffy's sub-processors?",
        "conversation_history": []
    },
    timeout=60
)

print(f"Chat Status: {r.status_code}")
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    print(r.text)
