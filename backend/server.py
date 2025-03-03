from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from core.search import Searcher

import os
import csv
import datetime

app = Flask(__name__)
CORS(app)

searcher = Searcher()

currently_supported_platforms = [
    "instagram",
    "whatsapp",
    "wechat",
    "line"
]

currently_supported_languages = [
    "en", # English
    "zh-cn", # Simplified Chinese
    "zh-tw", # Traditional Chinese
]

@app.route('/api/isAlive', methods=['GET'])
def flask_isAlive():
    """
    Simple function to check if the server is alive.
    """
    return jsonify({"status": "alive"})

def flask_getAllParsedChats() -> list[str]:
    """
    Gets the internal chat names from all the parsed chats, located within the `core/out/*` directories.

    Returns:
        parsed_chats: (list[str]) list of internal chat names (e.g. ["chat_1", "chat_2", ...])
    """
    parsed_chats = []
    for filename in os.listdir('core/out/info/'):
        if filename.endswith('.csv'):
            parsed_chats.append(filename.split('.')[0])
    return parsed_chats

def flask_sortChatsByPlatform() -> dict[str, list[str]]:
    """
    Sorts the internal chat names by platform. Returns a dictionary in the format:
    ```
    {
        "instagram": ["chat_1", "chat_2", ...],
        "whatsapp": ["chat_3", "chat_4", ...],
        ...
    }
    ```
    """
    sorted_chats = {}
    for groupchat in flask_getAllParsedChats():
        platform = groupchat.split('_')[0]
        if platform not in sorted_chats:
            sorted_chats[platform] = []
        sorted_chats[platform].append(groupchat)
    return sorted_chats

@app.route('/api/GetAllParsedChatsForPlatform', methods=['POST'])
def flask_getAllParsedChatsForPlatform():
    """
    Gets all the parsed chats for a given platform.

    Args:
        platform: (str) the name of the platform (e.g. "instagram", "whatsapp", "wechat", "line")
    Returns:
        parsed_chats: (list[str]) list of internal chat names (e.g. ["chat_1", "chat_2", ...])
    """
    data = request.get_json()
    platform = data['platform']
    sorted_chats = flask_sortChatsByPlatform()
    if platform not in sorted_chats:
        return jsonify({"error": f"Platform \"{platform}\" not supported. Currently supported platforms are: {currently_supported_platforms}"})
    return jsonify(sorted_chats[platform])

# Rendering individual groupchats from ChatList
def flask_getDisplayNameFromChat(chat_name:str) -> str:
    """
    Given an internal `chat_name`, gets the display name of the chat.

    Args:
        chat_name: (str) the internal chat name (e.g. "chat_1")
    Returns:
        display_name: (str) the display name of the chat
    """
    with open(f'core/out/info/{chat_name}.info.csv', 'r') as f:
        reader = csv.reader(f)
        display_name = [row for row in reader][1][1]
        return display_name

def flask_getLastMessageFromChat(chat_name:str) -> dict:
    """
    Given an internal `chat_name`, finds the latest message sent to that chat and returns the sender, message, and timestamp.

    Args:
        chat_name: (str) the internal chat name (e.g. "chat_1")
    Returns:
        last_message: (dict) { "doc_id": int, "sender": str, "message": str, "timestamp": int }
    """
    with open(f'core/out/chatlogs/{chat_name}.chatlog.csv', 'r') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
        if len(rows) > 1:
            last_message = rows[1]
        else:
            return {"sender": "Error", "message": "No messages found", "timestamp": 0}
        return {"doc_id": last_message[0], "sender": last_message[2], "message": last_message[3], "timestamp": int(last_message[1])}
    
@app.route('/api/GetInfoForGroupChat', methods=['POST'])
def flask_getInfoForGroupChat():
    """
    Gets the display name and last message for a given chat.

    Args:
        chat_name: (str) the internal chat name (e.g. "chat_1")
    Returns:
        chat_info: (dict) { "display_name": str, "last_message": { "sender": str, "message": str, "timestamp": int } }
    """
    try:
        data = request.get_json()
        chat_name = data['chat_name']
        display_name = flask_getDisplayNameFromChat(chat_name)
        last_message = flask_getLastMessageFromChat(chat_name)
        return jsonify({"display_name": display_name, "last_message": last_message})
    except FileNotFoundError as e:
        print(f"DEBUG: FILENOTFOUND ERROR with chat {chat_name} {str(e)}")
        return jsonify({"error": f"Could not find file for chat {chat_name}"}), 404
    except Exception as e:
        print(f"DEBUG: OTHER ERROR with chat {chat_name} {str(e)}")
        return jsonify({"error": str(e)}), 500

