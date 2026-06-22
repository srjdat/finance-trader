import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

# variables
ticker = 'AAPL'
red = 'red'
green = 'green'
width1 = .6
width2 = .1

df = pd.DataFrame(yf.Ticker(ticker=ticker).history(period='2y'))
df['pos'] = np.arange(len(df)) # add a position index for displaying
# print(df.axes)

plt.figure(figsize=(14, 7))

# which days are going up and which days are goind won
up = df[df.Close >= df.Open]
down = df[df.Close < df.Open]

# moving average
df['SMA20'] = df.Close.rolling(window=20).mean()
df['SMA50'] = df.Close.rolling(window=50).mean()

# display all the ups and downs
# using position to display first
plt.bar(up.pos, up.Close-up.Open, width=width1, bottom=up.Open, color=green)
plt.bar(up.pos, up.High-up.Close, width=width2, bottom=up.Close, color=green)
plt.bar(up.pos, up.Low-up.Open, width=width2, bottom=up.Open, color=green)
plt.bar(down.pos, down.Close-down.Open, width=width1, bottom=down.Open, color=red)
plt.bar(down.pos, down.High-down.Open, width=width2, bottom=down.Open, color=red)
plt.bar(down.pos, down.Low-down.Close, width=width2, bottom=down.Close, color=red)
plt.plot(df.pos, df['SMA20'], color='blue', label='SMA 20', linewidth=.5)


# find the step for slicing
step = max(len(df) // 7, 1)

# include first and last
tick_pos = list(df['pos'][::step])
tick_label = list(df.index.date[::step])

# if first isn't in there 
if df['pos'].iloc[0] not in tick_pos: 
    tick_pos.insert(0, df['pos'].iloc[0])
    tick_label.insert(0, df.index.date[0])

# if last isn't in there
if df['pos'].iloc[-1] not in tick_pos: 
    tick_pos.append(df['pos'].iloc[-1])
    tick_label.append(df.index.date[-1])

# plot the data and show it 
plt.title(ticker + " Stock Price for the past month") 
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.xticks(tick_pos, tick_label, rotation=45, ha='right') # changing the x axis to dates instead of position
plt.show()