with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "api reference" in line.lower() or "quick start" in line.lower() or "mcp guides" in line.lower():
        print(f"Line {idx+1}: {line.strip()[:140]}")
