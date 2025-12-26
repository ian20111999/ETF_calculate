"""
Monte Carlo 模擬示範腳本

展示如何使用 MonteCarloSimulator 進行投資組合模擬
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.monte_carlo import MonteCarloSimulator
from core.calculator import MonthlyWealthCalculator
import pandas as pd


def demo_simple_simulation():
    """示範 1: 簡化版模擬（不考慮槓桿和稅務）"""
    print("=" * 80)
    print("示範 1: 簡化版蒙地卡羅模擬")
    print("=" * 80)
    
    # 設定參數
    simulator = MonteCarloSimulator(
        mu=0.08,                    # 年化報酬率 8%
        sigma=0.15,                 # 年化波動度 15%
        initial_capital=100000,     # 初始資金 10 萬
        years=10,                   # 投資 10 年
        num_simulations=1000,       # 模擬 1000 次
        monthly_contribution=10000, # 每月定投 1 萬
        random_seed=42              # 固定隨機種子
    )
    
    # 執行簡化模擬
    print("\n執行模擬中...")
    results = simulator.simulate_simple()
    
    # 分析結果
    print("\n模擬完成！生成摘要表格...")
    summary = simulator.get_summary_table(results)
    print("\n" + "=" * 80)
    print("投資組合模擬結果摘要")
    print("=" * 80)
    print(summary.to_string(index=False))
    
    # 詳細統計
    stats = simulator.analyze_results(results)
    print("\n" + "=" * 80)
    print("詳細統計資訊")
    print("=" * 80)
    print(f"平均最終資產: ${stats['mean']:,.0f}")
    print(f"標準差: ${stats['std']:,.0f}")
    print(f"最小值: ${stats['min']:,.0f}")
    print(f"最大值: ${stats['max']:,.0f}")
    
    return results, simulator


def demo_full_simulation():
    """示範 2: 完整模擬（使用 MonthlyWealthCalculator，包含槓桿和稅務）"""
    print("\n\n" + "=" * 80)
    print("示範 2: 完整蒙地卡羅模擬（含槓桿與稅務）")
    print("=" * 80)
    
    # 設定 MonthlyWealthCalculator（使用正確的參數）
    calculator = MonthlyWealthCalculator(
        use_leverage=True,
        ltv=60.0,                      # 貸款成數 60%（傳入百分比）
        maintenance_ratio=130.0,       # 維持率 130%
        liquidation_ratio=120.0,       # 斷頭線 120%
        margin_interest_rate=6.0,      # 年利率 6%（傳入百分比）
        transaction_fee_rate_buy=0.1425,  # 買入手續費 0.1425%
        transaction_fee_rate_sell=0.4425, # 賣出手續費 0.4425%
        dividend_frequency=4,          # 季配息
        re_leverage_ratio=1.5,         # 目標槓桿倍數
        dividend_tax_rate=2.11,        # 二代健保補充保費率
        dividend_credit_rate=8.5       # 可抵減稅額比率
    )
    
    # 設定蒙地卡羅模擬器（較少模擬次數以加快速度）
    simulator = MonteCarloSimulator(
        mu=0.08,
        sigma=0.15,
        initial_capital=100000,
        years=5,                    # 5 年（較短以加快計算）
        num_simulations=100,        # 100 次模擬
        monthly_contribution=10000,
        random_seed=42
    )
    
    # 進度回調函數
    def progress_callback(current, total):
        print(f"進度: {current}/{total} ({current/total*100:.1f}%)")
    
    # 執行完整模擬
    print("\n執行完整模擬中（這可能需要一些時間）...")
    results = simulator.simulate_with_calculator(
        calculator=calculator,
        dividend_yield=0.04,        # 年化殖利率 4%
        progress_callback=progress_callback
    )
    
    # 分析結果
    print("\n模擬完成！生成摘要表格...")
    summary = simulator.get_summary_table(results, wealth_column='Final_Net_Equity')
    print("\n" + "=" * 80)
    print("完整模擬結果摘要（含槓桿與稅務）")
    print("=" * 80)
    print(summary.to_string(index=False))
    
    # 詳細統計
    stats = simulator.analyze_results(results, wealth_column='Final_Net_Equity')
    print("\n" + "=" * 80)
    print("詳細統計資訊")
    print("=" * 80)
    print(f"平均最終淨值: ${stats['mean']:,.0f}")
    print(f"標準差: ${stats['std']:,.0f}")
    
    if 'roi_mean' in stats:
        print(f"\n平均 ROI: {stats['roi_mean']:.2f}%")
        print(f"ROI 標準差: {stats['roi_std']:.2f}%")
        print(f"ROI 5% 分位: {stats['roi_percentiles']['P5']:.2f}%")
        print(f"ROI 50% 分位: {stats['roi_percentiles']['P50']:.2f}%")
        print(f"ROI 95% 分位: {stats['roi_percentiles']['P95']:.2f}%")
    
    if 'liquidation_rate' in stats:
        print(f"\n斷頭機率: {stats['liquidation_rate']:.2f}%")
    
    return results, simulator


def demo_risk_comparison():
    """示範 3: 比較不同槓桿比例的風險"""
    print("\n\n" + "=" * 80)
    print("示範 3: 槓桿風險比較分析")
    print("=" * 80)
    
    leverage_ratios = [1.0, 1.3, 1.5, 2.0]
    comparison_results = []
    
    for leverage in leverage_ratios:
        print(f"\n分析槓桿倍數: {leverage}x...")
        
        use_leverage = leverage > 1.0
        ltv = (leverage - 1.0) / leverage * 100 if use_leverage else 0  # 轉換為百分比
        
        calculator = MonthlyWealthCalculator(
            use_leverage=use_leverage,
            ltv=ltv,
            maintenance_ratio=130.0,
            liquidation_ratio=120.0,
            margin_interest_rate=6.0,
            transaction_fee_rate_buy=0.1425,
            transaction_fee_rate_sell=0.4425,
            dividend_frequency=4,
            re_leverage_ratio=leverage,
            dividend_tax_rate=2.11,
            dividend_credit_rate=8.5
        )
        
        simulator = MonteCarloSimulator(
            mu=0.08,
            sigma=0.15,
            initial_capital=100000,
            years=5,
            num_simulations=100,
            monthly_contribution=10000,
            random_seed=42
        )
        
        results = simulator.simulate_with_calculator(
            calculator=calculator,
            dividend_yield=0.04
        )
        
        stats = simulator.analyze_results(results, wealth_column='Final_Net_Equity')
        
        comparison_results.append({
            'Leverage': f"{leverage}x",
            'Mean_Wealth': stats['mean'],
            'P5_Worst': stats['percentiles']['P5'],
            'P50_Median': stats['percentiles']['P50'],
            'P95_Best': stats['percentiles']['P95'],
            'Liquidation_Rate': stats.get('liquidation_rate', 0)
        })
    
    # 顯示比較表
    comparison_df = pd.DataFrame(comparison_results)
    print("\n" + "=" * 80)
    print("不同槓桿倍數比較")
    print("=" * 80)
    print(comparison_df.to_string(index=False))
    
    print("\n觀察：")
    print("- 槓桿越高，平均報酬和最佳情況報酬越高")
    print("- 但槓桿越高，最差情況也更差，且斷頭風險增加")
    print("- 建議根據個人風險承受能力選擇適當的槓桿倍數")


if __name__ == "__main__":
    # 執行示範 1: 簡化模擬
    results_simple, sim_simple = demo_simple_simulation()
    
    # 執行示範 2: 完整模擬
    results_full, sim_full = demo_full_simulation()
    
    # 執行示範 3: 風險比較
    demo_risk_comparison()
    
    print("\n\n" + "=" * 80)
    print("所有示範完成！")
    print("=" * 80)
    print("\n提示：")
    print("1. 可以調整 mu (報酬率) 和 sigma (波動度) 來模擬不同市場環境")
    print("2. 增加 num_simulations 可以獲得更準確的統計結果")
    print("3. 使用 plot_distribution() 方法可以繪製結果分布圖（需要安裝 matplotlib）")
