with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="page-botconfig"' in line:
        print(f"Found page-botconfig at line {idx+1}")
        for i in range(idx, idx + 80):
            print(f"{i+1}: {lines[i].encode('ascii', 'ignore').decode('ascii').rstrip()}")
