import pandas as pd

def build_positional_inverted_index_from_csv(csv_path):
    """
    building PII from csv
    Processed CSV format:
        doc_id, original_message, processed_tokens, tfidf_keywords, embedding_vector
    returns:
        index: dict { token: { doc_id: [pos1, pos2, ...], ... } }
    """
    # Read CSV
    df = pd.read_csv(csv_path)

    # Create PII dictionary
    index = {}
    position_track = {}  # Track position per document

    for _, row in df.iterrows():
        doc_id = row["doc_id"]
        tokens_str = row["processed_tokens"]

        # Avoid empty token 
        if pd.isna(tokens_str):
            continue

        tokens = tokens_str.split()  # Convert space-separated tokens into a list

        # Initialize position tracking for each document
        if doc_id not in position_track:
            position_track[doc_id] = 0  # Start position for this doc_id

        # Record token position
        for token in tokens:
            if token not in index:
                index[token] = {}
            if doc_id not in index[token]:
                index[token][doc_id] = []

            index[token][doc_id].append(position_track[doc_id])

            # Increment position after each token
            position_track[doc_id] += 1

    return index

def write_positional_index_to_file(index, output_path):
    """   
    Writes the positional inverted index to a file.

    Format:
        token: df
           docID: pos1, pos2, ....
           docID: pos1, pos2, ....
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for token, postings in index.items():
            df_value = len(postings)  # Number of documents containing this token
            f.write(f"{token}: {df_value}\n")
            for doc_id, positions in postings.items():
                pos_str = ", ".join(str(pos) for pos in positions)
                f.write(f"   {doc_id}: {pos_str}\n")
            f.write("\n")

# File paths
input_csv = "processed_chatlog.csv"  # Input file
output_index_file = "positional_inverted_index.txt"  # Output file

# Build and save the positional inverted index
print("Building PII from input CSV...")
pi_index = build_positional_inverted_index_from_csv(input_csv)
print("PII construction completed")

# Write PII into file
print("Writing PII to file...")
write_positional_index_to_file(pi_index, output_index_file)
print("Saved file:", output_index_file)
print("Completed")
