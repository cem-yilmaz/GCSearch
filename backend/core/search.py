from .tokenisers.ttds_tokeniser import Tokeniser
import pickle
import os
import math
import re
from datetime import datetime

import chardet

def detect_encoding(file_path, language, sample_size=10000):
    """
    Detects the encoding of a file by reading a small sample.
    """
    with open(file_path, "rb") as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    return result['encoding'] if language == "turkish" else "utf-8-sig"

class Searcher():
    """
    A class to search for stuff in a given PII.

    Args:
        language (str): The language to be used for tokenising the queries. Ideally, this should be the language of the PII, but no such restriction is in place (although I can't imagine you'll get useful results for most different language pairings)
    """
    def __init__(self, language:str="english"):
        self.tokeniser = Tokeniser(language)
        self.language = language

    def load_pii(self, pii_name:str, pii_dir:str="piis") -> dict:
        """
        Unpickles the PII with the given name and returns it.
        
        Args:
            pii_name (str): The name of the PII to load. If you wish to open `<chatname>.pii.pkl`, pass in `<chatname>`.
            pii_dir (str): The directory in which the PII is stored. Default is `piis`.
        """
        relative_pii_dir = os.path.join(os.path.dirname(__file__), pii_dir)
        pii_path = f"{relative_pii_dir}/{pii_name}.pii.pkl"
        encoding = detect_encoding(pii_path, self.language)
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

        k1 = 0.75 # default - 1.2
        b = 0.75 # default - 0.75
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
        # make sure we're preserving the path to piis to be relative to where search.py is
        pii_dir = os.path.join(os.path.dirname(__file__), input_dir)
        print(f"DEBUG: Searching in {pii_dir}")
        results = []
        for pii_file in os.listdir(pii_dir):
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
    
    def get_display_name_from_chatname(self, chatname:str, out_dir="out") -> str:
        """
        Given an internal chatname, returns the display name of the chat.

        Args:
            chatname (str): The internal chatname to get the display name for.
            out_dir (str): The directory in which the info files are stored. Default is `out`.
        """
        relative_out_dir = os.path.join(os.path.dirname(__file__), out_dir)
        info_path = f"{relative_out_dir}/info/{chatname}.info.csv"
        encoding = detect_encoding(info_path, self.language)
        with open(info_path, "r", encoding=encoding, errors="replace") as f:
            display_name = f.readlines()[1].split(",")[1]
            f.close()
        return display_name
    
    def get_row_from_docno(self, docno:int, chatlog_path:str) -> str:
        """
        Given a docno, returns the row in the chatlog that corresponds to that docno.

        Args:
            docno (int): The docno to search for.
            chatlog_path (str): The path to the chatlog to search in.
        """
        encoding = detect_encoding(chatlog_path, self.language)
        with open(chatlog_path, "r", encoding=encoding, errors="replace") as f:
            chatlog = f.readlines()
            f.close()
        for row in chatlog:
            if row.split(",")[0] == str(docno):
                return row
        return None
    
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
        relative_out_dir = os.path.join(os.path.dirname(__file__), out_dir)
        # First we need the proper chatname. This can be found at out_dir/info/<internal_chatname>.info.csv, under the "Display name" column
        info_path = f"{relative_out_dir}/info/{internal_chatname}.info.csv"
        print(f"DEBUG: Looking for file at {info_path}")
        encoding = detect_encoding(info_path, self.language)
        with open(info_path, "r", encoding=encoding, errors="replace") as f:
            chatname = f.readlines()[1].split(",")[1]
            f.close()
        # Now we can get the remaining information by reading the chatlog, at out_dir/chatlogs/<internal_chatname>.chatlog.csv
        chatlog_path = f"{relative_out_dir}/chatlogs/{internal_chatname}.chatlog.csv"
        encoding = detect_encoding(chatlog_path, self.language)
        with open(chatlog_path, "r", encoding=encoding, errors="replace") as f:
            chatlog = f.readlines()
            f.close()
        message = self.get_row_from_docno(docNo, chatlog_path).split(",") # we should only really get one message here, so as a hack we just get the first
        date = self.convert_unix_timestamp_to_datetime(int(message[1]))
        sender = message[2]
        text = message[3]
        if not text:
            text = "[Media]"
        has_reactions = message[6]
        if has_reactions:
            reactions = message[7] + "\n"
        else:
            reactions = "[No reactions]\n"
        return f"({chatname}) [{date}] {sender}: {text}\n{reactions}"
    
    def flask_get_message_details_new(self, search_result:tuple[str, str, float], out_dir="out") -> tuple[str, str, str, str, str]:
        internal_chatname, docNo, _ = search_result
        relative_out_dir = os.path.join(os.path.dirname(__file__), out_dir)
        # First we need the proper chatname. This can be found at out_dir/info/<internal_chatname>.info.csv, under the "Display name" column
        info_path = f"{relative_out_dir}/info/{internal_chatname}.info.csv"
        with open(info_path, "r", encoding='utf-8-sig', errors='replace') as f:
            chatname = f.readlines()[1].split(",")[1]
            f.close()
        # Now we can get the remaining information by reading the chatlog, at out_dir/chatlogs/<internal_chatname>.chatlog.csv
        chatlog_path = f"{relative_out_dir}/chatlogs/{internal_chatname}.chatlog.csv"
        with open(chatlog_path, "r", encoding='utf-8-sig', errors='replace') as f:
            chatlog = f.readlines()
            f.close()
        message = self.get_row_from_docno(docNo, chatlog_path).split(",") # we should only really get one message here, so as a hack we just get the first
        date = self.convert_unix_timestamp_to_datetime(int(message[1]))
        sender = message[2]
        text = message[3]
        if not text:
            text = "[Media]"
        has_reactions = False
        if has_reactions:
            reactions = message[7] + "\n"
        else:
            reactions = "[No reactions]\n"
        return (chatname, date, sender, text, reactions)

    def flask_get_message_details_from_search_result(self, search_result:tuple[str, str, float], out_dir="out") -> dict:
        """
        Given a search result, returns the message in a dictionary. 

        Args:
            search_result (tuple[str, str, float]): The search result to get the message for (in the format `(chatname, docNo, score)`).
            out_dir (str): The directory in which the chatlogs are stored. Default is `out`.
        Returns:
            (dict): Returns the following fields:
            ```
            {
                "doc_id": the doc_id of the message,
                "message": the message,
                "sender": the sender of the message,
                "timestamp": the unix timestamp of the message,
            }
            ```
        """
        doc_id = search_result[1]
        # we cheat a bit by using the get_message_from_search_result function parsing the information that we need using regex
        _, timestamp, sender, message_text, _ = self.flask_get_message_details_new(search_result, out_dir)
        return {
            "doc_id": doc_id,
            "message": message_text,
            "sender": sender,
            "timestamp": timestamp,
        }

    def search(self, query:str) -> None:
        """
        Searches for the query in all PIIs in the `piis` directory.
        """
        results = self.search_all_piis_in_folder(query)
        for result in results:
            message = self.get_message_from_search_result(result)
            print(message)

    def flask_get_message_data(self, search_result:tuple[str, str, float], out_dir="out") -> dict:
        """
        Given a search result (`chatname`, `docNo`, `score`), returns the message data in a dictionary. 

        Args:
            search_result (tuple[str, str, float]): The search result to get the message for (in the format `(chatname, docNo, score)`).
            out_dir (str): The directory in which the chatlogs are stored. Default is `out`.
        Returns:
            (dict): Returns the following fields:
            ```
            {
                "chatName": internal_chatname,
                "platform": the platform of the chat,
                "message_details" : {
                    "message": the message,
                    "sender": the sender of the message,
                    "timestamp": the unix timestamp of the message,
                }
            }
            ```
        """
        internal_chat_name = search_result[0]
        chatName = self.get_display_name_from_chatname(internal_chat_name)
        platform = internal_chat_name.split("__")[0]
        if platform not in ["instagram", "whatsapp", "line", "wechat"]:
            print(f"DEBUG ERROR: Unknown platform {platform}")
            platform = "instagram" # fallback
        message_details = self.flask_get_message_details_from_search_result(search_result, out_dir)
        return {
            "internal_chat_name": internal_chat_name,
            "chatName": chatName,
            "platform": platform,
            "message_details": message_details
        }
        

    # now for the functions that will be used in the api
    def flask_search(self, query:str, n:int=50) -> list[str]:
        """
        Searches for the query in all PIIs in the `piis` directory.

        Args:
            query (str): The query to search for.
            n (int): The number of results to return. Default is 50.

        Returns:
            (list[str]) A list of the top `n` messages that match the query.
        """
        results = self.search_all_piis_in_folder(query, top_n=n)
        messages = [self.flask_get_message_data(result) for result in results]
        return messages[:n]
    
    def proximity_search(self, terms:list[str], positional_inverted_index:dict, n:int, top_n:int=25) -> list[tuple[int, float]]:
        """
        Performs a proximity search for the terms in the given positional inverted index.

        Args:
            terms (list[str]): The terms to search for.
            positional_inverted_index (dict): The positional inverted index to search in.
            n (int): The proximity parameter.
            top_n (int): The number of results to return. Default is 10.

        Returns:
            (list[tuple[int, float]]) A list of the top N results for the given queries in the format `(docNo, score)`.
        """

        doc_scores = {}

        postings_by_terms = {term: positional_inverted_index[term]["postings"] for term in terms if term in positional_inverted_index and "postings" in positional_inverted_index[term]} # love a good dict comprehension
        if not postings_by_terms:
            return []
        
        docs_containing_some_term = set()
        for posting in postings_by_terms.values():
            docs_containing_some_term.update(posting.keys())

        print(f"DEBUG: Searching for {terms} in {len(docs_containing_some_term)} documents")
        print(f"DEBUG: {docs_containing_some_term}")

        for docNo in docs_containing_some_term:
            positions_by_term = []
            for term in terms:
                print(f"DEBUG: Checking {term} in {docNo}")
                if term in positional_inverted_index and str(docNo) in positional_inverted_index[term]["postings"]:
                    positions_by_term.append(positional_inverted_index[term]["postings"][str(docNo)])
                else:
                    positions_by_term = []
                    break
            if not positions_by_term:
                continue # avoid checking docs that don't contain all terms
            
            score_for_doc = 0
            print(f"DEBUG: {positions_by_term}")

            for i in range(len(positions_by_term) - 1):
                for j in positions_by_term[i]:
                    for k in positions_by_term[i + 1]:
                        if abs(j - k) <= n:
                            score_for_doc += 1
                            

            if score_for_doc > 0:
                doc_scores[docNo] = doc_scores.get(docNo, 0) + score_for_doc

        return sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def prox_search_pii(self, query:str, n:int, pii:dict, top_n:int=10) -> list[tuple[int, float]]:
        """
        Proximity searches a query in a given PII, returning the top N results.

        Args:
            query (str): The query to search for.
            n (int): The proximity parameter.
            pii (dict): The PII to search in.
            top_n (int): The number of results to return. Default is 10.

        Returns:
            (list[tuple[int, float]]) A list of the top N results for that PII in the format `(docNo, score)`.
        """
        terms = self.tokeniser.tokenise(query)
        return self.proximity_search(terms, pii, n, top_n)
    
    def prox_search_all_piis(self, query:str, n:int, input_dir:str="piis", top_n:int=10) -> list[tuple[str, str, float]]:
        """
        Performs a proximity search for all of the terms in the query in all PIIs in the given directory. Each PII returns the top N results for that PII, which is then truncated to the top N results for all PIIs.

        Args:
            query (str): The query to search for.
            n (int): The proximity parameter for the search.
            input_dir (str): The directory in which the PIIs are stored. Default is `piis`.
            top_n (int): The number of results to return for each PII. Default is 10.

        Returns:
            (list[tuple[str, str, float]]) A list of the top N results for all PIIs in the format `(pii_name, docNo, score)`.
        """
        pii_dir = os.path.join(os.path.dirname(__file__), input_dir)
        
        terms = query.split() # split on whitespace by default
        if len(terms) < 2:
            # silently fallback to normal search
            return self.search_all_piis_in_folder(query, input_dir, top_n)
        print(f"DEBUG: Proximity searching \"{query}\" ({terms}) with parameter {n} in {pii_dir}")
        results = []
        for pii_file in os.listdir(pii_dir):
            if pii_file.endswith(".pii.pkl"):
                pii_name = pii_file.split(".")[0]
                pii = self.load_pii(pii_name)
                top_n_results = self.prox_search_pii(query, n, pii, top_n)
                results.extend([(pii_name, docNo, score) for docNo, score in top_n_results if top_n_results])
        return sorted(results, key=lambda x: x[2], reverse=True)[:top_n]
    
    def flask_prox_search(self, query:str, n:int, top_n:int=25) -> list[str]:
        """
        Proximity searches for the query in all PIIs in the `piis` directory.

        Args:
            query (str): The query to search for.
            n (int): The proximity parameter for the search.
            top_n (int): The number of results to return. Default is 25.

        Returns:
            (list[str]) A list of the top `n` messages that match the query.
        """
        results = self.prox_search_all_piis(query, n, top_n=top_n)
        messages = [self.flask_get_message_data(result) for result in results]
        return messages[:top_n]
