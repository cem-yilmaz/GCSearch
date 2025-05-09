import csv
import re
import os
from datetime import datetime

# input file and output file
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
input_file = os.path.join(BASE_PATH, "export", "line", "LINE__chat.txt")  # input file path
platform="line"
chatname="Chat 1"
output_file = os.path.join(BASE_PATH,  "out", "chatlogs", f"{platform}__{chatname}.chatlog.csv")  # output file path

chat_rooms_file = os.path.join(BASE_PATH,  "out", "info", f"{platform}__{chatname}.info.csv")

#input(f"We will be reading from {input_file} and writing to {output_file} and {chat_rooms_file}. Press Enter to continue.")

# line chatroom pattern：capture [LINE] chatname pattern
chat_id_pattern = re.compile(r"\[LINE\]\s+(.*)")

# date patterns
date_patterns = [
    re.compile(r"([A-Za-z]{3}), (\d{2}/\d{2}/\d{4})"),         # Format: Tue, 01/28/2025
    re.compile(r"(\d{4}/\d{1,2}/\d{1,2})（.{1,2}）"),            # Format: 2023/10/2（週一）
    re.compile(r"^\d{4}/\d{1,2}/\d{1,2}（.{1,2}）$")             # Format: 2024/04/24（三）
]

# time patterns
time_patterns = [
    re.compile(r"(\d{1,2}:\d{2}[APM]*)\t(.+?)\t(.+)"),           # Format: 11:20    sender    message
    re.compile(r"(上午|下午)(\d{1,2}):(\d{2})\t(.+?)\t(.+)")        # Format: 上午/下午 HH:MM sender message
]

# media keywords
media_keywords = ["[photo]", "[video]", "[照片]", "[影片]", "[檔案]", "[file]", "[sticker]", "[貼圖]"]
media_extensions = (".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".flac", ".pdf")

# create sender dic{}
participants_by_chat = {}

def convert_to_unix(date_str, time_str):
    """time/date transform Unix timestamp"""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y/%m/%d %H:%M")
        return int(dt.timestamp())
    except ValueError:
        return None  

def detect_media(message):
    """check is_media (boolean True/ False)"""
    if any(keyword in message for keyword in media_keywords):
        return True  
    url_pattern = re.compile(r"https?://\S+")  
    urls = url_pattern.findall(message)
    return any(url.lower().endswith(media_extensions) for url in urls)

def detect_remote_url(message):
    """ detect remote_url """
    url_pattern = re.compile(r"https?://\S+")  
    urls = url_pattern.findall(message) 
    media_urls = [url for url in urls if url.lower().endswith(media_extensions)]
    return media_urls[0] if media_urls else "FALSE"


def generate_chatlog():  
    messages = []
    current_date = None
    last_sender = None
    last_message_index = None  
    chat_counter = 0
    message_counter=0

    chat_rooms = {} 
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        
        chat_match = chat_id_pattern.match(line)
        if chat_match:
            chat_room_name = chat_match.group(1).strip()
            chat_counter += 1
            chat_rooms[chat_counter] = chat_room_name
            participants_by_chat[chat_counter] = set()
            continue

        
        is_date_line = False
        for date_pattern in date_patterns:
            date_match = date_pattern.match(line)
            if date_match:
                groups = date_match.groups()
                if groups:
                    current_date = groups[-1] if len(groups) >= 2 else groups[0]
                is_date_line = True
                break
        if is_date_line:
            continue  

        message_added = False
        skipped_line = False  # 

        for time_pattern in time_patterns:
            time_match = time_pattern.match(line)
            if time_match and current_date:
                groups = time_match.groups()
                if len(groups) == 3:
                    time_str, sender, message = groups
                else:
                    period, hour, minute, sender, message = groups
                    hour = int(hour)
                    if period == "下午" and hour != 12:
                        hour += 12
                    elif period == "上午" and hour == 12:
                        hour = 0
                    time_str = f"{hour:02}:{minute}"

                if not sender.strip():
                    skipped_line = True
                    break

                unix_time = convert_to_unix(current_date, time_str)
                unix_time *= 1000
                if unix_time is not None:
                    is_media = detect_media(message)
                    remote_url = detect_remote_url(message) 
                    local_url = ""  # 

                    # 
                    message_counter += 1
                    doc_id = message_counter

                    messages.append([
                        doc_id, unix_time, sender, message,
                        False,  # isReply
                        False,  # who_replied_to
                        False, False,  # has_reactions, reactions
                        False,  # translated
                        is_media,  # is_media
                        False,  # is_OCR
                        local_url,  # local_url
                        remote_url  # remote_url
                    ])
                    
                    last_sender = sender
                    last_message_index = len(messages) - 1
                    message_added = True
                break  

        if message_added or skipped_line:
            continue  

        if last_message_index is not None:
            messages[last_message_index][3] += " " + line

    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "docNo", "time", "sender", "message", "isReply", "who_replied_to",
            "has_reactions", "reactions", "translated", "is_media", "is_OCR", "local_url", "remote_url"
        ])
        writer.writerows(messages)

    #  CSV
    with open(chat_rooms_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["display_name", "internal_chat_name", "participants"])
        for chat_id, chat_room_name in chat_rooms.items():
            participants = ",".join(sorted(list(participants_by_chat.get(chat_id, []))))
            writer.writerow([chat_id, chat_room_name, participants])
