#Efe

# Used imports: re for regex, PorterStemmer for stemming, ElementTree for XML parsing,
# math for log10 calculation
import re
from nltk import PorterStemmer
import xml.etree.ElementTree
import math

# Initialise Porter Stemmer and Element Tree
stemmer = PorterStemmer()
element_tree = xml.etree.ElementTree

# XML Parsing using ElementTree
with open(r'C:\Users\efeoz\PycharmProjects\TTDSCW1\resources\trec.5000.xml', 'r', encoding='utf-8') as file:
    xml_content = file.read()
xml_content = f"<ROOT>\n{xml_content}\n</ROOT>"
root = element_tree.fromstring(xml_content)

# Extracting the stop words (using the given set for the coursework) and splitting them
with open(r"C:\Users\efeoz\PycharmProjects\TTDSCW1\resources\ttds_2023_english_stop_words.txt", 'r', encoding='utf-8') as file:
    stop_words_set = set(file.read().split())

# Initialize an empty positional inverted index that will be updated in main()
positional_inverted_index = {}

# Initial document processing, first function to be called in main() before anything else
def document_processing():
    # Search for all DOC elements to find documents and initialise empty document term position list
    documents = root.findall('.//DOC')
    doc_term_positions = {}
    # Extracting document ID (DOCNO), document headline (HEADLINE) and document's main text (TEXT)
    # If headline or main text does not exist then just assign an empty string
    for document in documents:
        document_id = document.find('DOCNO').text.strip()
        headline = document.find('HEADLINE').text.lower() if document.find('HEADLINE') is not None else ""
        text = document.find('TEXT').text.lower() if document.find('TEXT') is not None else ""
        # Combine relevant headline and text
        combined_text = f"{headline} {text}"

        # Regex for tokenizing the combined text using the re library
        # First check: matching words & phrases with alphabetic characters (both upper and lower case)
        # Second check: matching Boolean operators -> AND, OR, NOT
        # Third check: matching queries starting with hashtag for proximity search
        tokenized_list = re.findall(r'\b[a-zA-Z]+\b|\b(?:AND|OR|NOT)\b|#\d+\b', combined_text)

        # Remove stop words and stem using Porter Stemmer and update document term positions with that
        stopped_list = [term for term in tokenized_list if term not in stop_words_set]
        normalized_list = [stemmer.stem(term) for term in stopped_list]
        doc_term_positions[document_id] = normalized_list

    return doc_term_positions

# Positional inverted indexing on the normalized list (doc_term_positions)
def positional_inverted_indexing(doc_term_positions):
    # Iterating over each item in the document term positions
    for doc_id, normalized_list in doc_term_positions.items():
        for index, term in enumerate(normalized_list):
            # Building the positional inverted index by appending the current index
            # If term or document ID does not exist, append empty lists to their places
            if term not in positional_inverted_index:
                positional_inverted_index[term] = {}
            if doc_id not in positional_inverted_index[term]:
                positional_inverted_index[term][doc_id] = []
            positional_inverted_index[term][doc_id].append(index)

    # Writing the positional inverted index into a file index.txt in appropriate format as described
    with open(r'C:\Users\efeoz\PycharmProjects\TTDSCW1\index.txt', 'w', encoding='utf-8') as file:
        for term, doc_positions in sorted(positional_inverted_index.items()):
            df = len(doc_positions)
            file.write(f"{term}:{df}\n")
            for doc_id, positions in sorted(doc_positions.items()):
                positions_str = ', '.join(map(str, positions))
                file.write(f"\t{doc_id}: {positions_str}\n")

# The next 3 functions are used for boolean search overall

# Part 1: Phrase search
def phrase_search(terms, doc_term_positions, positional_inverted_index):
    # Initialise a result list
    results = []

    # Iterate over each item with their document ID and positions and create a position list using list comprehension
    for doc_id, positions in doc_term_positions.items():
        positions_list = [positional_inverted_index[term][doc_id] for term in terms if
                          term in positional_inverted_index and doc_id in positional_inverted_index[term]]

        # If the length of the position list is not the same as the number of terms then skip this document
        if len(positions_list) != len(terms):
            continue

        # Iterate through positions of the first term and check for consecutive matches
        for i in range(len(positions_list[0])):
            consecutive_match = True
            for j in range(1, len(terms)):
                # Ensure the index does not go out of range and check if positions are consecutive
                if i + j >= len(positions_list[j]) or positions_list[j][i] != positions_list[0][i] + j:
                    consecutive_match = False
                    break

            # If consecutive positions are found, add the document to the result
            if consecutive_match:
                results.append(doc_id)
                break  # Move to the next document once a match is found

    # Return the phrase search results
    return results

