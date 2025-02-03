import re # used for tokenisation
import xmltodict # used for parsing xml
#import json # used for pretty-printing the xml [unused in final submission]
from nltk import PorterStemmer # for stemming
#import random # used for testing purposes (e.g. picking random documents) [unused in final submission]
#import time # used for computing the time remaining for some algorithms [unused in final submission]
import math # used for tfidf stuff

# Defining a few globals

## stopwords
with open("stopwords.txt", "r") as f:
    stopwords = f.read().splitlines()

## collections xml filepath
collections_xml = "collections/trec.sample.xml"

## Porter Stemmer
stemmer = PorterStemmer()

# Pre-processing the xml file
challenge = True
## Pre-processing an individual token
def pre_process_token(token: str) -> str:
    """
    Pre-processes a single token. Applies
    - Case folding
    - Elimination if token is a stopword
    - Porter Stemming
    Args:
        token: Token to be pre-processed.
        challenge: If this is enabled, the challenge tokenisation (no stopping) will be applied. Default is `False`.
    Returns:
        The pre-processed token (`None` if token was stopword).
    """
    #if not re.match(r'^[a-zA-Z]+$', token):
    #   return None
    
    if (token in stopwords) and not challenge: 
        return None
    else:
        stemmed_token = stemmer.stem(token, to_lowercase=True) # stemmer will do the Case Folding for us
        return stemmed_token

## Creating a list of tokens from the document   
def create_tokens_from_document(doc : str) -> list[str]:
    """
    Given a document, returns a list of tokens in that document (in order of appearance)
    Args:
        doc: The document to be tokenised, all as one string
    Returns:
        A list of tokens in the document.
    """
    # Split the document at non-letter characters
    tokens = re.split(r'[^a-zA-Z]', doc) # could possible be edited to include numbers?
    # remove empty tokens from the list, and also remove any tokens containing numbers
    return [token for token in tokens if token and not any(char.isdigit() for char in token)]

## Combining the previous functions to FULLY pre-process the document
def pre_process_document(doc : str) -> list[str]:
    """
    FULLY Pre-processes a document. Applies
    - Tokenisation
    - Case folding
    - Elimination of stopwords
    - Porter Stemming
    Args:
        doc: The document to be pre-processed, all in one string.
    Returns:
        The pre-processed document, as a list of tokens.
    """
    tokens = create_tokens_from_document(doc)
    # pre-process each token, and add it to the list of pre-processed tokens if it is not None
    return [pre_process_token(token) for token in tokens if pre_process_token(token)]

## Actually pre-processing the xml file into a dictionary, indexed by `DOCNO`
def pre_process_xml_file(xml_filepath : str) -> dict:
    """
    Extracts text from an xml file, pre-processes it, and returns it as a dictionary (indexed by `DOCNO`, with a combination of `HEADLINE` and `TEXT` as the value).

    The headline will be trimmed to isolate the actual text content. An example transformation is:
    ```
    FT  14 MAY 91 / (CORRECTED) UK Company News: Geevor merger hits rocks over pre-conditions -> Geevor merger hits rocks over pre-conditions
    ```

    Intended for use with `trec.sample.xml`, but could technically be used with any xml file with the following structure:

    ```
    <document>
        <DOC>
            <DOCNO>...</DOCNO>
            ...
            <HEADLINE>...</HEADLINE>
            <TEXT>...</TEXT>
            ...
        </DOC>
        ...
    ```
    Args:
        xml_filepath: The path to the xml file.
    Returns:
        A simplified dictionary representation of the xml file, indexed by `DOCNO`.
    """
    with open(xml_filepath, "r") as f:
        xml_str = f.read() # get the raw representation of the xml file

    xml_dict = xmltodict.parse(xml_str)
    # using xmltodict, all documents are stored as children of the single "document" key
    docs = xml_dict["document"]["DOC"]

    def process_headline(headline : str) -> str:
        """
        Processes a headline, trimming it to isolate the actual text content.
        Args:
            headline: The headline to be processed.
        Returns:
            The text content of the headline.
        """
        # All headlines start with the format "FT  DD MMM YY /", which we remove by getting the content after the 4th space
        removed_date = headline.split(" ", 4)[-1]
        # The headline then also sometimes contains "(CORRECTED)" to denote a correction
        #   The actual document content will denote this correction so we don't need to worry about losing information
        removed_correction = removed_date.replace("(CORRECTED)", "").strip()
        # Finally, the document may also have a category prefix (e.g. "UK Company News:"). We want to remove this as well, if it exists
        if ":" in removed_correction:
            return removed_correction.split(":", 1)[-1].strip()
        else:
            return removed_correction

        
    return {
        doc["DOCNO"]: pre_process_document(
            process_headline(doc["HEADLINE"]) + " " + doc["TEXT"]
        ) for doc in docs
    }

