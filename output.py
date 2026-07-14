import pandas as pd

def generate_signal(df: pd.DataFrame): 

    # macd and signal line
    # if macd is above signal line
    higher_macd: int = 1 if df['MACD'].iloc[-1] >= df['Signal Line'].iloc[-1] else -1 # not sure what to do with this right now

    # how close are they
    typical_distance = df['macd hist'].abs().rolling(window=20).mean()
    today_distance = abs(round(df['MACD'].iloc[-1] - df['Signal Line'].iloc[-1], 2))
    how_close = today_distance / typical_distance.iloc[-1]
    # flip risk is gonna be a modifier
    flip_risk = min(1, how_close)
    
    # trend
    macd_sma_5 = df['MACD'].rolling(window=5).mean()
    upward_macd_trend: int = 1 if macd_sma_5.iloc[-1] >= macd_sma_5.iloc[-5] else -1
    # crossover
    crossover: int = 0
    if (df['MACD'].iloc[-2] < df['Signal Line'].iloc[-2] and df['MACD'].iloc[-1] > df['Signal Line'].iloc[-1]):
        crossover = 1
    elif  (df['MACD'].iloc[-2] > df['Signal Line'].iloc[-2] and df['MACD'].iloc[-1] < df['Signal Line'].iloc[-1]):
        crossover = -1

    # final macd weighted value
    macd_weighted_value = (crossover * .4) + (higher_macd * .3 * flip_risk) + (upward_macd_trend * .3 * flip_risk)


    # sma 20 and sma 50
    higher_sma20: int = 1 if df['SMA20'].iloc[-1] >= df['SMA50'].iloc[-1] else -1

    # how close they are
    df['SMA20-50'] = df['SMA20'] - df['SMA50'] 
    typical_distance = df['SMA20-50'].abs().rolling(window=20).mean()
    today_distance = abs(round(df['SMA20-50'].iloc[-1], 2))
    how_close = today_distance / typical_distance.iloc[-1]
    # flip risk is gonna be a modifier
    flip_risk = min(1, how_close)

    # trend 
    df['sma20_5'] = df['SMA20-50'].rolling(window=5).mean()
    upward_sma_trend: int
    if df['sma20_5'].iloc[-1] > df['sma20_5'].iloc[-5]: 
        upward_sma_trend = 1
    elif df['sma20_5'].iloc[-1] < df['sma20_5'].iloc[-5]:
        upward_sma_trend = -1
    else: 
        upward_sma_trend = 0

    # crossover
    crossover: int = 0
    if (df['SMA20'].iloc[-2] < df['SMA50'].iloc[-2] and df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]):
        crossover = 1
    elif  (df['SMA20'].iloc[-2] > df['SMA50'].iloc[-2] and df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]):
        crossover = -1

    # final sma weighted value 
    sma_weighted_value = (crossover * .4) + (higher_sma20 * .3 * flip_risk) + (upward_sma_trend * .3 * flip_risk) 


    # rsi
    # over bought or over sold
    over_sold_bought: float 
    if df['rsi'].iloc[-1] < 30: 
        # if it's super low then the weight should be super high
        weight = 1 - df['rsi'].iloc[-1] / 100
        over_sold_bought = 1 * weight
    elif df['rsi'].iloc[-1] > 70: 
        weight = df['rsi'].iloc[-1] / 100
        over_sold_bought = -1 * weight
    else: 
        over_sold_bought = 0

    # trend 
    # if today is greater than 5 days ago it's going up otherwise most likely going down
    rsi_trend = 1 if df['rsi'].iloc[-1] > df['rsi'].iloc[-5] else -1

    # weighted trend
    # if it's going up and it's between 30 - 50 it should be a stronger confidence 
    rsi_weight = (50 - df['rsi'].iloc[-1]) / 50
    
    # total weighted value
    rsi_weighted_value = round((over_sold_bought * .6) + (rsi_trend * rsi_weight * .4), 1)


    # bollinger bands
    upper = df['Upper Band'].iloc[-1]
    lower = df['Lower Band'].iloc[-1]
    close = df['Close'].iloc[-1]

    # get a proportion based on the range of the bands
    bb_proportion = (close-lower)/(upper-lower)
    weighted_bb_value = round((.5 - bb_proportion) / .5, 1)


    # 52 week high/low
    # momentum wise -> close to high = bullish; close to low -> bearish 
    high = df['52wkHigh'].iloc[-1]
    low = df['52wkLow'].iloc[-1]
    close = df['Close'].iloc[-1]
    week_52_proportion =  (close - low) / (high - low)
    weighted_52_week_value = round((week_52_proportion - .5) / .5, 1)


    # volume, rvol 
    rvol = min(1, df['rvol'].iloc[-1])

    trend_score_group = (macd_weighted_value * .5) + (sma_weighted_value * .5) * rvol
    momentum_group_score = (rsi_weighted_value * 0.5) + (weighted_bb_value * 0.5)
    context_group_score = weighted_52_week_value

    overall_score = (trend_score_group * (1/3)) + (momentum_group_score * (1/3)) + (context_group_score * (1/3))
    print(f"one day return: {round(df['one_day_window'].iloc[-1], 4)}")
    print(f"one week return: {round(df['one_week_window'].iloc[-1], 4)}")
    print(f"one month return: {round(df['one_month_window'].iloc[-1], 4)}")
    print(f"three month return: {round(df['three_month_window'].iloc[-1], 4)}")
    print(f"six month return: {round(df['six_month_window'].iloc[-1], 4)}")
    print(f"one year return: {round(df['one_year_window'].iloc[-1], 4)}")
    print(f"overall score {round(overall_score, 4)}")

    threshold = .25
    if overall_score > threshold: 
        print("buy")
    elif overall_score < -threshold: 
        print("sell")
    else: 
        print("hold")