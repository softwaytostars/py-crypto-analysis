
import tensorflow as tf

from sklearn.datasets import fetch_mldata
mnist = fetch_mldata(' /Users/Thomas/Dropbox/Learning/Upwork/tuto_TF/data/mldata/MNIST original')
print(mnist.data.shape)
print(mnist.target.shape)

def neuralNN(df):
    dataset = tf.data.Dataset.from_tensor_slices((df.values, target.values))
