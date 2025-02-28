import os
import csv
from flask import request, jsonify

"""
Note: The metadata file should be named in the format <platform>__<chatname>.info.csv (with two underscores between <platform> and <chatname>). 
This CSV file must contain the following columns exactly as specified:
    - internal_chat_name
    - display_name
    - participants
"""
def GetMetaChatDataFromPIIName(pii_name):
    # Extract just the filename from the given absolute path.
    filename = os.path.basename(pii_name)
    if not filename.endswith(".pii.pkl"):
        return {}
    
    # remove the extension and split on "__"
    base_name = filename.replace(".pii.pkl", "")  # e.g., "<platform>__<chatname>"
    parts = base_name.split("__")
    if len(parts) < 2:
        return {}
    
    platform = parts[0]
    chatname = parts[1]  # We'll use this for matching the metadata row.
    
    # construct the metadata file path using double underscores.
    BASEPATH="/backend/core/out/info/"
    metadata_file = os.path.join(BASEPATH, f"{platform}__{chatname}.info.csv")
    
    if not os.path.exists(metadata_file):
        return {}
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Use the exact header names from the CSV file.
            internal_chat = row.get("internal_chat_name", "").strip()
            display = row.get("display_name", "").strip()
            participants_str = row.get("participants", "").strip()
            participants = [p.strip() for p in participants_str.split(",")] if participants_str else []
            
            # Only return the row where the internal_chat matches the extracted chatname.
            if internal_chat.lower() == chatname.lower():
                return {
                    "Internal Chat Name": internal_chat,
                    "Display Name": display,
                    "Participants": participants
                }
    return {}

# flask endpoint
def flask_GetMetaChatDataFromPIIName():
    data = request.get_json()
    pii_name = data.get("pii_name", "")
    metadata = GetMetaChatDataFromPIIName(pii_name)
    return jsonify(metadata)



