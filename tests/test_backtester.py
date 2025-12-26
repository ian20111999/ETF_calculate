import pytest
import pandas as pd
from monthly_calculator import MonthlyWealthCalculator
from backtester import BacktestCalculator

@pytest.fixture
def mock_historical_returns():
    """建立一個假的、3個月的歷史回報數據"""
    data = {
        'Year': [2023, 2023, 2023],
        'Month': [1, 2, 3],
        'Monthly_Return': [0.01, -0.02, 0.03]  # 1%, -2%, 3%
    }
    return pd.DataFrame(data)

@pytest.fixture
def calculator_instance():
    """返回一個標準的 MonthlyWealthCalculator 實例"""
    return MonthlyWealthCalculator(
        use_leverage=False, # 初始為 False
        ltv=60.0,
        maintenance_ratio=130.0,
        liquidation_ratio=120.0,
        margin_interest_rate=6.5,
        transaction_fee_rate_buy=0.1425,
        transaction_fee_rate_sell=0.4425,
        dividend_frequency=4,
        re_leverage_ratio=180.0,
        dividend_tax_rate=2.11
    )

def test_run_backtest_no_leverage(calculator_instance, mock_historical_returns):
    """測試在無槓桿情況下的回測流程"""
    backtester = BacktestCalculator(
        monthly_calculator=calculator_instance,
        historical_returns=mock_historical_returns
    )
    
    df_regular, df_with_leverage = backtester.run_backtest(
        initial_capital=100000,
        monthly_contribution=10000,
        dividend_yield=3.0,
        use_leverage_from_ui=False # 明確指定不使用槓桿
    )
    
    # 驗證返回的 DataFrame
    assert isinstance(df_regular, pd.DataFrame)
    assert isinstance(df_with_leverage, pd.DataFrame)
    
    # 驗證無槓桿結果
    assert not df_regular.empty
    assert len(df_regular) == 4  # 1 (Year 0) + 3 (months)
    
    # 驗證槓桿結果應為空
    assert df_with_leverage.empty
    
    # 驗證本金計算
    # 初始 100000, M1 +10000, M2 +10000, M3 +10000 -> 最終 130000
    assert df_regular.iloc[-1]['Principal'] == 130000
    
    # 驗證淨值應有變化
    assert df_regular.iloc[-1]['Net Equity'] != df_regular.iloc[-1]['Principal']

def test_run_backtest_with_leverage(calculator_instance, mock_historical_returns):
    """測試在有槓桿情況下的回測流程"""
    backtester = BacktestCalculator(
        monthly_calculator=calculator_instance,
        historical_returns=mock_historical_returns
    )

    df_regular, df_with_leverage = backtester.run_backtest(
        initial_capital=100000,
        monthly_contribution=10000,
        dividend_yield=3.0,
        use_leverage_from_ui=True # 明確指定使用槓桿
    )

    # 驗證返回的 DataFrame
    assert isinstance(df_regular, pd.DataFrame)
    assert isinstance(df_with_leverage, pd.DataFrame)
    
    # 驗證兩種結果都存在
    assert not df_regular.empty
    assert not df_with_leverage.empty
    
    assert len(df_regular) == 4
    assert len(df_with_leverage) == 4
    
    # 驗證槓桿策略的初始貸款不為零
    assert df_with_leverage.iloc[0]['Loan Amount'] > 0
    # 驗證無槓桿策略的貸款始終為零
    assert df_regular['Loan Amount'].sum() == 0

    # 驗證最終淨值不同
    # 在這個短時間、正報酬的例子中，槓桿淨值應高於無槓桿
    assert df_with_leverage.iloc[-1]['Net Equity'] > df_regular.iloc[-1]['Net Equity']
