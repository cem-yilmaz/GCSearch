from tokenisers.ttds_tokeniser import Tokeniser
import csv
from collections import defaultdict

class PIIConstructor:
    """
    A class to create Positional Inverted Indexes (PIIs) from a given `chatlog.csv` file. This file defines the *behaviour* of the PII construction, and is not instantiated for a given file. To create a PII, use the `build_positional_inverted_index_from_csv` method. You can also provide an input folder (of `chatlog.csv` files) and output folder to batch process multiple files.

    Args:
        language (str): The language of the chatlog files used. Defaults to `english`. No checks are made to ensure the language is correct, **undefined behaviour may occur in a language mismatch**.
    """
    def __init__(self, language:str='english'):
        self.language = language
        self.tokeniser = Tokeniser(language=language)
        
    def __repr__(self):
        return f"PII Constructor tokenising using \"{self.tokeniser.language}\" tokeniser"

    def build_pii_from_csv(self, csv_file_path:str) -> dict:
        """
        Builds a Positional Inverted Index (PII) from the given `chatlog.csv` file.
        
        Args:
            csv_file_path (str): Path to the `chatlog.csv` file

        Returns:
            dict: A dictionary representing the PII. The keys are the tokens, and the values are dictionaries. The inner dictionaries have the document IDs as keys, and the positions of the tokens in the document as values.
        """
        index = {}

        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                docNo = row["docNo"]
                tokens_str = row["processed_tokens"]

                tokens = self.tokeniser.tokenise(tokens_str)

                for position, term in enumerate(tokens, 1):
                    if term not in index:
                        index[term] = {
                            "document_frequency": 0,
                            "postings": {}
                        }
                    
                    if docNo not in index[term]["postings"]:
                        index[term["document_frequency"]] += 1
                        index[term]["postings"][docNo] = []

                    index[term]["postings"][docNo].append(position)
            f.close()

        return index
        