# -*- coding: utf-8 -*-


def proximity_search(n: int, terms: list[str], pos_inv_index: dict, collection: dict) -> set:

    if not terms or n < 1 or not isinstance(n, int):
        return set()

    results = set()
    terms = [pre_process_token(term) for term in terms]  

    if any(term not in pos_inv_index for term in terms):
        return set()  

    terms.sort(key=lambda term: len(pos_inv_index[term]["postings"]))  
    first_term = terms[0]
    first_term_postings = pos_inv_index[first_term]["postings"]

    for docNo, first_term_positions in first_term_postings.items():
        if docNo not in collection:
            continue  

        doc_tokens = collection[docNo]  
        word_positions = {term: pos_inv_index[term]["postings"].get(docNo, []) for term in terms[1:]}

        for first_pos in first_term_positions:
            start, end = max(0, first_pos - (n - 1)), min(len(doc_tokens), first_pos + (n - 1) + 1)
            words_in_range = doc_tokens[start:end]

            if not all(term in words_in_range for term in terms[1:]):
                continue  

            positions = sorted([first_pos] + [min(word_positions[term], default=float('inf')) for term in terms[1:]])
            if max(positions) - min(positions) <= (n - 1):
                results.add(docNo)
                break  

    return results
