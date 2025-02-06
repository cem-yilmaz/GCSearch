import sys, re, math, time
from collections import defaultdict
import functools
import Stemmer
import xml.etree.ElementTree as ET

file_list = ['trec.5000.xml']
# Initialize the stemmer
stemmer = Stemmer.Stemmer('english')

# Load stopwords
with open('ttds_2023_english_stop_words.txt', 'r') as file:
    stop_words_set = set(re.findall(r'\b\w+\b', file.read()))

# Parsing the XML file to extract DOCNO, HEADLINE, and TEXT
def parse_trec_xml(file_path):
    # Dictionary to store document ID as key and a dictionary of HEADLINE and TEXT as value
    doc_texts = {}
    try:
        # Parse the XML tree structure from the given file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Iterate over each document in the XML tree
        for doc in root.findall('DOC'):
            # Extract DOCNO, HEADLINE, and TEXT fields, stripping extra spaces
            doc_id = doc.find('DOCNO').text.strip()
            headline = doc.find('HEADLINE').text.strip() if doc.find('HEADLINE') is not None else ""
            text = doc.find('TEXT').text.strip() if doc.find('TEXT') is not None else ""
            # Store the extracted fields in the doc_texts dictionary
            doc_texts[doc_id] = {'HEADLINE': headline, 'TEXT': text}

        return doc_texts  # Return the parsed document data
    except ET.ParseError as e:
        # Handle XML parsing errors gracefully
        print(f"XML parsing error: {e}")
    except Exception as e:
        # Catch other exceptions and print the error message
        print(f"An error occurred: {e}")

    return doc_texts  # Return an empty dictionary in case of errors

# Process each file in the file_list
for file_name in file_list:
    # print(f"\nProcessing file: {file_name}")
    start_time = time.time()  # Track the start time for performance measurement
    # Initialize an empty inverted index as a defaultdict of dictionaries where lists store term positions
    inverted_index = defaultdict(lambda: defaultdict(list))
    # Prepare output file names for the inverted index and preprocessed text
    inverted_index_output_file = f"index.txt"
    preprocessed_text_output_file = f"text_preprocessed.txt"

    # Parse the XML file to get the document texts (HEADLINE, TEXT)
    doc_texts = parse_trec_xml(file_name)

    # Open the output file to write the preprocessed document texts
    with open(preprocessed_text_output_file, 'w') as preprocessed_file:
        for doc_id, content in doc_texts.items():
            headline = content['HEADLINE']
            text = content['TEXT']

            # Write ID
            preprocessed_file.write(f"ID: {doc_id}\n")

            # Process HEADLINE
            if headline:
                tokenized_headline = re.findall(r'\b\w+(?:-\w+)*\b', headline.lower())
                stopped_headline = [term for term in tokenized_headline if term not in stop_words_set]
                normalized_headline = stemmer.stemWords(stopped_headline)
                preprocessed_file.write(f"HEADLINE: {' '.join(normalized_headline)}\n")

                # Add terms to the inverted index with positions starting from 1 for the headline
                for position, term in enumerate(normalized_headline, start=1):
                    inverted_index[term][doc_id].append(position)

            # Process TEXT
            if text:
                tokenized_text = re.findall(r'\b\w+(?:-\w+)*\b', text.lower())
                stopped_text = [term for term in tokenized_text if term not in stop_words_set]
                normalized_text = stemmer.stemWords(stopped_text)
                preprocessed_file.write(f"TEXT: {' '.join(normalized_text)}\n")

                # Continue the position numbering after the headline for the text terms
                start_position = len(normalized_headline) + 1  # Continue position after headline
                for position, term in enumerate(normalized_text, start=start_position):
                    inverted_index[term][doc_id].append(position)

    # Write the inverted index to the output file with sorted document IDs
    with open(inverted_index_output_file, 'w') as output_file:
        for term, doc_positions in sorted(inverted_index.items()):
            df = len(doc_positions)
            output_file.write(f"{term}: {df}\n")

            # Sort doc_positions by document IDs in ascending order
            for doc_id, positions in sorted(doc_positions.items(), key=lambda x: int(x[0])):
                positions_str = ",".join(map(str, positions))
                output_file.write(f"\t{doc_id}: {positions_str}\n")

    # Calculate and print the elapsed time for processing the file
    end_time = time.time()
    elapsed_time = end_time - end_time

    # Print the index.txt file and text_preprocessed.txt file and the time if you want to look at

    # print(f"Processed {file_name}, inverted index saved as {inverted_index_output_file}, "
    #       f"preprocessed text saved as {preprocessed_text_output_file}, "
    #       f"time taken: {elapsed_time:.4f} seconds")