## The following functions aren't really used in the coursework but are for my own development purposes
def print_pre_processed_document(doc : list[str]) -> None:
    """
    Pretty-prints a pre-processed document.
    Args:
        doc: The pre-processed document to be printed.
    """
    print(" ".join(doc))

def export_pre_processed_dict(pre_processed_dict : dict, output_filepath : str, addLineBreaks=False) -> None:
    """
    Exports the pre-processed dictionary to a file. 
    
    Exports the following structure:
    ```
    DOCNO: token1 token2 token3 ...
    DOCNO: token1 token2 token3 ...
    ...
    ```

    Intended for use for dictionaries created from `pre_process_xml_file(trec.sample.xml)`.
    Args:
        pre_processed_dict: The pre-processed dictionary to be exported.
        output_filepath: The path to the file to be written to.
        addLineBreaks: Whether to add line breaks between documents. This eases user readability but parsing may be more annoying with this enabled. Default is `False`.
    """
    with open(output_filepath, "w") as f:
        for docno, doc in pre_processed_dict.items():
            f.write(f"{docno}: {' '.join(doc)}\n")
            if addLineBreaks:
                f.write("\n")

def import_dict_from_file(filepath : str) -> dict:
    """
    Imports a dictionary from a file. 
    
    Expects the following structure:
    ```
    DOCNO: token1 token2 token3 ...
    DOCNO: token1 token2 token3 ...
    ...
    ```

    Intended for use for dictionaries exported with `export_pre_processed_dict(pre_processed_dict, output_filepath)`.
    Args:
        filepath: The path to the file to be read from.
    Returns:
        The dictionary read from the file.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()
    return {
        line.split(":")[0]: line.split(":")[1].split() for line in lines
    }

#trec = pre_process_xml_file(collections_xml)
#export_pre_processed_dict(trec, "trec.sample.preprocessed.txt")
#trec = import_dict_from_file("trec.sample.preprocessed.txt")
# Creating the Positional Inverted Index

## Getting the stuff to fill the index

### Getting the unique terms
def get_unique_terms(dict_of_docs : dict) -> set:
    """
    Given a dictionary of documents, returns the set of unique terms in the documents.
    Args:
        dict_of_docs: The dictionary of documents.
    Returns:
        The set of unique terms in the documents.
    """
    return {term for doc in dict_of_docs.values() for term in doc}

### Getting the number of documents that contain a term
def get_num_of_docs_with_term(dict_of_docs : dict, term : str) -> int:
    """
    Gets the number of documents that contain a term.
    Args:
        dict_of_docs: The dictionary of documents.
        term: The term to search.
    Returns:
        The number of documents that contain the term.
    """
    return sum(1 for doc in dict_of_docs.values() if term in doc)

### Getting the positions of a term in a given document
def get_positions_in_doc(document : list[str], term : str) -> list[int]:
    """
    Get a list of all the positions of `term` in `document`. Terms are 1-INDEXED, NOT 0-INDEXED
    """
    return [i+1 for i, token in enumerate(document) if token == term]
    
### Getting the postings for a term for all documents in that term
def get_postings_for_term(dict_of_docs : dict, term : str) -> dict:
    """
    Gets the postings for a term in a dictionary of documents.
    Args:
        dict_of_docs: The dictionary of documents.
        term: The term to search.
    Returns:
        A dictionary of the postings for the term, in the format
        ```
        {
            doc1: pos1 pos2 ...
            doc2: pos3 pos4 ...
            ...
        }
        ```
    """
    return {docno: get_positions_in_doc(doc, term) for docno, doc in dict_of_docs.items() if term in doc}

## Actually creating the index
def create_positional_iverted_index(dict_of_docs : dict) -> dict:
    """
    Creates an inverted positional index from a dictionary of docs (parsed from an xml file).
    Args:
        dict_of_docs: The dictionary of documents. Reccomended to be generated by passing an xml file into `pre_process_xml_file`
    Returns:
        A dictionary of the positional inverted index, in the following format
        ```
        {
            term: {
                document_frequency
                postings : {
                    doc1: pos1 pos2 ...
                    doc2: pos3 pos4 ...
                    ...
                }
            },
            ...
        }
        ```
    """
    unique_terms = get_unique_terms(dict_of_docs)
    pos_inv_index = {term: [] for term in unique_terms}
    num_terms_to_process = len(unique_terms)
    for term in unique_terms:
        pos_inv_index[term] = {
            "document_frequency": get_num_of_docs_with_term(dict_of_docs, term),
            "postings": {docno: get_positions_in_doc(doc, term) for docno, doc in dict_of_docs.items() if term in doc} # seperate dictionary for the postings
        }
        num_terms_to_process -= 1
        print(f"\rProcessing: {num_terms_to_process} terms remaining", end="\r") # So I can see how long it's taking
        
    return pos_inv_index

## Writing the index to a file in the desired format
def write_positional_inverted_index_to_file(pos_inv_index : dict, output_filepath : str) -> None:
    """
    Writes a positional inverted index to a file. The file is in the format
    ```
    term: document_frequency
        doc1: pos1, pos2 ...
        doc2: pos3, pos4 ...
        ................
    ```

    Args:
        pos_inv_index: The positional inverted index to be written. Should preferably be generated with `create_positional_iverted_index`.
        output_filepath: The path to the file to be written to.
    """
    with open(output_filepath, "w") as f:
        for term, data in pos_inv_index.items():
            f.write(f"{term}: {data['document_frequency']}\n") # writing document frequency
            for docno, positions in data["postings"].items():
                f.write(f"\t{docno}: {', '.join(map(str, positions))}\n") # formatting the postings to be in the required submission format
        f.close()

## Reading the index from a file
def read_positional_inverted_index_from_file(filepath : str) -> dict:
    """
    Reads a positional inverted index from a file. The file is in the format
    ```
    term: document_frequency
        doc1: pos1, pos2 ...
        doc2: pos3, pos4 ...
        ................
    ```

    Args:
        filepath: The path to the file to be read from.
    Returns:
        The positional inverted index read from the file.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()
    pos_inv_index = {}
    current_term = None
    for line in lines:
        if line[0] == "\t":
            docno, positions = line.strip().split(": ")
            pos_inv_index[current_term]["postings"][docno] = list(map(int, positions.split(", ")))
        else:
            current_term, doc_freq = line.strip().split(": ")
            pos_inv_index[current_term] = {
                "document_frequency": int(doc_freq),
                "postings": {}
            }
    return pos_inv_index

