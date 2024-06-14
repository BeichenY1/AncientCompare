import pandas as pd
import matplotlib.pyplot as plt
from math import log

# 文档集合
documents = [
    "the cat in the hat",
    "the cat is in the bag",
    "the cat and the hat"
]

# 词频统计
def compute_tf(doc):
    tf_dict = {}
    words = doc.split()
    for word in words:
        tf_dict[word] = tf_dict.get(word, 0) + 1
    tf_dict = {word: tf_dict[word] / len(words) for word in tf_dict}
    return tf_dict

# 逆文档频率统计
def compute_idf(doc_list):
    idf_dict = {}
    N = len(doc_list)
    for doc in doc_list:
        words = set(doc.split())
        for word in words:
            idf_dict[word] = idf_dict.get(word, 0) + 1
    idf_dict = {word: log(N / idf_dict[word]) for word in idf_dict}
    return idf_dict

# 计算TF-IDF
def compute_tfidf(doc_list):
    tfidf_list = []
    idf_dict = compute_idf(doc_list)
    for doc in doc_list:
        tf_dict = compute_tf(doc)
        tfidf_dict = {word: tf_dict[word] * idf_dict[word] for word in tf_dict}
        tfidf_list.append(tfidf_dict)
    return tfidf_list

# 计算每个文档的TF-IDF值
tfidf_values = compute_tfidf(documents)

# 转换为DataFrame以便展示
df = pd.DataFrame(tfidf_values)
df = df.fillna(0)

# 绘制图表
df.plot(kind='bar', figsize=(12, 8))
plt.title('TF-IDF Values for Each Document')
plt.xlabel('Documents')
plt.ylabel('TF-IDF')
plt.legend(title='Words', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()