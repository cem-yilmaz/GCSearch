from insta_chatlog_creator import InstaChatlogCreator

class Parser():
    """
    A super class to call the individual parsings on all of the possible message exports.

    Args:
        language (str): The language of the message export (`english`, `chinese)
        include_media (bool): (Default: `False`) Whether or not to include media in the parsed data.
    """
    def __init__(self, language:str="en", include_media:bool=False):
        supported_languages = ["english", "chinese", "traditional_chinese", "turkish"]
        if language not in supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
        self.include_media = include_media
        