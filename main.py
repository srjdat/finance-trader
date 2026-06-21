import yfinance as yf
import pandas as pd
import numpy
import matplotlib.pyplot as plt

price_array: list[numpy.float64] = []
total_change: numpy.float64 = numpy.float64(0.0)
x_array = numpy.arange(1, 252)
y_array = numpy.empty(251)

pd.DatetimeIndex

def get_each_day(open: numpy.float64, close: numpy.float64, high: numpy.float64, low: numpy.float64): 
    y_array[len(price_array)-1] = open
    price_array.append(open)
    
    global total_change
    if len(price_array) > 1: 
        total_change += (price_array[len(price_array)-1] - price_array[len(price_array)-2])

def get_open_close(open: numpy.float64, close: numpy.float64):
    open_close_difference: numpy.float64 = close - open
    return open_close_difference 
    
def get_support(df: pd.DataFrame): 
    print("hello")

hp_data = yf.Ticker("HPE") 
hp_history = hp_data.history(period="1y")

df = pd.DataFrame(data=hp_history)

# print(df)

for index, row in df.iterrows():
    # printtype(row['Open'], row['High'], row['Low'], row['Close'])
    get_each_day(row['Open'], row['High'], row['Low'], row['Close'])
    open_close_difference = get_open_close(row['Open'], row['Close'])

print(df)
# print(total_change)
# print(open_close_difference)
print(len(price_array))
plt.plot(x_array, y_array)
plt.show()

# if total_change < 0: 
#     print("stock went down")
# elif total_change > 0: 
#     print("stock went up")
# else: 
#     print("no change")