import os
import pandas as pd
import chardet
import random
import string

# Set WeChat data storage paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # /export_parsers directory
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up to /backend directory
WECHAT_EXPORT_DIR = os.path.join(BASE_DIR, "core", "export", "wechat")
OUTPUT_DIR = os.path.join(BASE_DIR, "core", "out")

def detect_encoding(file_path):
    """Detect file encoding"""
    with open(file_path, "rb") as f:
        raw_data = f.read(100000)  # Read the first 100KB for encoding detection
    return chardet.detect(raw_data)['encoding']

class WeChatChatlogCreator:
    def __init__(self, input_csv):
        self.input_csv = input_csv
        self.out_dir = OUTPUT_DIR
        self.chatlogs_dir = os.path.join(self.out_dir, "chatlogs")
        self.info_dir = os.path.join(self.out_dir, "info")
        self.create_directories()
        self.internal_chat_id = self.generate_internal_chat_id()

    def create_directories(self):
        """Create output directories"""
        os.makedirs(self.chatlogs_dir, exist_ok=True)
        os.makedirs(self.info_dir, exist_ok=True)

    def generate_internal_chat_id(self):
        """Generate a unique internal chat ID"""
        random_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"wechat_{random_code}"

    def process_csv(self):
        """Parse WeChat exported CSV file"""
        encoding_detected = detect_encoding(self.input_csv)
        print(f"📌 Detected encoding: {encoding_detected}")

        # Read CSV file
        df = pd.read_csv(self.input_csv, encoding=encoding_detected)
        print("🔍 CSV columns:", df.columns)

        transformed_data = []
        participants = set()

        for idx, (_, row) in enumerate(df.iterrows(), start=1):
            sender = row.get("NickName", "Unknown")
            participants.add(sender)

            transformed_entry = {
                "docNo": idx,
                "time": row.get("CreateTime", ""),
                "sender": sender,
                "message": row.get("StrContent", ""),
                "isReply": False,
                "who_replied_to": None,
                "has_reactions": False,
                "reactions": "[]",
                "translated": False,
                "is_media": row.get("Type", 1) != 1,  # Type = 1 is text, others are media
                "is_OCR": False,
                "local_uri": None,
                "remote_url": None
            }
            transformed_data.append(transformed_entry)

        return transformed_data, participants

    def create_csv_files(self):
        """Create `chatlog.csv` and `info.csv` files"""
        chat_entries, participants = self.process_csv()
        if not chat_entries:
            print(f"❌ No chat records found: {self.input_csv}")
            return

        # Determine display name
        if len(participants) > 2:
            participants.discard(chat_entries[0]["sender"])
        display_name = chat_entries[0]["sender"] if len(participants) != 2 else " & ".join(sorted(participants))

        # Generate `info.csv`
        info_csv_path = os.path.join(self.info_dir, f"{self.internal_chat_id}.info.csv")
        with open(info_csv_path, "w", encoding="utf-8", newline='') as csvfile:
            fieldnames = ["Internal chat name", "Display name", "Participants"]
            writer = pd.DataFrame([{
                "Internal chat name": self.internal_chat_id,
                "Display name": display_name,
                "Participants": ", ".join(sorted(participants))
            }])
            writer.to_csv(info_csv_path, index=False)
        print(f"✅ Generated info.csv: {info_csv_path}")

        # Generate `chatlog.csv`
        chatlog_csv_path = os.path.join(self.chatlogs_dir, f"{self.internal_chat_id}.info.csv")
        df_transformed = pd.DataFrame(chat_entries)
        df_transformed.to_csv(chatlog_csv_path, index=False, encoding="utf-8-sig")
        print(f"✅ Generated chatlog.csv: {chatlog_csv_path}")

def process_all_wechat_exports():
    """Process all WeChat data"""
    if not os.path.isdir(WECHAT_EXPORT_DIR):
        print(f"❌ Error: {WECHAT_EXPORT_DIR} does not exist")
        return

    csv_files = [f for f in os.listdir(WECHAT_EXPORT_DIR) if f.endswith(".csv")]
    if not csv_files:
        print(f"⚠️ No CSV files found in: {WECHAT_EXPORT_DIR}")
        return

    for filename in csv_files:
        full_path = os.path.join(WECHAT_EXPORT_DIR, filename)
        creator = WeChatChatlogCreator(full_path)
        creator.create_csv_files()

def generate_chatlog():
    process_all_wechat_exports()
