from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 将文本分割成固定长度的子串，并记录每个子串的起始和终止位置
def split_text_fixed_length(text, min_window_size=500, max_window_size=600, step=550):
    length = len(text)
    substrings = []
    for window_size in range(min_window_size, max_window_size + 1):
        substrings.extend([(text[i:i+window_size], i, i+window_size-1) for i in range(0, length - window_size + 1, step)])
    return substrings

# 计算段落的TF-IDF向量
def compute_tfidf_vectorizer(segments1, segments2):
    vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 4))  # 使用unigram、bigram和trigram
    # 合并两个文档集以创建统一的词汇表
    combined_segments = [segment[0] for segment in segments1] + [segment[0] for segment in segments2]
    vectorizer.fit(combined_segments)
    
    tfidf1 = vectorizer.transform([segment[0] for segment in segments1])
    tfidf2 = vectorizer.transform([segment[0] for segment in segments2])
    
    return tfidf1, tfidf2

# 使用余弦相似度进行初步过滤，找出相似的子串，并按字典形式表示
def cosine_similarity_filter(segments1, segments2, threshold=0.1):  # 降低阈值
    # 计算TF-IDF矩阵
    tfidf1, tfidf2 = compute_tfidf_vectorizer(segments1, segments2)
    
    # 计算余弦相似度矩阵
    similarity_matrix = cosine_similarity(tfidf1, tfidf2)
    print(similarity_matrix)
    similarity_dict = {}

    for i in range(len(segments1)):
        key = f"文章1-子串{i}-{segments1[i][1]}-{segments1[i][2]}"
        for j in range(len(segments2)):
            if similarity_matrix[i, j] >= threshold:
                if key not in similarity_dict:
                    similarity_dict[key] = []
                segment_info = f"文章2-子串{j}-{segments2[j][1]}-{segments2[j][2]}"
                similarity_dict[key].append(segment_info)
    
    return similarity_dict

# 读取文件
shiji_text = read_file('./shiji.txt')
hanshu_text = read_file('./hanshu.txt')

# 将文章按子串分割
min_window_size = 1000  # 可以根据需要调整最小窗口长度
max_window_size = 1200  # 可以根据需要调整最大窗口长度
step = 900  # 可以根据需要调整步长
shiji_segments = split_text_fixed_length(shiji_text, min_window_size, max_window_size, step)
hanshu_segments = split_text_fixed_length(hanshu_text, min_window_size, max_window_size, step)

# 使用余弦相似度进行初步过滤
similarity_dict = cosine_similarity_filter(shiji_segments, hanshu_segments, threshold=0.1)

# 打印最终结果
print("\n相似的子串对:")
for key, values in similarity_dict.items():
    print(f"{key} 对应于 {values}")

# 输出相似的子串
with open('./filtered_segments.txt', 'w', encoding='utf-8') as file:
    for key, values in similarity_dict.items():
        file.write(f"{key} 对应于 {values}\n")

print("初步过滤后的子串已输出到filtered_segments.txt。")