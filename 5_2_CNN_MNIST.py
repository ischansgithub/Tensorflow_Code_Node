#%%
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
sess = tf.InteractiveSession()


def weight_variable(shape):
  #truncated_normal:从截断的正态分布中输出随机值
  #shape: A 1-D integer Tensor or Python array. The shape of the output tensor.
  #stddev: standard deviation 截断的正态分布的标准偏差
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  #创建一个shape为shape的list，并全用0.1填充
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

#计算二维卷积
def conv2d(x, W):
  #x:输入   W：卷积的参数，eg参数[5,5,1,32]，5，5代表卷积核尺寸；1灰色单色；32个卷积核
  #strides:卷积模板移动的步长；
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


#最大池化函数，将2*2的像素块降为1*1像素块
def max_pool_2x2(x):
  #第一个参数value：需要池化的输入，一般池化层接在卷积层后面，所以输入通常是feature map，
  #依然是[batch, height, width, channels]这样的shape
  #ksize: 池化窗口的大小，一般是[1, height, width, 1]
  #tf.nn.max_pool 返回一个tensor，shape仍然是[batch, height, width, channels]这种形式
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')  
                        
x = tf.placeholder(tf.float32, [None, 784])  #特征
y_ = tf.placeholder(tf.float32, [None, 10])  #label
x_image = tf.reshape(x, [-1,28,28,1])        #reshape()把1*784 转化为28*28,并赋于x_image变量

###########################第一个卷积层#################################                        
W_conv1 = weight_variable([5, 5, 1, 32])  #卷积核尺寸5，5；图像为灰色单色；32个卷积核
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)  #ReLU激活函数进行非线性处理
h_pool1 = max_pool_2x2(h_conv1)

###########################第二个卷积层#################################
W_conv2 = weight_variable([5, 5, 32, 64]) #卷积核变为64，能提取64种特征
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])
h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

#dropout():为了防止或减轻过拟合而使用的函数，它一般用在全连接层
#keep_prob: 设置神经元被选中的概率,在初始化时keep_prob是一个占位符, keep_prob = tf.placeholder(tf.float32) 
#tensorflow在run时设置keep_prob具体的值，例如keep_prob: 0.5
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob) 

W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])
y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

#tf.equal(A, B)是对比这两个矩阵或者向量的相等的元素
#如果是相等的那就返回True，反正返回False，返回的值的矩阵维度和A是一样的

#tf.argmax(vector, 1)：返回的是vector中的最大值的索引号，如果vector是一个向量，那就返回一个值
#如果是一个矩阵，那就返回一个向量，这个向量的每一个维度都是相对应矩阵行的最大值元素的索引号。

#cast(x, dtype, name=None) 将x的数据格式转化成dtype
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
tf.global_variables_initializer().run()
#eval() 其实就是tf.Tensor的Session.run()的另外一种写法
for i in range(20000):
  batch = mnist.train.next_batch(50)
  #每100次训练，评测一次准确率
  if i%100 == 0:
    train_accuracy = accuracy.eval(feed_dict={
        x:batch[0], y_: batch[1], keep_prob: 1.0})
    print("step %d, training accuracy %g"%(i, train_accuracy))
  train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

print("test accuracy %g"%accuracy.eval(feed_dict={
    x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))



