from difflib import SequenceMatcher
from rapidfuzz import fuzz
import Levenshtein
import jellyfish

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 使用 get_matching_blocks 找出满足指定条件（长度）的所有相似子字符串
def get_max_similar_substrings(s1, s2, min_length=4, min_similarity=90):
    matcher = SequenceMatcher(None, s1, s2)
    matching_blocks = matcher.get_matching_blocks()
    similar_substrings = []

    for block in matching_blocks:
        if block.size >= min_length:  # 忽略小于指定长度的块
            substring_s1 = s1[block.a:block.a + block.size]
            substring_s2 = s2[block.b:block.b + block.size]
            
            similarity = fuzz.ratio(substring_s1, substring_s2)
            if similarity >= min_similarity:
                similar_substrings.append((substring_s1, block.a, block.a + block.size, 
                                           substring_s2, block.b, block.b + block.size, similarity))

    return similar_substrings

# 使用 find_longest_match 找出最长的相似子字符串
def find_longest_substring(s1, s2):
    matcher = SequenceMatcher(None, s1, s2)
    match = matcher.find_longest_match(0, len(s1), 0, len(s2))
    
    longest_substring_s1 = s1[match.a: match.a + match.size]
    longest_substring_s2 = s2[match.b: match.b + match.size]
    
    return longest_substring_s1, match.a, match.a + match.size, longest_substring_s2, match.b, match.b + match.size

# 主函数
def main():
    hanshu_text = read_file('./hanshu.txt')
    shiji_text = read_file('./shiji.txt')

    min_length = 4
    min_similarity = 90

    max_similar_substrings = get_max_similar_substrings(hanshu_text, shiji_text, min_length, min_similarity)
    for i, (s1_sub, s1_start, s1_end, s2_sub, s2_start, s2_end, similarity) in enumerate(max_similar_substrings):
        print(f"Match found {i}: 文章一-'{s1_sub}'-{s1_start}-{s1_end}：文章二-'{s2_sub}'-{s2_start}-{s2_end}，相似度：{similarity:.1f}%")

    
    # longest_substring_s1, start_s1, end_s1, longest_substring_s2, start_s2, end_s2 = find_longest_substring(hanshu_text, shiji_text)
    # print(f"Longest match: 文章一-'{longest_substring_s1}'-{start_s1}-{end_s1}:文章二-'{longest_substring_s2}'-{start_s2}-{end_s2}]")

if __name__ == "__main__":
    main()