# Tokenization function using regex to capture numbers, words, and hyphenated words
def tokenize_advanced(text):
    tokens = re.findall(r"\b\d+(?:\.\d+)?(?:-\w+)*'?\w*\b|\b\w+(?:-\w+)*'?\w*\b", text)
    return [token for token in tokens if token]

# Removes stopwords from token list
def remove_stopwords(tokens, stop_words):
    return [token.lower() for token in tokens if token.lower() not in stop_words]

# Applies stemming using the pystemmer library
def apply_pystemmer_stemming(tokens):
    stemmer = Stemmer.Stemmer('english')
    return [stemmer.stemWord(token) for token in tokens]

# Load custom stopwords from a file and store them in a set
def load_custom_stopwords(file_path):
    with open(file_path, 'r') as f:
        stop_words = set(word.strip() for word in f)
    return stop_words

# Preprocess single term
def preprocess_term(term):
    tokens = tokenize_advanced(term)  # Tokenize the query
    stop_words = load_custom_stopwords('ttds_2023_english_stop_words.txt')
    filtered_tokens = remove_stopwords(tokens, stop_words)
    stemmed_tokens = apply_pystemmer_stemming(filtered_tokens)  # Apply stemming
    return stemmed_tokens

# Loads the positional inverted index from a file
@functools.lru_cache()  # functools.lru_cache is mainly used for caching. It can save the results of relatively time-consuming functions to avoid repeated calculations of the same parameters.
def load_index(index_file):
    index = defaultdict(dict)  # The outer defaultdict for terms, inner dict for docID -> positions
    with open(index_file, 'r') as f:
        term = None  # Track the current term being processed
        for line in f:
            if line.startswith(' ') or line.startswith('\t'):  # If the line starts with space/tab -> docID and positions
                doc_id, positions = line.strip().split(':')
                doc_id = doc_id.strip()
                positions = list(map(int, positions.strip().split(',')))
                index[term][doc_id] = positions  # Store positions for the document under the current term
            else:
                term, df = line.strip().split(':')  # Split term and document frequency (df)
                term = term.strip().lower()  # In lowercase
                index[term] = defaultdict(list)  # Initialize with a defaultdict for documents
    return index

# Perform proximity search, checking if two terms appear within a specified distance
def proximity_search(term1, term2, distance):
    # Preprocess both terms before searching
    processed_term1 = preprocess_term(term1)[0]
    processed_term2 = preprocess_term(term2)[0]

    index = load_index("index.txt")
    postings_term1 = index.get(processed_term1, {})
    postings_term2 = index.get(processed_term2, {})
    result_docs = []

    # Find common documents containing both terms
    common_docs = set(postings_term1.keys()) & set(postings_term2.keys())
    for doc_id in common_docs:
        positions_term1 = postings_term1[doc_id]
        positions_term2 = postings_term2[doc_id]
        # Check if the terms occur within the specified distance in any common document
        if check_proximity(positions_term1, positions_term2, distance):
            result_docs.append(doc_id)
    return sorted(result_docs)

# Helper function to check if any pair of positions in two lists are within the specified proximity distance
def check_proximity(positions_term1, positions_term2, distance):
    for pos1 in positions_term1:
        for pos2 in positions_term2:
            if abs(pos1 - pos2) < distance:
                return True
    return False

