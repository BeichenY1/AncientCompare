import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 读取文件内容
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 将文本分割成固定长度的子串（##？ 滑动窗口，考虑调整窗口尺寸和步长进行微调）
def split_text_fixed_length(text, window_size=4, step=2):
    length = len(text)
    return [text[i:i+window_size] for i in range(0, length - window_size + 1, step)]

# 使用Jaccard相似度快速排除不相似的句子
def jaccard_similarity(str1, str2):
    set1 = set(str1)  ##？这里考虑不用集合，因为要总结出所有的对应位置
    set2 = set(str2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

# 保留剩余的句子
def filter_sentences(sentences1, sentences2, threshold=0.2):
    filtered_sentences1 = []
    filtered_sentences2 = []

    for s1 in sentences1:
        for s2 in sentences2:
            if jaccard_similarity(s1, s2) > threshold:
                filtered_sentences1.append(s1)
                filtered_sentences2.append(s2)

    return list(set(filtered_sentences1)), list(set(filtered_sentences2))

def tfidf_filter(sentences1, sentences2, threshold=0.2):
    # 创建TF-IDF向量化器
    vectorizer = TfidfVectorizer()
    # 对sentences1执行fit_transform：学习词汇表并转换为TF-IDF矩阵
    tfidf_matrix1 = vectorizer.fit_transform(sentences1)
    # 对sentences2执行transform：使用已经学习到的词汇表将其转换为TF-IDF矩阵
    tfidf_matrix2 = vectorizer.transform(sentences2)
    # 计算两个TF-IDF矩阵之间的余弦相似度
    cosine_sim = cosine_similarity(tfidf_matrix1, tfidf_matrix2)

    filtered_sentences1 = set() ##？这里考虑不用集合，因为要总结出所有的对应位置
    filtered_sentences2 = set()

    for i, row in enumerate(cosine_sim):
        for j, score in enumerate(row):
            if score > threshold:
                filtered_sentences1.add(sentences1[i])
                filtered_sentences2.add(sentences2[j])

    return list(filtered_sentences1), list(filtered_sentences2)

# 读取文件内容
shiji_text = read_file('./shiji.txt')
hanshu_text = read_file('./hanshu.txt')

# 将文章分割成句子
shiji_sentences = split_text_fixed_length(shiji_text)
hanshu_sentences = split_text_fixed_length(hanshu_text)
print(hanshu_sentences)

# 使用Jaccard相似度进行初步过滤
jaccard_filtered_shiji, jaccard_filtered_hanshu = filter_sentences(shiji_sentences, hanshu_sentences)

# 使用TF-IDF相似度进行进一步过滤
tfidf_filtered_shiji, tfidf_filtered_hanshu = tfidf_filter(jaccard_filtered_shiji, jaccard_filtered_hanshu)

# 将过滤后的句子重新组合成文章
filtered_shiji_text = '。'.join(tfidf_filtered_shiji) + '。'
filtered_hanshu_text = '。'.join(tfidf_filtered_hanshu) + '。'

# 输出过滤后的文章
with open('./filtered_shiji.txt', 'w', encoding='utf-8') as file:
    file.write(filtered_shiji_text)

with open('./filtered_hanshu.txt', 'w', encoding='utf-8') as file:
    file.write(filtered_hanshu_text)

print("初步过滤后的文章已输出到filtered_shiji.txt和filtered_hanshu.txt。")

##? 1、由于最后的输出是两篇文章中对应相似的词语、句子或段落，而索引必须是原文章的索引，如果直接过滤掉某些句子，是不是索引会发生改变呢，所以原先关于set的用法是否也不太对呢，比如文章1中的“学而时习之”和文章2中的好多处“学而时习之”都一样，那么都需要列出来。你能够相应优化吗
##? 1、每个过滤阶段都有相应的输出，输出到相应的文本中
##? 2、所有在指定长度之上（例如：4），指定相似度（例如：相似度90%）的子字符串，所以定为查找 4~20 长度之间的句子