# Testing the functions
def test_pos_inv_index_file_io():
    """
    Tests whether the code for writing and reading positional inverted indexes to and from files works.
    """
    trec = {} # this only here to remove the pylance warning cause I removed the definition for trec
    trec_pii = create_positional_iverted_index(trec)
    write_positional_inverted_index_to_file(trec_pii, "index_test.txt")
    trec_pii_read = read_positional_inverted_index_from_file("index.txt")
    return trec_pii == trec_pii_read

#trec_pii = create_positional_iverted_index(trec)
#write_positional_inverted_index_to_file(trec_pii, "index.txt")
#trec_pii = read_positional_inverted_index_from_file("index.txt")

# Searching

## Searching for one term
def search_for_one_term(search_term : str, pos_inv_index : dict) -> set:
    """
    Performs a simple boolean search for a term in a positional inverted index.
    Args:
        search_term: The term to search for.
        pos_inv_index: The positional inverted index to search in.
    Returns:
        A set of document numbers where the document's text contains the term. 
        - Type `str` because the `pos_inv_index` is indexed by DOCNO strings, not numbers. 
        - `set` because it makes combining these results in boolean searches easier.
    """
    search_term = pre_process_token(search_term)
    if search_term not in pos_inv_index:
        return set()
    else:
        return set(list(pos_inv_index[search_term]["postings"].keys()))
    
