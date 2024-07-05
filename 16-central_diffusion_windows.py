from difflib import SequenceMatcher, Differ
from rapidfuzz import fuzz

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 中心扩散算法找到最大相似子字符串，使用滑动窗口方法
def expand_around_center(s1, s2, start1, start2, size, window_size=10, min_similarity=90):
    def slide_window_compare(s1, s2, start1, start2, direction, window_size, min_similarity):
        expanded = 0
        while 0 <= start1 + direction * (expanded + window_size) < len(s1) and \
              0 <= start2 + direction * (expanded + window_size) < len(s2):
            end1 = start1 + direction * (expanded + window_size)
            end2 = start2 + direction * (expanded + window_size)
            
            if direction == -1:
                window_s1 = s1[max(0, start1 - expanded - window_size):start1 - expanded]
                window_s2 = s2[max(0, start2 - expanded - window_size):start2 - expanded]
            else:
                window_s1 = s1[start1 + expanded:end1]
                window_s2 = s2[start2 + expanded:end2]

            if fuzz.partial_ratio(window_s1, window_s2) < min_similarity:
                break
            expanded += window_size

        # 检查是否还有剩余字符串片段不满足窗口长度
        if direction == -1:
            remaining_s1 = s1[max(0, start1 - expanded):start1]
            remaining_s2 = s2[max(0, start2 - expanded):start2]
        else:
            remaining_s1 = s1[start1 + expanded:min(len(s1), end1)]
            remaining_s2 = s2[start2 + expanded:min(len(s2), end2)]

        if len(remaining_s1) > 0 and fuzz.partial_ratio(remaining_s1, remaining_s2) >= min_similarity:
            expanded += len(remaining_s1) if direction == 1 else -len(remaining_s1)

        return expanded

    left_expanded = slide_window_compare(s1, s2, start1, start2, -1, window_size, min_similarity)
    right_expanded = slide_window_compare(s1, s2, start1 + size - 1, start2 + size - 1, 1, window_size, min_similarity)

    expanded_substring_s1 = s1[max(0, start1 - left_expanded) : min(len(s1), start1 + size + right_expanded)]
    expanded_substring_s2 = s2[max(0, start2 - left_expanded) : min(len(s2), start2 + size + right_expanded)]
    
    return expanded_substring_s1, max(0, start1 - left_expanded), min(len(s1), start1 + size + right_expanded), \
           expanded_substring_s2, max(0, start2 - left_expanded), min(len(s2), start2 + size + right_expanded)

# 找出满足指定条件（长度）的所有相似子字符串
def get_max_similar_substrings(s1, s2, min_length=4, min_similarity=90, window_size=10):
    matcher = SequenceMatcher(None, s1, s2)
    matching_blocks = matcher.get_matching_blocks()
    similar_substrings = []

    # 记录已扩展的范围
    expanded_ranges_s1 = []
    expanded_ranges_s2 = []

    for block in matching_blocks:
        if block.size >= min_length:  # 忽略小于指定长度的块
            new_start1, new_end1 = block.a, block.a + block.size
            new_start2, new_end2 = block.b, block.b + block.size

            # 检查当前块是否与之前的范围重叠
            overlap = False
            for (start1, end1), (start2, end2) in zip(expanded_ranges_s1, expanded_ranges_s2):
                if not (new_end1 <= start1 or new_start1 >= end1 or new_end2 <= start2 or new_start2 >= end2):
                    overlap = True
                    break
            
            if not overlap:
                # 进行扩展
                expanded_s1, new_start1, new_end1, expanded_s2, new_start2, new_end2 = expand_around_center(
                    s1, s2, block.a, block.b, block.size, window_size, min_similarity
                )
                expanded_similarity = fuzz.ratio(expanded_s1, expanded_s2)

                if expanded_similarity >= min_similarity:
                    similar_substrings.append((expanded_s1, new_start1, new_end1, 
                                               expanded_s2, new_start2, new_end2, expanded_similarity))
                    expanded_ranges_s1.append((new_start1, new_end1))
                    expanded_ranges_s2.append((new_start2, new_end2))

    return similar_substrings

# 打印两段相似子字符串的差别
def print_differences(s1, s2):
    d = Differ()
    diff = list(d.compare(s1, s2))
    
    # 提取差异
    s1_diff = []
    s2_diff = []
    for line in diff:
        # 如果这一行以 - 开头，表示这是第一个字符串中有而第二个字符串中没有的部分。
        if line.startswith('- '): 
            s1_diff.append(f"\033[91m{line[2:]}\033[0m")  # 红色表示不同部分
            s2_diff.append(' ' * (len(line) - 2))  # 对齐

        # 如果这一行以 + 开头，表示这是第二个字符串中有而第一个字符串中没有的部分。
        elif line.startswith('+ '): 
            s1_diff.append(' ' * (len(line) - 2))  # 对齐
            s2_diff.append(f"\033[92m{line[2:]}\033[0m")  # 绿色表示不同部分
        else:
            s1_diff.append(line[2:])
            s2_diff.append(line[2:])
    
    # 打印对比结果
    print("".join(s1_diff))
    print("".join(s2_diff))

# 主函数
def main():
    hanshu_text = read_file('./zhuangzi.txt')
    shiji_text = read_file('./lvshichunqiu.txt')

    min_length = 1
    min_similarity = 10
    window_size = 10

    max_similar_substrings = get_max_similar_substrings(hanshu_text, shiji_text, min_length, min_similarity, window_size)
    for i, (s1_sub, s1_start, s1_end, s2_sub, s2_start, s2_end, similarity) in enumerate(max_similar_substrings):
        print(f"Match found {i+1}:")
        print(f"文章一-{s1_start}-{s1_end}：'{s1_sub}'")
        print(f"文章二-{s2_start}-{s2_end}：'{s2_sub}'")
        print(f"相似度：{similarity:.1f}%")
        print("具体差别：")
        print_differences(s1_sub, s2_sub)
        print("-" * 100)

if __name__ == "__main__":
    main()
