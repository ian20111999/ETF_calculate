import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 快取目錄
CACHE_DIR = Path(__file__).parent.parent / "data_cache"

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
    "00919": {
        "name": "00919 (群益台灣精選高息)",
        "yield": 7.0,  # 現金殖利率 %
        "cagr": 1.8,   # 股價成長率（不含息）%
        "stock_dividend": 0.0,  # 股票股利率 %
        "yahoo_symbol": "00919.TW"
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
        ticker = yf.Ticker(symbol)
        # 獲取最近的收盤價
        hist = ticker.history(period="5d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            return round(current_price, 2)
    except Exception as e:
        print(f"無法獲取 {symbol} 的價格: {e}")
    
    return None


def fetch_data(ticker: str, 
               start_date: str = None, 
               end_date: str = None,
               interval: str = "1mo",
               max_cache_age_hours: int = 24) -> pd.DataFrame:
    """
    獲取股票數據，支援快取機制
    
    Args:
        ticker: Yahoo Finance 股票代碼（如 "0050.TW"）
        start_date: 開始日期（格式："YYYY-MM-DD"）
        end_date: 結束日期（格式："YYYY-MM-DD"）
        interval: 數據間隔（"1d", "1mo" 等）
        max_cache_age_hours: 快取有效期（小時）
    
    Returns:
        pd.DataFrame: 包含歷史價格數據
    """
    # 確保快取目錄存在
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # 生成快取文件名（包含參數以避免衝突）
    cache_key = f"{ticker}_{interval}_{start_date}_{end_date}"
    cache_file = CACHE_DIR / f"{cache_key}.parquet"
    
    # 檢查快取是否存在且有效
    if cache_file.exists():
        # 檢查快取時間
        cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - cache_time
        
        if age < timedelta(hours=max_cache_age_hours):
            try:
                # 從快取讀取
                df = pd.read_parquet(cache_file)
                print(f"✓ 從快取載入 {ticker} 數據（{age.seconds // 3600} 小時前）")
                return df
            except Exception as e:
                print(f"警告：讀取快取失敗 ({ticker}): {e}")
                # 快取損壞，刪除並重新下載
                cache_file.unlink()
    
    # 從 Yahoo Finance 下載數據
    try:
        print(f"⬇ 正在下載 {ticker} 數據...")
        hist = yf.download(
            ticker, 
            start=start_date, 
            end=end_date, 
            interval=interval, 
            progress=False
        )
        
        if hist.empty:
            print(f"警告：無法獲取 {ticker} 的數據")
            return pd.DataFrame()
        
        # 儲存到快取
        hist.to_parquet(cache_file)
        print(f"✓ {ticker} 數據已儲存至快取")
        
        return hist
        
    except Exception as e:
        print(f"下載數據時發生錯誤 ({ticker}): {e}")
        return pd.DataFrame()


def clear_cache(ticker: str = None):
    """
    清除快取數據
    
    Args:
        ticker: 指定清除的股票代碼，如果為 None 則清除所有快取
    """
    if not CACHE_DIR.exists():
        print("快取目錄不存在")
        return
    
    if ticker:
        # 清除特定股票的快取
        pattern = f"{ticker}_*.parquet"
        files = list(CACHE_DIR.glob(pattern))
        for file in files:
            file.unlink()
            print(f"已刪除快取：{file.name}")
    else:
        # 清除所有快取
        files = list(CACHE_DIR.glob("*.parquet"))
        for file in files:
            file.unlink()
        print(f"已清除所有快取（{len(files)} 個文件）")


def get_cache_info() -> pd.DataFrame:
    """
    獲取快取信息
    
    Returns:
        pd.DataFrame: 包含快取文件的信息
    """
    if not CACHE_DIR.exists():
        return pd.DataFrame()
    
    cache_files = list(CACHE_DIR.glob("*.parquet"))
    
    if not cache_files:
        return pd.DataFrame()
    
    info_list = []
    for file in cache_files:
        stat = file.stat()
        cache_time = datetime.fromtimestamp(stat.st_mtime)
        age = datetime.now() - cache_time
        
        info_list.append({
            'File': file.name,
            'Size (KB)': stat.st_size / 1024,
            'Modified': cache_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Age (hours)': age.total_seconds() / 3600
        })
    
    return pd.DataFrame(info_list)
