from rapidfuzz import process, fuzz

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

#2 RapidFuzz
def calculate_similarity_rapidfuzz(str1, str2):
    return fuzz.ratio(str1, str2) / 100.0

# 获取所有最大相似子字符串
def get_max_similar_substrings(text1, text2, min_length=4, min_similarity=90):
    similar_substrings = []

    # 遍历 text1 中所有长度大于等于 min_length 的子串
    for i in range(len(text1) - min_length + 1):
        for j in range(i + min_length, len(text1) + 1):
            substring = text1[i:j]
            # 使用 RapidFuzz 找出 text2 中与当前子串相似度最高的部分
            matches = process.extract(substring, [text2], scorer=fuzz.ratio, limit=1)
            for match, score, _ in matches:
                if score >= min_similarity:
                    similar_substrings.append((substring, match, score))

    return similar_substrings

# 主函数
def main():
    hanshu_text = read_file('./hanshu.txt')
    shiji_text = read_file('./shiji.txt')
    


    similarity2 = calculate_similarity_rapidfuzz(hanshu_text, shiji_text)
    print(f"RapidFuzz-相似度: {similarity2 * 100:.2f}%")
    
    # min_length = 4
    # min_similarity = 90
    #similar_substrings = get_max_similar_substrings(hanshu_text, shiji_text, min_length, min_similarity)

    # print(f"所有最大相似子字符串 (长度 >= {min_length}, 相似度 >= {min_similarity}%):")
    # for substring, match, score in similar_substrings:
    #     print(f"{substring} <-> {match} (相似度: {score}%)")

if __name__ == "__main__":
    main()