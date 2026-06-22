with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
start_idx = 0
for idx, line in enumerate(lines):
    if "function loadOverview" in line:
        start_idx = idx
        found = True
        break

if found:
    print(f"Found loadOverview function starting at line {start_idx+1}")
    for i in range(start_idx, start_idx + 120):
        if i < len(lines):
            print(f"{i+1}: {lines[i].rstrip()}")
else:
    print("loadOverview function not found with exact signature 'function loadOverview'")
