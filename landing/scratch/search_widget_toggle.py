with open("c:/Users/LENOVO/Documents/Voicera/voicera-landing/src/widget.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "toggle" in line.lower() or "open" in line.lower():
        if idx > 450 and idx < 550:
            print(f"{idx+1}: {line.encode('ascii', 'ignore').decode('ascii').rstrip()}")
