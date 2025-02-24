# import modules
import re
import math
import Stemmer  # using PyStemmer
import xml.etree.ElementTree as ET  # to read the xml file
from collections import defaultdict  # for positional inverted index

# stop words for removing provided common words
def sw(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        stop_words = set(word.strip() for word in f if word.strip())
    return stop_words
stop_words = sw('stopwords.txt')
# import porter stemmer from the Pystemmer
stemmer = Stemmer.Stemmer('english')

def token_text(text, stop_words):
    text = text.lower()  # case folding
    token = re.findall(r'\b\w+\b', text.replace("-", " ").replace("'", ""))  
    stop_w = [t for t in token if t not in stop_words]  # remove stopword
    stem_w = [stemmer.stemWord(t) for t in stop_w]  # stemming
    return stem_w


def xml_r(filename):
    p_index = defaultdict(lambda: defaultdict(list))  # positional inverted index
    documents = {}
    # read xml file
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for doc in root.findall('DOC'):
        doc_id = int(doc.find('DOCNO').text.strip())  # extract document <ID>
        headline = doc.find('HEADLINE').text.strip() # extract <headline>
        text = doc.find('TEXT').text.strip() # extract <text>
        documents[doc_id] = {'headline': headline, 'text': text} # save the findings into the dictionary
        terms = token_text(text, stop_words)
        for position, t in enumerate(terms):
            p_index[t][doc_id].append(position)  # store positions of the terms' to the p_index

    return documents, p_index

def phrase_search(phrase, p_index, documents):
    terms = token_text(phrase, stop_words)
    if not terms:
        return set()
    
    if any(t not in p_index for t in terms): # ensuring all terms are in the index
        return set()

    first_t_docs = p_index[terms[0]] # finding the first term
    results_ph = set()

    for doc_id, positions in first_t_docs.items():
        for pos in positions:
            if all((pos + i) in p_index[terms[i]][doc_id] for i in range(1, len(terms))):
                results_ph.add(doc_id)
    
    return results_ph


def proximity_search(t1, t2, distance, p_index):
    
    if t1 not in p_index or t2 not in p_index:
        return set()
    results_pro = set()

    for doc_id in p_index[t1]:
        if doc_id in p_index[t2]:
            pos1 = p_index[t1][doc_id] # position 1
            pos2 = p_index[t2][doc_id] # position 2
            for p1 in pos1:
                for p2 in pos2:
                    if abs(p1 - p2) <= distance: # the distance between two positions
                        results_pro.add(doc_id)   
    return results_pro

def boolean(query, documents, stop_words, p_index):
    tokens = query.split() 

    result = None
    operator = None
    i = 0

    while i < len(tokens):
        token = tokens[i]
        m_doc = set()  # initialize

        # for the phrase searching
        if token.startswith('"') and token.endswith('"'): # determined to be a phrase
            phrase = token.strip('"') # removing "
            m_doc = phrase_search(phrase, p_index, documents)
            
        # for the proximity searcing
        elif token.startswith('#'):  # determined to be a proximity search
            match = re.match(r"#(\d+)\((\w+),\s*(\w+)\)", token) # ensure it is for the proximity searching
            if match:
                distance = int(match.group(1))
                t1 = token_text(match.group(2), stop_words)[0]
                t2 = token_text(match.group(3), stop_words)[0]
                m_doc = proximity_search(t1, t2, distance, p_index)
                
        # boolean searching
        elif token.upper() == 'AND':
            operator = 'AND'
        elif token.upper() == 'OR':
            operator = 'OR'        
        elif token.upper() == 'AND NOT':
            operator = 'AND NOT'
        else:  # if it is not for the above search, then view it as the normal word search
            t = token_text(token, stop_words)
            if t:  
                m_doc = {doc_id for doc_id, content in documents.items() if t[0] in token_text(content["text"], stop_words)}                
        if result is None:
            if m_doc:  
                result = m_doc
        else:
            if operator == 'AND':
                result &= m_doc if m_doc else result
            elif operator == 'OR':
                result |= m_doc
            # for the 'AND NOT', finding the documents with the term after 'NOT', and then remove them from the result
            elif operator == 'AND NOT':
                if m_doc: 
                    if i + 1 < len(tokens):
                        next_t = token_text(tokens[i + 1], stop_words)
                        if next_t:  
                            remove = {doc_id for doc_id, content in documents.items() if next_t[0] in token_text(content["text"], stop_words)}
                            result -= remove
                            
                    i += 1  # next document
        i += 1

    return result if result else set()

def tfidf(documents, stop_words):
    t_freq = defaultdict(lambda: defaultdict(int)) # t frequencies
    d_freq = defaultdict(int) # document frequencies
    total = len(documents)

    # calculate t frequencies and document frequencies
    for doc_id, doc_content in documents.items():
        terms = token_text(doc_content['text'], stop_words)
        doc_t = set()

        for t in terms:
            t_freq[t][doc_id] += 1  # calculate t freq. in the doc.
            doc_t.add(t)

        for t in doc_t:
            d_freq[t] += 1  # calculate doc freq. that t appears in

    return t_freq, d_freq, total

# calculate the scores
def tfidf_score(t, doc_id, t_freq, d_freq, total):
    tf = t_freq[t][doc_id]  # t freq. in document
    df = d_freq[t]  # doc freq. within documents
    idf = math.log10(total / (1 + df))  # calculate the idf
    return (1 + math.log10(tf)) * idf 

# the ranking
def tfidf_search(query, t_freq, d_freq, total, stop_words):
    q_t = token_text(query, stop_words) # queries 
    doc_scores = defaultdict(float)

    for t in q_t:
        if t in t_freq:
            for doc_id in t_freq[t]:
                tfidf_scores = tfidf_score(t, doc_id, t_freq, d_freq, total)
                doc_scores[doc_id] += tfidf_scores  # sum the tfidf score for each documents

    # the ranking of the scores
    rank = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    return rank


# to output the file
def output(index, output_file):
    with open(output_file, 'w') as file:
        for t, postings in index.items():
            df = len(postings)  
            file.write(f'{t}:{df}\n')
            for doc_id, positions in postings.items():
                positions_str = ",".join(map(str, positions))  # separating by commas
                file.write(f'\t{doc_id}: {positions_str}\n')


stop_words = sw('stopwords.txt') # using the stop words list provided on the website
CW1 = 'trec.5000.xml'  # input file
CW1_b = 'queries.boolean.txt' 
CW1_r = 'queries.ranked.txt'
CW1_1 = 'index.txt'  # index output filename
documents, p_index = xml_r(CW1)
output(p_index, CW1_1) # output index file

# output boolean file
with open(CW1_b, 'r') as query_file:
    boolean_queries = query_file.readlines() #read

with open('results.boolean.txt', 'w') as file:
    for line in boolean_queries:
        q_num, query = line.split(maxsplit=1)
        q_num = int(q_num.strip())
        query = query.strip()
        bool_q = boolean(query, documents, stop_words, p_index)
        for doc_id in bool_q: #write into the output file
            file.write(f'{q_num},{doc_id}\n')
            
# output ranked file
with open(CW1_r, 'r') as query_file:
    ranked_queries = query_file.readlines() #read

with open('results.ranked.txt', 'w') as file:
    for line in ranked_queries:
        q_num, query = line.split(maxsplit=1)
        q_num = int(q_num.strip())
        query = query.strip()
        t_freq, d_freq, total = tfidf(documents, stop_words)
        rank = tfidf_search(query, t_freq, d_freq, total, stop_words)
        for doc_id, score in rank: # write into the output file
            file.write(f'{q_num},{doc_id},{score:.4f}\n')


