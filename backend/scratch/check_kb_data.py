import requests
import json

SUPABASE_URL = "https://tvqpmkazbzkviyegbwtc.supabase.co/rest/v1"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2cXBta2F6Ynprdml5ZWdid3RjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzY0MzUyMywiZXhwIjoyMDkzMjE5NTIzfQ.-Rw-OrvIibNwiRHrtgjLh_lLvKUjFNshABhLSXfgQk4"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

def check_data():
    print("Checking for 'demo-client' or other test data...")
    
    # Check clients
    res = requests.get(f"{SUPABASE_URL}/clients?select=id,company_name", headers=headers)
    print("\n--- Clients ---")
    print(json.dumps(res.json(), indent=2))
    
    # Check documents
    res = requests.get(f"{SUPABASE_URL}/kb_documents?select=client_id,file_name", headers=headers)
    print("\n--- Documents ---")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    check_data()
