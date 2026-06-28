import csv
from datetime import date
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import yfinance as yf
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# read the csv file with all the names and tickers
df = pd.read_csv('all.csv')

app = Dash()

app.layout = [
    html.H1(children='', style={'textAlign':'center'}),

    html.Div([
        dcc.Dropdown(
            id='dropdown-selection',
            options=[
                {'label': row['Company Name'], 'value': row['Ticker']}
                for _, row in df.iterrows()
            ], 
            style={'width': '200px'}
        ),
        dcc.DatePickerRange(
            id='dates',  
            min_date_allowed=date(2000,1,1), # type: ignore
            max_date_allowed=date(2026,6,27), # type: ignore
            initial_visible_month=date(2026, 6, 27), # type: ignore
            style={'width': '230px'}
        ),
    ], 
    style={'display': 'flex', 'gap': '15px', 'margin': '20px'}
    ),
    dcc.Graph(id='stock-chart')
]

@callback(
    Output('stock-chart', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('dates','start_date'), 
    Input('dates','end_date')
)

def update_graph(value, start_date, end_date):
    # print(value)
    # print(start_date)
    # print(type(end_date))
    if not value or not start_date or not end_date: 
        return go.Figure()

    df = pd.DataFrame(yf.Ticker(ticker=value).history(start=start_date, end=end_date))

    figure = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[.7,.3])

    # moving average
    df['SMA20'] = df.Close.rolling(window=20).mean()
    df['SMA50'] = df.Close.rolling(window=50).mean()

    # plotting candlestick, sma20/50, and volume bars
    figure.add_trace(go.Candlestick(open=df['Open'], close=df['Close'], high=df['High'], low=df['Low'], x=df.index), row=1, col=1)
    figure.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA20'), row=1, col=1)
    figure.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='SMA50'), row=1, col=1)
    figure.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'), row=2, col=1)

    figure.update_layout(
        xaxis_rangeslider_visible=False,
        height=700,
        title=f"{value} Stock Price {start_date} to {end_date}"
    )   

    return figure

if __name__ == '__main__':
    app.run(debug=True)