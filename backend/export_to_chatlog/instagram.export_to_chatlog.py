import os
import zipfile
import json
import logging
import csv

logging.basicConfig(level=logging.DEBUG)

def log(msg : str, level : int = logging.DEBUG):
    logging.log(level, msg)

# debug variables
zipped_files_dir = 'OG_Zips'
dir_containing_messages = 'the_one_with_the_messages_in_them'
## shorthands
d1 = zipped_files_dir
d2 = dir_containing_messages

path_from_correct_zip_to_messages = "/your_instagram_activity/messages/inbox"

d3 = d2 + path_from_correct_zip_to_messages

root_output_dir = 'out'
info_output_dir = f'{root_output_dir}/info/'
chatlogs_output_dir = f'{root_output_dir}/chatlogs/'

def zips_in_dir(path : str) -> list[str]:
    """
    Gets all the zip files in a directory
    """
    return [name for name in os.listdir(path) if name.endswith('.zip')]

def subdirs(path : str) -> list[str]:
    """
    Gets all the subdirectories in a directory
    """
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

def decode_special_characters(content : str) -> str:
    """
    Removes the weird byte-encoding of non-ASCII characters from the content
    """
    return content.encode('latin1').decode('utf-8')

# todo: remove default d2 here
def num_chats(dir_with_messages : str=d2) -> int:
    """
    Gets the number of chats in a directory
    """
    return len(subdirs(dir_with_messages + path_from_correct_zip_to_messages))

def get_info_about_chat(chat_name:str, chat_dir:str) -> tuple[str, str, list[str]]:
    """
    Gets the internal name, the display name of the chat and the participants in the chat
    """
    internal_chat_name = chat_name
    with open(os.path.join(chat_dir, chat_name, 'message_1.json'), 'r') as f:
        # the display name of the chat can be found under the title key in message_1.json
        parsed_file = json.load(f)
        display_name = decode_special_characters(parsed_file['title'])
        participants = [decode_special_characters(p['name']) for p in parsed_file['participants']]
        f.close()
    return (internal_chat_name, display_name, participants)

def get_info_about_all_chats(chat_dir:str=d3) -> list[tuple[str, str, list[str]]]:
    """
    Gets the internal name, the display name of the chat and the participants in all chats. Returns a tuple of the form:
    ``` 
    (
        internal_chat_name : str, 
        display_name : str, 
        participants : [
            participant_1 : str,
            participant_2 : str,
            ...
        ]
    )
    ```
    """
    return [get_info_about_chat(chat, chat_dir) for chat in subdirs(chat_dir)]

def pretty_print_chat_info(chat_info : tuple[str, str, list[str]]) -> None:
    """
    Pretty prints the chat info
    """
    internal_chat_name, display_name, participants = chat_info
    log(f"Internal chat name: {internal_chat_name}")
    log(f"Display name: {display_name}")
    log("Participants:")
    for participant in participants:
        log(f"\t{participant}")

def create_info_file_for_chat(chat_name:str, chat_dir:str=d3) -> None:
    """
    Creates an `info.csv` file for a chat
    """
    internal_chat_name, display_name, participants = get_info_about_chat(chat_name, chat_dir)
    with open(os.path.join(info_output_dir, f'{internal_chat_name}.info.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Internal chat name', 'Display name', 'Participants'])
        writer.writerow([internal_chat_name, display_name, '['+', '.join(participants)+']'])
        f.close()

def create_info_files_for_all_chats(chat_dir:str=d3) -> None:
    """
    Creates `info.csv` files for all chats
    """
    for chat in subdirs(chat_dir):
        create_info_file_for_chat(chat, chat_dir)

