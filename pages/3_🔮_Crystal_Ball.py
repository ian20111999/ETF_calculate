import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from simulation.monte_carlo import MonteCarloSimulator
from core.calculator import MonthlyWealthCalculator
from data.fetcher import get_etf_options

st.set_page_config(
    page_title="水晶球 - 未來模擬",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 水晶球 - 未來投資模擬")
st.caption("使用蒙地卡羅模擬預測未來投資表現，評估風險與報酬")

# ============================================================================
# Sidebar - Parameters
# ============================================================================
st.sidebar.header("⚙️ 模擬參數設定")

# Portfolio Selection
st.sidebar.subheader("📊 投資組合")
etf_options = get_etf_options()

selected_etfs = st.sidebar.multiselect(
    "選擇 ETF 標的",
    options=list(etf_options.keys()),
    default=["0050"],
    format_func=lambda x: etf_options[x]["name"]
)

if not selected_etfs:
    st.sidebar.error("請至少選擇一個 ETF")
    st.stop()

# Weights
weights = {}
for etf in selected_etfs:
    weight = st.sidebar.number_input(
        f"{etf_options[etf]['name']} 權重 (%)",
        value=100.0 / len(selected_etfs),
        min_value=0.0,
        max_value=100.0,
        step=5.0,
        key=f"weight_{etf}"
    )
    weights[etf] = weight

total_weight = sum(weights.values())
if abs(total_weight - 100.0) > 0.01:
    st.sidebar.warning(f"權重總和: {total_weight:.1f}% (應為 100%)")

# Investment Parameters
st.sidebar.subheader("💼 投資計畫")
initial_capital = st.sidebar.number_input("初始資金 (元)", value=1000000, step=10000)
monthly_contribution = st.sidebar.number_input("每月定投 (元)", value=20000, step=1000)

# Simulation Parameters
st.sidebar.subheader("🎲 模擬設定")
mc_years = st.sidebar.number_input("模擬年數", value=10, min_value=1, max_value=30)
mc_num_sims = st.sidebar.number_input("模擬次數", value=1000, min_value=100, max_value=5000, step=100)

col1, col2 = st.sidebar.columns(2)
with col1:
    mc_mu = st.number_input("預期報酬率 (%)", value=8.0, min_value=-20.0, max_value=30.0, step=0.5) / 100
with col2:
    mc_sigma = st.number_input("波動度 (%)", value=15.0, min_value=5.0, max_value=50.0, step=1.0) / 100

# Leverage
use_leverage = st.sidebar.checkbox("使用槓桿", value=False)
if use_leverage:
    ltv = st.sidebar.slider("質押成數 (%)", 0, 70, 60, 5)
    margin_rate = st.sidebar.number_input("融資利率 (%)", value=6.5, step=0.1)
else:
    ltv = 0
    margin_rate = 0

# ============================================================================
# Main Content
# ============================================================================

# Info Box
st.info("""
💡 **蒙地卡羅模擬說明**：透過大量隨機模擬來預測未來可能的投資結果。
- 模擬次數越多，結果越準確
- 信賴區間顯示 90% 的可能結果範圍
- 結果僅供參考，不保證未來表現
""")

# Run Simulation Button
if st.button("🎲 執行蒙地卡羅模擬", type="primary", use_container_width=True):
    with st.spinner(f"正在執行 {mc_num_sims} 次模擬..."):
        
        # Calculate weighted dividend yield
        avg_yield = np.average(
            [etf_options[etf]['yield'] for etf in selected_etfs],
            weights=[weights[etf] for etf in selected_etfs]
        ) / 100
        
        # Create simulator
        simulator = MonteCarloSimulator(
            mu=mc_mu,
            sigma=mc_sigma,
            initial_capital=initial_capital,
            years=mc_years,
            num_simulations=mc_num_sims,
            monthly_contribution=monthly_contribution,
            random_seed=42
        )
        
        # Run simulation (simple mode for speed)
        results = simulator.simulate_simple()
        wealth_col = 'Final_Wealth'
        
        # Analyze results
        stats = simulator.analyze_results(results, wealth_col)
        percentiles = stats['percentiles']
        
        # ========================================
        # Display Results
        # ========================================
        
        # 1. Key Metrics
        st.subheader("📊 模擬結果總覽")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("中位數（50%）", f"NT$ {percentiles['P50']:,.0f}")
        with col2:
            st.metric("最佳情況（95%）", f"NT$ {percentiles['P95']:,.0f}")
        with col3:
            st.metric("最差情況（5%）", f"NT$ {percentiles['P5']:,.0f}")
        with col4:
            total_contrib = initial_capital + monthly_contribution * mc_years * 12
            loss_prob = (results[wealth_col] < total_contrib).mean() * 100
            st.metric("虧損機率", f"{loss_prob:.2f}%")
        
        # 2. Summary Table
        st.subheader("📈 關鍵百分位數分析")
        summary = simulator.get_summary_table(results, wealth_col)
        st.dataframe(summary, use_container_width=True, hide_index=True)
        
        # 3. Distribution Histogram
        st.subheader("📊 最終財富分布")
        
        fig_hist = go.Figure()
        
        fig_hist.add_trace(go.Histogram(
            x=results[wealth_col],
            nbinsx=50,
            marker_color='lightblue',
            opacity=0.7
        ))
        
        for p, color, name in [(5, 'red', 'P5'), (50, 'green', 'P50'), (95, 'blue', 'P95')]:
            fig_hist.add_vline(
                x=percentiles[f'P{p}'],
                line_dash="dash",
                line_color=color,
                annotation_text=f"{name}: ${percentiles[f'P{p}']:,.0f}"
            )
        
        fig_hist.update_layout(
            title=f"最終財富分布 ({mc_num_sims} 次模擬)",
            xaxis_title="最終財富 (NT$)",
            yaxis_title="頻率",
            showlegend=False
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # 4. Confidence Interval Chart
        st.subheader("🎯 信賴區間預測")
        
        # Generate sample paths for visualization
        sample_sim = MonteCarloSimulator(
            mu=mc_mu, sigma=mc_sigma,
            initial_capital=initial_capital,
            years=mc_years,
            num_simulations=min(100, mc_num_sims),
            monthly_contribution=monthly_contribution,
            random_seed=42
        )
        
        returns = sample_sim.generate_return_paths()
        wealth_paths = np.zeros((min(100, mc_num_sims), mc_years * 12 + 1))
        wealth_paths[:, 0] = initial_capital
        
        for sim in range(min(100, mc_num_sims)):
            wealth = initial_capital
            for month in range(mc_years * 12):
                wealth *= (1 + returns[sim, month])
                wealth += monthly_contribution
                wealth_paths[sim, month + 1] = wealth
        
        months = np.arange(mc_years * 12 + 1)
        p5 = np.percentile(wealth_paths, 5, axis=0)
        p50 = np.percentile(wealth_paths, 50, axis=0)
        p95 = np.percentile(wealth_paths, 95, axis=0)
        
        fig_paths = go.Figure()
        
        # Confidence interval (shaded area)
        fig_paths.add_trace(go.Scatter(
            x=months / 12, y=p95,
            mode='lines', line=dict(width=0),
            showlegend=False, hoverinfo='skip'
        ))
        
        fig_paths.add_trace(go.Scatter(
            x=months / 12, y=p5,
            mode='lines', line=dict(width=0),
            fillcolor='rgba(0, 123, 255, 0.2)',
            fill='tonexty',
            name='5%-95% 信賴區間'
        ))
        
        # Median line
        fig_paths.add_trace(go.Scatter(
            x=months / 12, y=p50,
            mode='lines',
            name='中位數 (50%)',
            line=dict(color='rgb(0, 123, 255)', width=3)
        ))
        
        # Principal line
        principal = initial_capital + monthly_contribution * months
        fig_paths.add_trace(go.Scatter(
            x=months / 12, y=principal,
            mode='lines',
            name='累計本金',
            line=dict(color='rgb(255, 193, 7)', width=2, dash='dot')
        ))
        
        fig_paths.update_layout(
            title=f"財富演進預測（{mc_years} 年）",
            xaxis_title="年數",
            yaxis_title="財富 (NT$)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_paths, use_container_width=True)
        
        # 5. Risk Assessment
        st.subheader("⚠️ 風險評估")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("虧損機率", f"{loss_prob:.2f}%",
                     help="最終資產低於累計投入本金的機率")
        
        with col2:
            roi_mean = results['ROI'].mean()
            st.metric("平均報酬率", f"{roi_mean:.2f}%")
        
        if loss_prob > 10:
            st.warning(f"⚠️ 虧損機率較高 ({loss_prob:.1f}%)，請考慮調整策略")
        elif loss_prob > 5:
            st.info(f"💡 虧損機率適中 ({loss_prob:.1f}%)，建議謹慎評估")
        else:
            st.success(f"✅ 虧損機率較低 ({loss_prob:.1f}%)，策略相對穩健")
        
        st.success(f"✅ 模擬完成！（執行了 {mc_num_sims} 次）")

else:
    st.info("👈 請在左側設定參數後，點擊「執行蒙地卡羅模擬」")
    
    # Educational content
    with st.expander("📚 如何解讀結果？"):
        st.write("""
        - **中位數（50%）**：一半的模擬結果高於此值，一半低於此值
        - **最佳情況（95%）**：只有 5% 的模擬結果優於此值
        - **最差情況（5%）**：只有 5% 的模擬結果劣於此值
        - **信賴區間**：陰影區域代表 90% 的可能結果範圍
        - **虧損機率**：最終資產低於累計本金的機率
        """)
