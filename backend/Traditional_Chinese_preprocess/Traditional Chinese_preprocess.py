import pandas as pd
import jieba
import jieba.analyse
from sentence_transformers import SentenceTransformer
from symspellpy import SymSpell, Verbosity

# stopwords
def load_stopwords(filepath="stop_words.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        stopwords = set(f.read().splitlines())
    return stopwords

# SymSpell (spelling correction)
def load_symspell(dictionary_path="bigram_dictionary.txt"):
    sym_spell = SymSpell(max_dictionary_edit_distance=2)
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
    return sym_spell

# correct wrong spelling
def correct_spelling(text, sym_spell):
    corrected_words = []
    words = jieba.lcut(text)  # jieba tokenize

    for word in words:
        suggestions = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)
        corrected_words.append(suggestions[0].term if suggestions else word)

    return "".join(corrected_words)

# initialize jieba
jieba.set_dictionary("dict.txt.big")  # Traditional Chinese dic
jieba.analyse.set_idf_path("idf.txt.big")  # TF-IDF use

# jieba tokenizer for search engine use
def jieba_tokenizer(text, stopwords, sym_spell):
    # correct wrong spelling
    text = correct_spelling(text, sym_spell)

    # keep only chinese words
    # text = re.sub(r'[^\u4e00-\u9fff]', ' ', text)

    # jieba search engine mode
    words = jieba.cut_for_search(text)

    # apply stopwords
    words = [word for word in words if word not in stopwords and len(word) > 1]

    return " ".join(words)

# jieba-TF-IDF
def extract_tfidf_keywords(text, stopwords, topK=5):
    keywords = jieba.analyse.extract_tags(text, topK=topK)
    
    
    filtered_keywords = [word for word in keywords if word not in stopwords]
    
    return " ".join(filtered_keywords)


# read csv file
def read_csv_file(filepath):
    df = pd.read_csv(filepath)

    if "message" not in df.columns or "is_media" not in df.columns:
        raise ValueError("CSV should have included 'message' and 'is_media' col")

    text_df = df[df["is_media"] == False][["message"]].dropna().astype(str)

    return text_df

# pre-process
def preprocess_messages(df, stopwords, sym_spell):
    chat_messages = df["message"].dropna().astype(str)

    # token
    processed_tokens = chat_messages.apply(lambda text: jieba_tokenizer(text, stopwords, sym_spell))

    # TF-IDF
    tfidf_keywords = chat_messages.apply(lambda text: extract_tfidf_keywords(text, stopwords, topK=5))


    # create DataFrame
    processed_df = pd.DataFrame({
        "original_message": chat_messages,
        "processed_tokens": processed_tokens,
        "tfidf_keywords": tfidf_keywords  
    })

    return processed_df

input_csv_path = "chatlog.csv"  # input csv
output_csv_path = "tra_chinese_preprocess.csv"  # output csv

# read csv
df = read_csv_file(input_csv_path)
print("read csv file")

# stopwords
stopwords = load_stopwords("stop_words.txt")
print("loading stopwords")

# spelling correction model
sym_spell = load_symspell("bigram_dictionary.txt")
print("loading spelling correction")

# pre-processing
processed_chat_df = preprocess_messages(df, stopwords, sym_spell)
print("pre-processing messages")

# save file
processed_chat_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print("save into output csv file")

print("Completed")