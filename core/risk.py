"""
風險管理模組
處理槓桿投資的維持率、追繳與強制平倉邏輯
"""


class RiskEngine:
    """
    槓桿風險管理引擎
    
    負責：
    1. 維持率計算
    2. 追繳保證金檢查
    3. 強制平倉（斷頭）檢查
    4. 再槓桿機會評估
    """
    
    def __init__(self,
                 maintenance_ratio: float = 130.0,
                 liquidation_ratio: float = 120.0,
                 re_leverage_ratio: float = 180.0,
                 ltv: float = 60.0):
        """
        初始化風險引擎
        
        Args:
            maintenance_ratio: 維持率門檻（%），低於此值觸發追繳
            liquidation_ratio: 斷頭線（%），低於此值強制平倉
            re_leverage_ratio: 再槓桿門檻（%），高於此值可增加貸款
            ltv: 質押成數（Loan-to-Value, %）
        """
        self.maintenance_ratio_threshold = maintenance_ratio / 100.0
        self.liquidation_ratio_threshold = liquidation_ratio / 100.0
        self.re_leverage_threshold = re_leverage_ratio / 100.0
        self.ltv = ltv / 100.0
    
    def calculate_maintenance_ratio(self, stock_value: float, loan_amount: float) -> float:
        """
        計算維持率
        
        維持率 = 股票市值 / 貸款金額
        
        Args:
            stock_value: 當前股票市值（TWD）
            loan_amount: 貸款金額（TWD）
        
        Returns:
            float: 維持率（小數，如 1.3 表示 130%）
                   如果無貸款返回 inf
        """
        if loan_amount <= 0:
            return float('inf')
        
        return stock_value / loan_amount
    
    def check_liquidation(self, maintenance_ratio: float) -> bool:
        """
        檢查是否觸發強制平倉（斷頭）
        
        Args:
            maintenance_ratio: 當前維持率（小數）
        
        Returns:
            bool: True 表示觸發斷頭
        """
        if maintenance_ratio == float('inf'):
            return False
        
        return maintenance_ratio < self.liquidation_ratio_threshold
    
    def check_margin_call(self, maintenance_ratio: float) -> bool:
        """
        檢查是否觸發追繳保證金
        
        Args:
            maintenance_ratio: 當前維持率（小數）
        
        Returns:
            bool: True 表示需要追繳
        """
        if maintenance_ratio == float('inf'):
            return False
        
        # 追繳發生在維持率低於門檻但尚未斷頭
        return (maintenance_ratio < self.maintenance_ratio_threshold and 
                maintenance_ratio >= self.liquidation_ratio_threshold)
    
    def check_re_leverage_opportunity(self, maintenance_ratio: float) -> bool:
        """
        檢查是否可以再槓桿（增加貸款）
        
        Args:
            maintenance_ratio: 當前維持率（小數）
        
        Returns:
            bool: True 表示可以再槓桿
        """
        if maintenance_ratio == float('inf'):
            return False
        
        return maintenance_ratio > self.re_leverage_threshold
    
    def calculate_liquidation_impact(self, 
                                    stock_value: float, 
                                    loan_amount: float, 
                                    shares: float,
                                    share_price: float,
                                    sell_fee_rate: float) -> dict:
        """
        計算強制平倉的影響
        
        Args:
            stock_value: 當前股票市值
            loan_amount: 貸款金額
            shares: 持有股數
            share_price: 當前股價
            sell_fee_rate: 賣出手續費率（小數）
        
        Returns:
            dict: {
                'shares_to_sell': 需要賣出的股數,
                'remaining_shares': 剩餘股數,
                'cash_from_sale': 賣出所得（扣除手續費）,
                'loan_repaid': 償還貸款金額,
                'remaining_loan': 剩餘貸款,
                'total_loss': 總損失金額
            }
        """
        # 計算需要賣出的市值來還清貸款（考慮手續費）
        required_sell_value = loan_amount / (1 - sell_fee_rate)
        shares_to_sell = min(required_sell_value / share_price, shares)
        
        # 實際賣出金額
        gross_sale_value = shares_to_sell * share_price
        net_sale_value = gross_sale_value * (1 - sell_fee_rate)
        
        # 計算剩餘
        remaining_shares = shares - shares_to_sell
        loan_repaid = min(net_sale_value, loan_amount)
        remaining_loan = max(0, loan_amount - loan_repaid)
        
        # 總損失 = 原持股價值 - 剩餘持股價值 - 手續費
        total_loss = gross_sale_value - net_sale_value
        
        return {
            'shares_to_sell': shares_to_sell,
            'remaining_shares': remaining_shares,
            'cash_from_sale': net_sale_value,
            'loan_repaid': loan_repaid,
            'remaining_loan': remaining_loan,
            'total_loss': total_loss,
            'forced_liquidation': True
        }
    
    def calculate_margin_call_requirement(self,
                                         stock_value: float,
                                         loan_amount: float,
                                         available_cash: float,
                                         shares: float,
                                         share_price: float,
                                         sell_fee_rate: float) -> dict:
        """
        計算追繳所需金額及處理方式
        
        Args:
            stock_value: 當前股票市值
            loan_amount: 貸款金額
            available_cash: 可用現金
            shares: 持有股數
            share_price: 當前股價
            sell_fee_rate: 賣出手續費率（小數）
        
        Returns:
            dict: {
                'required_stock_value': 需達到的股票市值,
                'value_to_add': 需要補充的價值,
                'can_cover_with_cash': 是否能用現金補足,
                'cash_used': 使用的現金,
                'shares_to_sell': 需要賣出的股數（如果現金不足）,
                'margin_call_resolved': 追繳是否解決
            }
        """
        # 計算需要達到的股票市值（維持率門檻）
        required_stock_value = loan_amount * self.maintenance_ratio_threshold
        value_to_add = required_stock_value - stock_value
        
        if value_to_add <= 0:
            # 不需要追繳
            return {
                'required_stock_value': required_stock_value,
                'value_to_add': 0,
                'can_cover_with_cash': True,
                'cash_used': 0,
                'shares_to_sell': 0,
                'margin_call_resolved': True
            }
        
        # 檢查現金是否足夠
        can_cover_with_cash = available_cash >= value_to_add
        
        if can_cover_with_cash:
            # 用現金補足
            return {
                'required_stock_value': required_stock_value,
                'value_to_add': value_to_add,
                'can_cover_with_cash': True,
                'cash_used': value_to_add,
                'shares_to_sell': 0,
                'margin_call_resolved': True
            }
        else:
            # 需要賣股
            cash_used = available_cash
            value_from_selling = value_to_add - cash_used
            required_sell_value = value_from_selling / (1 - sell_fee_rate)
            shares_to_sell = required_sell_value / share_price
            
            return {
                'required_stock_value': required_stock_value,
                'value_to_add': value_to_add,
                'can_cover_with_cash': False,
                'cash_used': cash_used,
                'shares_to_sell': shares_to_sell,
                'margin_call_resolved': shares_to_sell <= shares
            }
    
    def calculate_re_leverage_amount(self, stock_value: float, current_loan: float) -> float:
        """
        計算可增加的貸款金額
        
        Args:
            stock_value: 當前股票市值
            current_loan: 當前貸款金額
        
        Returns:
            float: 可增加的貸款金額
        """
        max_loan = stock_value * self.ltv
        additional_loan = max(0, max_loan - current_loan)
        return additional_loan
