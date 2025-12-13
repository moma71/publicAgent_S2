import glob
import os
import re

files = glob.glob(r'src/Ep*_Story.md')

# Sort naturally (Ep1, Ep2, ..., Ep10)
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

files.sort(key=natural_sort_key)

for f in files:
    try:
        with open(f, encoding='utf-8') as file:
            first_line = file.readline().strip()
            # Extract clean title: "# Episode 1: Title" -> "Title"
            # Or "# Ep 1: Title"
            print(f"{os.path.basename(f)}: {first_line}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
