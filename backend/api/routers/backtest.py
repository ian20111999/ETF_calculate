"""
Backtest API Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from core.calculator import MonthlyWealthCalculator
from core.engine import HistoricalDataFetcher, BacktestCalculator
from data.fetcher import get_etf_options

router = APIRouter()


class LeverageConfig(BaseModel):
    ltv: float = 60.0
    margin_interest_rate: float = 6.5
    maintenance_ratio: float = 130.0
    liquidation_ratio: float = 120.0
    re_leverage_ratio: float = 180.0


class BacktestRequest(BaseModel):
    portfolio: Dict[str, float]  # {"0050": 60, "0056": 40}
    initial_capital: float = 1000000
    monthly_contribution: float = 20000
    start_year: int = 2014
    end_year: int = 2024
    use_leverage: bool = False
    leverage_config: Optional[LeverageConfig] = None
    dividend_frequency: int = 4
    transaction_fee_buy: float = 0.1425
    transaction_fee_sell: float = 0.4425
    dividend_tax_rate: float = 2.11


@router.post("/")
def run_backtest(request: BacktestRequest):
    """執行歷史回測"""
    try:
        etf_options = get_etf_options()
        
        # 驗證 ETF
        for etf in request.portfolio.keys():
            if etf not in etf_options:
                return {"success": False, "error": f"Unknown ETF: {etf}"}
        
        # 計算加權殖利率
        total_weight = sum(request.portfolio.values())
        weighted_yield = sum(
            etf_options[etf]["yield"] * weight / total_weight
            for etf, weight in request.portfolio.items()
        )
        
        # 使用第一個 ETF 的歷史數據（簡化版）
        main_etf = list(request.portfolio.keys())[0]
        ticker = etf_options[main_etf]["yahoo_symbol"]
        
        # 獲取歷史數據
        fetcher = HistoricalDataFetcher()
        historical_returns = fetcher.fetch_monthly_returns(
            ticker=ticker,
            start_year=request.start_year,
            end_year=request.end_year,
            use_cache=True
        )
        
        if historical_returns.empty:
            return {"success": False, "error": "Unable to fetch historical data"}
        
        # 設定槓桿參數
        leverage_config = request.leverage_config or LeverageConfig()
        
        # 建立計算器
        monthly_calc = MonthlyWealthCalculator(
            use_leverage=request.use_leverage,
            ltv=leverage_config.ltv,
            maintenance_ratio=leverage_config.maintenance_ratio,
            liquidation_ratio=leverage_config.liquidation_ratio,
            margin_interest_rate=leverage_config.margin_interest_rate,
            transaction_fee_rate_buy=request.transaction_fee_buy,
            transaction_fee_rate_sell=request.transaction_fee_sell,
            dividend_frequency=request.dividend_frequency,
            re_leverage_ratio=leverage_config.re_leverage_ratio,
            dividend_tax_rate=request.dividend_tax_rate
        )
        
        backtest_calc = BacktestCalculator(
            monthly_calculator=monthly_calc,
            historical_returns=historical_returns
        )
        
        # 執行回測
        df_regular, df_leverage = backtest_calc.run_backtest(
            initial_capital=request.initial_capital,
            monthly_contribution=request.monthly_contribution,
            dividend_yield=weighted_yield,
            use_leverage_from_ui=request.use_leverage
        )
        
        # 處理結果
        def process_df(df):
            if df.empty:
                return None
            
            final_row = df.iloc[-1]
            records = df.to_dict(orient="records")
            
            return {
                "records": records,
                "summary": {
                    "final_equity": float(final_row["Net Equity"]),
                    "total_principal": float(final_row["Principal"]),
                    "net_profit": float(final_row["Net Equity"] - final_row["Principal"]),
                    "roi": float((final_row["Net Equity"] / final_row["Principal"] - 1) * 100)
                }
            }
        
        result = {
            "success": True,
            "data": {
                "regular": process_df(df_regular)
            }
        }
        
        if not df_leverage.empty:
            result["data"]["leverage"] = process_df(df_leverage)
            
            # 計算超額報酬
            if result["data"]["regular"] and result["data"]["leverage"]:
                regular_equity = result["data"]["regular"]["summary"]["final_equity"]
                leverage_equity = result["data"]["leverage"]["summary"]["final_equity"]
                result["data"]["leverage"]["summary"]["outperformance"] = \
                    float((leverage_equity / regular_equity - 1) * 100)
        
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}
