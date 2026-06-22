with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "botconfig" in line.lower() or "bot config" in line.lower():
        if idx > 1300:
            cleaned = line.encode("ascii", "ignore").decode("ascii")
            print(f"Line {idx+1}: {cleaned.strip()[:140]}")
