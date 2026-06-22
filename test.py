import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

ticker = 'AAPL'

df = pd.DataFrame(yf.Ticker(ticker=ticker).history(period='1mo'))

df.lo

print(df.index)

plt.figure()

# up and down days
up = df[df.Close >= df.Open]
down = df[df.Close < df.Open]

# variables
red = 'red'
green = 'green'
width1 = .3
width2 = .03

plt.bar(up.index.date, up.Close-up.Open, width=width1, bottom=up.Open, color=green)
plt.bar(up.index.date, up.High-up.Close, width=width2, bottom=up.Close, color=green)
plt.bar(up.index.date, up.Low-up.Open, width=width2, bottom=up.Open, color=green)

plt.bar(down.index.date, down.Close-down.Open, width=width1, bottom=down.Open, color=red)
plt.bar(down.index.date, down.High-down.Open, width=width2, bottom=down.Open, color=red)
plt.bar(down.index.date, down.Low-down.Close, width=width2, bottom=down.Close, color=red)

plt.title(ticker + " Stock Price for the past month")
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.xticks(rotation=45, ha='right')
plt.show()