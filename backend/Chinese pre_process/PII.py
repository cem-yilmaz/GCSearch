# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 01:42:12 2025

@author: Layla
"""

import pandas as pd
from collections import defaultdict

# 读取数据
file_path = "F:/processed_chatlog_optimized.csv"
df = pd.read_csv(file_path)

# 为数据添加唯一的 document_id（使用索引）
df['document_id'] = df.index

# 选择所需列
if 'processed_tokens' in df.columns:
    df = df[['document_id', 'processed_tokens']].dropna()
else:
    raise ValueError("CSV 文件缺少 'processed_tokens' 列")

# 构建位置倒排索引
positional_inverted_index = defaultdict(lambda: defaultdict(list))

for _, row in df.iterrows():
    doc_id = row['document_id']
    words = row['processed_tokens'].split()  # 假设词语以空格分隔

    for position, word in enumerate(words):
        positional_inverted_index[word][doc_id].append(position)

# 转换为 DataFrame 以便存储或展示
index_list = []
for word, doc_positions in positional_inverted_index.items():
    for doc_id, positions in doc_positions.items():
        index_list.append({'Term': word, 'Document ID': doc_id, 'Positions': positions})

index_df = pd.DataFrame(index_list)

# 保存结果
index_df.to_csv("F:/positional_inverted_index.csv", index=False)

print("位置倒排索引已生成，并保存为 'positional_inverted_index.csv'")