## boolean search (needs intermediate query representation from below function)
def boolean_search(query : str, pos_inv_index : dict, collection : dict) -> set:
    """
    Parses a query containing multiple types of searches (proximity, phrase, boolean), and returns the total result. Uses a boolean search to combine the results.
    Args:
        query: The query to search for. Can be a combination of boolean, phrase, and proximity searches e.g. ("middle east" AND peace), (#10(income, taxes) AND NOT "executive)
        pos_inv_index: The positional inverted index to search in.
        collection: The collection of documents to search in.
    Returns:
        A set of document numbers which satisfy the query.
    """
    # What we actually want to do is use parse_query to get a list of the set results and the operators and then just comb over the list and combine them based on the operators
    parsed_query = parse_query(query, pos_inv_index, collection)
    results = None # instantiate to an None to allow set operations
    i = 0
    while i < len(parsed_query):
        query_part = parsed_query[i]
        if type(query_part) == set: # if it's a set, we can just combine it with the results
            if results == None:
                results = query_part
            else:
                results &= query_part # not sure why we'd get here under normal operations but I feel it'd be good to have this here
        else: # we have a boolean operator
            if query_part == "&":
                results &= parsed_query[i+1]
            elif query_part == "|":
                results |= parsed_query[i+1]
            else: # both ! and &! are will remove the next set from the results
                results -= parsed_query[i+1]
            i += 1 # We've already processed parsed_query[i+1] so we want to now check parsed_query[(i+1)+1], which thankfully our loop will do for us
        i += 1 # We want to get to the next set

    return results # todo: fix this

## Create intermediate query representation
def parse_query(query : str, pos_inv_index : dict, collection : dict) -> list:
    """
    Parses a boolean query into an intermediate form that can be easily processed. Accepts: 
    - boolean operators (AND, OR, NOT)
    - proximity searches (#n(term1, term2, ...))
    - phrase searches ("phrase search")

    This function will run any query that it can, and combine boolean operators together to output a *mixed type list* of **strings** and  **sets**. 

    # Example Parse
    
    For example, the query
    ```
    "middle east" AND peace AND NOT #10(uk, foreign)
    ```

    contains:
    - A phrase search ("middle east")
    - A single term search (peace)
    - A proximity search (#10(uk, foreign))
    - Boolean Operators "AND" and "AND NOT"

    If we call the sets of results for the searches "$1", "$2", and "$3", the parsed query would return
    ```
    [$1, "&", $2, "&!", $3]
    ```
    _(Here the &! means "AND NOT")_
    
    ## Args:
        query: The combined query to be parsed
        pos_inv_index: The positional inverted index to perform the intermediate queries on
        collection: The collection of documents to search in.
    ## Returns:
        A list containing the results of the intermediate individual queries, and representations of how they should be combined with the boolean operators.
    """
    # Split the query at spaces, preserving the searches in their entirety
    query_terms = re.split(r'\s*\b(AND|OR|NOT)\b\s*', query)
    #query_terms = re.split(r'\s+', query)
    # This sometimes gives us empty string which should be removed
    query_terms = [term for term in query_terms if term]
    parsed_query = []
    i = 0
    while i < len(query_terms):

        term = query_terms[i] # Why not just for term in terms? We need to combine boolean operators which involves seeking ahead in the list, and thus need to increment i different amounts (notably incremementing by 1 when we've combined our boolean operators, and then always incrementing by 1 after parsing the term)

        if term[0] == '#': # proximity search
            # we have to format the term into the number and the list of string
            match = re.match(r'#(\d+)\(([^)]+)\)', term)
            if match:
                n = int(match.group(1)) # get the number after the #
                print(f'DEBUG (n): {n}')
                terms = match.group(2).split(", ") # match.group returns a comma separated list so we just split it at them
                parsed_query.append(proximity_search(n, terms, pos_inv_index, collection))

        elif term[0] == "\"": # phrase search
            parsed_query.append(phrase_search(term, pos_inv_index, collection))

        elif term in ["AND", "OR", "NOT"]: # term is a boolean operator
            if term == "OR":
                if query_terms[i+1] == "NOT":
                    i +=1 # increment one more to skip past - OR NOT is no different to OR from what I can tell
                parsed_query.append("|")
            elif term == "NOT":
                parsed_query.append("!")
            else: # AND is special, because we can combine it with NOT. I have checked and I can't think of why we could combine it with OR, or if we could combine OR with NOT in this context, so I've only added the lookahead for AND NOT, meaning it is the only valid combined boolean term
                if query_terms[i+1] == "NOT":
                    parsed_query.append("&!")
                    i += 1 # since we've checked term i+1, we want to check term (i+1)+1 next. Thankfully, the end of the loop will do this extra increment for us, meaning we just have to incrememnt once here.
                else:
                    parsed_query.append("&")

        else: # term is a single term search
            parsed_query.append(search_for_one_term(term, pos_inv_index))

        i += 1

    return parsed_query

