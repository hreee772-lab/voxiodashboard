with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "kpi-card" in line.lower() or "page-" in line.lower() or "knowledgebase" in line.lower():
        if idx > 1200 and idx < 1500:
            print(f"Line {idx+1}: {line.strip()[:140]}")
