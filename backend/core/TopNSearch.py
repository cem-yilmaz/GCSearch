import os
import math
import jieba
import jieba.analyse
import thulac
import nltk
import re
import pandas as pd
from nltk import PorterStemmer
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize jieba (for Traditional Chinese)
jieba.set_dictionary("jeiba/dict.txt.big")

# Initialize THULAC (for Simplified Chinese)
thulac_model = thulac.thulac(seg_only=True)

# Initialize Porter Stemmer (for English)
stemmer = PorterStemmer()

# Download NLTK resources
nltk.download("punkt")
nltk.download("stopwords")
nltk.download('punkt_tab')

# Function to load stopwords from file
def load_stopwords(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())

# Load stopwords for various languages
STOPWORDS = {
    "zh_trad": load_stopwords("jeiba/stop_words.txt"),   # Traditional Chinese
    "zh_simp": load_stopwords("jeiba/hit_stopwords.txt"),  # Simplified Chinese
    "en": set(stopwords.words("english")),
    "tr": set(stopwords.words("turkish"))
}


# Tokenize function using a specified language if provided
def tokenize(text, lang=None):   
    if lang in ["zh_trad", "zh_simp"]:
        # For Chinese, we don't filter out single characters.
        if lang == "zh_trad":
            words = jieba.cut_for_search(text)
        else:
            text = re.sub(r'[^\u4e00-\u9fff]', ' ', text)
            words = thulac_model.cut(text, text=True).split()
        tokens = [w for w in words if w not in STOPWORDS[lang]]
    elif lang == "en":
        words = nltk.word_tokenize(text)
        words = [stemmer.stem(word.lower()) for word in words if word.isalpha()]
        tokens = [w for w in words if w not in STOPWORDS[lang] and len(w) > 1]
    elif lang == "tr":
        words = nltk.word_tokenize(text, language="turkish")
        tokens = [w for w in words if w not in STOPWORDS[lang] and len(w) > 1]
    else:
        tokens = text.split()
    
    return " ".join(tokens)

# Compute BERT embeddings using SentenceTransformers
def compute_sentence_embedding(texts):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(texts)
    return embeddings

def compute_tfidf(corpus):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    
    tfidf_scores = []
    for row in tfidf_matrix.toarray():
        sorted_indices = row.argsort()[::-1]
        keywords = [feature_names[i] for i in sorted_indices[:5]]
        tfidf_scores.append(" ".join(keywords))
    
    return tfidf_scores

# merge message by same doc_n
def merge_messages_by_doc_id(df):
    # merge the same doc_n messages
    merged_df = df.groupby("doc_id")["message"].apply(
        lambda msgs: " ".join([str(msg) for msg in msgs if pd.notnull(msg)])
    ).reset_index()
    return merged_df

# pre_process the message and make into tokenized csv file
def preprocess_messages(df, default_lang=None):
    # merge doc_n message to comput score
    merged_df = merge_messages_by_doc_id(df)
    
    doc_ids = merged_df["doc_id"]
    chat_messages = merged_df["message"].astype(str)
    
    # tokenization
    processed_tokens = chat_messages.apply(lambda text: tokenize(text, lang=default_lang))
    
    # compute TF-IDF
    tfidf_keywords = compute_tfidf(processed_tokens.tolist())
    embeddings = compute_sentence_embedding(processed_tokens.tolist())
    processed_df = pd.DataFrame({
        "doc_id": doc_ids,
        "original_message": chat_messages,
        "processed_tokens": processed_tokens,
        "tfidf_keywords": tfidf_keywords,
        "embedding_vector": list(embeddings)
    })
    return processed_df

# Build the positional inverted index (PII)
def build_positional_inverted_index_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    index = {}
    position_track = {}
    
    for _, row in df.iterrows():
        doc_id = row["doc_id"]
        tokens_str = row["processed_tokens"]
        if pd.isna(tokens_str):
            continue
        tokens = tokens_str.split()
        if doc_id not in position_track:
            position_track[doc_id] = 0
        for token in tokens:
            if token not in index:
                index[token] = {}
            if doc_id not in index[token]:
                index[token][doc_id] = []
            index[token][doc_id].append(position_track[doc_id])
            position_track[doc_id] += 1
    return index

# Write the positional inverted index to a file
def write_positional_index_to_file(index, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for token, postings in index.items():
            df_value = len(postings)
            f.write(f"{token}: {df_value}\n")
            for doc_id, positions in postings.items():
                pos_str = ", ".join(str(pos) for pos in positions)
                f.write(f"   {doc_id}: {pos_str}\n")
            f.write("\n")

def read_csv_file(filepath):
    # sep
    df = pd.read_csv(filepath)
    
    # ensure the columns are there
    required_cols = ["doc_id", "message", "is_media"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV must include '{col}' column")
    
    # select is_media is False message
    filtered_df = df[df["is_media"].astype(str).str.upper() == "FALSE"]
    
    # keep ["doc_id"] and ["message"] 
    text_df = filtered_df[["doc_id", "message"]].dropna().astype(str)
    return text_df

def search_query(query, positional_index, tokenize_fn, top_n=10):
    """
    Search for a text query against a positional inverted index (PII) using
    variable tokenising. Supports:
      - a basic Boolean search (if query contains operators like AND/OR/NOT)
      - default BM25 ranking search otherwise
      
    Returns:
      List of tuples (doc_id, score) ranked by score.
    """
    
    # If query contains Boolean operators, call the boolean search parser.
    if any(op in query.upper() for op in [" AND ", " OR ", " NOT "]):
        return boolean_search(query, positional_index, tokenize_fn, top_n)
    
    # Default: tokenize and use BM25 scoring.
    tokens = tokenize_fn(query).split()
    return bm25_search(tokens, positional_index, top_n)

def bm25_search(tokens, positional_index, top_n=10):
    """
    Computes BM25 scores for documents that contain query tokens.
    Uses the PII to extract term frequency and positional data.
    """
    # build a document lengths dictionary from the index.
    doc_lengths = {}
    for token, postings in positional_index.items():
        for doc_id, positions in postings.items():
            # assuming positions start at 0 and are contiguous,
            # document length is max(position) + 1.
            doc_lengths[doc_id] = max(doc_lengths.get(doc_id, 0), max(positions) + 1)
    N = len(doc_lengths)
    avgdl = sum(doc_lengths.values()) / N if N > 0 else 0

    k1 = 1.5
    b = 0.75
    scores = {}

    for token in tokens:
        if token not in positional_index:
            continue
        doc_freq = len(positional_index[token])
        idf = math.log((N - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
        for doc_id, positions in positional_index[token].items():
            tf = len(positions)
            dl = doc_lengths[doc_id]
            score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avgdl))))
            scores[doc_id] = scores.get(doc_id, 0) + score

    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return ranked_results

