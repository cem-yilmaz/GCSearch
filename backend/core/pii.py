from core.tokenisers.ttds_tokeniser import Tokeniser
import csv
import os
from pathlib import Path
import concurrent.futures
from functools import reduce
import math
import pickle
import sys

try:
    csv.field_size_limit(sys.maxsize)  # may lead OverflowError
except OverflowError:
    csv.field_size_limit(2147483647)  # 2GB


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
    
    def _process_chunk(self, rows: list) -> dict:
        """Process a chunk of rows and return a partial index."""
        index = {}
        for row in rows:
            docNo = row["docNo"]
            message = row["message"]
            try:
                tokens = self.tokeniser.tokenise(message)
            except:
                continue
            for position, term in enumerate(tokens, 1):
                if term not in index:
                    index[term] = {"document_frequency": 0, "postings": {}}

                if docNo not in index[term]["postings"]:
                    index[term]["document_frequency"] += 1
                    index[term]["postings"][docNo] = []

                index[term]["postings"][docNo].append(position)

        return index

    def _merge_indexes(self, indexes: list) -> dict:
        """Merge multiple partial indexes into one."""
        merged = {}
        for index in indexes:
            for term, data in index.items():
                if term not in merged:
                    merged[term] = {"document_frequency": 0, "postings": {}}

                merged[term]["document_frequency"] += data["document_frequency"]

                for docNo, positions in data["postings"].items():
                    merged[term]["postings"][docNo] = positions

        return merged

    def build_pii_from_csv(self, csv_file_path:str, num_threads:int=os.cpu_count()) -> dict:
        """
        Builds a Positional Inverted Index (PII) from the given `chatlog.csv` file.
        
        Args:
            csv_file_path (str): Path to the `chatlog.csv` file
            num_threads (int): Number of threads to use for processing. Defaults to `os.cpu_count()`, or 4 as a fallback.

        Returns:
            dict: A dictionary representing the PII. The keys are the tokens, and the values are dictionaries. The inner dictionaries have the document IDs as keys, and the positions of the tokens in the document as values.
        """
        if num_threads is None:
            num_threads = 4

        # Read all rows first
        with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if len(rows) == 0:
            return None

        # Calculate chunk size
        chunk_size = math.ceil(len(rows) / num_threads)
        chunks = [rows[i:i+chunk_size] for i in range(0, len(rows), chunk_size)]

        # Process chunks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self._process_chunk, chunk) for chunk in chunks]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Merge results
        return self._merge_indexes(results)
    
    def pickle_pii(self, pii:dict, output_file:str) -> None:
        """
        Pickles a PII to a file.

        Args:
            pii (dict): The PII to be pickled.
            output_file (str): The output file path to pickle the PII to.
        """
        if pii is not None:
            with open(output_file, "wb") as f:
                pickle.dump(pii, f)
                f.close()
    
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
        if pii is not None:
            with open(output_file, "w") as f:
                for term, docs in pii.items():
                    f.write(f"{term}: {docs['document_frequency']}\n")
                    for doc, positions in docs["postings"].items():
                        f.write(f"\t{doc}: {', '.join(map(str, positions))}\n")
                f.close()

    def create_pii_from_csv(self, csv_file_path:str, output_dir:str="piis") -> None:
        """
        Creates a PII from the given `chatlog.csv` file, and pickles it.

        If the chatlog.csv file is named `<chatname>.chatlog.csv`, the PII will be written to `<chatname>.pii.txt`.

        Args:
            csv_file_path (str): Path to the `chatlog.csv` file
            output_dir (str): The directory to write the PII to. Defaults to `piis`.
        """
        try:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            script_dir = Path(os.path.abspath('backend/core'))

        # if the output directory does not exist, create it
        output_path = script_dir / output_dir
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        csv_basename = os.path.basename(csv_file_path)
        chatname = csv_basename.replace(".chatlog.csv", "")
        
        output_path = script_dir / output_dir / f"{chatname}.pii.pkl"

        pii = self.build_pii_from_csv(csv_file_path)
        self.pickle_pii(pii, output_path)

    def create_piis_from_folder(self, input_dir:str="out/chatlogs", output_dir:str="piis") -> None:
        """
        Creates PIIs from all `chatlog.csv` files in a given directory, and writes them to TXT files. Wrapper for `create_pii_from_csv`.

        Args:
            input_dir (str): The directory containing the `chatlog.csv` files. Defaults to `out/chatlogs`.
            output_dir (str): The directory to write the PIIs to. Defaults to `piis`.
        """
        try:
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            script_dir = Path(os.path.abspath('backend/core'))

        input_path = script_dir / input_dir
        output_path = script_dir / output_dir

        input(f"Reading chatlogs from {input_path}, and writing PIIs to {output_path}. Please terminate program execution (Ctrl+C) if this is incorrect. Press Enter to continue otherwise.")

        chatlogs = os.listdir(input_path)
        num_logs = len(chatlogs)

        for i in range(num_logs):
            file = chatlogs[i]
            if file.endswith(".chatlog.csv"):
                print(f"Processing {file} ({i+1}/{num_logs})")
                self.create_pii_from_csv(str(input_path / file), str(output_path))
                print()
