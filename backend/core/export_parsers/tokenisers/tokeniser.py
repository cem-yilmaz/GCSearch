from english_tokeniser import en_tokenise_document

class Tokeniser():
    """
    Tokeniser class to tokenise messages. Please call the `tokenise` method to tokenise a message (document).

    Args:
        language: The language of the message. Will determine which tokenisation algorithm is used.
    """
    def __init__(self, language: str):
        self.language = language
        if language == "english":
            self.tokenise = en_tokenise_document
        else:
            raise ValueError(f"Language '{language}' is not supported.")