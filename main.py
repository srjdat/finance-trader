import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.ticker as mlt
import matplotlib.pyplot as plt
import tkinter as tkr
import tkcalendar
from tkinter import ttk
from datetime import datetime
# import mplfinance as mpf

def format_volume(x, pos): 
    return f"{round(x/1000000)}M"

def enter_command(): 
    print(ticker_str.get())
    print(start_date_str.get())
    print(end_date_str.get())
    root.destroy()

    start_date = start_date_str.get().split("/")
    main(ticker_str.get(), '2020-01-01', '2026-01-01')


def gui(): 
    global root
    root = tkr.Tk()
    root.title("User Inputs")
    root.geometry('1030x890')

    global ticker_str, start_date_str, end_date_str

    # user enters the ticker first
    ticker_str = tkr.StringVar()
    ttk.Label(root, text="Ticker", font='15').grid(row=0, column=0, padx=15, pady=(6, 3))
    ticker = ttk.Entry(root, textvariable=ticker_str, width=19)
    ticker.grid(row=0, column=1, padx=5, pady=6)
    
    ttk.Label(root, text='Start Date', font='15').grid(row=1, column=0, padx=15, pady=(6, 3))
    start_date_str = tkr.StringVar()
    start_date = tkcalendar.DateEntry(root, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, font='Segoe 14', textvariable=start_date_str)
    start_date.grid(row=1, column=1, padx=5, pady=6)

    ttk.Label(root, text='End Date', font='15').grid(row=2, column=0, padx=15, pady=(6, 3))
    end_date_str = tkr.StringVar()
    end_date = tkcalendar.DateEntry(root, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, font='Segoe 14', textvariable=end_date_str)
    end_date.grid(row=2, column=1, padx=5, pady=6)

    button = ttk.Button(root, text='Enter', command=enter_command)
    button.grid(row=3, column=0, columnspan=2, pady=6)


    root.mainloop()

def main(ticker: str, start_date: str, end_date: str): 
    # variables
    red = 'red'
    green = 'green'
    width1 = .6
    width2 = .1

    df = pd.DataFrame(yf.Ticker(ticker=ticker).history(start=start_date, end=end_date))
    df['pos'] = np.arange(len(df)) # add a position index for displaying
    # print(df.axes)
    # print(df['Volume'])

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(14, 7), gridspec_kw={'height_ratios': [2,1]})

    # which days are going up and which days are going down
    up = df[df.Close >= df.Open]
    down = df[df.Close < df.Open]
    # same thing for volume
    up_volume = df[df.Close >= df.Open]
    down_volume = df[df.Close < df.Open]

    # moving average
    df['SMA20'] = df.Close.rolling(window=20).mean()
    df['SMA50'] = df.Close.rolling(window=50).mean()

    # display all the ups and downs
    # using position to display first
    plt.bar
    ax1.bar(up.pos, up.Close-up.Open, width=width1, bottom=up.Open, color=green)
    ax1.bar(up.pos, up.High-up.Close, width=width2, bottom=up.Close, color=green)
    ax1.bar(up.pos, up.Low-up.Open, width=width2, bottom=up.Open, color=green)
    ax1.bar(down.pos, down.Close-down.Open, width=width1, bottom=down.Open, color=red)
    ax1.bar(down.pos, down.High-down.Open, width=width2, bottom=down.Open, color=red)
    ax1.bar(down.pos, down.Low-down.Close, width=width2, bottom=down.Close, color=red)
    ax1.plot(df.pos, df['SMA20'], color='blue', label='SMA 20', linewidth=.6)
    ax1.plot(df.pos, df['SMA50'], color='green', label='SMA 50', linewidth=.6)

    ax2.bar(up_volume.pos, up_volume['Volume'], width1, color=green)
    ax2.bar(down_volume.pos, down_volume['Volume'], width1, color=red)

    # find the step for slicing
    step = max(len(df) // 7, 1)

    # include first and last
    tick_pos = list(df['pos'][::step])
    tick_label = list(df.index.date[::step]) # type: ignore

    # if first isn't in there 
    if df['pos'].iloc[0] not in tick_pos: 
        tick_pos.insert(0, df['pos'].iloc[0])
        tick_label.insert(0, df.index.date[0]) # type: ignore

    # if last isn't in there
    if df['pos'].iloc[-1] not in tick_pos: 
        # check if second to last is really close to last
        max_step = step * .5
        if df['pos'].iloc[-1] - tick_pos[-1] <= max_step: # too close so just make second to last the last one
            tick_pos[-1] = df['pos'].iloc[-1] # make the last one we're displaying the last position
            tick_label[-1] = df.index.date[-1] # make the last one we're displaying the last date # type: ignore
        else: # second to last date is not too close 
            tick_pos.append(df['pos'].iloc[-1])
            tick_label.append(df.index.date[-1]) # type: ignore


    # plot the data and show it 
    ax1.set_title(ticker + " Stock Price for the past month") 
    ax1.set_ylabel("Stock Price")
    ax1.set_xticks(ticks=tick_pos, labels=tick_label, rotation=45, ha='right')
    ax1.legend()
    ax1.margins(x=0.02)

    ax2.set_ylabel("Volume")
    ax2.set_xlabel("Date")
    ax2.set_xticks(ticks=tick_pos, labels=tick_label, rotation=45, ha='right')
    ax2.margins(x=0.02)
    ax2.yaxis.set_major_formatter(mlt.FuncFormatter(format_volume))

    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    plt.show()




if __name__ == "__main__": 
    gui()
