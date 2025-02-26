from tokenisers.ttds_tokeniser import Tokeniser
import csv
import os
from pathlib import Path
from collections import defaultdict

class PIIConstructor:
    """
    A class to create Positional Inverted Indexes (PIIs) from a given `chatlog.csv` file. This file defines the *behaviour* of the PII construction, and is not instantiated for a given file. To create a PII, use the `build_pii_from_csv` method. You can also provide an input folder (of `chatlog.csv` files) and output folder to batch process multiple files.

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
                message = row["message"]

                tokens = self.tokeniser.tokenise(message)

                for position, term in enumerate(tokens, 1):
                    if term not in index:
                        index[term] = {
                            "document_frequency": 0,
                            "postings": {}
                        }
                    
                    if docNo not in index[term]["postings"]:
                        index[term]["document_frequency"] += 1
                        index[term]["postings"][docNo] = []

                    index[term]["postings"][docNo].append(position)
            f.close()

        return index
    
    def write_pii_to_txt(self, pii:dict, output_file:str) -> None:
        """
        Writes a PII to a TXT file. The file is in the format
        ```
        term: document_frequency
            doc1: pos1, pos2 ...
            doc2: pos3, pos4 ...
            ................
        ```

        Args:
            pii (dict): The PII to be written.
            output_file (str): The output file path to write the PII to.
        """
        with open(output_file, "w") as f:
            for term, docs in pii.items():
                f.write(f"{term}: {docs['document_frequency']}\n")
                for doc, positions in docs["postings"].items():
                    f.write(f"\t{doc}: {', '.join(map(str, positions))}\n")
            f.close()

    def create_pii_from_csv(self, csv_file_path:str, output_dir:str="piis") -> None:
        """
        Creates a PII from the given `chatlog.csv` file, and writes it to a TXT file.

        If the chatlog.csv file is named `<chatname>.chatlog.csv`, the PII will be written to `<chatname>.pii.txt`.

        Args:
            csv_file_path (str): Path to the `chatlog.csv` file
            output_dir (str): The directory to write the PII to. Defaults to `piis`.
        """
        try:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            script_dir = Path(os.path.abspath('backend/core'))

        chatname = csv_file_path.split("/")[-1]
        
        output_path = script_dir / output_dir / f"{chatname}.pii.txt"
        input(f"DEBUG: writing to {output_path}")

        pii = self.build_pii_from_csv(csv_file_path)
        self.write_pii_to_txt(pii, output_path)
        