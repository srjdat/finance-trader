from datetime import date

import dash_bootstrap_components as dbc
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
                ),  # type: ignore
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
            style={"display": "column", "gap": "15px"},
        ),
        dcc.Graph(id="stock-chart", responsive=True, style={"height": 800}),
    ]
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
    start_date = "2025-05-01"
    end_date = "2026-06-01"

    if not value or not start_date or not end_date:
        return go.Figure()

    df = pd.DataFrame(yf.Ticker(ticker=value).history(start=start_date, end=end_date))
    df["pos"] = np.arange(
        len(df)
    )  # same idea as last time, to not have weekends and holidays

    # label = company name of the ticker we're using
    label = csv_df[csv_df["Ticker"] == value]["Company Name"].iloc[0]  # type: ignore

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.0,
    )

    # moving average
    df["SMA20"] = df.Close.rolling(window=20).mean()
    df["SMA50"] = df.Close.rolling(window=50).mean()

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
    up_volume = df[df["Close"] >= df["Open"]]  # when the day is positive
    down_volume = df[df["Close"] < df["Open"]]  # when the day is negative
    figure.add_trace(
        go.Candlestick(
            open=df["Open"],
            close=df["Close"],
            high=df["High"],
            low=df["Low"],
            x=df.pos,
            name="Stock",
        ),
        row=1,
        col=1,
    )
    figure.add_trace(go.Scatter(x=df.pos, y=df["SMA20"], name="SMA20"), row=1, col=1)
    figure.add_trace(go.Scatter(x=df.pos, y=df["SMA50"], name="SMA50"), row=1, col=1)
    figure.add_trace(  # green volume bars
        go.Bar(
            x=up_volume.pos,
            y=up_volume["Volume"],
            name="Volume",
            marker=dict(color="green"),
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
        ),
        row=2,
        col=1,
    )

    figure.update_layout(
        xaxis_rangeslider_visible=False,
        height=800,
        title=f"{label} Stock Price {start_date} to {end_date}",
        margin=dict(l=10, r=10, pad=2),
    )

    # figure.update_yaxes(showzeroaxis=False, row=1, col=1)

    # for candlestick and sma
    figure.update_xaxes(
        tickvals=tick_pos,
        ticktext=tick_label,
        showgrid=True,
        type="linear",
        showticklabels=False,
        row=1,
        col=1,
    )

    # for the volume chart
    #
    figure.update_xaxes(
        tickvals=tick_pos,
        ticktext=tick_label,
        tickangle=-45,
        showgrid=True,
        type="linear",
        row=2,
        col=1,
    )

    return figure


if __name__ == "__main__":
    app.run(debug=True)
