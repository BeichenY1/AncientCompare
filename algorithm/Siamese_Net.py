import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, Lambda
import matplotlib.pyplot as plt

# 加载MNIST数据
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images.astype('float32') / 255.0
test_images = test_images.astype('float32') / 255.0
train_images = np.expand_dims(train_images, axis=-1)
test_images = np.expand_dims(test_images, axis=-1)

# 定义基础卷积神经网络
def create_base_network(input_shape):
    input = Input(shape=input_shape)
    x = Conv2D(32, (3, 3), activation='relu')(input)
    x = MaxPooling2D((2, 2))(x)
    x = Flatten()(x)
    x = Dense(128, activation='relu')(x)
    return Model(input, x)

# 创建Siamese Network
input_shape = (28, 28, 1)
base_network = create_base_network(input_shape)

input_a = Input(shape=input_shape)
input_b = Input(shape=input_shape)

processed_a = base_network(input_a)
processed_b = base_network(input_b)

# 计算欧几里得距离
def euclidean_distance(vects):
    x, y = vects
    return tf.sqrt(tf.reduce_sum(tf.square(x - y), axis=1, keepdims=True))

distance = Lambda(euclidean_distance)([processed_a, processed_b])

# 定义Siamese Network模型
siamese_network = Model([input_a, input_b], distance)

# 对比损失函数
def contrastive_loss(y_true, y_pred):
    margin = 1
    return tf.reduce_mean(y_true * tf.square(y_pred) +
                          (1 - y_true) * tf.square(tf.maximum(margin - y_pred, 0)))

siamese_network.compile(optimizer='adam', loss=contrastive_loss)

# 生成配对数据
def create_pairs(x, digit_indices):
    pairs = []
    labels = []
    n = min([len(digit_indices[d]) for d in range(10)]) - 1
    for d in range(10):
        for i in range(n):
            z1, z2 = digit_indices[d][i], digit_indices[d][i + 1]
            pairs += [[x[z1], x[z2]]]
            inc = np.random.choice([i for i in range(1, 10) if i != d])
            dn = (d + inc) % 10
            z1, z2 = digit_indices[d][i], digit_indices[dn][i]
            pairs += [[x[z1], x[z2]]]
            labels += [1, 0]
    return np.array(pairs), np.array(labels)

digit_indices = [np.where(train_labels == i)[0] for i in range(10)]
tr_pairs, tr_y = create_pairs(train_images, digit_indices)

digit_indices = [np.where(test_labels == i)[0] for i in range(10)]
te_pairs, te_y = create_pairs(test_images, digit_indices)

# 训练Siamese Network
siamese_network.fit([tr_pairs[:, 0], tr_pairs[:, 1]], tr_y,
                    batch_size=128,
                    epochs=10,
                    validation_data=([te_pairs[:, 0], te_pairs[:, 1]], te_y))

# 可视化特征向量
embeddings = base_network.predict(test_images[:5000])
from sklearn.manifold import TSNE
tsne = TSNE(n_components=2)
embeddings_2d = tsne.fit_transform(embeddings)

plt.figure(figsize=(10, 10))
plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], c=test_labels[:5000], cmap='tab10')
plt.colorbar()
plt.show()