# Searching
@app.route('/api/GetTopNResultsFromSearch', methods=['POST'])
def flask_GetTopNResultsFromSearch():
    """
    Gets the top N results from a search query for all PIIs.

    Args:
        query: (str) search query
        n: (int) number of results to return. If n > number of docs m, return m results.

    Returns:
        top_n_results: (dict) { doc_id (int): score (int):, ... }
    """
    data = request.get_json()
    query = data['query'] 
    n = data['n'] 
    top_n_results = searcher.flask_search(query, n)
    print(f"DEBUG: got {len(top_n_results)} results for query \"{query}\"")
    return jsonify(top_n_results)

@app.route('/api/GetMetaChatDataFromPIIName', methods=['POST'])
def flask_GetMetaChatDataFromPIIName():
    """
    Gets the metadata (Internal Chat Name, Display name, Participants) from a given positional inverted index. Returns a dictionary e.g.
    ```
    {
        "Internal Chat Name": "chat_1",
        "Display Name": "Chat 1",
        "Participants": ["Alice", "Bob"]
    }
    ```
    where we have:
    - an Internal Chat Name (str), unique to that chat and used to find the actual related files
    - a Display Name (str), the name of the chat as it appears to the user (and presented in the frontend)
    - a list of Participants (list[str]), the names of the participants in the chat.

    Args: 
        pii_name: (str) name of the positional inverted index. If the PII is called "`<pii_name>`.pii.txt", then `<pii_name>` is "pii".
    
    Returns:
        metadata: (dict) { "Internal Chat Name": str, "Display Name": str, "Participants": list[str] }
    """
    data = request.get_json()
    pii_name = data['pii_name']
    #metadata = core.GetMetaChatDataFromPIIName(pii_name)
    #return jsonify(metadata)

def flask_getNumChatsInGC(GC_name:str) -> int:
    """
    Gets the number of chats in a given GC from it's name

    Args:
        pii_name: (str) name of the positional inverted index. If the PII is called "`<pii_name>`.pii.txt", then `<pii_name>` is "pii".

    Returns:
        num_chats: (int) number of chats in the GC
    """
    with open(f'core/out/chatlogs/{GC_name}.chatlog.csv', 'r') as f:
        reader = csv.reader(f)
        num_chats = len([row for row in reader]) - 1
        f.close()
    return num_chats
        
    

def flask_getChatDataFromDocIDGivenPIIName(doc_id:int, pii_name:str) -> dict:
    """
    *Helper function for `GetChatsBetweenRangeForChatGivenPIIName`*

    Gets data for a single chat from a given doc_id. Returns a dictionary in the following format e.g.
    ```
    {
        doc_id (int): 0,
        time (int): 1234567890 (unix timestamp),
        sender (str): "Alice" (sender name should be in participants),
        message (str): "Hello, world!" (message may be a transcription of an image, see is_OCR),
        /* We are currently not supporting replies */
        reactions (list[str, str]) (_optional_): ['Alice: ❤️', 'Bob: 😂'],
        is_OCR (bool): (_default_: False) (tag on whether the message field is a transcription of the image),
        is_media (bool): (_default_: False) (tag on whether the message is a media file. If so, the message field is ignored and should be left blank),
        uri (str) (_optional_): "https://example.com/image.jpg" (uri to the media file. This may be a remote link, or a local path to the image file. This field is ignored if is_media is False)
    }
    ```

    Args:
        doc_id: (int) the document ID of the chat
        pii_name: (str) name of the positional inverted index. If the PII is called "`<pii_name>`.pii.txt", then `<pii_name>` is "pii".
    """
    # we already have this functionality in search.py
    wrapper = (pii_name, doc_id, None)
    return searcher.flask_get_message_details_from_search_result(wrapper)

