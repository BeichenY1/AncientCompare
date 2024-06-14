import numpy as np
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import os

# 读取文件
with open('./shiji.txt', 'r', encoding='utf-8') as f:
    shiji = f.read()
with open('./hanshu.txt', 'r', encoding='utf-8') as f:
    hanshu = f.read()

# 定义片段长度
segment_length = 10

# 分割文本为片段
def split_text(text, length):
    return [text[i:i+length] for i in range(0, len(text), length)]

shiji_segments = split_text(shiji, segment_length)
hanshu_segments = split_text(hanshu, segment_length)

# 加载BERT模型和分词器: https://huggingface.co/google-bert/bert-base-chinese
model_path = os.path.expanduser('~/bert-models/bert-base-chinese')
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertModel.from_pretrained(model_path)

def encode_texts(texts):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.detach().numpy()

# 编码文本片段
shiji_vectors = encode_texts(shiji_segments)
hanshu_vectors = encode_texts(hanshu_segments)

# 计算相似度矩阵
similarity_matrix = cosine_similarity(shiji_vectors, hanshu_vectors)

# 设置相似度阈值
threshold = 0.8

# 找到相似的片段对并逐步扩展
similar_pairs = []
for i in range(len(shiji_segments)):
    for j in range(len(hanshu_segments)):
        if similarity_matrix[i, j] > threshold:
            k = 1
            while (i+k < len(shiji_segments) and j+k < len(hanshu_segments) and 
                   cosine_similarity([shiji_vectors[i+k]], [hanshu_vectors[j+k]])[0][0] > threshold):
                k += 1
            similar_pairs.append({
                'shiji_start': i * segment_length,
                'shiji_end': (i + k) * segment_length,
                'shiji_text': shiji[i:i+k],
                'hanshu_start': j * segment_length,
                'hanshu_end': (j + k) * segment_length,
                'hanshu_text': hanshu[j:j+k],
                'similarity': similarity_matrix[i, j]
            })

# 打印结果
for item in similar_pairs:
    print(f"《史记》: [{item['shiji_start']}, {item['shiji_end']}] {''.join(item['shiji_text'])}")
    print(f"《汉书》: [{item['hanshu_start']}, {item['hanshu_end']}] {''.join(item['hanshu_text'])}")
    print(f"相似度: {item['similarity']:.2f}\n")