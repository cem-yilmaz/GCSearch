# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 02:01:34 2025

@author: Layla
"""

import os
import json

BASE_PATH = "/GCSearch"

def getChatDataFromDocIDGivenPIIName(doc_id: int, pii_name: str) -> dict:
    """
    Retrieves chat data for a given doc_id.

    Returns data in the following format:
    {
        "doc_id": 0,
        "time": 1234567890,
        "sender": "Alice",
        "message": "Hello, world!",
        "reactions": ["Alice: ❤️", "Bob: 😂"],
        "is_OCR": False,
        "is_media": False,
        "uri": "https://example.com/image.jpg"
    }

    Args:
        doc_id (int): The document ID of the chat.
        pii_name (str): Name of the positional inverted index 
                        (file name will be `{pii_name}.pii.txt`).

    Returns:
        dict: Chat data. If `doc_id` is not found, returns `{}`.
    """
    # Construct the PII file path
    pii_file = os.path.join(BASE_PATH, "backend", "core", "piis", f"{pii_name}.pii.txt")

    # Return an error if the PII file does not exist
    if not os.path.exists(pii_file):
        return {"error": "PII file not found"}

    # Read the file line by line
    with open(pii_file, "r", encoding="utf-8") as file:
        for line in file:
            try:
                # Parse JSON data
                chat = json.loads(line.strip())
                
                # Check if the current chat matches the given doc_id
                if chat.get("doc_id") == doc_id:
                    return {
                        "doc_id": doc_id,
                        "time": chat.get("time", 0),
                        "sender": chat.get("sender", "Unknown"),
                        "message": "" if chat.get("is_media", False) else chat.get("message", ""),
                        "reactions": chat.get("reactions", []),
                        "is_OCR": chat.get("is_OCR", False),
                        "is_media": chat.get("is_media", False),
                        "uri": chat.get("uri", "") if chat.get("is_media", False) else ""
                    }
            except json.JSONDecodeError:
                continue  # Skip malformed JSON lines

    # Return an empty dictionary if no matching doc_id is found
    return {}
