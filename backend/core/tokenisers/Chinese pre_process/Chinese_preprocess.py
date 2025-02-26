# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 23:28:43 2025

@author: Layla
"""

import pandas as pd
import thulac
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

# 1. loadingstopwords
def load_stopwords(filepath="F:/hit_stopwords.txt"):
 
    with open(filepath, "r", encoding="utf-8") as f:
        stopwords = set(f.read().splitlines())
    return stopwords

# 2.inicialise
thulac_model = thulac.thulac(seg_only=True)

# 3. using THULAC tokeniser
def thulac_tokenizer(text, stopwords):
    
    text = re.sub(r'[^\u4e00-\u9fff]', ' ', text)

  
    words = thulac_model.cut(text, text=True).split()

    
    words = [word for word in words if word not in stopwords and len(word) > 1]

    return " ".join(words)


def compute_tfidf(corpus):
    """
    计算 TF-IDF 关键词权重，提取重要词。
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    
    tfidf_scores = []
    for row in tfidf_matrix.toarray():
        sorted_indices = row.argsort()[::-1]  # 按权重降序排列
        keywords = [feature_names[i] for i in sorted_indices[:5]]  # 取前 5 个关键词
        tfidf_scores.append(" ".join(keywords))
    
    return tfidf_scores

# 5. BERT 或 Word2Vec
def compute_sentence_embedding(texts):
   
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(texts)
    return embeddings

def preprocess_messages(df, stopwords):
    chat_messages = df['message'].dropna().astype(str)
    

    processed_tokens = chat_messages.apply(lambda text: thulac_tokenizer(text, stopwords))

 
    tfidf_keywords = compute_tfidf(processed_tokens)

  
    embeddings = compute_sentence_embedding(processed_tokens.tolist())

    
    processed_df = pd.DataFrame({
        "original_message": chat_messages,
        "processed_tokens": processed_tokens,
        "tfidf_keywords": tfidf_keywords,
        "embedding_vector": list(embeddings)  # 向量数据格式化
    })

    return processed_df


file_path = "F:/chatlog.csv"  # 确保文件路径正确
df = pd.read_csv(file_path)


stopwords = load_stopwords("F:/hit_stopwords.txt")


processed_chat_df = preprocess_messages(df, stopwords)


processed_chat_df.to_csv("F:/processed_chatlog_optimized.csv", index=False, encoding="utf-8-sig")


print(processed_chat_df.head())

