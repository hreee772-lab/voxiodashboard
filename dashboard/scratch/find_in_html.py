with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

queries = ["onboarding-overlay", "onboard-company-name", "saveOnboarding", "onboard-"]
for q in queries:
    print(f"\nSearching for '{q}':")
    found = 0
    for idx, line in enumerate(lines):
        if q in line:
            print(f"Line {idx+1}: {line.strip()[:120]}")
            found += 1
            if found >= 15:
                print("... (truncated)")
                break
