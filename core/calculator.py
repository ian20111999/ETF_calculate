import pandas as pd
from .tax import TaxCalculator
from .risk import RiskEngine


class MonthlyWealthCalculator:
    """
    執行一個月財富變化的計算引擎。
    這個類別被設計為一個狀態計算機，由 BacktestCalculator 在每個月呼叫。
    """
    def __init__(self, 
                 use_leverage: bool, 
                 ltv: float, 
                 maintenance_ratio: float, 
                 liquidation_ratio: float, 
                 margin_interest_rate: float, 
                 transaction_fee_rate_buy: float, 
                 transaction_fee_rate_sell: float, 
                 dividend_frequency: int,
                 re_leverage_ratio: float,
                 dividend_tax_rate: float = 2.11,
                 dividend_credit_rate: float = 8.5):
        
        # 將傳入的百分比轉換為小數以便計算
        self.use_leverage = use_leverage
        self.ltv = ltv / 100.0
        self.monthly_interest_rate = (1 + margin_interest_rate / 100.0)**(1/12) - 1
        self.fee_buy = transaction_fee_rate_buy / 100.0
        self.fee_sell = transaction_fee_rate_sell / 100.0
        self.dividend_frequency = dividend_frequency
        
        # 初始化稅務計算器
        self.tax_calculator = TaxCalculator(
            dividend_tax_rate=dividend_tax_rate,
            dividend_tax_threshold=20000,
            dividend_credit_rate=dividend_credit_rate,
            annual_dividend_credit_cap=80000
        )
        
        # 初始化風險引擎
        self.risk_engine = RiskEngine(
            maintenance_ratio=maintenance_ratio,
            liquidation_ratio=liquidation_ratio,
            re_leverage_ratio=re_leverage_ratio,
            ltv=ltv
        )

    def run_monthly_cycle(self, month: int, prev_state: dict, monthly_data: dict) -> dict:
        """
        執行單個月的計算循環。

        Args:
            month (int): 當前月份 (1-based)。
            prev_state (dict): 上個月的狀態。
            monthly_data (dict): 這個月的市場數據和用戶輸入。

        Returns:
            dict: 這個月結束時的新狀態。
        """
        # 初始狀態
        shares = prev_state['Shares']
        loan = prev_state['Loan Amount']
        cash = 0  # 現金流帳戶，用於處理本月所有現金交易
        
        # 1. 股價變動 (月初)
        new_share_price = prev_state['Share Price'] * (1 + monthly_data['monthly_return'])
        stock_value = shares * new_share_price

        # 2. 處理配息
        cash_dividend = 0
        dividend_tax = 0
        tax_credit = 0
        month_in_year = (month - 1) % 12 + 1
        
        is_dividend_month = False
        if self.dividend_frequency > 0 and self.dividend_frequency <= 12:
             is_dividend_month = month_in_year % (12 / self.dividend_frequency) == 0

        if is_dividend_month:
            # 依據年化殖利率計算當次股息
            dividend_per_share = new_share_price * (monthly_data['dividend_yield'] / self.dividend_frequency)
            cash_dividend = shares * dividend_per_share
            
            # 使用 TaxCalculator 計算稅務
            current_year = monthly_data.get('year', None)
            tax_result = self.tax_calculator.calculate_dividend_tax(cash_dividend, current_year)
            
            dividend_tax = tax_result['supplementary_premium']
            tax_credit = tax_result['tax_credit']
            net_dividend = tax_result['net_dividend_after_tax']
            
            # 加入淨股利收入（已扣除補充保費並加上抵減）
            cash += net_dividend
            
            # 除息後股價調整
            new_share_price /= (1 + (monthly_data['dividend_yield'] / self.dividend_frequency))
            stock_value = shares * new_share_price

        # 3. 處理利息 (如果有貸款)
        interest_paid = 0
        if self.use_leverage and loan > 0:
            interest_paid = loan * self.monthly_interest_rate
            cash -= interest_paid

            # 如果現金不足以支付利息，賣出股票
            if cash < 0:
                # 需要從賣股中補足的現金
                shortfall = -cash
                cash = 0
                # 計算需要賣出多少價值的股票 (計入賣出手續費)
                value_to_sell = shortfall / (1 - self.fee_sell)
                shares_to_sell = value_to_sell / new_share_price
                
                if shares_to_sell > shares:
                    # 如果需要賣出的比持有的還多，這是一個極端情況 (破產)
                    # 在此簡化模型中，我們賣掉所有股票
                    liquidated = True
                    shares = 0
                else:
                    shares -= shares_to_sell
                
                stock_value = shares * new_share_price


        # 4. 維持率檢查與追繳
        maintenance_ratio = float('inf')
        margin_call_triggered = False
        liquidated = False
        
        if self.use_leverage and loan > 0:
            # 使用 RiskEngine 計算維持率
            maintenance_ratio = self.risk_engine.calculate_maintenance_ratio(stock_value, loan)
            
            # 檢查是否觸發斷頭
            if self.risk_engine.check_liquidation(maintenance_ratio):
                liquidated = True
                
                # 使用 RiskEngine 計算斷頭影響
                liquidation_result = self.risk_engine.calculate_liquidation_impact(
                    stock_value=stock_value,
                    loan_amount=loan,
                    shares=shares,
                    share_price=new_share_price,
                    sell_fee_rate=self.fee_sell
                )
                
                shares = liquidation_result['remaining_shares']
                loan = liquidation_result['remaining_loan']
                stock_value = shares * new_share_price
                cash = 0  # 假設所有現金都用於還款
                
            # 檢查是否觸發追繳
            elif self.risk_engine.check_margin_call(maintenance_ratio):
                margin_call_triggered = True
                
                # 使用 RiskEngine 計算追繳需求
                margin_call_result = self.risk_engine.calculate_margin_call_requirement(
                    stock_value=stock_value,
                    loan_amount=loan,
                    available_cash=cash,
                    shares=shares,
                    share_price=new_share_price,
                    sell_fee_rate=self.fee_sell
                )
                
                # 執行追繳
                cash -= margin_call_result['cash_used']
                if margin_call_result['shares_to_sell'] > 0:
                    shares -= margin_call_result['shares_to_sell']
                    stock_value = shares * new_share_price

        # 5. 處理再槓桿
        if self.use_leverage and loan > 0 and not liquidated:
            # 使用 RiskEngine 檢查再槓桿機會
            if self.risk_engine.check_re_leverage_opportunity(maintenance_ratio):
                additional_loan = self.risk_engine.calculate_re_leverage_amount(stock_value, loan)
                
                if additional_loan > 0:
                    loan += additional_loan
                    cash += additional_loan  # 借出的錢變成現金

        # 6. 加入本月定投
        cash += monthly_data['monthly_contribution']

        # 7. 將所有現金再投資
        if cash > 0:
            value_to_invest = cash * (1 - self.fee_buy)
            shares_bought = value_to_invest / new_share_price
            shares += shares_bought
            cash = 0 # 剩餘零頭忽略不計

        # 8. 如果未使用槓桿，在期末計算一次可貸金額並投入 (模擬首次開槓桿)
        if self.use_leverage and loan == 0 and shares > 0:
            stock_value = shares * new_share_price
            new_loan = stock_value * self.ltv
            loan += new_loan
            
            # 將借來的錢再投資
            value_to_invest = new_loan * (1 - self.fee_buy)
            shares_bought = value_to_invest / new_share_price
            shares += shares_bought

        # 計算最終資產
        final_stock_value = shares * new_share_price
        net_equity = final_stock_value - loan
        
        # 更新維持率
        final_maintenance_ratio = self.risk_engine.calculate_maintenance_ratio(final_stock_value, loan)

        # 返回本月最終狀態
        return {
            "Share Price": new_share_price,
            "Shares": shares,
            "Stock Value": final_stock_value,
            "Loan Amount": loan,
            "Net Equity": net_equity,
            "Cash Dividend": cash_dividend,
            "Dividend Tax": dividend_tax,
            "Tax Credit": tax_credit,  # 新增：稅務抵減
            "Interest Paid": interest_paid,
            "Maintenance Ratio": final_maintenance_ratio * 100 if final_maintenance_ratio != float('inf') else float('inf'),
            "Margin Call": margin_call_triggered,
            "Liquidation": liquidated,
        }
