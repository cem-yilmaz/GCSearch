from tokenisers.ttds_tokeniser import Tokeniser
import pickle
import os
import math

class Searcher():
    """
    A class to search for stuff in a given PII.

    Args:
        language (str): The language to be used for tokenising the queries. Ideally, this should be the language of the PII, but no such restriction is in place (although I can't imagine you'll get useful results for most different language pairings)
    """
    def __init__(self, language:str="english"):
        self.tokeniser = Tokeniser(language)

    def load_pii(self, pii_name:str, pii_dir:str="piis") -> dict:
        """
        Unpickles the PII with the given name and returns it.
        
        Args:
            pii_name (str): The name of the PII to load. If you wish to open `<chatname>.pii.pkl`, pass in `<chatname>`.
            pii_dir (str): The directory in which the PII is stored. Default is `piis`.
        """
        pii_path = f"{pii_dir}/{pii_name}.pii.pkl"
        with open(pii_path, "rb") as f:
            pii = pickle.load(f)
            f.close()
        return pii
    
    def bm25_search(self, tokens, positional_index, top_n=10):
        """
        Computes BM25 scores for documents that contain query tokens.
        Uses the PII to extract term frequency and positional data.
        """
        # build a document lengths dictionary from the index.
        doc_lengths = {}
        for token, postings in positional_index[token]["postings"].items():
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



    def search_pii(self, query:str, pii:str, top_n:int=10) -> list[tuple[str, float]]:
        """
        Searches for the query in the given PII, returning the top N results.

        Currently uses BM25 search.

        Args:
            query (str): The query to search for.
            pii (str): The PII to search in.
            top_n (int): The number of results to return. Default is 10.

        Returns:
            (list[tuple[str, float]]) A list of the top N results for that PII in the format `(docNo, score)`.
        """
        tokens = self.tokeniser.tokenise(query)
        return self.bm25_search(tokens, pii, top_n)
    
    def search_all_piis_in_folder(self, query:str, input_dir:str="piis", top_n:int=10) -> list[tuple[str, str, float]]:
        """
        Searches for the query in all PIIs in the given directory. Each PII returns the top N results for that PII, which is then truncated to the top N results for all PIIs.

        Args:
            query (str): The query to search for.
            input_dir (str): The directory in which the PIIs are stored. Default is `piis`.
            top_n (int): The number of results to return for each PII. Default is 10.

        Returns:
            (list[tuple[str, str, float]]) A list of the top N results for all PIIs in the format `(pii_name, docNo, score)`.
        """
        results = []
        for pii_file in os.listdir(input_dir):
            pii_name = pii_file.split(".")[0]
            print(f"Searching {pii_name}")
            pii = self.load_pii(pii_name)
            top_n_results = self.search_pii(query, pii, top_n)
            results.extend([(pii_name, docNo, score) for docNo, score in top_n_results if top_n_results])
        return results[:top_n]


s = Searcher() # delete this line