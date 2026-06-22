with open("c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

queries = ["fetch", "chart", "Overview", "Call Volume", "Peak Traffic", "Avg Handle Time", "Resolution Rate"]
for q in queries:
    print(f"\nSearching for '{q}':")
    found = 0
    for idx, line in enumerate(lines):
        if q.lower() in line.lower():
            print(f"Line {idx+1}: {line.strip()[:140]}")
            found += 1
            if found >= 15:
                print("... (truncated)")
                break
