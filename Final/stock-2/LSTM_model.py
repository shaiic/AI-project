import pandas as pd
import numpy as np
import get_prices as hist
import tensorflow as tf
from preprocessing import DataProcessing
import pandas_datareader.data as pdr
import yfinance as fix
import matplotlib.pyplot as plt
import WXBizSendMsg

fix.pdr_override()

start = "2000-01-01"
end = "2019-08-22"

stock="000001.SS"

hist.get_stock_data(stock, start_date=start, end_date=end)
process = DataProcessing("stock_prices.csv", 0.9)

process.gen_test(10)
process.gen_train(10)


X_train = process.X_train / np.array([process.value_max, process.volume_max])  # 归一化， 包括Adj Close 和 Volume
Y_train = process.Y_train / process.value_max

X_test = process.X_test / np.array([process.value_max, process.volume_max])
Y_test = process.Y_test / process.value_max

model = tf.keras.Sequential()
model.add(tf.keras.layers.LSTM(20, input_shape=(10, 2), return_sequences=True))
model.add(tf.keras.layers.LSTM(20))
model.add(tf.keras.layers.Dense(1))

model.compile(optimizer="adam",loss="mean_squared_error")

h=model.fit(X_train, Y_train, epochs=50,shuffle=True,batch_size=1)


print("history.loss:",h.history)
plt.title('loss') 
losses=h.history['loss']
plt.plot(losses, label='loss')  
plt.legend()  
plt.show()

print(model.evaluate(X_test, Y_test))

X_predict = model.predict(X_test)
plt.title(start+"—"+end) 
plt.plot(Y_test * process.value_max, label="Actual", c="blue")
plt.plot(X_predict * process.value_max, label="Predict", c="red")
plt.legend()
plt.savefig('stock.png')
plt.show()

data = pdr.get_data_yahoo(stock, "2019-08-09", "2019-08-22")
stock = data[["Adj Close", "Volume"]]
X1_predict = np.array(stock) / np.array([process.value_max, process.volume_max])
X1_predict = X1_predict.reshape(1, -1, 2)

print("predict:")
predict=model.predict(X1_predict) * process.value_max
print(predict)


api = WXBizSendMsg.WXBizSendMsg(WXBizSendMsg.sCorpID,WXBizSendMsg.corpsecret)
#发送图片
media_id = api.upload_media("file","./stock.png")
message = WXBizSendMsg.ImageMessage(WXBizSendMsg.agentID,touser="@all",media_id=media_id)
res = api.send_message(message)
print(res)#

predict="{:.2f}".format(predict[0][0])
message = WXBizSendMsg.TextMessage(WXBizSendMsg.agentID,touser='@all',content="明日上证指数:"+predict)
res = api.send_message(message)
print(res)



# If instead of a full backtest, you just want to see how accurate the model is for a particular prediction, run this:
#data = pdr.get_data_yahoo("AAPL", "2017-12-19", "2018-01-03")
#stock = data["Adj Close"]
#X_predict = np.array(stock).reshape((1, 10)) / 200
#print("predict:")
#print(model.predict(X_predict)*200)
