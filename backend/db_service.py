import json
import os

def save_results(data, filename="results.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_results(filename="results.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None
