from tokenisers.ttds_tokeniser import Tokeniser
import pickle
import os
import math
from datetime import datetime

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
    
    def bm25_search(self, tokens:list[str], positional_index:dict, top_n:int=10):
        """
        Computes BM25 scores for documents that contain query tokens.
        Uses the PII to extract term frequency and positional data.
        """
        # build a document lengths dictionary from the index.
        doc_lengths = {}
        
        for term in positional_index:
            if term in positional_index and "postings" in positional_index[term]:
                for docNo, positions in positional_index[term]["postings"].items():
                    doc_lengths[docNo] = max(doc_lengths.get(docNo, 0), max(positions) + 1)

        N = len(doc_lengths)
        if N == 0:
            return []
        
        avgdl = sum(doc_lengths.values()) / N if N > 0 else 0

        k1 = 1.5
        b = 0.75
        scores = {}

        for token in tokens:
            if token not in positional_index:
                continue
            doc_freq = positional_index[token]["document_frequency"]
            idf = math.log((N - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            for doc_id, positions in positional_index[token]["postings"].items():
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
            if pii_file.endswith(".pii.pkl"):
                pii_name = pii_file.split(".")[0]
                pii = self.load_pii(pii_name)
                top_n_results = self.search_pii(query, pii, top_n)
                results.extend([(pii_name, docNo, score) for docNo, score in top_n_results if top_n_results])
        return sorted(results, key=lambda x: x[2], reverse=True)[:top_n]
    
    def convert_unix_timestamp_to_datetime(self, timestamp:int) -> str:
        """
        Converts a Unix timestamp to a human-readable datetime string.

        Args:
            timestamp (int): The Unix timestamp to convert.

        Returns:
            (str) The human-readable datetime string.
        """
        return datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    
    def get_message_from_search_result(self, search_result:tuple[str, str, float], out_dir="out") -> str:
        """
        Given a search result, returns the message.
        
        The message is returned in the following format
        ```
        (<chatname>) [<datetime>] <sender> <message>
        <reactions (if any)>
        ```

        Args:
            search_result (tuple[str, str, float]): The search result to get the message for (in the format `(chatname, docNo, score)`).
            out_dir (str): The directory in which the chatlogs are stored. Default is `out`.
        """
        internal_chatname, docNo, _ = search_result
        # First we need the proper chatname. This can be found at out_dir/info/<internal_chatname>.info.csv, under the "Display name" column
        info_path = f"{out_dir}/info/{internal_chatname}.info.csv"
        with open(info_path, "r") as f:
            chatname = f.readlines()[1].split(",")[1]
            f.close()
        # Now we can get the remaining information by reading the chatlog, at out_dir/chatlogs/<internal_chatname>.chatlog.csv
        chatlog_path = f"{out_dir}/chatlogs/{internal_chatname}.chatlog.csv"
        with open(chatlog_path, "r") as f:
            chatlog = f.readlines()
            f.close()
        # Now we can get the message
        message = [msg for msg in chatlog if msg.split(",")[0] == docNo][0].split(",")
        #print(f"DEBUG: {message}")
        date = self.convert_unix_timestamp_to_datetime(int(message[1]))
        sender = message[2]
        text = message[3]
        has_reactions = message[6]
        if has_reactions:
            reactions = message[7] + "\n"
        else:
            reactions = ""
        return f"({chatname}) [{date}] {sender}: {text}\n{reactions}"

    def search(self, query:str) -> None:
        """
        Searches for the query in all PIIs in the `piis` directory.
        """
        results = self.search_all_piis_in_folder(query)
        for result in results:
            message = self.get_message_from_search_result(result)
            print(message)


s = Searcher() # delete this line