from collections import defaultdict
from rapidfuzz import fuzz
import Levenshtein

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

# 使用RapidFuzz计算段落间的相似度
def calculate_fuzz_similarity(str1, str2):
    return fuzz.ratio(str1, str2) / 100.0

# 计算字符串相似度（Levenshtein）
def calculate_levenshtein_similarity(str1, str2):
    return Levenshtein.ratio(str1, str2)

# 计算段落相似度并筛选
def filter_similar_segments(segments1, segments2, seg_threshold):
    similar_segments = defaultdict(list)
    for seg1, idx1_start, idx1_end in segments1:
        for seg2, idx2_start, idx2_end in segments2:
            similarity = calculate_fuzz_similarity(seg1, seg2)
            if similarity >= seg_threshold:
                key = f"文章一-段落-{idx1_start}-{idx1_end}"
                similar_segments[key].append((f"文章二-段落-{idx2_start}-{idx2_end}-{similarity * 100:.2f}%"))
    return similar_segments

# 使用最长公共子串筛选并输出最大相似子串
def lcs_based_filtering(segments1, segments2, seg_threshold, lcs_threshold, window_size):
    similar_segments = defaultdict(list)
    lcs_results = []

    for seg1, idx1_start, idx1_end in segments1:
        for seg2, idx2_start, idx2_end in segments2:
            lcs_similarity = calculate_levenshtein_similarity(seg1, seg2)
            if lcs_similarity >= lcs_threshold:
                lcs_results.append((seg1, idx1_start, idx1_end, seg2, idx2_start, idx2_end, lcs_similarity))
                segments1 = [seg for seg in segments1 if seg1 not in seg[0]]
                segments2 = [seg for seg in segments2 if seg2 not in seg[0]]

    # 打印并保存LCS和相似度结果
    with open('./final_similar_segments.txt', 'a', encoding='utf-8') as file:
        file.write(f"\n窗口长度: {window_size}\n")
        file.write(f"{'文章一':<40} {'文章二':<40} {'相似度':<10}\n")
        print(f"\n窗口长度: {window_size}\n")
        for seg1, start1, end1, seg2, start2, end2, similarity in lcs_results:
            similarity_percentage = f"{similarity * 100:.2f}%"
            article1 = f"{seg1}-{start1}-{end1}"
            article2 = f"{seg2}-{start2}-{end2}"
            print(f"{article1:<40} {article2:<40} {similarity_percentage:<10}")
            file.write(f"{article1:<40} {article2:<40} {similarity_percentage:<10}\n")
    
    for seg1, idx1_start, idx1_end in segments1:
        for seg2, idx2_start, idx2_end in segments2:
            similarity = calculate_fuzz_similarity(seg1, seg2)
            if similarity >= seg_threshold:
                key = f"文章一-段落-{idx1_start}-{idx1_end}"
                similar_segments[key].append((f"文章二-段落-{idx2_start}-{idx2_end}-{similarity * 100:.2f}%"))

    return similar_segments

# 初步过滤并逐步细化
def progressive_filtering(text1, text2, initial_window_size, step, seg_threshold, lcs_threshold, min_window_size, max_window_size):
    segments1 = split_text_fixed_length(text1, initial_window_size, step)
    segments2 = split_text_fixed_length(text2, initial_window_size, step)
    similar_segments = filter_similar_segments(segments1, segments2, seg_threshold)

    current_window_size = initial_window_size
    print(f"Initial window size: {initial_window_size}, step: {step}")
    print(f"Initial segments count - text1: {len(segments1)}, text2: {len(segments2)}")
    print(f"Initial similar segments count: {len(similar_segments)}")
    print("Initial similar segments (sample):")
    for k, v in list(similar_segments.items())[:5]:  # Print first 5 similar segments as a sample
        print(f"{k}: {v}") 

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
            # 使用字符串分割来解析索引
            parts = key.split('-')
            idx1_start, idx1_end = int(parts[2]), int(parts[3])
            new_segments1.extend(split_text_fixed_length(text1[idx1_start:idx1_end+1], next_window_size, step, idx1_start))
            
            for seg in value:
                # 确保seg是字符串并使用字符串分割来解析索引
                if isinstance(seg, str):
                    seg_parts = seg.split('-')
                    idx2_start, idx2_end = int(seg_parts[2]), int(seg_parts[3])
                    if (idx2_start, idx2_end) not in seen_segments2:
                        new_segments2.extend(split_text_fixed_length(text2[idx2_start:idx2_end+1], next_window_size, step, idx2_start))
                        seen_segments2.add((idx2_start, idx2_end))
                else:
                    print(f"Unexpected format for seg: {seg}")

        if next_window_size > max_window_size:
            similar_segments = filter_similar_segments(new_segments1, new_segments2, seg_threshold)
        else:
            similar_segments = lcs_based_filtering(new_segments1, new_segments2, seg_threshold, lcs_threshold, next_window_size)

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
    
    initial_window_size = 1000
    step = 1000
    seg_threshold = 0.01  # 用于Segment过滤的阈值
    lcs_threshold = 0.8  # 用于LCS过滤的阈值
    min_window_size = 4
    max_window_size = 30
    progressive_filtering(shiji_text, hanshu_text, initial_window_size, step, seg_threshold, lcs_threshold, min_window_size, max_window_size)

    print("最终相似的段落对已输出到final_similar_segments.txt。")

if __name__ == "__main__":
    main()