def boolean_search(query, positional_index, tokenize_fn, top_n=10):
    tokens = [t for t in tokenize_fn(query).split() if t.upper() not in ["AND", "OR", "NOT"]]
    
    candidate_docs = None
    for token in tokens:
        if token in positional_index:
            docs = set(positional_index[token].keys())
            candidate_docs = docs if candidate_docs is None else candidate_docs.intersection(docs)
        else:
            candidate_docs = set()
            break
    
    scores = {}
    if candidate_docs:
        for doc in candidate_docs:
            score = 0
            for token in tokens:
                if token in positional_index and doc in positional_index[token]:
                    score += len(positional_index[token][doc])
            scores[doc] = score
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

def load_index(index_file):
    index = {}
    with open(index_file, "r", encoding="utf-8") as f:
        current_token = None
        for line in f:
            if line.strip() == "":
                continue
            if not line.startswith(" "):
                parts = line.split(":", 1)
                current_token = parts[0].strip()
                index[current_token] = {}
            else:
                line_content = line.lstrip()  # 只移除左側空格
                doc_part = line_content.split(":", 1)
                if len(doc_part) == 2:
                    doc_id = doc_part[0].strip()
                    positions = [int(pos.strip()) for pos in doc_part[1].split(",") if pos.strip()]
                    index[current_token][doc_id] = positions
    return index

def search_pii(index_file, query, top_n=5):
    positional_index = load_index(index_file)
    return search_query(query, positional_index, tokenize, top_n)

#  server.py  format
def GetTopNResultsFromSearch(pii_name, query, n):
    """
    return topn results by pii and search query

    param:
      pii_name (str): e.g. core/piis/instagram__chatname.pii.txt
      query (str): query search
      n (int): top n results
      
    return:
      dict: e.g. { 4: 0.8169, 24: 0.7846, ... }
            key is doc_id (int),value is float
    """
    BASE_PATH = "/GCSearch"
    index_file = os.path.join(BASE_PATH, "backend", "core", "piis", f"{pii_name}.pii.txt")
    results = search_pii(index_file, query, top_n=n)
    
    result_dict = {}
    for doc_id, score in results:
        try:
            # doc_n to n
            doc_id_int = int(doc_id.split('_')[-1])
        except Exception:
            doc_id_int = doc_id
        result_dict[doc_id_int] = score
    return result_dict

#----------------- execution ------------------
if __name__ == "__main__":
    allowed_languages = {"zh_trad", "zh_simp", "en", "tr"}
    default_language = input("Please enter the default language (options: zh_trad, zh_simp, en, tr): ").strip()
    if default_language not in allowed_languages:
        print("Invalid input. Defaulting to English.")
        default_language = "en"
    inputpath = input("Please enter the ChatLog csv file path: ")
    input_csv_path = inputpath
    # platform and chatname
    platform = input("Please enter the platform name: ")      # e.g.LINE
    chatname = input("Please enter the chatname: ")   # e.g.chatname
    BASE_PATH = "/GCSearch"
    output_csv_path = os.path.join(BASE_PATH, "backend", "core", "out", "chatlogs", f"{platform}__{chatname}.chatlog.csv")

    print("Reading chatlog CSV file")
    df = read_csv_file(input_csv_path)

    print("Pre-processing text messages using default language:", default_language)
    processed_chat_df = preprocess_messages(df, default_lang=default_language)
    print("Completed process stage")

    print("Saving processed chatlog to CSV...")
    processed_chat_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print("Completed!")

    print("Building PII from input CSV...")
    pi_index = build_positional_inverted_index_from_csv(output_csv_path)
    print("PII construction completed.")

    
    BASE_PATH = "/GCSearch"
    output_index_file = os.path.join(BASE_PATH, "backend", "core", "piis", f"{platform}__{chatname}.pii.txt")
    print("Writing PII to file...")
    write_positional_index_to_file(pi_index, output_index_file)
    print("Saved file:", output_index_file)

    print("\nTopN Search Function: ")
    # if query contains operator ['AND','OR','NOT'] then return boolean score, 
    # otherwise, default as BM25 score
    query = input("Enter a search query: ") 
    
    # test GetTopNResultsFromSearch def
    #  pii_name same with "line__chatname"
    pii_name = input("Enter the pii_name (e.g. line__chatname): ")
    n = int(input("Enter the number of top results to return: "))
    top_results = GetTopNResultsFromSearch(pii_name, query, n)
    print("GetTopNResultsFromSearch result:", top_results)
    