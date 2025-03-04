import os
import re
import csv
import random
import string
import unicodedata
from datetime import datetime

# Adjust these paths to match the folder structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # /export_parsers directory
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up to /backend directory
WHATSAPP_EXPORT_DIR = os.path.join(BASE_DIR, "core", "export", "whatsapp")
OUTPUT_DIR = os.path.join(BASE_DIR, "core", "out")

def remove_format_chars(text: str) -> str:
    # Remove zero-width or invisible format characters ([LTR] or [RTL] type)
    # This is a Whatsapp specific issue where some characters are not visible but affect the text layout
    # leading to incorrect parsing of the messages
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")

class WhatsappChatlogCreator:
    def __init__(self, export_file):
        self.export_file = export_file
        # Adjust output directories
        self.out_dir = OUTPUT_DIR
        self.chatlogs_dir = os.path.join(self.out_dir, "chatlogs")
        self.info_dir = os.path.join(self.out_dir, "info")
        self.create_directories()
        self.internal_chat_id = self.generate_internal_chat_id()

    def create_directories(self):
        os.makedirs(self.chatlogs_dir, exist_ok=True)
        os.makedirs(self.info_dir, exist_ok=True)

    def generate_internal_chat_id(self):
        # Generate a random internal chat ID for CSV creation.
        # Format: whatsapp_{9 random lowercase letters/digits}
        # Just an arbitrary one I picked
        random_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"{random_code}"

    def parse_line(self, line):
        pattern = r"^(?:\[[A-Z]+\])?\[(\d{2}/\d{2}/\d{4}),\s(\d{2}:\d{2}:\d{2})\]\s(~?[^:]+):\s(.*)$"
        match = re.match(pattern, line)
        if match:
            date_str, time_str, sender, message = match.groups()
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                unix_time = int(dt.timestamp())  # Convert to Unix timestamp
            except ValueError:
                unix_time = 0  # Handle invalid timestamps

            return {"datetime": unix_time, "sender": sender.strip(), "message": message}
        return None

    def process_export(self):
        chat_entries = []
        with open(self.export_file, encoding="utf-8") as f:
            for line in f:
                # Strip trailing whitespace
                line = line.strip()

                # Remove zero-width or invisible format characters via the first function
                line = remove_format_chars(line)

                # Skip empty lines
                if not line:
                    continue

                parsed = self.parse_line(line)
                if parsed:
                    chat_entries.append(parsed)
                else:
                    # Append to the previous message if it's a multi-line continuation
                    if chat_entries:
                        chat_entries[-1]["message"] += "\n" + line
        return chat_entries

    def create_csv_files(self):
        # Creates two CSV files: info_{internal_chat_id}.csv and chatlog_{internal_chat_id}.csv
        # under the 'out/info' and 'out/chatlogs' directories respectively
        chat_entries = self.process_export()
        if not chat_entries:
            # If no entries were parsed, skip file
            return

        # Build the set of participants from the chat entries
        participants = set(entry["sender"] for entry in chat_entries if entry["sender"])

        # This is used to determine the display name for group chats
        # since when Whatsapp exports a group chat, the first parsed
        # sender is the group name, not a participant
        if len(participants) > 2:
            participants.discard(chat_entries[0]["sender"])

        # Determine display name based on the number of participants
        # If it's a group chat, use the group name as the display name (same logic as above)
        # If it's a 1 on 1 chat, use "(participant1name) & (participant2name)"
        if len(participants) == 2:
            display_name = " & ".join(sorted(participants))
        else:
            display_name = chat_entries[0]["sender"]

        # Write the info CSV
        info_csv_path = os.path.join(self.info_dir, f"whatsapp__{self.internal_chat_id}.info.csv")
        with open(info_csv_path, "w", encoding="utf-8", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Internal chat name", "Display name", "Participants"])
            writer.writeheader()
            writer.writerow({
                "Internal chat name": self.internal_chat_id,
                "Display name": display_name,
                "Participants": ", ".join(sorted(participants))
            })

        # Write the chatlog CSV
        chatlog_csv_path = os.path.join(self.chatlogs_dir, f"whatsapp__{self.internal_chat_id}.chatlog.csv")
        with open(chatlog_csv_path, "w", encoding="utf-8", newline='') as csvfile:
            fields = [
                "docNo", "time", "sender", "message", "isReply",
                "who_replied_to", "has_reactions", "translated",
                "is_media", "is_OCR", "local_url", "remote_url"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            docNum = 1

            for entry in chat_entries:
                message_lower = entry["message"].lower()
                is_media = ("video omitted" in message_lower) or ("image omitted" in message_lower) \
                           or ("<attached:" in message_lower)

                writer.writerow({
                    "docNo": docNum,
                    "time": int(entry["datetime"]) if isinstance(entry["datetime"], (int, float)) else "",
                    "sender": entry["sender"],
                    "message": entry["message"],
                    "isReply": False,
                    "who_replied_to": False,
                    "has_reactions": False,
                    "translated": False,
                    "is_media": is_media,
                    "is_OCR": False,
                    "local_url": None,   # Placeholder
                    "remote_url": None   # Placeholder
                })
                docNum += 1

        print(f"Created CSV files for {self.export_file} with internal chat ID {self.internal_chat_id}")

def process_all_whatsapp_exports():
    # Looks for all text files in WHATSAPP_EXPORT_DIR and creates CSV files for each
    if not os.path.isdir(WHATSAPP_EXPORT_DIR):
        print(f"Error: {WHATSAPP_EXPORT_DIR} does not exist or is not a directory.")
        return # Error for a non-existent directory

    txt_files = [f for f in os.listdir(WHATSAPP_EXPORT_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"No .txt files found in {WHATSAPP_EXPORT_DIR}.")
        return # Error if no text files are found

    for filename in txt_files:
        full_path = os.path.join(WHATSAPP_EXPORT_DIR, filename)
        creator = WhatsappChatlogCreator(full_path)
        creator.create_csv_files()

def generate_chatlog():
    process_all_whatsapp_exports()
