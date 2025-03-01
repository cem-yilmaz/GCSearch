from flask import Flask, request, jsonify
from flask_cors import CORS
from core import *

app = Flask(__name__)
CORS(app)

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

# Searching
@app.route('/GetTopNResultsFromSearch', methods=['POST'])
def flask_GetTopNResultsFromSearch():
    """
    Gets the top N results from a search query for a given positional inverted index.

    Args:
        pii_name: (str) name of the positional inverted index. If the PII is called "`<pii_name>`.pii.txt", then `<pii_name>` is "pii".
        query: (str) search query
        n: (int) number of results to return. If n > number of docs m, return m results.

    Returns:
        top_n_results: (dict) { doc_id (int): score (int):, ... }
    """
    data = request.get_json()
    pii_name = data['pii_name'] 
    query = data['query'] 
    n = data['n'] 
    #top_n_results = core.GetTopNResultsFromSearch(pii_name, query, n)
    #return jsonify(top_n_results)

@app.route('/GetMetaChatDataFromPIIName', methods=['POST'])
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
    pass

def flask_getChatDataFromDocIDGivenPIIName:
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
 
    """ Retrieve a specific chat message using its document ID from a given PII. """
    data = request.get_json()
    doc_id = data.get('doc_id')
    pii_name = data.get('pii_name')

    if doc_id is None or not pii_name:
        return jsonify({"error": "Missing doc_id or pii_name"}), 400

    chat_data = getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
    return jsonify(chat_data)

@app.route('/GetChatsBetweenRangeForChatGivenPIIName', methods=['POST'])
def flask_GetChatsBetweenRangeForGC():
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
    doc_id = data['doc_id']
    n = data['n']
    pii_name = data['pii_name']
    include_media = data['include_media']
    GC_name = None #TODO: get the GC name from the PII name
    num_chats_in_GC = flask_getNumChatsInGC(GC_name) # you will have to do some processing to get the GC name from the PII name
    chats = []
    # get the previous n chats
    chats_left_to_add = n
    while chats_left_to_add > 0:
        doc_id -= 1
        if doc_id < 0:
            break
        chat_data = flask_getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
        if chat_data['is_media'] and not include_media:
            continue
        chats.append(chat_data)
        chats_left_to_add -= 1
    # get the current chat
    chats_left_to_add = n+1 # reset to get n+1 more chats
    # now lets check the current chat
    chat_data = flask_getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
    if not chat_data['is_media'] or include_media:
        chats.append(chat_data)
        chats_left_to_add -= 1 # decrement to indicate we've added the current chat, otherwise we're getting n+1 ones ahead to make up for it
    while chats_left_to_add > 0:
        doc_id += 1
        if doc_id > num_chats_in_GC:
            break
        chat_data = flask_getChatDataFromDocIDGivenPIIName(doc_id, pii_name)
        if chat_data['is_media'] and not include_media:
            continue
        chats.append(chat_data)
        chats_left_to_add -= 1

    return jsonify(chats)

@app.route('/CreateChatlogFromExport', methods=['POST'])
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
