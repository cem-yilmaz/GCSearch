# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 22:25:07 2024

@author: Layla
"""

#pre-process text
import re
import nltk
from   nltk.stem   import PorterStemmer
from   collections import defaultdict, Counter
import math
import os
import xml.etree.ElementTree as ET



#tokenisation
def tokenisation(text):
    tokens=re.findall(r'\b\w+\b',text.lower())
    return tokens

#stopwords
def load_stopwords():
    with open("F:/ttds_2023_english_stop_words.txt","r") as file:
        stopwords=set()
        for line in file:
            words=line.strip().split()
            stopwords.update(words)
    return stopwords

def remove_stopwords(tokens,stopwords):
    return [word for word in tokens if word not in stopwords]

#stemming
def stem(tokens):
    stemmer     = PorterStemmer()
    stem_tokens = [stemmer.stem(word) for word in tokens]
    return stem_tokens

#pre_process
def preprocess(text):
    tokens    = tokenisation(text)
    stopwords = load_stopwords()
    tokens    = remove_stopwords(tokens,stopwords)
    tokens    = stem(tokens)
    return tokens

#parsw XML
def xml(xml_path):
    with open(xml_path, "r", encoding="utf-8") as file:
        content = file.read().strip()
    
    root      = ET.fromstring(content)
    documents = []
    
    for doc in root.findall("DOC"):
        doc_id    = doc.find("DOCNO").text.strip()
        headline  = doc.find("HEAD").text.strip() if doc.find("HEAD") is not None else ""
        text      = doc.find("TEXT").text.strip() if doc.find("TEXT") is not None else ""
        full_text = headline + " " + text
        documents.append((doc_id, full_text))
    
    return documents

class position_inverse_index:
    def __init__(self):
        self.index     = defaultdict(lambda: defaultdict(list))
        self.doc_count = 0
    
    def add_doc(self,doc_id,text):
        tokens = preprocess(text)
        for pos, term in enumerate(tokens):
            self.index[term][doc_id].append(pos)
        self.doc_count += 1
    #positional inverted index
    def build_index_from_xml(self,text):
        documents = xml(text)  
        for doc_id, content in documents:
            self.add_doc(doc_id, content)  # 

    def write(self,output):
        with open(output, 'w', encoding='utf-8') as file:
            for term, docs in sorted(self.index.items()):
                df = len(docs)
                file.write(f"{term}:{df}\n")
                for doc_id, pos in docs.items():
                    positions_str = ",".join(map(str, pos))
                    file.write(f"\t{doc_id}: {positions_str}\n")
    
    #Boolean search
    def boolean_search(self, query):
        query = query.strip()
        #print(f"Processing Query: {query}")  # Debug output
    
        if "AND" in query:
            terms  = query.split("AND")
            result = None  # Initialize as None
        
            for term in terms:
                term = term.strip()
                if term in self.index:
                    if result is None:
                        result = set(self.index[term])  # Initialize with the first term's documents
                    else:
                        result &= set(self.index[term])  
            if result is None:  # If no terms were found, return an empty set
                return set()
        
            #print(f"Result for Query: {result}")  # Debug output
            return result

        elif "OR" in query:
            terms  = query.split("OR")
            result = set()
            for term in terms:
                term = term.strip()
                if term in self.index:
                    result |= set(self.index[term])  
            #print(f"Result for Query: {result}")  # Debug output
            return result

        elif "NOT" in query:
            terms  = query.split("NOT")
            term   = terms[0].strip()
            n_term = terms[1].strip()
            result = set(self.index[term]) if term in self.index else set()
            if n_term in self.index:
                result -= set(self.index[n_term])  # 执行 NOT 操作
            #print(f"Result for Query: {result}")  # Debug output
            return result
    
        else:
            result = set(self.index[query.strip()]) if query.strip() in self.index else set()
            #print(f"Result for Query: {result}")  # Debug output
            return result

  
    
  #Phrase search
    def phrase_search(self,phrase):
        word = phrase.strip('"').split
        if not word:
            return set()
        result = set(self.index[word[0]]) #initialisation
        for i in range(1, len(word)):
            result &= set(self.index[word[i]])
        
        valid_doc = set()
        for doc_id in result:
            position = [self.index[word][doc_id] for word in word]
            if all(any((pos1 - pos0) == i for i, pos0 in enumerate(position[j]) for pos1 in position[j + 1]) for j in range(len(position) - 1)):
                valid_doc.add(doc_id)
        return valid_doc
    
    #Proximity search
    def proximity_search(self, term1, term2, distance):
        doc1       = set(self.index[term1])
        doc2       = set(self.index[term2])
        results    = doc1 & doc2 
        valid_docs = set()

        for doc_id in results:
            position1 = self.index[term1][doc_id]
            position2 = self.index[term2][doc_id]
            for pos1 in position1:
                for pos2 in position2:
                    if abs(pos1 - pos2) <= distance:
                        valid_docs.add(doc_id)
                        break

        return valid_docs 
    
    #TFIDF
    def tfidf_search(self, query):
        tokens    = preprocess(query)
        tf_score  = defaultdict(float)
        doc_freq  = defaultdict(int)

        for term in tokens:
            if term in self.index:
                doc_freq[term] = len(self.index[term])
                for doc_id in self.index[term]:
                    tf_score[doc_id] += len(self.index[term][doc_id])

        N = self.doc_count
        scores = {}
        for doc_id, tf in tf_score.items():
            score = (1 + math.log10(tf)) * math.log10(N / doc_freq[term])  # TF-IDF calculation
            scores[doc_id] = score

        # Sort results by score in descending order
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores

def process_boolean(index, query_file, result_file):
    with open(query_file, 'r',encoding="utf-8") as file:
        queries = file.readlines()

    with open(result_file, 'w',encoding="utf-8") as file:
        for line in queries:
            query_num, query_text = line.split(maxsplit=1)
            results = index.boolean_search(query_text.strip())
            for doc_id in results:
                file.write(f"{query_num},{doc_id}\n")

def process_ranked(index, query_file, result_file):
    with open(query_file, 'r',encoding="utf-8") as file:
        queries = file.readlines()

    with open(result_file, 'w',encoding="utf-8") as file:
        for line in queries:
            query_num, query_text = line.split(maxsplit=1)
            results = index.tfidf_search(query_text.strip())
            sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
            top_results = sorted_results[:150]
            for doc_id, score in top_results:
                file.write(f"{query_num},{doc_id},{score:.4f}\n")




xml_path="F:/cw1collection/trec.5000.xml"
index = position_inverse_index()
index.build_index_from_xml(xml_path)
index.write("F:/index.txt")
process_boolean(index, "F:/cw1collection/queries.boolean.txt", 'F:/results.boolean.txt')
process_ranked(index, "F:/cw1collection/queries.ranked.txt", 'F:/results.ranked.txt')

      
