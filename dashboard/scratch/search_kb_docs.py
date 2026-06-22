with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
start_idx = 0
for idx, line in enumerate(lines):
    if "function loadKBDocuments" in line:
        start_idx = idx
        found = True
        break

if found:
    print(f"Found loadKBDocuments function starting at line {start_idx+1}")
    for i in range(start_idx, start_idx + 100):
        if i < len(lines):
            print(f"{i+1}: {lines[i].rstrip()}")
else:
    print("loadKBDocuments function not found")
