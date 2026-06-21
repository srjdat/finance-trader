import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf


ticker = 'AAPL'

df = pd.DataFrame(yf.Ticker(ticker=ticker).history(period='1mo'))
df['pos'] = np.arange(len(df)) # add a position index for displaying
# print(df.axes)

plt.figure()

# which days are going up and which days are goind won
up = df[df.Close >= df.Open]
down = df[df.Close < df.Open]

# variables
red = 'red'
green = 'green'
width1 = .3
width2 = .03

# display all the ups and downs
# using position to display first
plt.bar(up.pos, up.Close-up.Open, width=width1, bottom=up.Open, color=green)
plt.bar(up.pos, up.High-up.Close, width=width2, bottom=up.Close, color=green)
plt.bar(up.pos, up.Low-up.Open, width=width2, bottom=up.Open, color=green)
plt.bar(down.pos, down.Close-down.Open, width=width1, bottom=down.Open, color=red)
plt.bar(down.pos, down.High-down.Open, width=width2, bottom=down.Open, color=red)
plt.bar(down.pos, down.Low-down.Close, width=width2, bottom=down.Close, color=red)

step = max(len(df) // 7, 1)

plt.title(ticker + " Stock Price for the past month")
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.xticks(df['pos'][::step], df.index.date[::step], rotation=45, ha='right') # changing the x axis to dates instead of position
plt.show()