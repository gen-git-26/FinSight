import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM

def predict_price(symbol, days=60):
    data = yf.download(symbol, period='90d', interval='1d')
    if data.empty:
        return None

    close_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_prices)

    x_train = []
    y_train = []
    for i in range(days, len(scaled_data)):
        x_train.append(scaled_data[i-days:i, 0])
        y_train.append(scaled_data[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(x_train, y_train, epochs=5, batch_size=1, verbose=0)

    last_60_days = scaled_data[-days:]
    last_60_days = np.reshape(last_60_days, (1, last_60_days.shape[0], 1))
    predicted_price = model.predict(last_60_days)
    predicted_price = scaler.inverse_transform(predicted_price)
    
    return float(predicted_price[0][0])
