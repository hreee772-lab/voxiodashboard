import os
import pypdf
import re
import requests
import json

PDF_PATH = r"C:\Users\LENOVO\Downloads\Geniffy info.pdf"
BASE_URL = "https://voicera-backend-production.up.railway.app/api/v1"
CLEAN_TXT = "Geniffy_Clean.txt"

def clean_and_upload():
    print(f"Step 1: Reading and cleaning PDF from {PDF_PATH}...")
    reader = pypdf.PdfReader(PDF_PATH)
    text = " ".join(page.extract_text() for page in reader.pages)
    
    # Normalize whitespace: replace any sequence of whitespace (newlines, tabs, multiple spaces) with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    with open(CLEAN_TXT, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"  Cleaned text length: {len(text)} characters.")
    print(f"  Saved to {CLEAN_TXT}")

    print("\nStep 2: Logging in to production...")
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "test@example.com", "password": "password123"},
        timeout=30
    )
    if login_resp.status_code != 200:
        print(f"  ERROR: Login failed! {login_resp.text}")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\nStep 3: Uploading Cleaned KB...")
    with open(CLEAN_TXT, "rb") as f:
        upload_resp = requests.post(
            f"{BASE_URL}/kb/upload",
            headers=headers,
            files={"file": (CLEAN_TXT, f, "text/plain")},
            timeout=120
        )

    print(f"  Status: {upload_resp.status_code}")
    print(f"  Response: {upload_resp.text}")

if __name__ == "__main__":
    clean_and_upload()
