import json
import os
import sys

DATA_DIR = "data/conversations"

def check_files():
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} does not exist.")
        return

    print(f"Checking files in {DATA_DIR}...")
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            path = os.path.join(DATA_DIR, filename)
            try:
                with open(path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: Corrupted file found: {filename} - {e}")
            except Exception as e:
                print(f"ERROR: Issue with file {filename}: {e}")

if __name__ == "__main__":
    check_files()
