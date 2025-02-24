import os
import zipfile
import json
import csv

def test_func():
    return "Hi!"

class InstaChatlogCreator:
    """
    A class that creates the chatlogs and info files from a dump of Instagram data.
    Produces a folder in the current directory titled `out`, within it containing a `chatlogs` folder and an `info` folder.

    Place your exported Instagram data in a folder called `export` in the same directory as this script. Use the `main` method to generate the chatlogs and info files, which will be placed in the `out` folder.

    Args:
        export_location (str): The path to the folder containing the Instagram data dump. Defaults to a folder called `export`.
    """
    def __init__(self, export_location:str="export"): #TODO: turn these into customisable parameters
        self.root_output_dir = 'out'
        self.info_output_dir = os.path.join(self.root_output_dir, 'info')
        self.chatlogs_output_dir = os.path.join(self.root_output_dir, 'chatlogs')
        self.raw_export_archives_dir = export_location
        self.raw_messages_dir = 'raw_messages'

    def __repr__(self):
        return f"InstaChatlogCreator(export_location={self.raw_export_archives_dir}) | Will read zip archives from {self.raw_export_archives_dir}/, extract the core message data to {self.raw_messages_dir}/, and output chatlogs to {self.chatlogs_output_dir}/ and info files to {self.info_output_dir}/"

    def subdirs(self, path : str) -> list[str]:
        """
        Gets all the subdirectories in a directory.

        Args:
            path (str): The path to the directory.

        Returns:
            list[str]: A list of the subdirectories as strings.
        """
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    
    def make_dir_if_not_exists(self, dir_path : str) -> bool:
        """
        Makes a directory if it doesn't exist

        Args:
            dir_path (str): the name of the directory

        Returns:
            bool: whether the directory was successfully created
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return os.path.exists(dir_path)
    
    def zips_in_dir(self, path : str) -> list[str]:
        """
        Gets all the zip files in a directory.

        Args:
            path (str): The path to the directory.

        Returns:
            list[str]: A list of the zip files as strings.
        """
        return [name for name in os.listdir(path) if name.endswith('.zip')]
    
    def check_inbox_and_messages(self, zip_path: str) -> bool:
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
            print(f"Error while reading zip file {zip_path}: {e}")
            print("Skipping this file and continuing normal execution.")
            return False

            # Check if any file/directory starts with the inbox_prefi

        return True
    
    def correct_archives(self) -> list[str]:
        """
        Checks if an archive contains the directory `your_instagram_activity/messages/inbox`
        """
        return [archive for archive in self.zips_in_dir(self.raw_export_archives_dir) if self.check_inbox_and_messages(os.path.join(self.raw_export_archives_dir, archive))]

    def extract_messages_folder(self, prefix:str='your_instagram_activity/messages/inbox/') -> None:
        """
        Extracts only the messages folder (`your_instagram_activity/messages/inbox`) from an archive, 
        but places its contents directly in `raw_messages/`

        Raises:
            LookupError: If the export does not contain any archives with the messages in it
        """
        if not self.correct_archives():
            raise LookupError("No valid archive found in the export folder. Please make sure you have exported your Instagram data correctly, and downloaded all the zip files.")
        archive_path = os.path.join(self.raw_export_archives_dir, self.correct_archives()[0]) # This assumes we only have one correct archive
        # I've got a pretty sizeable archive, and can confirm this happens in many exports. Nevertheless, this should be changed to handle multiple valid archives in the future. TODO
        with zipfile.ZipFile(archive_path, 'r') as z:
            for member in z.infolist():
                if member.filename.startswith(prefix):
                    new_filename = member.filename[len(prefix):]
                    if not new_filename:
                        continue
                    new_filepath = os.path.join(self.raw_messages_dir, new_filename)
                    os.makedirs(os.path.dirname(new_filepath), exist_ok=True)
                    if not member.is_dir():
                        with z.open(member) as src, open(new_filepath, 'wb') as dst:
                            dst.write(src.read())

    def decode_special_characters(self, content : str) -> str:
        """
        Removes the weird byte-encoding of non-ASCII characters from the content

        Args:
            content (str): The text content to decode (example `\u00e2\u009d\u00a4\u00ef\u00b8\u008f`)

        Returns:
            str: The decoded text content (example `❤️`)
        """
        return content.encode('latin1').decode('utf-8')
    
    def get_info_about_chat(self, chat_name:str) -> tuple[str, str, list[str]]:
        """
        Gets the internal name, the display name of the chat and the participants in the chat
        """
        internal_chat_name = chat_name
        with open(os.path.join(self.raw_messages_dir, chat_name, 'message_1.json'), 'r') as f:
            # the display name of the chat can be found under the title key in message_1.json
            parsed_file = json.load(f)
            display_name = self.decode_special_characters(parsed_file['title'])
            participants = [self.decode_special_characters(p['name']) for p in parsed_file['participants']]
            f.close()
        return (internal_chat_name, display_name, participants)
    
    def get_info_about_all_chats(self) -> list[tuple[str, str, list[str]]]:
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
        return [self.get_info_about_chat(chat) for chat in self.subdirs(self.raw_messages_dir)]
    
    def create_info_file_for_chat(self, chat_name:str) -> None:
        """
        Creates an `info.csv` file for a chat
        """
        internal_chat_name, display_name, participants = self.get_info_about_chat(chat_name)
        with open(os.path.join(self.info_output_dir, f'{internal_chat_name}.info.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Internal chat name', 'Display name', 'Participants'])
            writer.writerow([internal_chat_name, display_name, '['+', '.join(participants)+']'])
            f.close()

    def create_info_files_for_all_chats(self) -> None:
        """
        Creates an `info.csv` file for all chats
        """
        self.make_dir_if_not_exists(self.info_output_dir)
        for chat in self.subdirs(self.raw_messages_dir):
            self.create_info_file_for_chat(chat)

    def create_chatlog_file_for_chat(self, chat_name:str, prefer_local_media:bool=False) -> None:
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
            prefer_local_media (bool, optional): whether to prefer local media. Defaults to False.
        """
        with(open(os.path.join(self.raw_messages_dir, chat_name, 'message_1.json'), 'r')) as f:
            parsed_file = json.load(f)
            f.close()
        with(open(os.path.join(self.chatlogs_output_dir, f'{chat_name}.chatlog.csv'), 'w')) as f:
            writer = csv.writer(f)
            writer.writerow(['docNo', 'time', 'sender', 'message', 'isReply', 'who_replied_to', 'has_reactions', 'reactions', 'translated', 'is_media', 'is_OCR', 'local_uri', 'remote_url']) #TODO: implement shared/forwarded posts
            for i in range(len(parsed_file['messages'])):
                print(f"Generating chatlog ({chat_name}) for message {i} of {len(parsed_file['messages'])}", end='\r')
                message = parsed_file['messages'][i]
                docNo = i
                sender = self.decode_special_characters(message['sender_name'])
                time = message['timestamp_ms']
                if 'content' in message:
                    message_content = self.decode_special_characters(message['content'])
                else:
                    message_content = '' # this likely means we have media
                isReply = False
                who_replied_to = ''
                if 'reactions' in message:
                    has_reactions = True
                    reactions = [f'{self.decode_special_characters(reaction["actor"])}: {self.decode_special_characters(reaction["reaction"])}' for reaction in message['reactions']]
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

    def create_chatlog_files_for_all_chats(self) -> None:
        """
        Creates `chatlog.csv` files for all chats
        """
        self.make_dir_if_not_exists(self.chatlogs_output_dir)
        for chat in self.subdirs(self.raw_messages_dir):
            self.create_chatlog_file_for_chat(chat)

    def create_chatlogs_and_info_for_all_chats(self) -> None:
        self.create_info_files_for_all_chats()
        self.create_chatlog_files_for_all_chats()

    def main(self) -> None:
        """
        \"*If you're going to run one function, make sure it's `main()`*\"

        This function turns the Instagram data dump in `export` into chatlogs and info files in the `out` folder.
        """
        self.extract_messages_folder()
        self.create_chatlogs_and_info_for_all_chats()