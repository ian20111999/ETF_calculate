"""
投資組合管理模組
支援多資產配置與再平衡
"""
import pandas as pd
from typing import Dict, Optional


class Portfolio:
    """
    多資產投資組合管理器
    
    管理多個 ETF/股票的持倉，支援：
    1. 持倉追蹤
    2. 市值計算
    3. 權重再平衡
    4. 資產配置調整
    """
    
    def __init__(self, assets: Optional[Dict[str, Dict]] = None):
        """
        初始化投資組合
        
        Args:
            assets: 資產字典，格式：
                {
                    '0050': {'shares': 1000, 'price': 150.0},
                    '00878': {'shares': 5000, 'price': 20.0}
                }
        """
        self.assets = assets if assets is not None else {}
    
    def add_asset(self, ticker: str, shares: float, price: float):
        """
        添加或更新資產
        
        Args:
            ticker: 股票代碼
            shares: 持有股數
            price: 當前價格
        """
        self.assets[ticker] = {
            'shares': shares,
            'price': price
        }
    
    def update_prices(self, prices: Dict[str, float]):
        """
        批量更新資產價格
        
        Args:
            prices: 價格字典，格式：{'0050': 150.0, '00878': 20.0}
        """
        for ticker, price in prices.items():
            if ticker in self.assets:
                self.assets[ticker]['price'] = price
    
    def get_total_value(self) -> float:
        """
        計算投資組合總市值
        
        Returns:
            float: 總市值
        """
        total = 0.0
        for ticker, data in self.assets.items():
            total += data['shares'] * data['price']
        return total
    
    def get_asset_value(self, ticker: str) -> float:
        """
        計算單一資產市值
        
        Args:
            ticker: 股票代碼
        
        Returns:
            float: 該資產市值
        """
        if ticker not in self.assets:
            return 0.0
        
        data = self.assets[ticker]
        return data['shares'] * data['price']
    
    def get_weights(self) -> Dict[str, float]:
        """
        計算當前各資產權重
        
        Returns:
            dict: 權重字典，格式：{'0050': 0.6, '00878': 0.4}
        """
        total_value = self.get_total_value()
        
        if total_value == 0:
            return {ticker: 0.0 for ticker in self.assets.keys()}
        
        weights = {}
        for ticker in self.assets.keys():
            asset_value = self.get_asset_value(ticker)
            weights[ticker] = asset_value / total_value
        
        return weights
    
    def rebalance(self, 
                  target_weights: Dict[str, float], 
                  transaction_fee_rate: float = 0.001425) -> Dict[str, Dict]:
        """
        再平衡投資組合至目標權重
        
        Args:
            target_weights: 目標權重，格式：{'0050': 0.6, '00878': 0.4}
            transaction_fee_rate: 交易手續費率（小數）
        
        Returns:
            dict: 交易明細，格式：
                {
                    '0050': {
                        'action': 'buy' or 'sell',
                        'shares': 100,
                        'value': 15000,
                        'fee': 21.38
                    }
                }
        """
        # 驗證目標權重總和為 1
        weight_sum = sum(target_weights.values())
        if abs(weight_sum - 1.0) > 0.001:
            raise ValueError(f"目標權重總和必須為 1.0，當前為 {weight_sum}")
        
        # 計算當前總市值
        total_value = self.get_total_value()
        
        if total_value == 0:
            raise ValueError("投資組合總市值為 0，無法再平衡")
        
        # 計算每個資產的目標市值和當前市值
        transactions = {}
        
        for ticker, target_weight in target_weights.items():
            if ticker not in self.assets:
                # 如果組合中沒有這個資產，需要買入
                target_value = total_value * target_weight
                current_value = 0
                # 需要設定一個初始價格（這裡假設從外部已經設定）
                if target_value > 0:
                    raise ValueError(f"資產 {ticker} 不存在於組合中，請先添加該資產")
            else:
                current_value = self.get_asset_value(ticker)
                target_value = total_value * target_weight
            
            value_diff = target_value - current_value
            
            # 如果差異小於 1%，不調整（避免頻繁小額交易）
            if abs(value_diff) < total_value * 0.01:
                continue
            
            price = self.assets[ticker]['price']
            
            if value_diff > 0:
                # 需要買入
                shares_to_buy = value_diff / price
                fee = value_diff * transaction_fee_rate
                
                transactions[ticker] = {
                    'action': 'buy',
                    'shares': shares_to_buy,
                    'value': value_diff,
                    'fee': fee,
                    'net_cost': value_diff + fee
                }
                
                # 更新持股
                self.assets[ticker]['shares'] += shares_to_buy
                
            else:
                # 需要賣出
                shares_to_sell = abs(value_diff) / price
                fee = abs(value_diff) * transaction_fee_rate
                
                transactions[ticker] = {
                    'action': 'sell',
                    'shares': shares_to_sell,
                    'value': abs(value_diff),
                    'fee': fee,
                    'net_proceeds': abs(value_diff) - fee
                }
                
                # 更新持股
                self.assets[ticker]['shares'] -= shares_to_sell
        
        return transactions
    
    def get_summary(self) -> pd.DataFrame:
        """
        獲取投資組合摘要
        
        Returns:
            pd.DataFrame: 包含各資產的持股、價格、市值、權重
        """
        if not self.assets:
            return pd.DataFrame()
        
        summary_data = []
        weights = self.get_weights()
        
        for ticker, data in self.assets.items():
            summary_data.append({
                'Ticker': ticker,
                'Shares': data['shares'],
                'Price': data['price'],
                'Value': data['shares'] * data['price'],
                'Weight': weights[ticker]
            })
        
        df = pd.DataFrame(summary_data)
        
        # 添加總計行
        total_row = pd.DataFrame([{
            'Ticker': 'TOTAL',
            'Shares': df['Shares'].sum(),
            'Price': '-',
            'Value': df['Value'].sum(),
            'Weight': df['Weight'].sum()
        }])
        
        df = pd.concat([df, total_row], ignore_index=True)
        
        return df
    
    def to_dict(self) -> Dict:
        """
        將投資組合轉換為字典格式
        
        Returns:
            dict: 投資組合數據
        """
        return {
            'assets': self.assets,
            'total_value': self.get_total_value(),
            'weights': self.get_weights()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Portfolio':
        """
        從字典創建投資組合
        
        Args:
            data: 包含資產數據的字典
        
        Returns:
            Portfolio: 投資組合實例
        """
        return cls(assets=data.get('assets', {}))
