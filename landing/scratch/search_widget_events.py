with open("c:/Users/LENOVO/Documents/Voicera/voicera-landing/src/widget.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "attachevents" in line.lower() or "toggle" in line.lower():
        print(f"Found on line {idx+1}")
        for i in range(idx, idx + 40):
            print(f"{i+1}: {lines[i].encode('ascii', 'ignore').decode('ascii').rstrip()}")
        break
