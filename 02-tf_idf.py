import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 读取文件
with open('./shiji.txt', 'r', encoding='utf-8') as f:
    shiji = f.read()
with open('./hanshu.txt', 'r', encoding='utf-8') as f:
    hanshu = f.read()

# 定义片段长度
segment_length = 2

# 分割文本为片段
def split_text(text, length):
    return [text[i:i+length] for i in range(0, len(text), length)]

shiji_segments = split_text(shiji, segment_length)
hanshu_segments = split_text(hanshu, segment_length)

# 使用TF-IDF向量化
vectorizer = TfidfVectorizer().fit(shiji_segments + hanshu_segments)
shiji_vectors = vectorizer.transform(shiji_segments)
hanshu_vectors = vectorizer.transform(hanshu_segments)

# 计算相似度矩阵
similarity_matrix = cosine_similarity(shiji_vectors, hanshu_vectors)

# 设置相似度阈值
threshold = 0.1

# 找到相似的片段对
similar_pairs = np.argwhere(similarity_matrix > threshold)

# 输出结果
result = []
for pair in similar_pairs:
    i, j = pair
    result.append({
        'shiji_start': i * segment_length,
        'shiji_end': (i + 1) * segment_length,
        'shiji_text': shiji_segments[i],
        'hanshu_start': j * segment_length,
        'hanshu_end': (j + 1) * segment_length,
        'hanshu_text': hanshu_segments[j],
        'similarity': similarity_matrix[i, j]
    })

# 打印结果
for item in result:
    print(f"《史记》: [{item['shiji_start']}, {item['shiji_end']}] {item['shiji_text']}")
    print(f"《汉书》: [{item['hanshu_start']}, {item['hanshu_end']}] {item['hanshu_text']}")
    print(f"相似度: {item['similarity']:.2f}\n")