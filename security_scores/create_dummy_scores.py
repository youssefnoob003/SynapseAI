import os
import json
import random
from glob import glob

def generate_scores(month_index):
    """Generate dummy scores that vary over time."""
    base_cyber_awareness = 50 + month_index * 2
    base_trustability = 60 + month_index * 1.5
    return {
        "cyber_awareness": min(100, max(0, base_cyber_awareness + random.randint(-5, 5))),
        "trustability": min(100, max(0, base_trustability + random.randint(-3, 3)))
    }

def update_json_files(directory):
    """Update all *monthly_collaboration.json files with dummy scores."""
    # If directory is a file, process it directly
    if os.path.isfile(directory) and directory.endswith('monthly_collaboration.json'):
        json_files = [directory]
    else:
        json_files = glob(os.path.join(directory, "*monthly_collaboration.json"))
    print(f"Found files: {json_files}")  # Debug print
    for file_path in json_files:
        with open(file_path, 'r') as file:
            data = json.load(file)
        # For dict-of-lists structure: each key is a month, value is a list of records
        for month_index, (month, records) in enumerate(data.items()):
            for record in records:
                scores = generate_scores(month_index)
                record["cyber_awareness"] = scores["cyber_awareness"]
                record["trustability"] = scores["trustability"]
                record["s_base"] = scores["cyber_awareness"] * 0.5 + scores["trustability"] * 0.5
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Updated {file_path}")

# Use the absolute path to the file since it's in the workspace root
directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'numpy_numpy_monthly_collaboration.json'))
update_json_files(directory_path)