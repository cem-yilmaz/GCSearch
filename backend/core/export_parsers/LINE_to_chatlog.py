import csv
import re
import os
from datetime import datetime

# input file and output file
input_file = "text/[LINE] TNXㄉ땡스們□的聊天記錄.txt"  # input file
output_file = "chatlog_latestneeeew1.csv"  # output file path

#  the format of the input file
chat_id_pattern = re.compile(r"\[LINE\] Chat (\d+)")  # [LINE] Chat n

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

# 媒體關鍵字
media_keywords = ["[photo]", "[video]", "[照片]", "[影片]", "[檔案]", "[file]", "[sticker]", "[貼圖]"]

# save the messages
messages = []
current_doc_id = None
current_date = None
last_sender = None
last_message_index = None  

def convert_to_unix(date_str, time_str):
    """time/date transform Unix timestamp"""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y/%m/%d %H:%M")
        return int(dt.timestamp())
    except ValueError:
        return None  

def detect_media(message):
    """check is_media (boolean True/ False)"""
    return any(keyword in message for keyword in media_keywords)

with open(input_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

for line in lines:
    line = line.strip()
    if not line:
        continue

    chat_match = chat_id_pattern.match(line)
    if chat_match:
        chat_number = chat_match.group(1)
        current_doc_id = f"doc_{chat_number}"
        continue

    # check date_line
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
        continue  # if date then skip

    message_added = False
    skipped_line = False  # if no sender then skip
    for time_pattern in time_patterns:
        time_match = time_pattern.match(line)
        if time_match and current_date and current_doc_id:
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
            
            # if no sender then skip
            if not sender.strip():
                skipped_line = True
                break

            unix_time = convert_to_unix(current_date, time_str)
            if unix_time is not None:
                is_media = detect_media(message)
                messages.append([
                    current_doc_id, unix_time, sender, message,
                    False,  # isReply (default False)
                    False,  # who_replied_to
                    False, False,  # has_reactions, reactions
                    False,  # translated (default False)
                    is_media,  # is_media
                    False  # is_OCR (default False)
                ])
                last_sender = sender
                last_message_index = len(messages) - 1
                message_added = True
            break  
    if message_added or skipped_line:
        continue  
    
    if last_message_index is not None:
        messages[last_message_index][3] += " " + line

# writing into csv file
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # col name
    writer.writerow([
        "doc_id", "unix_time", "sender", "message", "isReply", "who_replied_to",
        "has_reactions", "reactions", "translated", "is_media", "is_OCR"
    ])
    writer.writerows(messages)

print(f"LINE to csv completed")
