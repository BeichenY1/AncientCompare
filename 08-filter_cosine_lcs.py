from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 将文本分割成固定长度的子串，并记录每个子串的起始和终止位置
def split_text_fixed_length(text, min_window_size=4, max_window_size=8, step=4):
    length = len(text)
    substrings = []
    for window_size in range(min_window_size, max_window_size + 1):
        substrings.extend([(text[i:i+window_size], i, i+window_size-1) for i in range(0, length - window_size + 1, step)])
    return substrings

# 计算段落的TF-IDF向量
def compute_tfidf_vectorizer(segments1, segments2):
    vectorizer = TfidfVectorizer()
    # 合并两个文档集以创建统一的词汇表
    combined_segments = [segment[0] for segment in segments1] + [segment[0] for segment in segments2]
    vectorizer.fit(combined_segments)
    
    tfidf1 = vectorizer.transform([segment[0] for segment in segments1])
    tfidf2 = vectorizer.transform([segment[0] for segment in segments2])
    
    return tfidf1, tfidf2

# 使用余弦相似度进行初步过滤，找出相似的子串，并按字典形式表示
def cosine_similarity_filter(segments1, segments2, threshold=0.8):
    # 计算TF-IDF矩阵
    tfidf1, tfidf2 = compute_tfidf_vectorizer(segments1, segments2)
    
    # 计算余弦相似度矩阵
    similarity_matrix = cosine_similarity(tfidf1, tfidf2)
    similarity_dict = {}

    for i in range(len(segments1)):
        key = f"文章1-{segments1[i][0]}-{segments1[i][1]}-{segments1[i][2]}"
        for j in range(len(segments2)):
            if similarity_matrix[i, j] >= threshold:
                if key not in similarity_dict:
                    similarity_dict[key] = []
                segment_info = f"文章2-{segments2[j][0]}-{segments2[j][1]}-{segments2[j][2]}"
                similarity_dict[key].append(segment_info)
    
    return similarity_dict

# 合并重叠或包含关系的相似子串
def merge_overlapping_substrings(similarity_dict):
    merged_dict = {}
    for key, values in similarity_dict.items():
        segments1_pos = key.split('-')[2:]
        segments1_pos = list(map(int, segments1_pos))
        for value in values:
            segments2_pos = value.split('-')[2:]
            segments2_pos = list(map(int, segments2_pos))
            is_new = True
            for merged_key, merged_values in merged_dict.items():
                merged_segments1_pos = merged_key.split('-')[2:]
                merged_segments1_pos = list(map(int, merged_segments1_pos))
                merged_segments2_pos = merged_values[0].split('-')[2:]
                merged_segments2_pos = list(map(int, merged_segments2_pos))
                
                # Check if the current segment is part of any merged segment
                if (segments1_pos[0] >= merged_segments1_pos[0] and segments1_pos[1] <= merged_segments1_pos[1] and
                    segments2_pos[0] >= merged_segments2_pos[0] and segments2_pos[1] <= merged_segments2_pos[1]):
                    is_new = False
                    break
            
            if is_new:
                merged_dict[key] = values
    
    return merged_dict

# 读取文件
shiji_text = read_file('./shiji.txt')
hanshu_text = read_file('./hanshu.txt')

# 将文章按子串分割
min_window_size = 4  # 可以根据需要调整最小窗口长度
max_window_size = 8  # 可以根据需要调整最大窗口长度
step = 4  # 可以根据需要调整步长
shiji_segments = split_text_fixed_length(shiji_text, min_window_size, max_window_size, step)
hanshu_segments = split_text_fixed_length(hanshu_text, min_window_size, max_window_size, step)

# 使用余弦相似度进行初步过滤
similarity_dict = cosine_similarity_filter(shiji_segments, hanshu_segments, threshold=0.9)

# 合并重叠或包含关系的相似子串
merged_similarity_dict = merge_overlapping_substrings(similarity_dict)

# 打印最终结果
print("\n相似的子串对:")
for key, values in merged_similarity_dict.items():
    print(f"{key} 对应于 {values}")

# 输出相似的子串
with open('./filtered_segments.txt', 'w', encoding='utf-8') as file:
    for key, values in merged_similarity_dict.items():
        file.write(f"{key} 对应于 {values}\n")

print("初步过滤后的子串已输出到filtered_segments.txt。")