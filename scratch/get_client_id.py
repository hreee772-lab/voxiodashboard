import requests

URL = "https://tvqpmkazbzkviyegbwtc.supabase.co/rest/v1/clients?select=id&company_name=eq.Test Corp"
HEADERS = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2cXBta2F6Ynprdml5ZWdid3RjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzY0MzUyMywiZXhwIjoyMDkzMjE5NTIzfQ.-Rw-OrvIibNwiRHrtgjLh_lLvKUjFNshABhLSXfgQk4",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2cXBta2F6Ynprdml5ZWdid3RjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzY0MzUyMywiZXhwIjoyMDkzMjE5NTIzfQ.-Rw-OrvIibNwiRHrtgjLh_lLvKUjFNshABhLSXfgQk4"
}

res = requests.get(URL, headers=HEADERS)
print(res.json())
