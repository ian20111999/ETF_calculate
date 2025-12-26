import pytest
from core.calculator import MonthlyWealthCalculator

# 建立一個可重複使用的計算器實例 fixture
@pytest.fixture
def calculator():
    """返回一個帶有標準槓桿設定的 MonthlyWealthCalculator 實例"""
    return MonthlyWealthCalculator(
        use_leverage=True,
        ltv=60.0,
        maintenance_ratio=130.0,
        liquidation_ratio=120.0,
        margin_interest_rate=6.5,
        transaction_fee_rate_buy=0.1425,
        transaction_fee_rate_sell=0.4425,
        dividend_frequency=4, # 季配
        re_leverage_ratio=180.0,
        dividend_tax_rate=2.11
    )

# 建立一個基礎的初始狀態 fixture
@pytest.fixture
def initial_state():
    """返回一個標準的初始狀態字典"""
    return {
        "Share Price": 100.0,
        "Shares": 100.0,
        "Stock Value": 10000.0,
        "Loan Amount": 0.0,
        "Net Equity": 10000.0,
    }

def test_simple_growth_and_contribution(calculator, initial_state):
    """測試基本的月度增長和定投"""
    calculator.use_leverage = False # 在此測試中關閉槓桿
    
    monthly_data = {
        'monthly_return': 0.01,  # 1% 增長
        'monthly_contribution': 1000,
        'dividend_yield': 0.0,
    }
    
    new_state = calculator.run_monthly_cycle(month=1, prev_state=initial_state, monthly_data=monthly_data)

    # 驗證股價
    assert new_state['Share Price'] == pytest.approx(100.0 * 1.01)
    
    # 驗證定投和手續費
    # 投入 1000元，扣除手續費 1000 * 0.001425 = 1.425
    # 實際投入 998.575
    # 購買股數 998.575 / 101 = 9.88688
    # 總股數 100 + 9.88688 = 109.88688
    assert new_state['Shares'] == pytest.approx(100 + (1000 * (1 - 0.001425)) / 101.0)
    
    # 驗證最終淨值
    # 總股數 * 新股價
    assert new_state['Net Equity'] == pytest.approx(new_state['Shares'] * new_state['Share Price'])
    assert new_state['Loan Amount'] == 0 # 無槓桿

def test_dividend_payment(calculator, initial_state):
    """測試配息和再投資"""
    calculator.use_leverage = False

    monthly_data = {
        'monthly_return': 0.0, # 無市場波動
        'monthly_contribution': 0, # 無定投
        'dividend_yield': 0.05, # 5% 年化殖利率
    }

    # 假設是配息月 (e.g., month 3 for quarterly)
    new_state = calculator.run_monthly_cycle(month=3, prev_state=initial_state, monthly_data=monthly_data)

    # 初始股數 100, 股價 100
    # 年化殖利率 5% -> 季殖利率 1.25%
    # 股息 = 100 (股價) * 0.0125 * 100 (股數) = 125
    assert new_state['Cash Dividend'] == pytest.approx(125)
    assert new_state['Dividend Tax'] == 0 # 未超過 20000

    # 除息後股價
    assert new_state['Share Price'] == pytest.approx(100 / (1 + 0.05/4))

    # 再投資
    # 股息 125元，扣除手續費 125 * 0.001425 = 0.178
    # 實際投入 124.822
    # 新股價 100 / 1.0125 = 98.765
    # 購買股數 124.822 / 98.765 = 1.2638
    # 總股數 100 + 1.2638 = 101.2638
    assert new_state['Shares'] > 100 # 股息再投資後股數應增加

def test_leverage_and_interest(calculator):
    """測試開槓桿和支付利息"""
    # 為了單獨測試利息支付，建立一個不會觸發再槓桿的計算器實例
    calculator.re_leverage_threshold = 3.0 # 設定為 300%，高於初始的 266%
    
    leveraged_state = {
        "Share Price": 100.0,
        "Shares": 160.0, # 10000 自有 + 6000 借貸
        "Stock Value": 16000.0,
        "Loan Amount": 6000.0,
        "Net Equity": 10000.0,
    }
    
    monthly_data = {
        'monthly_return': 0.0, # 無市場波動
        'monthly_contribution': 0, # 無定投
        'dividend_yield': 0.0,
    }
    
    new_state = calculator.run_monthly_cycle(month=1, prev_state=leveraged_state, monthly_data=monthly_data)

    # 月利率 (1 + 0.065)**(1/12) - 1 = 0.00526
    # 利息 = 6000 * 0.00526 = 31.57
    assert new_state['Interest Paid'] == pytest.approx(6000 * ((1 + 0.065)**(1/12) - 1))
    
    # 因為付利息需要賣股
    # 賣出價值 31.57 / (1-0.004425) = 31.71 的股票
    # 賣出股數 31.71 / 100 = 0.3171
    # 剩餘股數 160 - 0.3171 = 159.6829
    assert new_state['Shares'] < 160
    assert new_state['Loan Amount'] == 6000.0 # 貸款金額不變
    assert new_state['Net Equity'] < 10000.0 # 淨值因付利息而減少
