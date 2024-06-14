import gensim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# 样本语料库
corpus = [
    "I love machine learning",
    "machine learning is fun",
    "I love deep learning"
]

# 预处理语料库
corpus = [gensim.utils.simple_preprocess(doc) for doc in corpus]

# 构建标签化的文档
tagged_data = [gensim.models.doc2vec.TaggedDocument(words=words, tags=[str(i)]) for i, words in enumerate(corpus)]

# 训练Doc2Vec模型
model = gensim.models.Doc2Vec(vector_size=10, window=2, min_count=1, workers=4, epochs=100)
model.build_vocab(tagged_data)
model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

# 获取文档向量
doc_vectors = [model.dv[str(i)] for i in range(len(corpus))]

# 打印文档向量
for i, vec in enumerate(doc_vectors):
    print(f"Document {i}: {vec}")

# 使用PCA将文档向量降维至2D以便可视化
pca = PCA(n_components=2)
doc_vecs_2d = pca.fit_transform(doc_vectors)

# 将文档向量转换为DataFrame以便展示
df = pd.DataFrame(doc_vecs_2d, columns=['PCA Component 1', 'PCA Component 2'])
df['Document'] = ['Document 1', 'Document 2', 'Document 3']

# 绘制文档向量
plt.figure(figsize=(10, 6))
for i in range(len(df)):
    plt.scatter(df['PCA Component 1'][i], df['PCA Component 2'][i])
    plt.text(df['PCA Component 1'][i] + 0.01, df['PCA Component 2'][i] + 0.01, df['Document'][i], fontsize=12)

plt.title('2D Visualization of Doc2Vec Document Embeddings')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()