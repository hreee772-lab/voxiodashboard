path = "c:/Users/LENOVO/Documents/Voicera/voicera-dashboard/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Locate index bounds
start_marker = "<!-- -- ANALYTICS -- -->"
end_marker = "<!-- -- SETTINGS -- -->"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + content[end_idx:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully removed analytics page block programmatically!")
else:
    print(f"Error: markers not found. Start: {start_idx}, End: {end_idx}")
