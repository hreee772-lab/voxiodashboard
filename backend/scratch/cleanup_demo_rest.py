import requests
import json

SUPABASE_URL = "https://tvqpmkazbzkviyegbwtc.supabase.co/rest/v1"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2cXBta2F6Ynprdml5ZWdid3RjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzY0MzUyMywiZXhwIjoyMDkzMjE5NTIzfQ.-Rw-OrvIibNwiRHrtgjLh_lLvKUjFNshABhLSXfgQk4"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

def cleanup():
    print("Cleaning up 'demo-client' data via Supabase REST API...")
    
    # Delete chunks
    res1 = requests.delete(
        f"{SUPABASE_URL}/kb_chunks?client_id=eq.demo-client",
        headers=headers
    )
    print(f"  Delete chunks status: {res1.status_code}")
    
    # Delete documents
    res2 = requests.delete(
        f"{SUPABASE_URL}/kb_documents?client_id=eq.demo-client",
        headers=headers
    )
    print(f"  Delete documents status: {res2.status_code}")
    
    print("Done.")

if __name__ == "__main__":
    cleanup()
