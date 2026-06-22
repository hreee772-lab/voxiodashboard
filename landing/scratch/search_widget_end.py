with open("c:/Users/LENOVO/Documents/Voicera/voicera-landing/src/widget.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines[-50:]):
    print(f"{len(lines)-50+idx+1}: {line.encode('ascii', 'ignore').decode('ascii').rstrip()}")