# Compute the TF-IDF score for a term in a specific document
def compute_tfidf(term, doc_id, index, total_documents=10039-5000):
    # Calculate term frequency (TF)
    freq = len(index[term][doc_id])
    if freq == 0:
        return 0
    tf = 1 + math.log10(freq)

    # Calculate document frequency (DF) and inverse document frequency (IDF)
    df = len(index[term])
    idf = math.log10(total_documents / df) if df > 0 else 0

    # Return the TF-IDF score
    return tf * idf

# Perform ranked search for a single query, returning documents ordered by TF-IDF score
def ranked_search_one(query):
    query_terms = preprocess_term(query)  # Preprocess the query
    # print(query_terms)
    doc_scores = defaultdict(float)  # Store the document scores

    index = load_index("index.txt")

    for term in query_terms:
        if term in index:
            for doc_id in index[term]:
                tfidf = compute_tfidf(term, doc_id, index)
                doc_scores[doc_id] += tfidf  # Accumulate the score for the document

    # Return documents sorted by score in descending order
    ranked_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
    return ranked_docs

# Write ranked search results to file
def write_ranked_results(query_results, query_number, result_file, mode):
    with open(result_file, mode) as f:
        for doc_id, score in query_results:
            f.write(f"{query_number},{doc_id},{score:.4f}\n")

# Perform ranked search for a list of queries
def ranked_search(queries_ranked):
    for i, query in enumerate(queries_ranked, 1):
        result = ranked_search_one(query)

        # Write ranked results to the output file, overwriting for the first query and appending for the rest
        mode = 'w' if i == 1 else 'a'
        write_ranked_results(result, i, "results.ranked.txt", mode)

# Extract phrases from a query, replacing them with placeholders
def process_query_with_phrases(query):
    phrases = re.findall(r'"(.*?)"', query)  # Extract phrases within quotes
    modified_query = re.sub(r'"(.*?)"', 'PHRASE', query)  # Replace phrases with placeholders
    return modified_query, phrases

# Check if terms appear consecutively in the document
def check_phrase_positions(positions):
    for pos_list in zip(*positions):  # Align positions by term
        # Check if all positions are consecutive
        if all(pos_list[i] - pos_list[i - 1] == 1 for i in range(1, len(pos_list))):
            return True  # Found terms in consecutive positions
    return False  # No consecutive terms found

# Perform phrase search for a query
def phrase_search(phrase):
    terms = phrase.strip('"').split()
    processed_terms = preprocess_term(' '.join(terms))  # Preprocess the phrase
    index = load_index("index.txt")
    initial_docs = set(index.get(processed_terms[0], {}).keys())  # Get docs for first term

    # Find common documents containing all terms
    for term in processed_terms[1:]:
        initial_docs &= set(index.get(term, {}).keys())

    phrase_docs = []
    for doc in initial_docs:
        positions = [index[term][doc] for term in processed_terms]
        if check_phrase_positions(positions):  # Check if terms appear consecutively
            phrase_docs.append(doc)
    return sorted(phrase_docs)

# Get search result for a term or phrase from the index
def get_search_result(phrases, term, phrase_idx):
    if term == "phrase":
        result = set(phrase_search(f'"{phrases[phrase_idx]}"'))
        phrase_idx += 1  # Move to the next phrase
    else:
        processed_term = preprocess_term(term)[0]
        index = load_index("index.txt")
        result = set(index.get(processed_term, {}).keys())
    return result, phrase_idx

