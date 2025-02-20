import pandas as pd

def build_positional_inverted_index_from_csv(csv_path):
    """
    building PII from csv
    param:
      csv_path: input file path, including doc_id and token
    return:
      index: dict, structure { token: { doc_id: [pos1, pos2, ...], ... } }
    """
    # read csv
    df = pd.read_csv(csv_path)
    
    # create PII dic
    index = {}
    
    for _, row in df.iterrows():
        doc_id = row["doc_id"]
        tokens_str = row["processed_tokens"]
        
        # avoid empty token 
        if pd.isna(tokens_str):
            continue
        
        tokens = tokens_str.split()
        
        # record token position
        for pos, token in enumerate(tokens):
            if token not in index:
                index[token] = {}
            if doc_id not in index[token]:
                index[token][doc_id] = []
            index[token][doc_id].append(pos)
    
    return index

def write_positional_index_to_file(index, output_path):
    """   
    token: df
       docID: pos1, pos2, ....
       docID: pos1, pos2, ....
    
    param:
      index: PII dic
      output_path: output file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for token, postings in index.items():
            df_value = len(postings)
            f.write(f"{token}: {df_value}\n")
            for doc_id, positions in postings.items():
                pos_str = ", ".join(str(pos) for pos in positions)
                f.write(f"   {doc_id}: {pos_str}\n")
            f.write("\n")

print("data file read")
input_csv = "processed_chatlog.csv"      # inpur file
output_index_file = "positional_inverted_index.txt"   # output file

# building PII from input csv file
print("PII converting")
pi_index = build_positional_inverted_index_from_csv(input_csv)
print("completed converting PII")

# writing PII results into txt file
print("writing PII into txt file")
write_positional_index_to_file(pi_index, output_index_file)

print("saving file as:", output_index_file)
print("completed")
