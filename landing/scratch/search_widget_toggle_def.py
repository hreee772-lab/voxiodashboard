with open("c:/Users/LENOVO/Documents/Voicera/voicera-landing/src/widget.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "class VoiceraWidget" in line or "function VoiceraWidget" in line:
        found = True
        print(f"Found VoiceraWidget constructor at line {idx+1}")
        for i in range(idx + 235, idx + 270):
            if i < len(lines):
                print(f"{i+1}: {lines[i].encode('ascii', 'ignore').decode('ascii').rstrip()}")
        break
