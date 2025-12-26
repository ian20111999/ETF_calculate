
ETF_METADATA = {
    "0050": {
        "name": "0050 (元大台灣50)",
        "yield": 3.2,  # 現金殖利率 %
        "cagr": 6.0,   # 股價成長率（不含息）%
        "stock_dividend": 0.0,  # 股票股利率 %（配股）
        "yahoo_symbol": "0050.TW"  # Yahoo Finance 代碼
    },
    "0056": {
        "name": "0056 (元大高股息)",
        "yield": 6.5,  # 現金殖利率 %
        "cagr": 1.5,   # 股價成長率（不含息）%
        "stock_dividend": 0.0,  # 股票股利率 %
        "yahoo_symbol": "0056.TW"
    },
    "00878": {
        "name": "00878 (國泰永續高股息)",
        "yield": 6.0,  # 現金殖利率 %
        "cagr": 2.0,   # 股價成長率（不含息）%
        "stock_dividend": 0.0,  # 股票股利率 %
        "yahoo_symbol": "00878.TW"
    },
    "2330": {
        "name": "2330 (台積電)",
        "yield": 2.0,  # 現金殖利率 %
        "cagr": 13.0,  # 股價成長率（不含息）%
        "stock_dividend": 0.5,  # 股票股利率 %（台積電偶爾配股）
        "yahoo_symbol": "2330.TW"
    }
}

def get_etf_options():
    return ETF_METADATA

def get_current_price(symbol):
    """獲取標的的當前價格"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        # 獲取最近的收盤價
        hist = ticker.history(period="5d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            return round(current_price, 2)
    except Exception as e:
        print(f"無法獲取 {symbol} 的價格: {e}")
    
    return None