# Part 2: Proximity search
def proximity_search(term1, term2, distance, doc_term_positions, positional_inverted_index):
    # Initialise a result list
    results = []

    # Initial check to see if both term 1 and term 2 are in the positional inverted index
    if term1 in positional_inverted_index and term2 in positional_inverted_index:
        # Then check if term 2 appears in the same document as term 1
        for doc_id in positional_inverted_index[term1]:
            if doc_id in positional_inverted_index[term2]:
                # Retrieve their positions
                positions_term1 = positional_inverted_index[term1][doc_id]
                positions_term2 = positional_inverted_index[term2][doc_id]
                # Check if any positions are within the specified distance
                for pos1 in positions_term1:
                    if any(abs(pos2 - pos1) <= distance for pos2 in positions_term2):
                        results.append(doc_id)
                        break
    # Return the proximity search results
    return results

# Part 3: Boolean search (including phrase and proximity search)
# NOTE: Try and except blocks and print statements exist in this function
# for debugging purposes since I had problems initially with query processing
# and therefore having missing values in the output
def boolean_search(positional_inverted_index, doc_term_positions):
    # Open the queries given in the coursework
    with open(r"C:\Users\efeoz\PycharmProjects\TTDSCW1\resources\queries.boolean.txt", 'r', encoding='utf-8') as file:
        queries = [query.strip() for query in file.readlines()]

    # Initialise a result list
    results = []
    # Iterate over each query in the specified queries.boolean file
    # Enumerate since file starts with "1 (query)" and continues like that
    for query_number, query in enumerate(queries, start=1):
        print(f"Processing query {query_number}: {repr(query)}")  # Debugging query content
        # If query has " then treat it as phrase search
        if '"' in query:
            # Extract the query inside the quotes
            phrase = re.findall(r'"([^"]+)"', query)[0]
            # Similar to index preprocessing, find words in the terms, turn them into lowercase
            # stem using Porter Stemmer and remove stop words
            phrase_terms = [stemmer.stem(term) for term in re.findall(r'\b\w+\b', phrase.lower()) if
                            term not in stop_words_set]
            # Execute phrase search on the terms and store the matching documents
            matching_docs = phrase_search(phrase_terms, doc_term_positions, positional_inverted_index)
        # If query has hashtag then treat it as proximity search
        # Due to problems with my regular expressions not working properly here
        # I used a splitting technique instead, this was before I had to debug
        elif '#' in query:
            # Try - except block for debugging purposes
            try:
                # Extract the proximity part, distance and the two terms
                proximity_part = query.split('#')[1].strip()
                distance = int(proximity_part.split('(')[0].strip())
                terms_part = proximity_part.split('(')[1].strip(')')
                term1, term2 = [term.strip().lower() for term in terms_part.split(',')]

                # Check extracted terms and distance for debugging purposes
                print(f"Proximity search for terms: '{term1}' and '{term2}' with distance {distance}")

                # Stem the terms
                term1 = stemmer.stem(term1)
                term2 = stemmer.stem(term2)

                # Check if terms exist in the index for debugging purposes
                if term1 in positional_inverted_index:
                    print(f"'{term1}' found in index.")
                else:
                    print(f"'{term1}' not found in index.")
                if term2 in positional_inverted_index:
                    print(f"'{term2}' found in index.")
                else:
                    print(f"'{term2}' not found in index.")

                # Execute proximity search on the terms and store the matching documents
                matching_docs = proximity_search(term1, term2, distance, doc_term_positions, positional_inverted_index)

                # Check results for debugging purposes
                if matching_docs:
                    print(f"Documents matched: {matching_docs}")
                else:
                    print("No matching documents found.")
            # Exception if error happens, again used for debugging purposes
            except Exception as e:
                print(f"Error processing proximity query {query}: {e}")
                continue
        # Otherwise just treat it as boolean search
        else:
            # Using the exact same regex in the document processing function
            # to ensure boolean operators are extracted
            terms = [stemmer.stem(term) for term in re.findall(r'\b[a-zA-Z]+\b|\b(?:AND|OR|NOT)\b|#\d+\b', query.lower()) if term not in stop_words_set]
            # Initialise matching documents containing the first term
            # then iterate over the rest to find intersections using &= shorthand
            matching_docs = set(positional_inverted_index.get(terms[0], {}).keys())
            for term in terms[1:]:
                matching_docs &= set(positional_inverted_index.get(term, {}).keys())

        # Appending the results in appropriate format
        for doc_id in matching_docs:
            results.append(f"{query_number},{doc_id}")

    # Writing the results into a file results.boolean.txt in appropriate format as described
    with open(r"C:\\Users\\efeoz\\PycharmProjects\\TTDSCW1\\results.boolean.txt", 'w') as file:
        for result in results:
            file.write(f"{result}\n")

