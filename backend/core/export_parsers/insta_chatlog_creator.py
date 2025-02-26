import os
import zipfile
import json
import csv
import re
from pathlib import Path
from ocr import OCR # This import looks silly just trust the plan

report_zip_file_errors = False # disable logging when a corrupt zip is attempted to be read
base_dir = Path(__file__).parent # used to resolve relative paths to the script

class InstaChatlogCreator:
    """
    A class that creates the chatlogs and info files from a dump of Instagram data.
    Produces a folder `core/out/`, within it containing a `chatlogs/` folder and an `info/` folder.

    Place your exported Instagram data in `export/`. Use the `main` method to generate the chatlogs and info files, which will be placed in the `out/` folder.

    These chatlogs will follow the naming scheme `instagram__<internal_chat_name>.chatlog.csv` and the info files will follow the naming scheme `instagram__<internal_chat_name>.info.csv`.

    Raises:
        ValueError: If the number of archives does not match the number of correct and extra archives. Your data is likely incomplete or corrupted if this occurs.
    """
    def __init__(self):
        # where the parsed files will be outputted to
        self.root_output_dir = (base_dir.parent / 'out')
        self.info_output_dir = (self.root_output_dir / 'info')
        self.chatlogs_output_dir = (self.root_output_dir / 'chatlogs')
        # where the archived data is stored
        self.raw_export_archives_dir:str = (base_dir.parent / 'export' / 'instagram')
        # where the raw data is extracted to
        self.raw_messages_dir:str = (base_dir.parent / 'insta_raw_message_data')
        # prefix for the output files
        self.export_prefix:str = 'instagram__'
        # sanity check
        self.num_archives = len(self.zips_in_dir(self.raw_export_archives_dir))
        self.num_correct_archives = len(self.correct_archives())
        self.num_extra_archives = len(self.extra_archives())

        if self.num_archives != self.num_correct_archives + self.num_extra_archives:
            raise ValueError(f"The number of archives does not match the number of correct and extra archives. Your data is likely incomplete or corrupted. You have {self.num_correct_archives} (correct) + {self.num_extra_archives} (extra) = {self.num_correct_archives + self.num_extra_archives} != {self.num_archives} archives.")

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
            if report_zip_file_errors:
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

    def extra_archives(self) -> list[str]:
        """
        Returns the extra archives. These do not contain raw message data but instead contain extra media data.
        """
        correct_archives = self.correct_archives()
        return [archive for archive in self.zips_in_dir(self.raw_export_archives_dir) if archive not in correct_archives]

    def extract_messages_folder(self, prefix:str='your_instagram_activity/messages/inbox/') -> None:
        """
        Extracts only the messages folder (`your_instagram_activity/messages/inbox`) from an archive, 
        but places its contents directly in `insta_raw_message_data/`

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
        with open(os.path.join(self.info_output_dir, f'{self.export_prefix}{internal_chat_name}.info.csv'), 'w') as f:
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

    def change_local_media_path(self, pathname:str) -> str:
        """
        Changes the export's local media path to the correct raw export data path.
        """
        return pathname.replace('your_instagram_activity/messages/inbox/', f"{str(self.raw_messages_dir)}/")
    
    def chat_is_system_message(self, message:str) -> bool:
        """
        Checks if a chat message matches a certain system message pattern.
        Current patterns checked:
        - <name> sent an attachment
        - Liked a message
        - <name> liked a message
        - Reacted <reaction> to your message
        - <name> reacted <reaction> to your message
        """
        patterns = [
            re.compile(r'^.* sent an attachment$'),
            re.compile(r'^Liked a message$'),
            re.compile(r'^.* liked a message$'),
            re.compile(r'^Reacted .* to your message$'),
            re.compile(r'^.* reacted .* to your message$')
        ]
        return any(pattern.match(message) for pattern in patterns)
    
    def get_num_of_message_jsons_for_chat(self, chat_name:str) -> int:
        """
        Returns the number of `message_<i>.json` files in a chat directory.

        Args:
            chat_name (str): The internal name of the chat
        """
        return len([name for name in os.listdir(os.path.join(self.raw_messages_dir, chat_name)) if name.startswith('message_')])

    def create_chatlog_file_for_chat(self, chat_name:str, handle_local_media:str="ignore") -> None:
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
            handle_local_media (str): (optional) ['*ignore*', '*include*'] How to handle local media. 'ignore' (default) will not include messages that only contain media. 'include' will include the media as a local path.
        """
        num_jsons = self.get_num_of_message_jsons_for_chat(chat_name)
        for j in range(1, num_jsons+1): # a single message_<i>.json file only stores 10000 messages
            with(open(os.path.join(self.raw_messages_dir, chat_name, f'message_{j}.json'), 'r')) as f:
                parsed_file = json.load(f)
                f.close()
            docNo = (j-1) * 10000 # to track the document number between message.jsons
            with(open(os.path.join(self.chatlogs_output_dir, f'{self.export_prefix}{chat_name}.chatlog.csv'), 'a')) as f:
                writer = csv.writer(f)
                if docNo == 0:
                    writer.writerow(['docNo', 'time', 'sender', 'message', 'isReply', 'who_replied_to', 'has_reactions', 'reactions', 'translated', 'is_media', 'is_OCR', 'local_uri', 'remote_url']) #TODO: implement shared/forwarded posts
                for i in range(len(parsed_file['messages'])):
                    print(f"Generating chatlog ({chat_name}) for message {i} of {len(parsed_file['messages']) * num_jsons}", end='\r')
                    message = parsed_file['messages'][i]
                    docNo = docNo + 1
                    sender = self.decode_special_characters(message['sender_name'])
                    time = message['timestamp_ms']
                    if 'content' in message:
                        message_content = self.decode_special_characters(message['content'])
                    else:
                        message_content = '' # this likely means we have media
                    # check if the message is a system message
                    if self.chat_is_system_message(message_content):
                        docNo -= 1 # correct the docNo
                        continue # skip writing this message
                    isReply = False
                    who_replied_to = ''
                    if 'reactions' in message:
                        has_reactions = True
                        reactions = [f'{self.decode_special_characters(reaction["actor"])}: {self.decode_special_characters(reaction["reaction"])}' for reaction in message['reactions']]
                    else:
                        has_reactions = False
                        reactions = ''
                    translated = False #TODO: implement translation tag
                    if 'photos' in message: #or message['videos']: TODO: support videos
                        is_media = True
                        local_uri = message['photos'][0]['uri']
                    else:
                        is_media = False
                        local_uri = ''
                    is_OCR = False # assume false to start
                    remote_url = '' # turns out instagram's remote urls from an export are temporary for about 3 days
                    #TODO: check for duplicated messages (perhaps in a pass after the main one?)
                    # Now we check how we're handling local media
                    if is_media:
                        # the current message is media, so we need to check how they want to handle it
                        if handle_local_media == 'ignore':
                            # we're ignoring media, so we'll skip this message
                            docNo -= 1 # correct the docNo
                            continue
                        else:
                            # we want to translate the path to be a proper local one
                            local_uri = self.change_local_media_path(local_uri)
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

    def create_chatlog_files_for_all_chats(self, handle_local_media:str) -> None:
        """
        Creates `chatlog.csv` files for all chats

        Args:
            handle_local_media (str, optional): ['*ignore*', '*include*'] How to handle local media. 'ignore' (default) will not include messages that only contain media. 'include' will include the media as a local path.
        """
        self.make_dir_if_not_exists(self.chatlogs_output_dir)
        for chat in self.subdirs(self.raw_messages_dir):
            self.create_chatlog_file_for_chat(chat, handle_local_media)

    def create_chatlogs_and_info_for_all_chats(self, handle_local_media:str) -> None:
        """
        Wrapper for `create_chatlog_files_for_all_chats` and `create_info_files_for_all_chats`.

        Args:
            handle_local_media (str, optional): ['*ignore*', '*include*'] How to handle local media. 'ignore' (default) will not include messages that only contain media. 'include' will include the media as a local path.
        """
        self.create_info_files_for_all_chats()
        self.create_chatlog_files_for_all_chats(handle_local_media)

    # OCR stuff
    # OCR'ing is so expensive we need to OCR individual chats *after* they have been chatlog'd
    def ocr_message(self, ocr_model:OCR, GCName:str="hannah_1414358549958244", chat_docID:int=29508) -> None:
        """
        Updates an individual message at `chat_docID` in the chatlog `GCName` with the OCR'd text.
        
        **This function is currently unused.**

        Args:
            ocr_model (OCR): The OCR model to use.
            GCName (str): The internal name of the chat.
            chat_docID (str): The document ID of the message
        """
        with open(os.path.join(str(self.chatlogs_output_dir), f'{self.export_prefix}{GCName}.chatlog.csv'), 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            print(len(rows))
            f.close()
        matches = [row for row in rows if row[0] == str(chat_docID)]
        if matches:
            # we should only get one match, so for now, just take the first value
            match = matches[0]
        else:
            match = None

        image_path = match[11]
        result = ocr_model.transcribe(image_path)
        if result:
            print(f"DEBUG: OCR successful. Replacing message {chat_docID} in chat {GCName} with OCR'd text ({result})")
            match[3] = result
            match[10] = True

    def main(self, handle_local_media:str='ignore') -> None:
        """
        \"*If you're going to run one function, make sure it's `main()`*\"

        This function turns the Instagram data dump in `export` into chatlogs and info files in the `out` folder.
        
        **It is not reccomended to run `ocr` on a machine with < 16GB of RAM; instead, use `include` and then manually OCR the chats needed.**
        
        Args:
            handle_local_media (str, optional): ['*ignore*', '*include*'] How to handle local media. 'ignore' (default) will not include messages that only contain media. 'include' will include the media as a local path.
        """
        self.extract_messages_folder()
        self.create_chatlogs_and_info_for_all_chats(handle_local_media)
        #TODO: tell the user they can safely delete the raw_messages folder IF they choose not to render images