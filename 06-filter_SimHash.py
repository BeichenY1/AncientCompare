from simhash import Simhash, SimhashIndex
import re

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 将文本分段（##? 段落分界处的字句不好判断）
def split_text_by_length(text, segment_length):
    return [(text[i:i+segment_length], i, i+segment_length-1) for i in range(0, len(text), segment_length)]

# 计算文本的SimHash值
def compute_simhash(text):
    return Simhash(text)

# 使用SimHash进行初步过滤，找出相似的大段落
# 使用SimHash进行初步过滤，找出相似的大段落，并按字典形式表示
def simhash_filter(segments1, segments2, threshold=0.1):
    index = SimhashIndex([], k=int((1 - threshold) * 64))
    
    for i, (segment, start_pos, end_pos) in enumerate(segments1):
        simhash = compute_simhash(segment)
        index.add(f"shiji_{i}", simhash)
    
    similarity_dict = {}

    for i, (segment, start_pos, end_pos) in enumerate(segments2):
        simhash = compute_simhash(segment)
        similar_items = index.get_near_dups(simhash)
        if similar_items:
            key = f"文章1-段落{i}-{start_pos}-{end_pos}"
            if key not in similarity_dict:
                similarity_dict[key] = []
            for item in similar_items:
                index_id = int(item.split('_')[1])
                segment_info = f"文章2-段落{index_id}-{segments1[index_id][1]}-{segments1[index_id][2]}"
                similarity_dict[key].append(segment_info)
    
    return similarity_dict


# 读取文件
shiji_text = read_file('./shiji.txt')
hanshu_text = read_file('./hanshu.txt')

# 将文章按段分割
segment_length = 4  # 可以根据需要调整段落长度
shiji_segments = split_text_by_length(shiji_text, segment_length)
hanshu_segments = split_text_by_length(hanshu_text, segment_length)

# 使用SimHash进行初步过滤
similarity_dict = simhash_filter(shiji_segments, hanshu_segments, threshold=0.9)

# 打印最终结果
print("\n相似的大段落对:")
for key, values in similarity_dict.items():
    print(f"{key} 对应于 {values}")

# 输出相似的大段落
with open('./filtered_segments.txt', 'w', encoding='utf-8') as file:
    for key, values in similarity_dict.items():
        file.write(f"{key} 对应于 {values}\n")

print("初步过滤后的大段落已输出到filtered_segments.txt。")