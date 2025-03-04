import re


def parse_query(query: str, pos_inv_index: dict, collection: dict) -> list:
    """
    Parses a boolean query into an intermediate representation. This supports:
    - Boolean operators: AND, OR, NOT
    - Proximity searches: #n(term1, term2, ...)
    - Phrase searches: "phrase search"

    Args:
        query (str): The input query string.
        pos_inv_index (dict): The positional inverted index.
        collection (dict): The collection of documents.

    Returns:
        list: A list containing search results and boolean operators.
    """
    # Split the query using boolean operators while preserving the structure
    query_terms = re.split(r'\s*\b(AND|OR|NOT)\b\s*', query)
    query_terms = [term.strip() for term in query_terms if term.strip()]

    parsed_query = []
    i = 0

    while i < len(query_terms):
        term = query_terms[i]

        if term.startswith("#"):  # Proximity search
            match = re.match(r'#(\d+)\(([^)]+)\)', term)
            if match:
                n = int(match.group(1))
                terms = match.group(2).split(", ")
                parsed_query.append(proximity_search(n, terms, pos_inv_index, collection))
            else:
                print(f"Warning: Invalid proximity search format: {term}")

        elif term.startswith('"') and term.endswith('"'):  # Phrase search
            parsed_query.append(phrase_search(term, pos_inv_index, collection))

        elif term in {"AND", "OR", "NOT"}:  # Boolean operators
            if term == "OR":
                if i + 1 < len(query_terms) and query_terms[i + 1] == "NOT":
                    i += 1  # OR NOT behaves the same as OR
                parsed_query.append("|")
            elif term == "NOT":
                parsed_query.append("!")
            elif term == "AND":
                if i + 1 < len(query_terms) and query_terms[i + 1] == "NOT":
                    parsed_query.append("&!")
                    i += 1
                else:
                    parsed_query.append("&")

        else:  # Single term search
            parsed_query.append(search_for_one_term(term, pos_inv_index))

        i += 1

    return parsed_query


def phrase_search(phrase: str, pos_inv_index: dict, collection: dict) -> set:
    """
    Performs a phrase search using a positional inverted index.

    Args:
        phrase (str): The phrase to search for.
        pos_inv_index (dict): The positional inverted index.
        collection (dict): The collection of documents.

    Returns:
        set: A set of document IDs containing the phrase.
    """
    phrase_terms = pre_process_document(phrase)

    if not phrase_terms:
        return set()

    # Get documents where all terms appear
    docs_with_all_terms = set.intersection(*[search_for_one_term(term, pos_inv_index) for term in phrase_terms])

    results = set()

    for doc_id in docs_with_all_terms:
        doc = collection.get(doc_id, [])
        for i in range(len(doc) - len(phrase_terms) + 1):
            if doc[i:i + len(phrase_terms)] == phrase_terms:
                results.add(doc_id)
                break  # Stop checking after the first match

    return results