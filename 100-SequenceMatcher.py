from difflib import SequenceMatcher
from rapidfuzz import fuzz
import Levenshtein
import jellyfish

#1 SequenceMatcher
def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

#2 RapidFuzz
def calculate_similarity_rapidfuzz(str1, str2):
    return fuzz.ratio(str1, str2) / 100.0

#3 Levenshtein
def calculate_similarity_levenshtein(str1, str2):
    return 1 - Levenshtein.distance(str1, str2) / max(len(str1), len(str2))

#4 Jellyfish
def calculate_similarity_jellyfish(str1, str2):
    return jellyfish.jaro_winkler_similarity(str1, str2)

# 示例1
similarity1 = calculate_similarity("学而时习之不亦说乎", "学而时习之不亦乐乎")
print(f"相似度: {similarity1 * 100:.2f}%")

# 示例2
similarity2 = calculate_similarity_rapidfuzz("学而时习之不亦说乎", "学而时习之不亦乐乎")
print(f"相似度: {similarity2 * 100:.2f}%")

# 示例3
similarity3 = calculate_similarity_levenshtein("学而时习之不亦说乎", "学而时习之不亦乐乎")
print(f"相似度: {similarity3 * 100:.2f}%")

# 示例4
similarity4 = calculate_similarity_jellyfish("学而时习之不亦说乎", "学而时习之不亦乐乎")
print(f"相似度: {similarity4 * 100:.2f}%")