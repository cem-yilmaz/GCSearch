import pandas as pd
import jieba
import jieba.analyse
from sentence_transformers import SentenceTransformer

# stopwords
def load_stopwords(filepath="stop_words.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        stopwords = set(f.read().splitlines())
    return stopwords

# initialize jieba
jieba.set_dictionary("dict.txt.big")  # Traditional Chinese dic
jieba.analyse.set_idf_path("idf.txt.big")  # TF-IDF use

# jieba tokenizer for search engine use
def jieba_tokenizer(text, stopwords):
    # correct wrong spelling
    # text = correct_spelling(text, sym_spell)

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

# BERT
def compute_sentence_embedding(texts):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(texts)
    return embeddings

def read_csv_file(filepath):
    df = pd.read_csv(filepath)
    
    # col exists or not
    required_cols = ["doc_id", "message", "is_media"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV must include '{col}' column")
    
    # is_media=False
    filtered_df = df[df["is_media"].astype(str).str.upper() == "FALSE"]
    
    # keep doc_id and message
    text_df = filtered_df[["doc_id", "message"]].dropna().astype(str)
    return text_df

# pre-process
def preprocess_messages(df, stopwords):
    doc_ids = df["doc_id"]
    chat_messages = df["message"].dropna().astype(str)

    # token
    processed_tokens = chat_messages.apply(lambda text: jieba_tokenizer(text, stopwords))

    # TF-IDF
    tfidf_keywords = chat_messages.apply(lambda text: extract_tfidf_keywords(text, stopwords, topK=5))

    # BERT
    embeddings = compute_sentence_embedding(processed_tokens.tolist())

    # create DataFrame
    processed_df = pd.DataFrame({
        "doc_id":doc_ids,
        "original_message": chat_messages,
        "processed_tokens": processed_tokens,
        "tfidf_keywords": tfidf_keywords,
        "embedding_vector": list(embeddings)  
    })

    return processed_df

input_csv_path = "LINE_chatlog.csv"  # input csv
output_csv_path = "LINE_processed_chatlog.csv"  # output csv

# read csv
print("read csv file")
df = read_csv_file(input_csv_path)

print("loading stopwords")
# stopwords
stopwords = load_stopwords("stop_words.txt")

# pre-processing
print("pre-processing text messages")
processed_chat_df = preprocess_messages(df, stopwords)
print("completed pre-processing messages")

# save file
print("saving into output csv file")
processed_chat_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

print("Completed")