# Perform Boolean search with support for phrases
def boolean_search_with_phrases(query):
    # Extract phrases from the query and replace them with placeholders
    modified_query, phrases = process_query_with_phrases(query)

    # Split query into terms and operators (AND, OR, NOT)
    pattern = r'(?<!\w)(AND|OR|NOT)(?!\w)'  # Regex to detect AND, OR, NOT as separate words
    terms = re.split(pattern, modified_query)
    terms = [term.strip().lower() for term in terms if term.strip()]  # Clean and normalize terms
    # print("Parsed terms:", terms)

    result_docs = None  # Stores the final result set of document IDs
    phrase_idx = 0  # Tracks the current phrase to replace in the search results

    i = 0
    operator = None  # Track current operator (AND/OR/NOT)
    previous_operator = None  # Track the previous operator

    # Iterate through all terms and operators in the query
    while i < len(terms):
        term = terms[i]
        # If the current term is a Boolean operator, update the operator and continue
        if term in {"and", "or", "not"}:
            previous_operator = operator
            operator = term  # Update operator
            # print("Operator:", operator)
            i += 1
            continue

        # Get the search results for the term/phrase and update the phrase index
        result, phrase_idx = get_search_result(phrases, term, phrase_idx)
        # print(f"Processed term: {term}, result: {result}")

        # Load the index
        index = load_index("index.txt")
        # Apply NOT logic if needed
        if operator == "not":
            all_docs = set(index.keys())
            result = all_docs - result  # Negate the result(all docs except the result set)

            # Apply the previous operator with the negated result
            if previous_operator == "and":
                result_docs &= result
            elif previous_operator == "or":
                result_docs |= all_docs - result
            # Reset operators after applying NOT
            operator = None
            previous_operator = None
        else:
            if result_docs is None:
                result_docs = result
            else:
                if operator == "and":
                    result_docs &= result
                elif operator == "or":
                    result_docs |= result

        i += 1

    # Return the sorted list of document IDs or an empty list if no results
    if result_docs is None:
        return []
    return sorted(result_docs)

def write_results(query_results, query_number, result_file, mode):
    with open(result_file, mode) as f:
        sorted_results = sorted(query_results, key=int)  # Sort the document IDs numerically
        for doc_id in sorted_results:
            f.write(f"{query_number},{doc_id}\n")  # Write the results in "query_number,doc_id" format

def boolean_search(queries_search):
    for i, query in enumerate(queries_search, 1):
        result = None
        # Check if the query is a proximity search (contains '#')
        if '#' in query:
            proximity_match = re.search(r'#(\d+)\(\s*([^,]+)\s*,\s*([^,]+)\s*\)', query)
            if proximity_match:
                # Extract the proximity distance and terms for proximity search
                distance = int(proximity_match.group(1))
                term1 = proximity_match.group(2).strip()
                term2 = proximity_match.group(3).strip()
                result = proximity_search(term1, term2, distance)
        # If not a proximity search, perform a Boolean search or phrase search
        else:
            result = boolean_search_with_phrases(query)

        # Write results to a file
        mode = 'w' if i == 1 else 'a'
        write_results(result, i, 'results.boolean.txt', mode)

if __name__ == '__main__':
    # List of queries for ranked search
    queries_ranked = [
        "corporation tax reduction",  # First query
        "stock market in China",  # Second query
        "health industries",  # Third query
        "the artificial intelligence market",  # Forth query
        "the Israeli Palestinian conflict",  # Fifth query
        "information retrieval",  # Sixth query
        "Dow Jones industrial average stocks",  # Seventh query
        "will there be a reduction in taxes for corporates?",  # Eighth query
        "the gold prices versus the dollar value",  # Ninth query
        "FT article on the deal between BBC and BSkyB"  # Tenth query
    ]
    # Perform ranked search
    result = ranked_search(queries_ranked)

    # List of queries for Boolean search
    queries_search = [
        "Sadness",  # First query
        "Glasgow AND SCOTLAND",  # Second query
        "corporate AND taxes",  # Third query
        '"corporate taxes"',  # Forth query
        "#30(corporate,taxes)",  # Fifth query
        '"middle east" AND israel',  # Sixth query
        "#5(Palestinian,organisations)",  # Seventh query
        '"Financial times" AND NOT BBC',  # Eighth query
        '"wall street" AND "dow jones"',  # Ninth query
        "#20(dow,stocks)"  # Tenth query
    ]
    # Perform Boolean search
    result = boolean_search(queries_search)