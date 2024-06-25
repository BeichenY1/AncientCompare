import re
from collections import defaultdict, Counter
from difflib import SequenceMatcher

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 滑动窗口分割文本
def split_text_fixed_length(text, window_size, step, start_offset=0):
    length = len(text)
    substrings = [(text[i:i+window_size], i + start_offset, i + window_size - 1 + start_offset) 
                  for i in range(0, length - window_size + 1, step)]
    return substrings

# 计算N-gram
def ngrams(text, n):
    return [text[i:i+n] for i in range(len(text) - n + 1)]

# 计算N-gram相似度
def ngram_similarity(str1, str2, n):
    ngrams1 = Counter(ngrams(str1, n))
    ngrams2 = Counter(ngrams(str2, n))
    intersection = sum((ngrams1 & ngrams2).values())
    union = sum((ngrams1 | ngrams2).values())
    return intersection / union if union != 0 else 0

# 计算段落相似度并筛选
def filter_similar_segments(segments1, segments2, n, ngram_threshold):
    similar_segments = defaultdict(list)
    for seg1, idx1_start, idx1_end in segments1:
        for seg2, idx2_start, idx2_end in segments2:
            similarity = ngram_similarity(seg1, seg2, n)
            if similarity >= ngram_threshold:
                key = f"文章一-段落-{idx1_start}-{idx1_end}"
                similar_segments[key].append(f"文章二-段落-{idx2_start}-{idx2_end}")
    return similar_segments

# 计算两个字符串之间的相似度
def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

# 计算最长公共子串(找到完全一样的字符串)
def longest_common_substrings(str1, str2):
    m, n = len(str1), len(str2)
    lcs_matrix = [[0] * (n + 1) for _ in range(m + 1)]
    length = 0
    substrings = set()

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                lcs_matrix[i][j] = lcs_matrix[i - 1][j - 1] + 1
                if lcs_matrix[i][j] > length:
                    length = lcs_matrix[i][j]
                    substrings = {str1[i - length:i]}
                elif lcs_matrix[i][j] == length:
                    substrings.add(str1[i - length:i])

    return list(substrings)

# 使用最长公共子串筛选并输出最大相似子串
def lcs_based_filtering(segments1, segments2, n, ngram_threshold, lcs_threshold, window_size):
    similar_segments = defaultdict(list)
    lcs_results = []

    for seg1, idx1_start, idx1_end in segments1:
        for seg2, idx2_start, idx2_end in segments2:
            lcs_list = longest_common_substrings(seg1, seg2)
            for lcs in lcs_list:
                lcs_similarity = len(lcs) / max(len(seg1), len(seg2))
                if lcs_similarity >= lcs_threshold:
                    lcs_results.append((lcs, idx1_start, idx1_end, idx2_start, idx2_end, lcs_similarity))
                    segments1 = [seg for seg in segments1 if seg1 not in seg[0]]
                    segments2 = [seg for seg in segments2 if seg2 not in seg[0]]
                else:
                    overall_similarity = calculate_similarity(seg1, seg2)
                    if overall_similarity >= lcs_threshold:
                        lcs_results.append((seg1, idx1_start, idx1_end, idx2_start, idx2_end, overall_similarity))
                        segments1 = [seg for seg in segments1 if seg1 not in seg[0]]
                        segments2 = [seg for seg in segments2 if seg2 not in seg[0]]

    # 打印并保存LCS和相似度结果
    with open('./final_similar_segments.txt', 'a', encoding='utf-8') as file:
        file.write(f"\n窗口长度: {window_size}\n")
        file.write(f"{'文章一':<40} {'文章二':<40} {'相似度':<10}\n")
        for lcs, start1, end1, start2, end2, similarity in lcs_results:
            similarity_percentage = f"{similarity * 100:.2f}%"
            article1 = f"{lcs}-{start1}-{end1}"
            article2 = f"{lcs}-{start2}-{end2}"
            print(f"{article1:<40} {article2:<40} {similarity_percentage:<10}")
            file.write(f"{article1:<40} {article2:<40} {similarity_percentage:<10}\n")
    
    for seg1, idx1_start, idx1_end in segments1:
        for seg2, idx2_start, idx2_end in segments2:
            similarity = ngram_similarity(seg1, seg2, n)
            if similarity >= ngram_threshold:
                key = f"文章一-段落-{idx1_start}-{idx1_end}"
                similar_segments[key].append(f"文章二-段落-{idx2_start}-{idx2_end}")

    return similar_segments

# 初步过滤并逐步细化
def progressive_filtering(text1, text2, initial_window_size, step, n, ngram_threshold, lcs_threshold, min_window_size, max_window_size):
    segments1 = split_text_fixed_length(text1, initial_window_size, step)
    segments2 = split_text_fixed_length(text2, initial_window_size, step)
    similar_segments = filter_similar_segments(segments1, segments2, n, ngram_threshold)

    current_window_size = initial_window_size
    print(f"Initial window size: {initial_window_size}, step: {step}")
    print(f"Initial segments count - text1: {len(segments1)}, text2: {len(segments2)}")
    print(f"Initial similar segments count: {len(similar_segments)}")
    # print("Initial similar segments (sample):")
    # for k, v in list(similar_segments.items())[:5]:  # Print first 5 similar segments as a sample
    #     print(f"{k}: {v}")

    while current_window_size > min_window_size:
        if current_window_size > max_window_size and (current_window_size // 2) > max_window_size :
            next_window_size = current_window_size // 2
        elif current_window_size > max_window_size and (current_window_size // 2) < max_window_size:
            next_window_size = max_window_size
        else:
            next_window_size = current_window_size - 1

        step = max(step // 2, 4)
        new_segments1 = []
        new_segments2 = []
        seen_segments2 = set()

        for key, value in similar_segments.items():
            idx1_start, idx1_end = map(int, re.findall(r'\d+', key))
            new_segments1.extend(split_text_fixed_length(text1[idx1_start:idx1_end+1], next_window_size, step, idx1_start))
            for seg in value:
                idx2_start, idx2_end = map(int, re.findall(r'\d+', seg))
                if (idx2_start, idx2_end) not in seen_segments2:
                    new_segments2.extend(split_text_fixed_length(text2[idx2_start:idx2_end+1], next_window_size, step, idx2_start))
                    seen_segments2.add((idx2_start, idx2_end))

        if next_window_size > max_window_size:
            similar_segments = filter_similar_segments(new_segments1, new_segments2, n, ngram_threshold)
        else:
            similar_segments = lcs_based_filtering(new_segments1, new_segments2, n, ngram_threshold, lcs_threshold, next_window_size)

        print(f"\nCurrent window size: {next_window_size}, step: {step}")
        print(f"New segments count - text1: {len(new_segments1)}, text2: {len(new_segments2)}")
        print(f"New similar segments count: {len(similar_segments)}")

        segments1, segments2 = new_segments1, new_segments2
        current_window_size = next_window_size

    return segments1, segments2, similar_segments

# 主函数
def main():
    hanshu_text = read_file('./hanshu.txt')
    shiji_text = read_file('./shiji.txt')
    
    initial_window_size = 100
    step = 100
    n = 2  # 使用2-gram相似度
    ngram_threshold = 0.05  # 用于n-gram过滤的阈值
    lcs_threshold = 0.80  # 用于LCS过滤的阈值
    min_window_size = 4
    max_window_size = 15
    progressive_filtering(shiji_text, hanshu_text, initial_window_size, step, n, ngram_threshold, lcs_threshold, min_window_size, max_window_size)

    print("最终相似的段落对已输出到final_similar_segments.txt。")

if __name__ == "__main__":
    main()