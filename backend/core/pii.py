from tokenisers.tokeniser import Tokeniser

class PIIConstructor:
    """
    A class to create Positional Inverted Indexes (PIIs) from a given `chatlog.csv` file.

    Args:
        language (str): The language of the chatlog files used. Defaults to `english`.
    """
    def __init__(self, language:str='english'):
        self.language = language
        self.tokeniser = Tokeniser(language=language)
        