# The next 2 functions are used for ranked IR using TFIDF overall

# Part 1: Calculate TF-IDF using the positional inverted index
def tfidf(positional_inverted_index, total_docs):
    # Initialise empty TF and IDF lists which will be updated later on
    tf = {}
    idf = {}

    # Part 1: Calculate TF
    # Iterate through each item in the positional inverted index and then
    # in that iterate through each document that contains the term
    for term, doc_list in positional_inverted_index.items():
        for doc_id, positions in doc_list.items():
            if doc_id not in tf:
                tf[doc_id] = {}
            # Calculate how many times the term appears in the document -> raw term frequency
            raw_term_frequency = len(positions)
            # Appropriate calculation using the TF formula described in lecture 7
            tf[doc_id][term] = 1 + math.log10(raw_term_frequency)

    # Part 2: Calculate IDF
    # Iterate through each item in the positional inverted index
    for term, doc_list in positional_inverted_index.items():
        # Calculate the number of documents that contain the term -> document frequency
        df = len(doc_list)
        # Appropriate calculation using the IDF formula described in lecture 7
        idf[term] = math.log10((total_docs) / (df))

    # Part 3: Calculate TF-IDF
    # Initialise empty TF-IDF list
    tfidf = {}
    # Iterate through each term
    for doc_id, term_freqs in tf.items():
        tfidf[doc_id] = {}
        for term, tf_value in term_freqs.items():
            # Multiply TF and IDF to get the final TF-IDF score for each term in the document
            # as described in the formula given in lecture 7
            tfidf[doc_id][term] = tf_value * idf.get(term, 0)

    # Return the TF-IDF result
    return tfidf


# Part 2: Calculate ranked IR using TF-IDF
def ranked_ir(tfidf, queries, positional_inverted_index):
    # Initialise a result list
    results = []
    # Iterate over each query in the specified queries.ranked file
    # Enumerate since file starts with "1 (query)" and continues like that
    for query_number, query in enumerate(queries, start=1):
        # Similar to index preprocessing, find words in the terms, turn them into lowercase,
        # stem using Porter Stemmer and remove stop words
        terms = [stemmer.stem(term) for term in re.findall(r'\b\w+\b', query.lower()) if term not in stop_words_set]
        # Initialise a dictionary to keep track of the scores
        doc_scores = {}
        # Iterate over the query terms
        for term in terms:
            # Check if the term is present and retrieve the relevant documents
            if term in positional_inverted_index:
                for doc_id in positional_inverted_index[term]:
                    if doc_id in tfidf and term in tfidf[doc_id]:
                        # Add the TF-IDF score of the term in the document to the document's score
                        doc_scores[doc_id] = doc_scores.get(doc_id, 0) + tfidf[doc_id][term]

        # Top 150 scores for each query are sorted in descending order for convenience
        # and rounded to 4 decimal places as described in the coursework
        sorted_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)[:150]
        for doc_id, score in sorted_docs:
            results.append(f"{query_number},{doc_id},{score:.4f}")

    # Writing the results into a file results.ranked.txt in appropriate format as described
    with open(r"C:\Users\efeoz\PycharmProjects\TTDSCW1\results.ranked.txt", 'w') as file:
        for result in results:
            file.write(f"{result}\n")

# Main loop to use all the implementations above and output the necessary files for coursework
def main():
    # Creation of the positional inverted index
    normalized_list = document_processing()
    positional_inverted_indexing(normalized_list)

    # Applying boolean search and outputting the results.boolean file
    boolean_search(positional_inverted_index, normalized_list)

    # Applying ranked IR using TFIDF and outputting the results.ranked file
    # Just an alternative approach in the main function for opening the relevant queries.ranked file
    # (could have been implemented like boolean search and vice versa)
    total_docs = len(normalized_list)
    tfidf_values = tfidf(positional_inverted_index, total_docs)
    with open(r"C:\Users\efeoz\PycharmProjects\TTDSCW1\resources\queries.ranked.txt", 'r', encoding='utf-8') as file:
        queries = [query.strip() for query in file.readlines()]
    ranked_ir(tfidf_values, queries, positional_inverted_index)

# Standard Python function for calling main()
if __name__ == '__main__':
    main()