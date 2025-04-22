import os
import json

with open("create_structure.json") as f:
    structure = json.load(f)

for folder, files in structure.items():
    if folder == "root_files":
        for file in files:
            open(file, "w").close()
    else:
        os.makedirs(folder, exist_ok=True)
        for file in files:
            open(os.path.join(folder, file), "w").close()
