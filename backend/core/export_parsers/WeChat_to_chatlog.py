import pandas as pd
import os
import chardet

def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(100000)  # 读取前100KB数据进行编码检测
    return chardet.detect(raw_data)['encoding']

def transform_csv_to_csv(input_csv, output_csv):
    # 检测编码格式
    encoding_detected = detect_encoding(input_csv)
    print(f"检测到的编码格式: {encoding_detected}")
    
    # 读取原始 CSV 文件
    df = pd.read_csv(input_csv, encoding=encoding_detected)
    
    # 转换数据格式
    transformed_data = []
    
    for idx, row in enumerate(df.iterrows(), start=1):
        transformed_entry = {
            "docNo": idx,
            "time": row[1]["CreateTime"],
            "sender": row[1]["NickName"],  # 直接使用 NickName 作为 sender
            "message": row[1]["StrContent"],
            "isReply": False,
            "who_replied_to": None,
            "has_reactions": False,
            "reactions": "[]",  # CSV 存储数组字段时通常用字符串
            "translated": False,
            "is_media": row[1]["Type"] != 1,  # 假设 Type=1 是文本消息，其余为媒体
            "is_OCR": False,
            "local_uri": None,
            "remote_url": None
            }
        transformed_data.append(transformed_entry)

    # 转换为 DataFrame 并导出为 CSV
    df_transformed = pd.DataFrame(transformed_data)
    df_transformed.to_csv(output_csv, index=False, encoding="utf-8-sig")
    
    print(f"转换完成，已保存到 {output_csv}")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
WECHAT_EXPORT_DIR = os.path.join(BASE_DIR, "core", "export", "wechat")
OUTPUT_DIR = os.path.join(BASE_DIR, "core", "export", "out")

# 使用示例
input_csv_name = "messages.csv" # 你的输入 CSV 文件路径
input_csv_path = os.path.join(WECHAT_EXPORT_DIR, input_csv_name)
output_csv_name = "chatlog.csv"  # 你的输出 CSV 文件路径
output_csv_path = os.path.join(OUTPUT_DIR, output_csv_name)


os.makedirs(OUTPUT_DIR, exist_ok=True)

transform_csv_to_csv(input_csv_path, output_csv_path)