@app.route('/api/GetChatsBetweenRangeForChatGivenPIIName', methods=['POST'])
def flask_GetChatsBetweenRangeForGC(include_media:bool=False):
    """
    Gets 2n+1 chats around a given chat in a GC given a PII name. Calls `getChatDataFromDocIDGivenPIIName` for each chat, so returns a list of dictionaries (in the format described in that function).

    If we do not have enough chats to return on either side of the given chat, we return as many as we can.

    Args:
        doc_id: (int) the document ID of the chat
        n: (int) number of chats to return on either side of the given chat
        pii_name: (str) name of the positional inverted index. If the PII is called "`<pii_name>`.pii.txt", then `<pii_name>` is "pii".
        include_media: (bool) (_default_: False) whether to include media messages in the response. If not,these will be skipped over (such that we have 2n+1 non-media messages).

    Returns:
        chats: (list[dict]) [chat_1, chat_2, ..., chat_(2n+1)]
    """
    data = request.get_json()
    doc_id = int(data['doc_id'])
    og_doc_id = doc_id
    n = int(data['n'])
    pii_name = data['pii_name']
    print(f"""
    doc_id: {doc_id}
    n: {n}
    pii_name: {pii_name}
    """)
    if 'include_media' in data:
        include_media = data['include_media']
    GC_name = flask_getDisplayNameFromChat(pii_name)
    num_chats_in_GC = flask_getNumChatsInGC(pii_name)
    chats = []
    # get the previous n chats
    chats_left_to_add = n
    print(f"DEBUG: We are at doc_id {doc_id} in {pii_name}. We're going to add the next {n} chats before this.")
    while chats_left_to_add > 0:
        doc_id -= 1
        if doc_id <= 0:
            break
        print(f"We're now going to get the chat data from {pii_name} for chat {doc_id}")
        chat_data = flask_getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
        #input(f"chat_data: {chat_data}")
        # we current dont check for media messages
        #if chat_data[9] and not include_media:
        #    continue
        chats.append(chat_data)
        print(f"added chat +1")
        chats_left_to_add -= 1
    print("Added the previous n chats")
    # get the current chat
    chats_left_to_add = n+1 # reset to get n+1 more chats
    # now lets check the current chat
    doc_id = og_doc_id
    chat_data = flask_getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
    
    chats.append(chat_data)
    chats_left_to_add -= 1 # decrement to indicate we've added the current chat, otherwise we're getting n+1 ones ahead to make up for it
    
    # now we get the next n chats
    chats_left_to_add = n
    while chats_left_to_add > 0:
        doc_id += 1
        if doc_id > num_chats_in_GC:
            break
        chat_data = flask_getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
        #if chat_data['is_media'] and not include_media:
        #    continue
        chats.append(chat_data)
        print(f"added chat +1")
        chats_left_to_add -= 1

    return jsonify(chats)

@app.route('/api/CreateChatlogFromExport', methods=['POST'])
def flask_CreateChatlogFromExports():
    """
    Calls the internal export -> chatlog function for a given social media platform. Will create the directories `core/out/info/` and `core/out/chatlogs/` (if they do not exist) and populate them with the export data. This data is located in the `export/<platform_name>/` directory.

    Args:
        platform: (str) the name of the social media platform. Must be one of the currently supported platforms. 
        include_media: True | 'OCR' | False (_default_: False) whether to include media messages in the chatlog. If 'OCR', then include media messages but transcribe them. If False, then skip over media messages.
        language: (str) (_default_: '`en`') the language of the chat. Must be one of the currently supported languages.
    """
    data = request.get_json()
    platform = data['platform']
    include_media = data['include_media']
    language = data['language']
    if platform not in currently_supported_platforms:
        return jsonify({"error": f"Platform \"{platform}\" not supported. Currently supported platforms are: {currently_supported_platforms}"})
    if language not in currently_supported_languages:
        return jsonify({"error": f"Language \"{language}\" not supported. Currently supported languages are: {currently_supported_languages}"})
    #core.CreateChatlogFromExport(platform, include_media, language)
    return jsonify({"success": "Export processed"})

if __name__ == '__main__':
    app.run(debug=True)