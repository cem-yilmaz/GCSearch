from english_tokeniser import en_tokenise_document
from simplified_chinese_tokeniser import zh_tokenise_document
from traditional_chinese_tokeniser import cn_tokenise_document

class Tokeniser():
    """
    Tokeniser class to tokenise messages. Please call the `tokenise` method to tokenise a message (document).

    Args:
        language: The language of the message. Will determine which tokenisation algorithm is used. Currently supported languages are 'english', 'chinese', and 'traditional_chinese'.
    """
    def __init__(self, language: str):
        if language not in ["english", "chinese", "traditional_chinese"]:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
        if language == "traditional_chinese":
            self.tokenise = cn_tokenise_document
        elif language == "chinese":
            self.tokenise = zh_tokenise_document
        else:
            self.tokenise = en_tokenise_document # fallback to english tokeniser
            