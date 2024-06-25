import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datasketch import MinHash, MinHashLSH
import numpy as np

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 将文本分割成固定长度的子串（滑动窗口），并记录每个子串的起始和终止位置
def split_text_fixed_length(text, min_window_size=4, max_window_size=6, step=4):
    length = len(text)
    substrings = []
    for window_size in range(min_window_size, max_window_size + 1):
        substrings.extend([(text[i:i+window_size], i, i+window_size-1) for i in range(0, length - window_size + 1, step)])
    return substrings

# 使用MinHash和LSH进行初步过滤，并保留原始索引
def lsh_filter(substrings1, substrings2, num_perm=128, threshold=0.9):
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    
    minhashes1 = []
    positions1 = []
    for i, (substring, start_pos, end_pos) in enumerate(substrings1):
        m = MinHash(num_perm=num_perm)
        for char in substring:
            m.update(char.encode('utf8'))
        lsh.insert(f"shiji_{i}", m)
        minhashes1.append((m, start_pos, end_pos))
    
    filtered_substrings1 = []
    filtered_substrings2 = []
    filtered_positions1 = []
    filtered_positions2 = []

    for i, (substring, start_pos, end_pos) in enumerate(substrings2):
        m = MinHash(num_perm=num_perm)
        for char in substring:
            m.update(char.encode('utf8'))
        
        # 查询相似的子串
        similar_items = lsh.query(m)
        if similar_items:
            filtered_substrings2.append(substring)
            filtered_positions2.append((start_pos, end_pos))
            for item in similar_items:
                index = int(item.split('_')[1])
                filtered_substrings1.append(substrings1[index][0])
                filtered_positions1.append((substrings1[index][1], substrings1[index][2]))
    
    return filtered_substrings1, filtered_substrings2, filtered_positions1, filtered_positions2

# 读取文件
shiji_text = read_file('./shiji.txt')
hanshu_text = read_file('./hanshu.txt')

# 将文章分割成固定长度的子串
min_window_size = 4  # 最小窗口大小
max_window_size = 10 # 最大窗口大小
step_size = 2        # 步长
shiji_substrings = split_text_fixed_length(shiji_text, min_window_size, max_window_size, step_size)
hanshu_substrings = split_text_fixed_length(hanshu_text, min_window_size, max_window_size, step_size)

# Debug 输出分割后的子串及其位置
print("Shiji substrings and positions:")
for substr, pos_s, pos_e in shiji_substrings[:10]:  # 仅输出前10个以作示例
    print(f"{substr} at position {pos_s, pos_e}")

print("\nHanshu substrings and positions:")
for substr, pos_s, pos_e in hanshu_substrings[:10]:  # 仅输出前10个以作示例
    print(f"{substr} at position {pos_s, pos_e}")

# 使用LSH进行初步过滤
filtered_shiji, filtered_hanshu, filtered_positions_shiji, filtered_positions_hanshu = lsh_filter(shiji_substrings, hanshu_substrings, threshold=0.9)

# 打印过滤后的子串及其位置
print("\nFiltered Shiji substrings and positions:")
for substr, (start_pos, end_pos) in zip(filtered_shiji, filtered_positions_shiji):
    print(f"{substr} at positions {start_pos}-{end_pos}")

print("\nFiltered Hanshu substrings and positions:")
for substr, (start_pos, end_pos) in zip(filtered_hanshu, filtered_positions_hanshu):
    print(f"{substr} at positions {start_pos}-{end_pos}")

# 计算并打印过滤指标
original_length_shiji = len(shiji_text)
original_length_hanshu = len(hanshu_text)
filtered_length_shiji = sum(len(substr) for substr in filtered_shiji)
filtered_length_hanshu = sum(len(substr) for substr in filtered_hanshu)

print(f"\nShiji filtered length: {filtered_length_shiji} / {original_length_shiji} ({filtered_length_shiji / original_length_shiji * 100:.2f}%)")
print(f"Hanshu filtered length: {filtered_length_hanshu} / {original_length_hanshu} ({filtered_length_hanshu / original_length_hanshu * 100:.2f}%)")

# 构建矩阵或哈希输出
result = {}
for substr1, (start_pos1, end_pos1), substr2, (start_pos2, end_pos2) in zip(filtered_shiji, filtered_positions_shiji, filtered_hanshu, filtered_positions_hanshu):
    key = f"文章1-'{substr1}'-{start_pos1}-{end_pos1}"
    if key not in result:
        result[key] = []
    result[key].append(f"文章2-'{substr2}'-{start_pos2}-{end_pos2}")

# 打印最终结果
print("\n相似的子字符串对:")
for key, values in result.items():
    print(f"{key}: {','.join(values)}")

# 输出过滤后的文章
with open('./filtered_shiji.txt', 'w', encoding='utf-8') as file:
    file.write(''.join(filtered_shiji))

with open('./filtered_hanshu.txt', 'w', encoding='utf-8') as file:
    file.write(''.join(filtered_hanshu))

print("初步过滤后的文章已输出到filtered_shiji.txt和filtered_hanshu.txt。")