import yfinance as yf
import pandas as pd
from datetime import datetime
from monthly_calculator import MonthlyWealthCalculator

class HistoricalDataFetcher:
    """獲取並處理歷史股價數據"""

    @staticmethod
    def fetch_monthly_returns(ticker: str, start_year: int, end_year: int) -> pd.DataFrame:
        """
        獲取指定時間範圍內的月度報酬率。

        Args:
            ticker (str): Yahoo Finance 的股票代碼 (e.g., "0050.TW")
            start_year (int): 開始年份
            end_year (int): 結束年份

        Returns:
            pd.DataFrame: 包含 'Year', 'Month', 'Monthly_Return' 的 DataFrame，
                          如果無法獲取數據則返回一個空的 DataFrame。
        """
        try:
            start_date = f"{start_year}-01-01"
            end_date = f"{end_year+1}-01-01"  # 抓到隔年一月一日以確保包含年底數據
            
            # 下載月度數據，'Adj Close' 會自動處理股息和分割
            hist = yf.download(ticker, start=start_date, end=end_date, interval="1mo", progress=False)
            
            if hist.empty:
                print(f"警告：無法獲取 {ticker} 在 {start_year}-{end_year} 的月度歷史數據")
                return pd.DataFrame()

            # 計算月度報酬率
            hist['Monthly_Return'] = hist['Adj Close'].pct_change()
            
            # 清理數據
            hist.dropna(subset=['Monthly_Return'], inplace=True)
            hist.reset_index(inplace=True)

            # 格式化輸出
            returns_df = pd.DataFrame({
                'Year': hist['Date'].dt.year,
                'Month': hist['Date'].dt.month,
                'Monthly_Return': hist['Monthly_Return']
            })
            
            return returns_df

        except Exception as e:
            print(f"獲取月度數據時發生錯誤 ({ticker}): {e}")
            return pd.DataFrame()


class BacktestCalculator:
    """使用月度歷史數據進行回測的協調器"""

    def __init__(self, monthly_calculator: MonthlyWealthCalculator, historical_returns: pd.DataFrame):
        self.monthly_calculator = monthly_calculator
        self.historical_returns = historical_returns

    def _run_simulation(self, initial_capital, monthly_contribution, dividend_yield):
        """內部函數，執行一次完整的模擬"""
        
        # 取得回測的年月範圍
        start_year = self.historical_returns['Year'].min()
        end_year = self.historical_returns['Year'].max()
        
        # 獲取初始股價 (使用歷史數據的第一天)
        # 為了簡化，我們假設初始股價為 100，避免引入過多複雜性
        initial_share_price = 100.0

        # 初始化 Year 0 / Month 0
        cash_after_fee = initial_capital * (1 - self.monthly_calculator.fee_buy)
        initial_shares = cash_after_fee / initial_share_price
        
        state = {
            "Year": start_year - 1,
            "Month": 12,
            "Share Price": initial_share_price,
            "Shares": initial_shares,
            "Stock Value": initial_capital,
            "Loan Amount": 0,
            "Net Equity": initial_capital,
            "Principal": initial_capital,
            "Cash Dividend": 0,
            "Dividend Tax": 0,
            "Interest Paid": 0,
            "Maintenance Ratio": float('inf'),
            "Margin Call": False,
            "Liquidation": False,
            "Monthly_Return": 0.0,
            "Annual Return": 0.0,
        }
        
        # 如果初始就使用槓桿
        if self.monthly_calculator.use_leverage:
            loan = state['Stock Value'] * self.monthly_calculator.ltv
            state['Loan Amount'] = loan
            
            # 將借來的錢再投資
            value_to_invest = loan * (1 - self.monthly_calculator.fee_buy)
            shares_bought = value_to_invest / state['Share Price']
            state['Shares'] += shares_bought
            state['Stock Value'] = state['Shares'] * state['Share Price']
            state['Net Equity'] = state['Stock Value'] - state['Loan Amount']
            state['Maintenance Ratio'] = state['Stock Value'] / state['Loan Amount'] * 100
            
        records = [state.copy()]
        
        cumulative_principal = initial_capital
        
        # 按月循環
        for _, row in self.historical_returns.iterrows():
            current_month_data = {
                'monthly_return': row['Monthly_Return'],
                'monthly_contribution': monthly_contribution,
                'dividend_yield': dividend_yield / 100.0,
            }
            
            # 更新累計本金
            cumulative_principal += monthly_contribution
            
            # 執行單月計算
            new_state = self.monthly_calculator.run_monthly_cycle(
                month=row['Month'],
                prev_state=records[-1],
                monthly_data=current_month_data
            )
            
            # 整理並記錄結果
            record = {
                "Year": row['Year'],
                "Month": row['Month'],
                "Principal": cumulative_principal,
                "Monthly_Return": row['Monthly_Return'] * 100,
                **new_state
            }
            records.append(record)
        
        # 轉換為 DataFrame
        results_df = pd.DataFrame(records)

        # 計算年度報酬率
        results_df['Calendar_Year'] = results_df['Year']
        annual_returns = results_df.groupby('Calendar_Year')['Monthly_Return'].apply(
            lambda r: ( (1 + r/100).prod() - 1 ) * 100
        )
        results_df['Annual Return'] = results_df['Calendar_Year'].map(annual_returns)
        
        return results_df.reset_index(drop=True)

    def run_backtest(self, initial_capital, monthly_contribution, dividend_yield, **kwargs):
        """
        執行回測，同時模擬有槓桿和無槓桿兩種情況。
        """
        # 1. 執行無槓桿模擬 (df_regular)
        self.monthly_calculator.use_leverage = False
        df_regular = self._run_simulation(initial_capital, monthly_contribution, dividend_yield)
        
        # 2. 執行有槓桿模擬 (df_with_leverage)
        # 從 app.py 傳入的 use_leverage 參數決定是否真的要跑槓桿版本
        original_use_leverage_setting = kwargs.get('use_leverage_from_ui', False)
        
        if original_use_leverage_setting:
            self.monthly_calculator.use_leverage = True
            df_with_leverage = self._run_simulation(initial_capital, monthly_contribution, dividend_yield)
        else:
            df_with_leverage = pd.DataFrame() # 返回空的 DataFrame
            
        return df_regular, df_with_leverage