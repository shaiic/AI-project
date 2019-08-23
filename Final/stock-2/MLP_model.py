import get_prices as hist
import tensorflow as tf
from preprocessing import DataProcessing
# import pandas_datareader.data as pdr if using the single test below
import pandas_datareader.data as pdr
import yfinance as fix
import numpy as np
#import matplotlib.pyplot as plt

fix.pdr_override()

start = "2003-01-01"
end = "2018-01-01"

hist.get_stock_data("AAPL", start_date=start, end_date=end)
process = DataProcessing("stock_prices.csv", 0.9)
process.gen_test(10) #滑动窗口构建测试样本
process.gen_train(10) #滑动窗口构建训练样本

X_train = process.X_train / np.array([200, 1e9])  # 归一化， 包括Adj Close 和 Volume, 是否比x' = (x-min/max-min)更靠谱？min=0,max=200
X_train = X_train.reshape(X_train.shape[0], 20)
Y_train = process.Y_train / 200

X_test = process.X_test / np.array([200, 1e9])
X_test = X_test.reshape(X_test.shape[0], 20)
Y_test = process.Y_test / 200

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(32, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(64, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(1, activation=tf.nn.relu))

model.compile(optimizer="adam", loss="mean_squared_error")

model.fit(X_train, Y_train, epochs=100)

print(model.evaluate(X_test, Y_test))

# If instead of a full backtest, you just want to see how accurate the model is for a particular prediction, run this:
data = pdr.get_data_yahoo("AAPL", "2017-12-19", "2018-01-03")
stock = data[["Adj Close", "Volume"]]  # adj close,除权价格(前除权)

X_predict = np.array(stock)
X_predict = X_predict / np.array([200, 1e9])
X_predict = X_predict.reshape(1, 20)

print("predict:")
print(model.predict(X_predict)*200)
