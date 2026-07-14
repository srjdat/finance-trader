# Finance Trader
### Features: 
- Candlestick for prices
- SMA 20/50, EMA 12/26
- Bollinger Bands based on SMA 20
- 52 Week High/Low
- Colored coded Volume Bars 
- Volume SMA 20
- Volatility, 
- Average True Range, 
- RSI with overbought and oversold lines
- MACD, Signal Line, and MACD Histogram
- Return over multiple periods
- Overall score and signal to buy, sell, or hold


### Output:     
- Right now, I plan on the program telling the user whether to buy, sell, or hold based on all the features I've added. This is a hobby project not a financial advisor, please take its output with a grain of salt and do your own research before investing into stocks!!


### How to Run: 
1. Make a virtual environment using `python -m venv venv`
2. Start it with `source venv/bin/activate` (MacOS and Linux) or `venv\Scripts\activate.bat` (Windows)
3. Run main using `python main.py`
4. Open `http://127.0.0.1:8050/` in your browser to see the graphs
5. In your terminal it will show the one day/week/month, three/six month, and one year returns alongside the overall score and its opinion on whether to buy, sell, or hold. 

The score and opinion should not be taken with full trust as the score is given on a rudimentary equation that I developed and the threshold is something I tested and found optimal. If you want to change the equation weightings or threshold you can do so in `output.py` 