def create_chatlog_file_for_chat(chat_name:str, chat_dir:str=d3, prefer_local_media:bool=False) -> None:
    """
    Creates a `chatlog.csv` file for a chat. The csv has the following format:

    **All items in bold must have a value**

    **`docNo`** - document number (possible generated at runtime)

    **`time`** - [UNIX timestamp](https://en.wikipedia.org/wiki/Unix_time) of the message

    **`sender`** - the *name* of the sender

    **`message`** - the message content. if non-text (e.g. photo) please mention this in some way (e.g. "*Photo*"). Refer below for OCR information

    **`isReply`** - boolean, defaults to `False` if the message is not a reply

    `who_replied_to` - the `docNo` that the message is a reply to.

    **`has_reactions`** - boolean, defaults to `False` if the message has no reactions attatched

    `reactions` - an array of reactions in the format `[user: {reaction}, user: {reaction}, ...]`

    **`translated`** - boolean, defaults to `False` if the message has not been translated into another language

    **`is_media`** - boolean, defaults to `False` if the message is just text

    **`is_OCR`** - booleandefaults to `False` if the message has been OCR'd (and the `message` field is the result of this OCR'ing)

    `local_uri` - the local filepath to the image (if available)

    `remote_url` - the url to the media stored on the server

    Args:
        chat_name (str): the internal name of the chat
        chat_dir (str, optional): the directory containing the chat. Defaults to d3.
        prefer_local_media (bool, optional): whether to prefer local media. Defaults to False.
    """
    with(open(os.path.join(chat_dir, chat_name, 'message_1.json'), 'r')) as f:
        parsed_file = json.load(f)
        f.close()
    with(open(os.path.join(chatlogs_output_dir, f'{chat_name}.chatlog.csv'), 'w')) as f:
        writer = csv.writer(f)
        writer.writerow(['docNo', 'time', 'sender', 'message', 'isReply', 'who_replied_to', 'has_reactions', 'reactions', 'translated', 'is_media', 'is_OCR', 'local_uri', 'remote_url']) #TODO: implement shared/forwarded posts
        for i in range(len(parsed_file['messages'])):
            print(f"Generating chatlog ({chat_name}) for message {i} of {len(parsed_file['messages'])}", end='\r')
            message = parsed_file['messages'][i]
            docNo = i
            sender = decode_special_characters(message['sender_name'])
            time = message['timestamp_ms']
            if 'content' in message:
                message_content = decode_special_characters(message['content'])
            else:
                message_content = '' # this likely means we have media
            isReply = False
            who_replied_to = ''
            if 'reactions' in message:
                has_reactions = True
                reactions = [f'{decode_special_characters(reaction["actor"])}: {decode_special_characters(reaction["reaction"])}' for reaction in message['reactions']]
            else:
                has_reactions = False
                reactions = ''
            translated = False
            if 'photos' in message: #or message['videos']: TODO: support videos
                is_media = True
                is_OCR = False # TODO: OCR
                local_uri = message['photos'][0]['uri']
                remote_url = '' # turns out instagram's remote urls from an export are temporary for about 3 days
            else:
                is_media = False
                is_OCR = False
                local_uri = ''
                remote_url = ''
            #TODO: check for duplicated messages (perhaps in a pass after the main one?)
            writer.writerow([
                docNo,
                time,
                sender,
                message_content,
                isReply,
                who_replied_to,
                has_reactions,
                reactions,
                translated,
                is_media,
                is_OCR,
                local_uri,
                remote_url
            ])
        f.close()
        print()
    
def create_chatlog_files_for_all_chats(chat_dir:str=d3, prefer_local_media:bool=False) -> None:
    """
    Creates `chatlog.csv` files for all chats
    """
    for chat in subdirs(chat_dir):
        create_chatlog_file_for_chat(chat, chat_dir, prefer_local_media)

def create_chatlogs_and_info_for_all_chats_in_dir(chat_dir:str=d3, prefer_local_media:bool=False) -> None:
    """
    Creates `chatlog.csv` and `info.csv` files for all chats
    """
    # check that the output directories exist
    if not os.path.exists(info_output_dir):
        os.makedirs(info_output_dir)
    if not os.path.exists(chatlogs_output_dir):
        os.makedirs(chatlogs_output_dir)
    create_info_files_for_all_chats(chat_dir)
    create_chatlog_files_for_all_chats(chat_dir, prefer_local_media)

def check_inbox_and_messages(zip_path: str) -> bool:
    """
    Checks that the zip file contains the directory
    'your_instagram_activity/messages/inbox' and
    that every subdirectory inside it has a 'message_1.json' file.
    """
    inbox_prefix = 'your_instagram_activity/messages/inbox/'
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = z.namelist()
            if not any(name.startswith(inbox_prefix) for name in names):
                return False

            # Identify chat directories inside the inbox
            chat_dirs = set()
            for name in names:
                if name.startswith(inbox_prefix):
                    parts = name.split('/')
                    # Expecting structure: your_instagram_activity/messages/inbox/<chat_dir>/...
                    if len(parts) >= 4 and parts[3]:
                        chat_dirs.add(parts[3])

            # For each chat directory, check for the presence of message_1.json
            for chat in chat_dirs:
                expected_file = f"{inbox_prefix}{chat}/message_1.json"
                if expected_file not in names:
                    return False
    except Exception as e:
        log(f"Error while reading zip file {zip_path}: {e}")

        # Check if any file/directory starts with the inbox_prefi

    return True
    
def correct_archives(zips_folder:str) -> list[str]:
    """
    Checks if an archive contains the directory `your_instagram_activity/messages/inbox`
    """
    for archive in zips_in_dir(zips_folder):
        if not check_inbox_and_messages(os.path.join(zips_folder, archive)):
            log(f"Archive {archive} does not contain the messages directory structure")
        else:
            log(f"Archive {archive} is correct")

#TODO: from a correct directory, work out whether we can extract the chatlogs from it, or if we need to export instead