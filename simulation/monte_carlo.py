"""
蒙地卡羅模擬模組
使用幾何布朗運動 (Geometric Brownian Motion) 生成資產價格路徑
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple
from core.calculator import MonthlyWealthCalculator


class MonteCarloSimulator:
    """
    蒙地卡羅模擬器
    
    使用 GBM 生成多條可能的資產價格路徑，並對每條路徑
    應用實際的投資策略（定期定額、槓桿、配息等），
    以評估投資組合在不同情境下的表現。
    """
    
    def __init__(self, 
                 mu: float,
                 sigma: float,
                 initial_capital: float,
                 years: int,
                 num_simulations: int = 1000,
                 monthly_contribution: float = 0,
                 random_seed: Optional[int] = None):
        """
        初始化蒙地卡羅模擬器
        
        Args:
            mu: 預期年化報酬率（小數，如 0.08 表示 8%）
            sigma: 年化波動度（小數，如 0.15 表示 15%）
            initial_capital: 初始資金
            years: 模擬年數
            num_simulations: 模擬次數
            monthly_contribution: 每月定投金額
            random_seed: 隨機種子（用於可重現的結果）
        """
        self.mu = mu
        self.sigma = sigma
        self.initial_capital = initial_capital
        self.years = years
        self.num_simulations = num_simulations
        self.monthly_contribution = monthly_contribution
        self.random_seed = random_seed
        
        # 計算月度參數
        self.months = years * 12
        self.monthly_mu = mu / 12
        self.monthly_sigma = sigma / np.sqrt(12)
        
        # 設定隨機種子
        if random_seed is not None:
            np.random.seed(random_seed)
    
    def generate_price_paths(self) -> np.ndarray:
        """
        使用幾何布朗運動生成價格路徑
        
        GBM 公式：S(t+1) = S(t) * exp((μ - σ²/2)Δt + σ√Δt * Z)
        其中 Z ~ N(0,1)
        
        Returns:
            np.ndarray: shape (num_simulations, months+1) 的價格路徑
                        每行是一條模擬路徑，列是時間步
        """
        # 初始化價格矩陣（假設初始價格為 100）
        initial_price = 100.0
        prices = np.zeros((self.num_simulations, self.months + 1))
        prices[:, 0] = initial_price
        
        # 生成隨機數（所有模擬一次性生成，提升效率）
        random_shocks = np.random.normal(0, 1, (self.num_simulations, self.months))
        
        # 計算漂移項和擴散項
        drift = (self.monthly_mu - 0.5 * self.monthly_sigma ** 2)
        diffusion = self.monthly_sigma * random_shocks
        
        # 生成價格路徑
        for t in range(self.months):
            prices[:, t + 1] = prices[:, t] * np.exp(drift + diffusion[:, t])
        
        return prices
    
    def generate_return_paths(self) -> np.ndarray:
        """
        從價格路徑生成報酬率路徑
        
        Returns:
            np.ndarray: shape (num_simulations, months) 的月度報酬率
        """
        prices = self.generate_price_paths()
        
        # 計算月度報酬率
        returns = np.zeros((self.num_simulations, self.months))
        for t in range(self.months):
            returns[:, t] = (prices[:, t + 1] - prices[:, t]) / prices[:, t]
        
        return returns
    
    def simulate_simple(self) -> pd.DataFrame:
        """
        簡化版模擬（不使用 MonthlyWealthCalculator）
        
        只考慮定期定額投資，不考慮槓桿、配息、稅務等
        適合快速估算和大量模擬
        
        Returns:
            pd.DataFrame: 包含每次模擬的最終資產
        """
        returns = self.generate_return_paths()
        
        # 初始化結果
        final_wealth = np.zeros(self.num_simulations)
        
        for sim in range(self.num_simulations):
            wealth = self.initial_capital
            
            for month in range(self.months):
                # 資產成長
                wealth *= (1 + returns[sim, month])
                
                # 加入定投
                wealth += self.monthly_contribution
            
            final_wealth[sim] = wealth
        
        # 創建結果 DataFrame
        results = pd.DataFrame({
            'Simulation': range(1, self.num_simulations + 1),
            'Final_Wealth': final_wealth,
            'Total_Contribution': self.initial_capital + self.monthly_contribution * self.months,
            'Net_Profit': final_wealth - (self.initial_capital + self.monthly_contribution * self.months)
        })
        
        return results
    
    def simulate_with_calculator(self,
                                 calculator: MonthlyWealthCalculator,
                                 dividend_yield: float,
                                 progress_callback: Optional[callable] = None) -> pd.DataFrame:
        """
        完整版模擬（使用 MonthlyWealthCalculator）
        
        對每條路徑應用完整的投資邏輯，包括：
        - 定期定額
        - 槓桿融資
        - 配息與稅務
        - 維持率管理
        - 追繳與斷頭
        
        Args:
            calculator: 月度財富計算器
            dividend_yield: 年化殖利率（小數）
            progress_callback: 進度回調函數（可選）
        
        Returns:
            pd.DataFrame: 每次模擬的詳細結果
        """
        returns = self.generate_return_paths()
        
        results_list = []
        
        for sim in range(self.num_simulations):
            # 初始化狀態
            initial_share_price = 100.0
            cash_after_fee = self.initial_capital * (1 - calculator.fee_buy)
            initial_shares = cash_after_fee / initial_share_price
            
            state = {
                "Share Price": initial_share_price,
                "Shares": initial_shares,
                "Stock Value": self.initial_capital,
                "Loan Amount": 0,
                "Net Equity": self.initial_capital,
            }
            
            # 如果使用槓桿，初始開槓桿
            if calculator.use_leverage:
                loan = state['Stock Value'] * calculator.ltv
                state['Loan Amount'] = loan
                
                value_to_invest = loan * (1 - calculator.fee_buy)
                shares_bought = value_to_invest / state['Share Price']
                state['Shares'] += shares_bought
                state['Stock Value'] = state['Shares'] * state['Share Price']
                state['Net Equity'] = state['Stock Value'] - state['Loan Amount']
            
            # 追蹤是否曾經斷頭
            ever_liquidated = False
            liquidation_month = None
            
            # 按月模擬
            for month in range(self.months):
                year = month // 12 + 1
                month_in_year = (month % 12) + 1
                
                monthly_data = {
                    'monthly_return': returns[sim, month],
                    'monthly_contribution': self.monthly_contribution,
                    'dividend_yield': dividend_yield,
                    'year': year
                }
                
                # 執行月度計算
                try:
                    new_state = calculator.run_monthly_cycle(
                        month=month_in_year,
                        prev_state=state,
                        monthly_data=monthly_data
                    )
                    state = new_state
                    
                    # 檢查是否斷頭
                    if new_state.get('Liquidation', False) and not ever_liquidated:
                        ever_liquidated = True
                        liquidation_month = month + 1
                        
                except Exception as e:
                    # 如果計算失敗，記錄錯誤並跳過
                    print(f"模擬 {sim + 1} 在第 {month + 1} 月發生錯誤: {e}")
                    break
            
            # 記錄最終結果
            total_contribution = self.initial_capital + self.monthly_contribution * self.months
            
            results_list.append({
                'Simulation': sim + 1,
                'Final_Net_Equity': state['Net Equity'],
                'Final_Stock_Value': state['Stock Value'],
                'Final_Loan_Amount': state['Loan Amount'],
                'Total_Contribution': total_contribution,
                'Net_Profit': state['Net Equity'] - total_contribution,
                'ROI': (state['Net Equity'] / total_contribution - 1) * 100 if total_contribution > 0 else 0,
                'Ever_Liquidated': ever_liquidated,
                'Liquidation_Month': liquidation_month if ever_liquidated else None
            })
            
            # 進度回調
            if progress_callback and (sim + 1) % 100 == 0:
                progress_callback(sim + 1, self.num_simulations)
        
        return pd.DataFrame(results_list)
    
    def analyze_results(self, results: pd.DataFrame, wealth_column: str = 'Final_Wealth') -> Dict:
        """
        分析模擬結果
        
        Args:
            results: 模擬結果 DataFrame
            wealth_column: 財富欄位名稱
        
        Returns:
            dict: 包含統計資訊的字典
        """
        # 如果欄位不存在，嘗試使用 Final_Net_Equity
        if wealth_column not in results.columns:
            if 'Final_Net_Equity' in results.columns:
                wealth_column = 'Final_Net_Equity'
            else:
                raise ValueError(f"找不到欄位 {wealth_column}")
        
        wealth = results[wealth_column]
        
        # 計算百分位數
        percentiles = {
            'P5': np.percentile(wealth, 5),      # 5% 最差情況
            'P25': np.percentile(wealth, 25),    # 25% 分位
            'P50': np.percentile(wealth, 50),    # 中位數
            'P75': np.percentile(wealth, 75),    # 75% 分位
            'P95': np.percentile(wealth, 95),    # 5% 最佳情況
        }
        
        # 基本統計
        stats = {
            'mean': wealth.mean(),
            'std': wealth.std(),
            'min': wealth.min(),
            'max': wealth.max(),
            'percentiles': percentiles
        }
        
        # 如果有 ROI 欄位，也分析 ROI
        if 'ROI' in results.columns:
            roi = results['ROI']
            stats['roi_mean'] = roi.mean()
            stats['roi_std'] = roi.std()
            stats['roi_percentiles'] = {
                'P5': np.percentile(roi, 5),
                'P50': np.percentile(roi, 50),
                'P95': np.percentile(roi, 95),
            }
        
        # 如果有斷頭資訊，計算斷頭機率
        if 'Ever_Liquidated' in results.columns:
            liquidation_rate = results['Ever_Liquidated'].mean() * 100
            stats['liquidation_rate'] = liquidation_rate
        
        return stats
    
    def get_summary_table(self, results: pd.DataFrame, wealth_column: str = 'Final_Wealth') -> pd.DataFrame:
        """
        生成摘要表格
        
        Args:
            results: 模擬結果
            wealth_column: 財富欄位名稱
        
        Returns:
            pd.DataFrame: 包含關鍵百分位數的摘要表
        """
        stats = self.analyze_results(results, wealth_column)
        percentiles = stats['percentiles']
        
        total_contribution = self.initial_capital + self.monthly_contribution * self.months
        
        summary_data = [
            {
                'Scenario': '最差情況 (5%)',
                'Final_Wealth': percentiles['P5'],
                'Total_Return': percentiles['P5'] - total_contribution,
                'ROI': (percentiles['P5'] / total_contribution - 1) * 100
            },
            {
                'Scenario': '25% 分位',
                'Final_Wealth': percentiles['P25'],
                'Total_Return': percentiles['P25'] - total_contribution,
                'ROI': (percentiles['P25'] / total_contribution - 1) * 100
            },
            {
                'Scenario': '中位數 (50%)',
                'Final_Wealth': percentiles['P50'],
                'Total_Return': percentiles['P50'] - total_contribution,
                'ROI': (percentiles['P50'] / total_contribution - 1) * 100
            },
            {
                'Scenario': '75% 分位',
                'Final_Wealth': percentiles['P75'],
                'Total_Return': percentiles['P75'] - total_contribution,
                'ROI': (percentiles['P75'] / total_contribution - 1) * 100
            },
            {
                'Scenario': '最佳情況 (95%)',
                'Final_Wealth': percentiles['P95'],
                'Total_Return': percentiles['P95'] - total_contribution,
                'ROI': (percentiles['P95'] / total_contribution - 1) * 100
            },
        ]
        
        return pd.DataFrame(summary_data)
    
    def plot_distribution(self, results: pd.DataFrame, wealth_column: str = 'Final_Wealth'):
        """
        繪製財富分布圖（需要 matplotlib）
        
        Args:
            results: 模擬結果
            wealth_column: 財富欄位名稱
        """
        try:
            import matplotlib.pyplot as plt
            
            # 處理欄位名稱
            if wealth_column not in results.columns:
                wealth_column = 'Final_Net_Equity'
            
            wealth = results[wealth_column]
            stats = self.analyze_results(results, wealth_column)
            percentiles = stats['percentiles']
            
            # 創建圖表
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 繪製直方圖
            ax.hist(wealth, bins=50, alpha=0.7, edgecolor='black')
            
            # 標記百分位數
            ax.axvline(percentiles['P5'], color='red', linestyle='--', 
                      label=f"5% 最差: ${percentiles['P5']:,.0f}")
            ax.axvline(percentiles['P50'], color='green', linestyle='--', 
                      label=f"中位數: ${percentiles['P50']:,.0f}")
            ax.axvline(percentiles['P95'], color='blue', linestyle='--', 
                      label=f"95% 最佳: ${percentiles['P95']:,.0f}")
            
            ax.set_xlabel('最終財富 ($)')
            ax.set_ylabel('頻率')
            ax.set_title(f'蒙地卡羅模擬結果分布 (n={self.num_simulations})')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return fig
            
        except ImportError:
            print("警告：需要安裝 matplotlib 才能繪圖")
            return None
