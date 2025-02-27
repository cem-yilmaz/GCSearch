import re
import os
import snowballstemmer

# Get the directory of this script and construct the stopwords file path
# I got stopwords-tr.txt from the following link and put it in the stopwords folder:
# https://github.com/stopwords-iso/stopwords-tr/blob/master/stopwords-tr.txt

script_dir = os.path.dirname(os.path.abspath(__file__))
stopwords_file_name = os.path.join(script_dir, "stopwords", "stopwords-tr.txt")

# Load Turkish stopwords from the file
with open(stopwords_file_name, "r", encoding="utf-8") as f:
    stopwords = f.read().splitlines()
    f.close()

stemmer = snowballstemmer.stemmer("turkish") # SnowballStemmer for Turkish

def pre_process_token(token: str) -> str:
    # Check if the token is a stopword, and if so, return None
    # Otherwise, stem the token and return it
    if token in stopwords:
        return None
    else:
        stemmed_token = stemmer.stemWord(token.lower())
        return stemmed_token

def create_tokens_from_document(doc: str) -> list[str]:
    # Split the document at characters that are not letters
    # Includes Turkish-specific letters: ç, Ç, ğ, Ğ, ı, İ, ö, Ö, ş, Ş, ü, Ü
    tokens = re.split(r'[^a-zA-ZçÇğĞıİöÖşŞüÜ]', doc)
    # Remove empty tokens and any tokens containing digits
    return [token for token in tokens if token and not any(char.isdigit() for char in token)]

def tr_tokenise_document(doc: str) -> list[str]:
    # Create tokens from the document
    tokens = create_tokens_from_document(doc)
    # Pre-process each token
    return [pre_process_token(token) for token in tokens if pre_process_token(token)]

# Example usage (commented it out just in case)
# if __name__ == "__main__":
#    text = "MERHABALAR NASILSINIZ İYİ MİSİNİZ"
#    processed_tokens = tr_tokenise_document(text)
#    print(processed_tokens)
