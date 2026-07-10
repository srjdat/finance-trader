import datetime
from datetime import date

import dash_bootstrap_components as dbc  # type: ignore (vs code bugging out here idk why)
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from dash import Dash, Input, Output, State, callback, dcc, html
from plotly.subplots import make_subplots

# read the csv file with all the names and tickers
csv_df = pd.read_csv("all.csv")

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        html.Div(
            [
                dbc.Button(
                    "Configure",
                    id="open-offcanvas",
                    n_clicks=0,
                    class_name="my-3",
                ),
                dbc.Offcanvas(  # side bar
                    children=[
                        dcc.Dropdown(
                            id="dropdown-selection",
                            options=[
                                {"label": row["Company Name"], "value": row["Ticker"]}
                                for _, row in csv_df.iterrows()
                            ],
                            style={"width": "260px", "padding-bottom": "15px"},
                        ),
                        dcc.DatePickerRange(
                            id="dates",
                            min_date_allowed=date(2000, 1, 1),  # type: ignore
                            max_date_allowed=date(2026, 6, 27),  # type: ignore
                            initial_visible_month=date(2026, 6, 27),  # type: ignore
                            style={"width": "260px"},
                        ),
                    ],
                    id="offcanvas",
                    title="Configure",
                    is_open=False,
                ),
            ],
            style={"display": "column"},
        ),
        dcc.Graph(id="stock-chart", style={"height": "95vh"}),
    ],
    fluid=True,
)


