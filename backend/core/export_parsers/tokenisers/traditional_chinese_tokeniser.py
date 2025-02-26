import re
import jieba
import logging
jieba.setLogLevel(logging.ERROR)

with open("stopwords/traditional_chinese_stop_words.txt", "r", encoding="utf-8") as f:
    stopwords = set(f.read().splitlines())
    f.close()

def cn_tokenise_document(doc:str) -> list[str]:
    """
    Tokenises a document in Traditional Chinese.
    Args:
        doc: The document to be tokenised, all in one string.
    Returns:
        The tokenised document, as a list of tokens.
    """
    cleaned_words = re.sub(r'[^\u4e00-\u9fff]', ' ', doc)
    # Tokenise the document
    words = jieba.cut_for_search(cleaned_words)
    # Remove stopwords
    return [word for word in words if word.strip() and word not in stopwords]