# Search for a phrase e.g. "income taxes"
def phrase_search(phrase : str, pos_inv_index : dict, collection : dict) -> set:
    """
    Performs a phrase search for a phrase in a positional inverted index. You could technically use this for a single term.
    Args:
        phrase: The phrase to search for.
        pos_inv_index: The positional inverted index to search in.
    Returns:
        A set of document numbers where the document's text contains the phrase. 
        - Type `str` because the `pos_inv_index` is indexed by DOCNO strings, not numbers. 
        - `set` because it makes combining these results in boolean searches easier.
    """
    phrase_terms = pre_process_document(phrase)
    docs_all_terms_appear_in = search_for_one_term(phrase_terms[0], pos_inv_index)
    # I have to populate the set first otherwise intersection isn't going to work with it
    for term in phrase_terms:
        docs_all_terms_appear_in = docs_all_terms_appear_in.intersection(search_for_one_term(term, pos_inv_index))

    # now we have the documents all the terms appear in, we need to check if the sequence of terms appears in any of the documents
    results = set()
    for docno in docs_all_terms_appear_in:
        doc = collection[docno]
        for i in range(len(doc) - len(phrase_terms) + 1):
            if doc[i:i+len(phrase_terms)] == phrase_terms:
                results.add(docno)
                break

    return results

# Helper for proximity search (basically returns the range in which we can more linearly search for terms)
def get_n_terms_before_and_after_term(doc: str, pos: int, n: int) -> list[str]:
    """
    Gets the `n` terms before and after a term (at position `pos`) in a document. *Does not include the term itself*
    Args:
        doc: The document to search in.
        term: The term to search for.
        n: The number of terms to get before and after the term.
    Returns:
        A list of the `n` terms before and after the term.
    """
    doc = doc.split()
    term_index = (pos - 1)
    return doc[max(0, term_index - n):term_index] + doc[term_index+1:term_index+n+1]

# Search for n terms within a range of m e.g. #m(n_1, n_2, ...)
def proximity_search(n : int, terms : list[str], pos_inv_index : dict, collection : dict) -> set:
    """
    Performs a proximity search of some terms on the positional inverted index
    Args:
        terms: A list of all the terms to search for
        n : The range of which all the terms must be all together in
        pos_inv_index: The positional inverted index to search in
    Returns:
        A set of document numbers where the terms appear within `n` terms of each other.
    """
    results = set()
    terms = [pre_process_token(term) for term in terms] # pre-processing the terms to search
    first_term = terms[0]
    # now we get all the documents that contain the first term
    postings = pos_inv_index[first_term]["postings"]
    for docNo, positions in postings.items():
        for pos in positions:
            doc = " ".join(collection[docNo])
            range_to_check = get_n_terms_before_and_after_term(doc, pos, n-1) # if all terms are within n terms of each other, then they'll all lie within this range
            if all(term in range_to_check for term in terms[1:]):
                # all of the terms are within this range, but are they within n terms of each other?
                indexes_of_terms_in_range = [range_to_check.index(term) for term in terms[1:]]
                if max(indexes_of_terms_in_range) - min(indexes_of_terms_in_range) <= n - 1:
                    results.add(docNo)
                    break
    return results

# TFIDF

## Term Frequency
def tf(term : str, doc : str) -> int:
    """
    Calculates the term frequency of a term in a document; the number of times the term appears in the document.
    Args:
        term: The term to calculate the term frequency for.
        doc: The document to search in.
    Returns:
        The term frequency of the term in the document.
    """
    return doc.count(term)

## Document Frequency
def df(term : str, pos_inv_index : dict) -> int:
    """
    Calculates the document frequency of a term in a positional inverted index; the number of documents that contain the term.
    Args:
        term: The term to calculate the document frequency for.
        pos_inv_index: The positional inverted index to search in.
    Returns:
        The document frequency of the term in the positional inverted index.
    """
    return pos_inv_index[term]["document_frequency"]

## Inverse Document Frequency
def idf(term : str, pos_inv_index : dict, N : int) -> float:
    """
    Calculates the inverse document frequency of a term in a positional inverted index; log_10(N/df), where N is the total number of documents in the collection.
    Args:
        term: The term to calculate the inverse document frequency for.
        pos_inv_index: The positional inverted index to search in.
        N: The total number of documents in the collection.
    Returns:
        The inverse document frequency of the term in the positional inverted index.
    """
    return math.log10(N / df(term, pos_inv_index))
    
