with open("c:/Users/LENOVO/Documents/Voicera/voicera-landing/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "widget" in line.lower() or "voice" in line.lower() or "iframe" in line.lower():
        print(f"Line {idx+1}: {line.strip()[:140]}")
