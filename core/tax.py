"""
稅務計算模組
處理台灣股利相關稅務規則
"""


class TaxCalculator:
    """
    台灣股利稅務計算引擎
    
    處理：
    1. 補充保費（單次股利 > 20,000 TWD 時課徵 2.11%）
    2. 股利所得稅抵減（8.5% 可抵稅額，上限 80,000 TWD/年）
    """
    
    def __init__(self, 
                 dividend_tax_rate: float = 2.11,
                 dividend_tax_threshold: float = 20000,
                 dividend_credit_rate: float = 8.5,
                 annual_dividend_credit_cap: float = 80000):
        """
        初始化稅務計算器
        
        Args:
            dividend_tax_rate: 補充保費率（%）
            dividend_tax_threshold: 補充保費門檻（TWD）
            dividend_credit_rate: 股利所得稅抵減率（%）
            annual_dividend_credit_cap: 年度股利抵減上限（TWD）
        """
        self.dividend_tax_rate = dividend_tax_rate / 100.0  # 轉換為小數
        self.dividend_tax_threshold = dividend_tax_threshold
        self.dividend_credit_rate = dividend_credit_rate / 100.0
        self.annual_dividend_credit_cap = annual_dividend_credit_cap
        
        # 追蹤年度累計（用於抵減上限）
        self.annual_dividend_credit_accumulated = 0.0
        self.current_tracking_year = None
    
    def reset_annual_tracking(self, year: int):
        """
        重置年度追蹤（每年初調用）
        
        Args:
            year: 當前年份
        """
        if self.current_tracking_year != year:
            self.current_tracking_year = year
            self.annual_dividend_credit_accumulated = 0.0
    
    def calculate_dividend_tax(self, 
                              cash_dividend: float, 
                              current_year: int = None) -> dict:
        """
        計算股利相關稅費
        
        Args:
            cash_dividend: 本次領取的現金股利（TWD）
            current_year: 當前年份（用於年度抵減上限追蹤）
        
        Returns:
            dict: {
                'supplementary_premium': 補充保費金額（支出）,
                'tax_credit': 股利所得稅抵減金額（正向現金流）,
                'net_tax_impact': 淨稅務影響（credit - premium）,
                'remaining_credit_cap': 本年度剩餘可抵減額度
            }
        """
        # 如果提供年份，檢查是否需要重置
        if current_year is not None:
            self.reset_annual_tracking(current_year)
        
        # 1. 計算補充保費
        supplementary_premium = 0.0
        if cash_dividend > self.dividend_tax_threshold:
            supplementary_premium = cash_dividend * self.dividend_tax_rate
        
        # 2. 計算股利所得稅抵減（8.5%）
        potential_tax_credit = cash_dividend * self.dividend_credit_rate
        
        # 檢查是否超過年度上限
        remaining_cap = self.annual_dividend_credit_cap - self.annual_dividend_credit_accumulated
        actual_tax_credit = min(potential_tax_credit, remaining_cap)
        
        # 更新累計
        self.annual_dividend_credit_accumulated += actual_tax_credit
        
        # 3. 計算淨稅務影響
        net_tax_impact = actual_tax_credit - supplementary_premium
        
        return {
            'supplementary_premium': supplementary_premium,
            'tax_credit': actual_tax_credit,
            'net_tax_impact': net_tax_impact,
            'remaining_credit_cap': self.annual_dividend_credit_cap - self.annual_dividend_credit_accumulated,
            'gross_dividend': cash_dividend,
            'net_dividend_after_tax': cash_dividend - supplementary_premium + actual_tax_credit
        }
    
    def get_annual_summary(self) -> dict:
        """
        獲取年度稅務摘要
        
        Returns:
            dict: 年度稅務統計
        """
        return {
            'tracking_year': self.current_tracking_year,
            'total_tax_credit_used': self.annual_dividend_credit_accumulated,
            'remaining_credit_cap': self.annual_dividend_credit_cap - self.annual_dividend_credit_accumulated,
            'credit_cap_utilized_percent': (self.annual_dividend_credit_accumulated / self.annual_dividend_credit_cap * 100)
                                          if self.annual_dividend_credit_cap > 0 else 0
        }