## Combining all above functions to get Term Frequency-Inverse Document Frequency
def tfidf(query : str, pos_inv_index : dict, collection : dict, returnSorted=True) -> list[tuple]:
    """
    Calculates the term frequency-inverse document frequency of all documents that satisfy a query in a collection
    Args:
        query: The query to calculate the term frequency-inverse document frequency for. Usually a string e.g. "income tax reduction".
        pos_inv_index: The positional inverted index to search in.
        collection: The collection of documents. Only used to calculate N.
        returnSorted: Whether to sort the results by tfidf when returning. Default is `True`.
    Returns:
        The tfidf of the term in all the documents it applies to, in the format (docno, tfidf). Sorted, if told so.
    """
    results = []
    pre_processed_query = pre_process_document(query)
    # We need to take the string term input and convert it into "term1 OR term2 OR term3" etc. to get the documents from the search
    ORd_query = " OR ".join(pre_processed_query)
    docs_to_rank = boolean_search(ORd_query, pos_inv_index, collection)
    N = len(collection) # not sure if this should be for ALL documents or just the ones we're searching through. will go for the prior for now, as it makes more sense when using df (and idf)
    for docno in docs_to_rank:
        score = 0 # each document gets its own score
        doc = collection[docno]
        for term in pre_processed_query:
            if term in doc:
                score += (1 + math.log10(tf(term, doc))) * idf(term, pos_inv_index, N)
        results.append((docno, score))

    return sorted(results, key=lambda x: x[1], reverse=True) if returnSorted else results
    
# COURSEWORK 1 - TEST SET

# create the cw1_trec index

## These functions were ran once, I read from the file to save debugging time. Uncomment them if you wish to see them run (and ofc chance the filepaths)
#cw1_trec = pre_process_xml_file("cw1testset/trec.5000.xml")
#export_pre_processed_dict(cw1_trec, "cw1_trec.preprocessed.txt")

## Reading from this file takes maybe less than a second, so I just use this
cw1_trec = import_dict_from_file("cw1_trec.preprocessed.txt")
cw1_trec_pii = read_positional_inverted_index_from_file("cw1_trec.index.txt")

# Answering the queries
## boolean queries
boolean_queries = [
    "Sadness",
    "Glasgow AND SCOTLAND",
    "corporate AND taxes",
    "\"corporate taxes\"",
    "#30(corporate, taxes)",
    "\"middle east\" AND israel",
    "#5(Palestinian, organisations)",
    "\"Financial times\" AND NOT BBC",
    "\"wall street\" AND \"dow jones\"",
    "#20(dow, stocks)"
]

#with open("submission/results.boolean.txt", "a") as f:
#    for i in range(len(boolean_queries)):
#        query = boolean_queries[i]
#        results = boolean_search(query, cw1_trec_pii, cw1_trec)
#        for result in results:
#            f.write(f"{i+1},{result}\n")

## ranked queries
ranked_queries = [
    "corporation tax reduction",
    "stock market in China",
    "health industries",
    "the artificial intelligence market",
    "the Israeli Palestinian conflict",
    "information retrieval",
    "Dow Jones industrial average stocks",
    "will there be a reduction in taxes for corporates?",
    "the gold prices versus the dollar value",
    "FT article on the deal between BBC and BSkyB"
]

#with open("submission/results.ranked.txt", "a") as f:
#    for i in range(len(ranked_queries)):
#        query = ranked_queries[i]
#        results = tfidf(query, cw1_trec_pii, cw1_trec)
#        # cut to the top 150 results
#        results = results[:150]
#        for j in range(len(results)):
#            f.write(f"{i+1},{results[j][0]},{results[j][1]}\n")


#cw1_challenge = pre_process_xml_file("cw1testset/trec.5000.xml") # do this with challenge=True
#export_pre_processed_dict(cw1_challenge, "cw1_challenge.preprocessed.txt")
cw1_challenge = import_dict_from_file("cw1_challenge.preprocessed.txt")

#cw1_challenge_pii = create_positional_iverted_index(cw1_challenge)
#write_positional_inverted_index_to_file(cw1_challenge_pii, "cw1_challenge.index.txt")
cw1_challenge_pii = read_positional_inverted_index_from_file("cw1_challenge.index.txt")

with open("submission/challenge.results.boolean.txt", "a") as f:
    for i in range(len(boolean_queries)):
        query = boolean_queries[i]
        results = boolean_search(query, cw1_trec_pii, cw1_trec)
        for result in results:
            f.write(f"{i+1},{result}\n")

with open("submission/challenge.results.ranked.txt", "a") as f:
    for i in range(len(ranked_queries)):
        query = ranked_queries[i]
        results = tfidf(query, cw1_trec_pii, cw1_trec)
        # cut to the top 150 results
        results = results[:150]
        for j in range(len(results)):
            f.write(f"{i+1},{results[j][0]},{results[j][1]}\n")