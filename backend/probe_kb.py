import requests, json

BASE_URL = "https://voicera-backend-production.up.railway.app/api/v1"
login = requests.post(f"{BASE_URL}/auth/login", json={"email": "test@example.com", "password": "password123"}, timeout=30)
token = login.json()["access_token"]
client_id = login.json()["user"]["client_id"]

session = requests.post(f"{BASE_URL}/sessions/start", json={"client_id": client_id, "user_email": "test@example.com", "user_name": "Test", "channel": "chat"}, timeout=15)
session_id = session.json()["session_id"]

questions = [
    "Tell me about Geniffy",
    "What services does Geniffy offer?",
    "What is Geniffy?",
]

for q in questions:
    r = requests.post(
        f"{BASE_URL}/chat/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_id": session_id, "client_id": client_id, "message": q, "conversation_history": []},
        timeout=30
    )
    data = r.json()
    print(f"Q: {q}")
    print(f"Chunks: {data.get('chunks_found')} | Confident: {data.get('confident')}")
    print(f"A: {data.get('response', '')[:400]}")
    print("-" * 60)
