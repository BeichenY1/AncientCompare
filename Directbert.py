import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM
from sklearn.metrics.pairwise import cosine_similarity
import jieba

# 加载BERT模型和分词器: https://huggingface.co/google-bert/bert-base-chinese
tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-chinese")
model = AutoModelForMaskedLM.from_pretrained("google-bert/bert-base-chinese")

# 加载文件
with open("./hanshu.txt", 'r', encoding='utf-8') as file:
    hanshu_text = file.read()

# 将文本分句
def split_text(text):
    sentences = list(jieba.cut(text, cut_all=False))
    return sentences

# 将句子转化为BERT向量
def get_sentence_vector(sentence):
    inputs = tokenizer(sentence, return_tensors='pt')
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# 计算句子相似度并筛选相似句子对
def find_similar_sentences(sentences1, sentences2, threshold=0.8):
    vectors1 = [get_sentence_vector(sentence) for sentence in sentences1]
    vectors2 = [get_sentence_vector(sentence) for sentence in sentences2]
    
    similar_sentences = []
    for i, vec1 in enumerate(vectors1):
        for j, vec2 in enumerate(vectors2):
            if cosine_similarity(vec1, vec2) > threshold:
                similar_sentences.append((sentences1[i], sentences2[j], i, j))
    return similar_sentences

# 预处理文本
sentences_hanshu = split_text(hanshu_text)

# 示例，仅处理一篇文章
# 加载《史记》并处理
shiji_text = "加载或输入史记文本"
sentences_shiji = split_text(shiji_text)

# 找出相似句子对
similar_sentences = find_similar_sentences(sentences_hanshu, sentences_shiji)

# 输出结果
result = {}
for s1, s2, idx1, idx2 in similar_sentences:
    key = f"文1: {s1}-{idx1}-{idx1 + len(s1)}"
    if key not in result:
        result[key] = []
    result[key].append({"文2": f"{s2}-{idx2}-{idx2 + len(s2)}"})

print(result)