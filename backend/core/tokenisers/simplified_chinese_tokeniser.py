import re
import os
from thulac import thulac

thulac_model = thulac(seg_only=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
stopwords_file_name = os.path.join(script_dir, "stopwords", "hit_stopwords.txt")

with open(stopwords_file_name, "r", encoding="utf-8-sig") as f:
    stopwords = set(f.read().splitlines())
    f.close()

def zh_tokenise_document(doc: str) -> list[str]:
    """
    Tokenises a document in simplified Chinese.
    Args:
        doc: The document to be tokenised, all in one string.
    Returns:
        The tokenised document, as a list of tokens.
    """
    clean_text = re.sub(r'[^\u4e00-\u9fff]', ' ', doc)
    tokens = thulac_model.cut(clean_text, text=True).split()
    return [token for token in tokens if token not in stopwords and token.strip()]