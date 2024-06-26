from difflib import SequenceMatcher
from rapidfuzz import fuzz
import Levenshtein
import jellyfish

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

#1 SequenceMatcher
def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).get_matching_blocks()
    return SequenceMatcher(None, str1, str2).rito()

#2 RapidFuzz
def calculate_similarity_rapidfuzz(str1, str2):
    return fuzz.ratio(str1, str2) / 100.0

#3 Levenshtein
def calculate_similarity_levenshtein(str1, str2):
    return 1 - Levenshtein.distance(str1, str2) / max(len(str1), len(str2))

#4 Jellyfish
def calculate_similarity_jellyfish(str1, str2):
    return jellyfish.jaro_winkler_similarity(str1, str2)

# 使用find_longest_match() 和相似度计算来找出满足指定条件（长度和相似度）的所有相似子字符串
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
                similar_substrings.append((substring_s1, substring_s2, similarity))

    return similar_substrings

# 主函数
def main():
    hanshu_text = read_file('./hanshu.txt')
    shiji_text = read_file('./shiji.txt')

    
    # # 示例1
    # matcher = calculate_similarity(hanshu_text, shiji_text)
    # matching_substrings = []
    # for i,block in enumerate(matcher):
    #     if block.size > 0:  # 忽略空块
    #         substring_s1 = hanshu_text[block.a:block.a + block.size]
    #         substring_s2 = shiji_text[block.b:block.b + block.size]
    #         print(i,substring_s1,substring_s2)
    #         matching_substrings.append((substring_s1, substring_s2, block.size))

    # 示例2
    similarity2 = calculate_similarity_rapidfuzz(hanshu_text, "我们")
    print(f"RapidFuzz-相似度: {similarity2 * 100:.2f}%")

    # # 示例3
    # similarity3 = calculate_similarity_levenshtein(hanshu_text, shiji_text)
    # print(f"Levenshtein-相似度: {similarity3 * 100:.2f}%")

    # # 示例4
    # similarity4 = calculate_similarity_jellyfish(hanshu_text, shiji_text)
    # print(f"Jellyfish-相似度: {similarity4 * 100:.2f}%")

    # 示例5
    # min_length = 4
    # min_similarity = 50

    # max_similar_substrings = get_max_similar_substrings(hanshu_text, shiji_text, min_length, min_similarity)
    # for i, (s1_sub, s2_sub, similarity) in enumerate(max_similar_substrings):
    #     print(f"Match found {i}: '{s1_sub}'-'{s2_sub}'- {similarity}%")

if __name__ == "__main__":
    main()
