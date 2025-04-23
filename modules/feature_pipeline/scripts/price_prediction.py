from price_perdiction.price_prediction import predict_price

pred = predict_price("AAPL")
print(f"Predicted Next Close Price: ${pred:.2f}")