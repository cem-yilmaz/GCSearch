import re
from nltk import PorterStemmer
porter = PorterStemmer()

stopwords_file_name = "stopwords/ttds_2023_english_stop_words.txt"

with open(stopwords_file_name, "r") as f:
    stopwords = f.read().splitlines()
    f.close()

def pre_process_token(token: str) -> str:
    """
    Pre-processes a single token. Applies
    - Case folding
    - Elimination if token is a stopword
    - Porter Stemming
    Args:
        token: Token to be pre-processed.
        challenge: If this is enabled, the challenge tokenisation (no stopping) will be applied. Default is `False`.
    Returns:
        The pre-processed token (`None` if token was stopword).
    """
    #if not re.match(r'^[a-zA-Z]+$', token):
    #   return None
    
    if (token in stopwords): 
        return None
    else:
        stemmed_token = porter.stem(token, to_lowercase=True) # stemmer will do the Case Folding for us
        return stemmed_token
    
def create_tokens_from_document(doc: str) -> list[str]:
    """
    Given a document, returns a list of tokens in that document (in order of appearance)
    Args:
        doc: The document to be tokenised, all as one string
    Returns:
        A list of tokens in the document.
    """
    # Split the document at non-letter characters
    tokens = re.split(r'[^a-zA-Z]', doc) # could possible be edited to include numbers?
    # remove empty tokens from the list, and also remove any tokens containing numbers
    return [token for token in tokens if token and not any(char.isdigit() for char in token)]

def en_tokenise_document(doc : str) -> list[str]:
    """
    FULLY Pre-processes a document. Applies
    - Tokenisation
    - Case folding
    - Elimination of stopwords
    - Porter Stemming
    Args:
        doc: The document to be pre-processed, all in one string.
    Returns:
        The pre-processed document, as a list of tokens.
    """
    tokens = create_tokens_from_document(doc)
    # pre-process each token, and add it to the list of pre-processed tokens if it is not None
    return [pre_process_token(token) for token in tokens if pre_process_token(token)]