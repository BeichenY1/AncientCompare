from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 将文本分割成句子
def split_text_fixed_length(text, min_window_size=4, max_window_size=8, step=4):
    length = len(text)
    substrings = []
    for window_size in range(min_window_size, max_window_size + 1):
        substrings.extend([(text[i:i+window_size], i, i+window_size-1) for i in range(0, length - window_size + 1, step)])
    return substrings

# 使用BERT模型生成子串的嵌入向量
def embed_substrings(substrings, model, tokenizer):
    embeddings = []
    for substring, start, end in substrings:
        inputs = tokenizer(substring, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        # 获取[CLS] token的向量
        cls_embedding = outputs.last_hidden_state[0, 0, :].numpy()
        embeddings.append(cls_embedding)
    return np.array(embeddings)

# 计算句子相似性并过滤相似段落
def filter_similar_substrings(substrings1, substrings2, embeddings1, embeddings2, threshold=0.1):
    similarity_matrix = cosine_similarity(embeddings1, embeddings2)
    similar_pairs = []

    for i, (substring1, start1, end1) in enumerate(substrings1):
        for j, (substring2, start2, end2) in enumerate(substrings2):
            if similarity_matrix[i, j] >= threshold:
                similar_pairs.append((substring1, substring2, similarity_matrix[i, j]))

    return similar_pairs

# 加载BERT模型和分词器: https://huggingface.co/google-bert/bert-base-chinese
model_path = os.path.expanduser('./bert-models/bert-base-chinese')
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertModel.from_pretrained(model_path)

# 读取文件
shiji_text = read_file('./shiji.txt')
hanshu_text = read_file('./hanshu.txt')

# 将文本分割成句子
min_window_size = 4  # 最小窗口长度
max_window_size = 8  # 最大窗口长度
step = 4  # 步长
shiji_substrings = split_text_fixed_length(shiji_text, min_window_size, max_window_size, step)
hanshu_substrings = split_text_fixed_length(hanshu_text, min_window_size, max_window_size, step)

# 生成句子的嵌入向量
shiji_embeddings = embed_substrings(shiji_substrings, model, tokenizer)
hanshu_embeddings = embed_substrings(hanshu_substrings, model, tokenizer)

# 计算子串相似性并过滤相似段落
similar_substring_pairs = filter_similar_substrings(shiji_substrings, hanshu_substrings, shiji_embeddings, hanshu_embeddings, threshold=0.7)

# 打印相似的子串对
print("\n相似的子串对:")
for pair in similar_substring_pairs:
    print(f"子串1: {pair[0]}")
    print(f"子串2: {pair[1]}")
    print(f"相似度: {pair[2]}")
    print()

# 输出相似的子串对
with open('./similar_substrings.txt', 'w', encoding='utf-8') as file:
    for pair in similar_substring_pairs:
        file.write(f"子串1: {pair[0]}\n")
        file.write(f"子串2: {pair[1]}\n")
        file.write(f"相似度: {pair[2]}\n\n")

print("相似的子串对已输出到similar_substrings.txt。")