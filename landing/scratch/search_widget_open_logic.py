with open("c:/Users/LENOVO/Documents/Voicera/voicera-landing/src/widget.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "open" in line.lower() and idx > 480 and idx < 650:
        print(f"{idx+1}: {line.encode('ascii', 'ignore').decode('ascii').rstrip()}")
