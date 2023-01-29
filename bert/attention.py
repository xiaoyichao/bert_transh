'''
Author: xiaoyichao xiaoyichao@haohaozhu.com
Date: 2023-01-29 14:04:06
LastEditors: root root@haohaozhu.com
LastEditTime: 2023-01-29 17:08:14
FilePath: /search_opt/bert_regress/test.py
Description: 
'''
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

tf.random.set_seed(5)

width = 768
batch_size,seq_length,num_attention_heads, attention_head_size = 16,512,12,int(width/12)
from_seq_length = seq_length
to_seq_length = seq_length
embedding = tf.random.normal(shape=[batch_size,from_seq_length,width])
to_mask = tf.random.normal(shape=[batch_size,from_seq_length],mean=0.5,stddev=1)

one = tf.ones_like(to_mask)   #生成与a大小一致的值全部为1的矩阵
zero = tf.zeros_like(to_mask)
to_mask = tf.where(to_mask <0.5, x=zero, y=one) #0.5为阈值
    


def transpose_for_scores(input_tensor):
    output_tensor = tf.reshape(input_tensor,[batch_size,seq_length,num_attention_heads, attention_head_size])
    output_tensor = tf.transpose(output_tensor,[0,2,1,3])
    return output_tensor

def create_attention_mask(from_seq_length, to_mask):
    # 二维扩增到三维，在不考虑batch的条件下，实际上是把seq_length的数据复制了seq_length次，构成了这个矩阵
    to_seq_length = to_mask.shape[1]
    to_mask = tf.cast(
        tf.reshape(to_mask, [batch_size, 1, to_seq_length]), tf.float32) # [B,T] ->[B,1,T]
    broadcast_ones = tf.ones(
      shape=[batch_size, from_seq_length, 1], dtype=tf.float32) # [B,F,1]

    mask = broadcast_ones * to_mask # [B,F,1] * [B,1,T] -> [B,F,T] 
    return mask 

create_attention_mask(from_seq_length, to_mask)

def attention_layer(from_tensor, to_tensor, attention_mask=None):
    dense_unit = 768
    q_layer = tf.keras.layers.Dense(units=dense_unit,name="q")
    k_layer = tf.keras.layers.Dense(units=dense_unit,name="k")
    v_layer = tf.keras.layers.Dense(units=dense_unit,name="v")

    q = q_layer(from_tensor) # [B,F,N*H]
    k = k_layer(to_tensor) # [B,T,N*H]
    v = v_layer(to_tensor) # [B,T,N*H]

    q = transpose_for_scores(q) # [B,F,N,H]->[B,N,F,H]
    k = transpose_for_scores(k) #[B,T,N,H]->[B,N,T,H]
    

    attention_scores = tf.matmul(q,k,transpose_b=True) # [B,N,F,H]* [B,N,H,T] -> [B,N,F,T]
    d_sqrt =  1/tf.math.sqrt(float(width))
    if attention_mask:
        attention_mask = tf.expand_dims(attention_mask, [1]) #[B, F, T] -> [B, 1, F, T]
    attention_scores = tf.multiply(attention_scores,d_sqrt) #[B,N,F,T]

    attention_porbs = tf.nn.softmax(attention_scores) # [B,N,F,T]
    attention_porbs = tf.keras.layers.Dropout(0.9)(attention_porbs)
    
    v = tf.reshape(to_tensor,[batch_size,seq_length,num_attention_heads, attention_head_size]) # [B,T,N,H]
    v = tf.transpose(v, [0,2,1,3]) # [B,N,T,H]

    y = tf.matmul(attention_porbs, v) #[B,N,F,T] * [B,N,T,H] -> [B,N,F,H]
    y = tf.transpose(y, [0,2,1,3]) # [B,F,N,H]
    y = tf.reshape(to_tensor,[batch_size,seq_length,num_attention_heads*attention_head_size]) # [B,F,N*H]
    return y

y = attention_layer(embedding, embedding)
print(y.shape)

    