@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
    Output("stock-chart", "figure"),
    Input("dropdown-selection", "value"),
    Input("dates", "start_date"),
    Input("dates", "end_date"),
)
def update_graph(value, start_date, end_date):

    # remove this later currently for testing
    value = "AAPL"
    start_date = "2023-05-01"
    end_date = "2026-07-7"

    if not value or not start_date or not end_date:
        return go.Figure()

    # start from a year back so we can have 52 week high low and other stuff already loaded in
    start_date_original = datetime.date.strptime(start_date, "%Y-%m-%d")
    start_date = start_date_original.replace(year=start_date_original.year-1)

    df = pd.DataFrame(yf.Ticker(ticker=value).history(start=start_date, end=end_date))
    df["pos"] = np.arange(
        len(df)
    )  # same idea as last time, to not have weekends and holidays

    # label = company name of the ticker we're using
    label = csv_df[csv_df["Ticker"] == value]["Company Name"].iloc[0]

    figure = make_subplots(
        rows=5,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.41, 0.12, 0.17, 0.15, 0.15],
        vertical_spacing=0.0,
    )

    # calculations for displaying stuff
    # keep this before cutting this down
    # got this from https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/distance-from-lows 
    # distance from 52-week high/low
    df['52wkHigh'] = df.High.rolling(window=252).max()
    df['52wkLow'] = df.Low.rolling(window=252).max()
    df['Distance From High'] = (df.Close - df['52wkHigh']) / df['52wkHigh'] * 100
    df['Distance From Low'] = (df.Close - df['52wkLow']) / df['52wkLow'] * 100

    # moving average
    df["SMA20"] = df.Close.rolling(window=20).mean()
    df["SMA50"] = df.Close.rolling(window=50).mean()

    # find the volatility
    df["Daily Change"] = df["Close"].pct_change()
    df["Volatility"] = 100 * (df["Daily Change"].rolling(window=20).std())

    # RVOL
    # find sma 10 for volume
    df['Volume SMA 20'] = df['Volume'].rolling(window=20).mean()
    df['rvol'] = df.Volume/df['Volume SMA 20'].shift(1)

    # find rsi
    daily_change = df["Close"].diff()  # today - yesterday

    # change up and down
    change_up, change_down = daily_change.copy(), daily_change.copy()
    change_up[change_up < 0] = 0  # up = close_now - close_prev down = 0
    change_down[change_down > 0] = 0  # up = 0 down = close_prev - close_now

    # average up and down
    average_up = change_up.rolling(14).mean()  # get average for up
    average_down = change_down.rolling(14).mean().abs()  # get average for down
    df['rsi'] = 100 * average_up / (average_up + average_down)
    # these are the most widely used values (got this from charles schwab youtube video: https://youtu.be/hbcCykbX14U?si=eaaSyrdYvQqW3a8Q)
    oversold = np.full(len(df), 30)  # 1d array with 30 as all the values
    overbought = np.full(len(df), 70)  # 1d array with 70 as all the values

    # MACD
    # ema
    df["EMA12"] = df.Close.ewm(span=12).mean()
    df["EMA26"] = df.Close.ewm(span=26).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal Line"] = df["MACD"].ewm(span=9).mean()
    df["macd hist"] = df["MACD"] - df["Signal Line"]

    # make df only from start date to end date
    df = df.iloc[250:len(df)]
    
    # separate volume based on up and down
    up_volume = df[df["Close"] >= df["Open"]]  # when the day is positive
    down_volume = df[df["Close"] < df["Open"]]  # when the day is negative

    # after this is all for displaying so this goes after slimming the df down
    # find the step for slicing
    step = max(len(df) // 7, 1)

    # include first and last
    tick_pos = list(df["pos"][::step])
    tick_label = list(df.index.date[::step])  # type: ignore

    # if first isn't in there
    if df["pos"].iloc[0] not in tick_pos:
        tick_pos.insert(0, df["pos"].iloc[0])
        tick_label.insert(0, df.index.date[0])  # type: ignore

    # if last isn't in there
    if df["pos"].iloc[-1] not in tick_pos:
        # check if second to last is really close to last
        max_step = step * 0.5
        if (
            df["pos"].iloc[-1] - tick_pos[-1] <= max_step
        ):  # too close so just make second to last the last one
            tick_pos[-1] = df["pos"].iloc[
                -1
            ]  # make the last one we're displaying the last position
            tick_label[-1] = df.index.date[  # type: ignore
                -1
            ]  # make the last one we're displaying the last date
        else:  # second to last date is not too close
            tick_pos.append(df["pos"].iloc[-1])
            tick_label.append(df.index.date[-1])  # type: ignore

    # plotting candlestick, sma20/50, and volume bars
    figure.add_trace(  # candle stick
        go.Candlestick(
            open=df["Open"],
            close=df["Close"],
            high=df["High"],
            low=df["Low"],
            x=df.pos,
            name="Stock",
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=(
                "%{text}<br>"
                "open: %{open:.4f}<br>"
                "high: %{high:.4f}<br>"
                "low: %{low:.4f}<br>"
                "close: %{close:.4f}<br>"
                "<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    # SMA 20 & 50
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df["SMA20"],
            name="SMA20",
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>SMA20: %{y:.4f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df["SMA50"],
            name="SMA50",
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>SMA50: %{y:.4f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )

    # ema 12 & 26
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df["EMA12"],
            name="EMA 12",
            marker=dict(color="#D4A24C"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>EMA 12: %{y:.4f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df["EMA26"],
            name="EMA 26",
            marker=dict(color="#8B5A2B"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>EMA 26: %{y:.4f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )

    # distance from 52 week high/low
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df['52wkHigh'],
            name="52 Week High",
            line=dict(color="#FF8C00", dash='dash'),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>52 Week High: %{y:.4f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df['52wkLow'],
            name="52 Week Low",
            line=dict(color="#4B0082", dash="dash"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>52 Week High: %{y:.4f}<br><extra></extra>"),
        ),
        row=1,
        col=1,
    )

    # volatility
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df["Volatility"],
            name="Volatility",
            marker=dict(color="#805B87"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>volatility: %{y:.1f}%<br><extra></extra>"),
        ),
        row=3,
        col=1,
    )

    # volume bars
    figure.add_trace(  # green volume bars
        go.Bar(
            x=up_volume.pos,
            y=up_volume["Volume"],
            name="Volume",
            marker=dict(color="green"),
            text=up_volume.index.strftime("%Y-%m-%d"),  # type: ignore
            customdata=up_volume["Volume"].apply(lambda x: f"{x / 1_000_000:.4f}M"),
            hovertemplate=("%{text}<br>volume: %{customdata}<extra></extra>"),
        ),
        row=2,
        col=1,
    )
    figure.add_trace(  # red volume bars
        go.Bar(
            x=down_volume.pos,
            y=down_volume["Volume"],
            name="Volume",
            marker=dict(color="red"),
            text=down_volume.index.strftime("%Y-%m-%d"),  # type: ignore
            customdata=down_volume["Volume"].apply(lambda x: f"{x / 1_000_000:.4f}M"),
            hovertemplate=("%{text}<br>volume: %{customdata}<extra></extra>"),
        ),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df['Volume SMA 20'],
            name='Volume SMA 20',
            marker=dict(color='blue'),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            customdata=df['Volume SMA 20'].apply(lambda x: f"{x / 1_000_000:.4f}M"),
            hovertemplate=("%{text}<br>Volume SMA 20: %{customdata}<extra></extra>"),
        ),
        row=2,
        col=1,
    )

    # rsi
    figure.add_trace(
        go.Scatter(
            x=df.pos,
            y=df['rsi'],
            name="RSI",
            marker=dict(color="cornflowerblue"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            customdata=df['rsi'],
            hovertemplate=("%{text}<br>rsi: %{customdata:.4f}<extra></extra>"),
        ),
        row=4,
        col=1,
    )
    figure.add_trace(  # over bought line
        go.Scatter(
            x=df.pos,
            y=overbought,
            name="Overbought",
            line=dict(color="red", dash="dash"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            customdata=overbought,
            hovertemplate=("%{text}<br>overbought: %{customdata}<extra></extra>"),
        ),
        row=4,
        col=1,
    )
    figure.add_trace(  # over sold line
        go.Scatter(
            x=df.pos,
            y=oversold,
            name="Oversold",
            line=dict(color="green", dash="dash"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            customdata=oversold,
            hovertemplate=("%{text}<br>oversold: %{customdata}<extra></extra>"),
        ),
        row=4,
        col=1,
    )

    # macd
    figure.add_trace(  # macd
        go.Scatter(
            x=df.pos,
            y=df["MACD"],
            name="MACD",
            marker=dict(color="gray"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>MACD: %{y:.4f}<extra></extra>"),
        ),
        row=5,
        col=1,
    )
    figure.add_trace(  # signal line
        go.Scatter(
            x=df.pos,
            y=df["Signal Line"],
            name="Signal Line",
            marker=dict(color="#89CFF0"),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>Signal Line: %{y:.4f}<extra></extra>"),
        ),
        row=5,
        col=1,
    )
    # histogram
    colors = ["green" if val >= 0 else "red" for val in df["macd hist"]]
    figure.add_trace(
        go.Bar(
            x=df.pos,
            y=df["macd hist"],
            name="MACD Histogram",
            marker=dict(color=colors),
            text=df.index.strftime("%Y-%m-%d"),  # type: ignore
            hovertemplate=("%{text}<br>Histogram: %{y:.4f}<extra></extra>"),
        ),
        row=5,
        col=1,
    )

    figure.update_layout(
        xaxis_rangeslider_visible=False,
        plot_bgcolor="white",
        title=f"{label} Stock Price {start_date_original} to {end_date}",
        margin=dict(l=10, r=10, pad=2),
    )

    figure.update_xaxes(
        showgrid=True,
        gridcolor="lightgrey",
        zeroline=True,
        zerolinecolor="lightgrey",
        zerolinewidth=1,
    )
    figure.update_yaxes(
        showgrid=True,
        gridcolor="lightgrey",
        zeroline=True,
        zerolinecolor="lightgrey",
        zerolinewidth=1,
    )

    # instead of having
    for row in range(1, 6):
        figure.update_xaxes(
            tickvals=tick_pos,
            ticktext=tick_label,
            tickangle=-15,
            type="linear",
            row=row,
            col=1,
        )

    return figure


if __name__ == "__main__":
    app.run(debug=True)
