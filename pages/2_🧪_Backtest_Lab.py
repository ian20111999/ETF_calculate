import streamlit as st
import datetime
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.calculator import MonthlyWealthCalculator
from core.portfolio import Portfolio
from data.fetcher import get_etf_options, get_current_price
from core.engine import HistoricalDataFetcher, BacktestCalculator
from simulation.monte_carlo import MonteCarloSimulator

st.set_page_config(page_title="台股 ETF 回測計算器 V2.0", layout="wide")

st.title("🇹🇼 台股 ETF 累積與槓桿回測計算器 V2.0")
st.caption("多資產組合 | 歷史回測 | 蒙地卡羅模擬 | 💡 全面升級的投資分析工具")

# ============================================================================
# Sidebar - 參數設定
# ============================================================================
st.sidebar.header("⚙️ 參數設定")

# 1. 多資產選擇
st.sidebar.subheader("📈 資產配置")
etf_options = get_etf_options()

# 使用 multiselect 讓用戶選擇多個 ETF
selected_etfs = st.sidebar.multiselect(
    "選擇 ETF 標的（可多選）",
    options=list(etf_options.keys()),
    default=["0050"],
    format_func=lambda x: etf_options[x]["name"],
    help="可選擇多個 ETF 建立投資組合"
)

if not selected_etfs:
    st.sidebar.error("⚠️ 請至少選擇一個 ETF")
    st.stop()

# 為每個選中的 ETF 設定權重
st.sidebar.write("**資產權重分配**")
weights = {}
total_weight = 0

for etf_key in selected_etfs:
    etf_name = etf_options[etf_key]["name"]
    default_weight = 100.0 / len(selected_etfs)  # 平均分配
    weight = st.sidebar.number_input(
        f"{etf_name} 權重 (%)",
        value=default_weight,
        min_value=0.0,
        max_value=100.0,
        step=5.0,
        key=f"weight_{etf_key}"
    )
    weights[etf_key] = weight
    total_weight += weight

# 顯示總權重
if abs(total_weight - 100.0) > 0.01:
    st.sidebar.warning(f"⚠️ 權重總和: {total_weight:.1f}% (應為 100%)")
else:
    st.sidebar.success(f"✅ 權重總和: {total_weight:.1f}%")

# 顯示選中的 ETF 資訊
with st.sidebar.expander("📊 選中的 ETF 詳情"):
    for etf_key in selected_etfs:
        etf_data = etf_options[etf_key]
        st.write(f"**{etf_data['name']}** ({etf_key})")
        st.write(f"- 代碼: {etf_data['yahoo_symbol']}")
        st.write(f"- 預期殖利率: {etf_data['yield']}%")
        st.write(f"- 權重: {weights[etf_key]:.1f}%")
        st.write("---")

# 2. 投資計畫
st.sidebar.subheader("💼 投資計畫")
initial_capital = st.sidebar.number_input("初始資金 (元)", value=1000000, step=10000)
monthly_contribution = st.sidebar.number_input("每月定投 (元)", value=20000, step=1000)

# 3. 回測設定
st.sidebar.subheader("📊 回測設定")
current_year = datetime.datetime.now().year - 1

duration_years = st.sidebar.number_input(
    "回測年數（從現在往回推）", 
    value=10, 
    min_value=1, 
    max_value=20,
    help=f"例如：10 年表示回測 {current_year-9}-{current_year} 的數據"
)

backtest_start_year = current_year - duration_years + 1
backtest_end_year = current_year

st.sidebar.info(f"""
📌 回測時間範圍：
{backtest_start_year} - {backtest_end_year} 年（{duration_years} 年）
""")

# 4. 配息設定
st.sidebar.subheader("💵 配息設定")
dividend_freq_map = {
    "年配（1次/年）": 1,
    "半年配（2次/年）": 2,
    "季配（4次/年）": 4,
    "月配（12次/年）": 12
}
dividend_freq_display = st.sidebar.selectbox(
    "配息頻率",
    options=list(dividend_freq_map.keys()),
    index=2,  # 預設季配
    help="多資產組合將使用相同配息頻率"
)
dividend_frequency = dividend_freq_map[dividend_freq_display]

# 5. 槓桿設定
st.sidebar.subheader("📊 槓桿設定")
use_leverage = st.sidebar.checkbox("使用槓桿（質押融資）", value=False)

if use_leverage:
    ltv = st.sidebar.slider("質押成數 (LTV, %)", min_value=0, max_value=70, value=60, step=5,
                           help="台灣股票質押規定：通常上市股票可質押成數為 60%")
    margin_interest_rate = st.sidebar.number_input("融資利率 (%)", value=6.5, step=0.1, 
                                                   help="台灣券商融資利率約 6%~7%")
    maintenance_ratio = st.sidebar.slider("維持率 (%)", min_value=100, max_value=150, value=130, step=5,
                                         help="低於此值會被券商追繳保證金")
    liquidation_ratio = st.sidebar.slider("斷頭線 (%)", min_value=100, max_value=130, value=120, step=5,
                                         help="低於此值會被強制平倉")
    re_leverage_ratio = st.sidebar.slider("再槓桿門檻 (%)", min_value=150, max_value=200, value=180, step=10,
                                         help="維持率超過此值時，可再進行質押融資")
else:
    ltv = 0
    margin_interest_rate = 0
    maintenance_ratio = 130
    liquidation_ratio = 120
    re_leverage_ratio = 180

# 6. 交易與稅費
st.sidebar.subheader("💸 交易與稅費")
transaction_fee_rate_buy = st.sidebar.number_input("買入手續費 (%)", value=0.1425, step=0.01, format="%.4f")
transaction_fee_rate_sell = st.sidebar.number_input("賣出手續費+證交稅 (%)", value=0.4425, step=0.01, format="%.4f")
dividend_tax_rate = st.sidebar.number_input("股利補充保費 (%)", value=2.11, step=0.01, format="%.2f")

# 7. Monte Carlo 模擬設定
st.sidebar.subheader("🔮 Monte Carlo 模擬")
mc_years = st.sidebar.number_input("模擬年數", value=10, min_value=1, max_value=30,
                                   help="預測未來多少年的投資表現")
mc_num_sims = st.sidebar.number_input("模擬次數", value=1000, min_value=100, max_value=5000, step=100,
                                      help="模擬次數越多，結果越準確，但計算時間也越長")

# ============================================================================
# 主要內容區 - 使用標籤頁
# ============================================================================
tab1, tab2 = st.tabs(["📈 歷史回測", "🔮 未來模擬 (Monte Carlo)"])

# ============================================================================
# Tab 1: 歷史回測
# ============================================================================
with tab1:
    st.header("📈 歷史回測分析")
    
    if st.button("🚀 開始回測", type="primary", key="backtest_btn"):
        with st.spinner('正在獲取歷史數據並進行回測...'):
            
            # 單資產模式（向後兼容）
            if len(selected_etfs) == 1:
                etf_key = selected_etfs[0]
                etf_data = etf_options[etf_key]
                ticker = etf_data['yahoo_symbol']
                expected_yield = etf_data['yield']
                
                # 獲取歷史數據
                fetcher = HistoricalDataFetcher()
                historical_returns = fetcher.fetch_monthly_returns(
                    ticker=ticker,
                    start_year=backtest_start_year,
                    end_year=backtest_end_year,
                    use_cache=True
                )
                
                if historical_returns.empty:
                    st.error(f"❌ 無法獲取 {ticker} 的歷史數據")
                    st.stop()
                
                # 設定計算器
                monthly_calc = MonthlyWealthCalculator(
                    use_leverage=use_leverage,
                    ltv=ltv,
                    maintenance_ratio=maintenance_ratio,
                    liquidation_ratio=liquidation_ratio,
                    margin_interest_rate=margin_interest_rate,
                    transaction_fee_rate_buy=transaction_fee_rate_buy,
                    transaction_fee_rate_sell=transaction_fee_rate_sell,
                    dividend_frequency=dividend_frequency,
                    re_leverage_ratio=re_leverage_ratio,
                    dividend_tax_rate=dividend_tax_rate
                )
                
                backtest_calc = BacktestCalculator(
                    monthly_calculator=monthly_calc,
                    historical_returns=historical_returns
                )
                
                df_regular, df_with_leverage = backtest_calc.run_backtest(
                    initial_capital=initial_capital,
                    monthly_contribution=monthly_contribution,
                    dividend_yield=expected_yield,
                    use_leverage_from_ui=use_leverage
                )
                
                # 選擇顯示的數據
                if use_leverage and not df_with_leverage.empty:
                    final_df = df_with_leverage
                    comparison_df = df_regular
                    strategy_name = "槓桿策略"
                    baseline_name = "無槓桿策略"
                else:
                    final_df = df_regular
                    comparison_df = None
                    strategy_name = "無槓桿策略"
                    baseline_name = None
            
            # 多資產模式
            else:
                st.info("🚧 多資產回測功能正在開發中，目前使用簡化版本")
                
                # 創建 Portfolio
                portfolio = Portfolio()
                for etf_key in selected_etfs:
                    # 簡化：初始配置根據權重分配
                    shares = (initial_capital * weights[etf_key] / 100) / 100  # 假設初始價格 100
                    portfolio.add_asset(etf_key, shares=shares, price=100.0)
                
                # 使用第一個 ETF 的數據作為市場代理（簡化）
                main_etf = selected_etfs[0]
                ticker = etf_options[main_etf]['yahoo_symbol']
                expected_yield = np.average([etf_options[etf]['yield'] for etf in selected_etfs], 
                                           weights=[weights[etf] for etf in selected_etfs])
                
                fetcher = HistoricalDataFetcher()
                historical_returns = fetcher.fetch_monthly_returns(
                    ticker=ticker,
                    start_year=backtest_start_year,
                    end_year=backtest_end_year,
                    use_cache=True
                )
                
                if historical_returns.empty:
                    st.error(f"❌ 無法獲取歷史數據")
                    st.stop()
                
                monthly_calc = MonthlyWealthCalculator(
                    use_leverage=use_leverage,
                    ltv=ltv,
                    maintenance_ratio=maintenance_ratio,
                    liquidation_ratio=liquidation_ratio,
                    margin_interest_rate=margin_interest_rate,
                    transaction_fee_rate_buy=transaction_fee_rate_buy,
                    transaction_fee_rate_sell=transaction_fee_rate_sell,
                    dividend_frequency=dividend_frequency,
                    re_leverage_ratio=re_leverage_ratio,
                    dividend_tax_rate=dividend_tax_rate
                )
                
                # 使用 Portfolio 的 BacktestCalculator
                backtest_calc = BacktestCalculator(
                    monthly_calculator=monthly_calc,
                    historical_returns=historical_returns,
                    portfolio=portfolio
                )
                
                df_regular, df_with_leverage = backtest_calc.run_backtest(
                    initial_capital=initial_capital,
                    monthly_contribution=monthly_contribution,
                    dividend_yield=expected_yield,
                    use_leverage_from_ui=use_leverage
                )
                
                if use_leverage and not df_with_leverage.empty:
                    final_df = df_with_leverage
                    comparison_df = df_regular
                    strategy_name = f"槓桿策略 ({len(selected_etfs)} 資產)"
                    baseline_name = f"無槓桿策略 ({len(selected_etfs)} 資產)"
                else:
                    final_df = df_regular
                    comparison_df = None
                    strategy_name = f"多資產組合 ({len(selected_etfs)} 資產)"
                    baseline_name = None
            
            # ========================================
            # 顯示回測結果
            # ========================================
            if final_df.empty:
                st.error("❌ 回測計算失敗")
                st.stop()
            
            # 1. 總覽指標
            st.subheader("📊 回測結果總覽")
            final_row = final_df.iloc[-1]
            final_equity = final_row["Net Equity"]
            total_principal = final_row["Principal"]
            net_profit = final_equity - total_principal
            roi = (net_profit / total_principal) * 100 if total_principal != 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="最終淨資產",
                    value=f"NT$ {final_equity:,.0f}",
                    delta=f"{roi:.1f}%"
                )
            
            with col2:
                st.metric(
                    label="累計投入本金",
                    value=f"NT$ {total_principal:,.0f}"
                )
            
            with col3:
                st.metric(
                    label="淨收益",
                    value=f"NT$ {net_profit:,.0f}"
                )
            
            with col4:
                if comparison_df is not None:
                    baseline_equity = comparison_df.iloc[-1]["Net Equity"]
                    outperformance = ((final_equity / baseline_equity) - 1) * 100
                    st.metric(
                        label="相對無槓桿超額報酬",
                        value=f"{outperformance:.1f}%"
                    )
                else:
                    st.metric(
                        label="總報酬率",
                        value=f"{roi:.1f}%"
                    )
            
            # 2. 累積財富折線圖
            st.subheader("📈 累積財富趨勢")
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=final_df['Year'],
                y=final_df['Net Equity'],
                mode='lines',
                name=strategy_name,
                line=dict(color='rgb(0, 123, 255)', width=3),
                hovertemplate='%{y:,.0f} 元<extra></extra>'
            ))
            
            if comparison_df is not None:
                fig.add_trace(go.Scatter(
                    x=comparison_df['Year'],
                    y=comparison_df['Net Equity'],
                    mode='lines',
                    name=baseline_name,
                    line=dict(color='rgb(108, 117, 125)', width=2, dash='dash'),
                    hovertemplate='%{y:,.0f} 元<extra></extra>'
                ))
            
            fig.add_trace(go.Scatter(
                x=final_df['Year'],
                y=final_df['Principal'],
                mode='lines',
                name='累計本金',
                line=dict(color='rgb(255, 193, 7)', width=2, dash='dot'),
                hovertemplate='%{y:,.0f} 元<extra></extra>'
            ))
            
            fig.update_layout(
                title=f'淨資產累積圖 ({backtest_start_year}-{backtest_end_year})',
                xaxis_title='時間（年）',
                yaxis_title='金額 (NT$)',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. 年度報酬率
            if 'Annual Return' in final_df.columns:
                st.subheader("📊 歷年報酬率")
                annual_data = final_df[final_df['Month'] == 12].copy()
                
                if 'Calendar_Year' in annual_data.columns:
                    fig_bar = go.Figure()
                    colors = ['green' if x >= 0 else 'red' for x in annual_data['Annual Return']]
                    
                    fig_bar.add_trace(go.Bar(
                        x=annual_data['Calendar_Year'],
                        y=annual_data['Annual Return'],
                        marker_color=colors,
                        hovertemplate='%{y:.2f}%<extra></extra>'
                    ))
                    
                    fig_bar.update_layout(
                        title='歷年報酬率',
                        xaxis_title='年份',
                        yaxis_title='報酬率 (%)',
                        hovermode='x',
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            # 4. 槓桿警告
            if use_leverage and 'Loan Amount' in final_df.columns:
                has_margin_call = (final_df['Maintenance Ratio'] < maintenance_ratio).any()
                has_liquidation = (final_df['Maintenance Ratio'] < liquidation_ratio).any()
                
                if has_liquidation:
                    st.error("⚠️ **警告：回測期間發生斷頭事件！**")
                elif has_margin_call:
                    st.warning("⚠️ **注意：回測期間曾發生追繳！**")
                else:
                    st.success("✅ 回測期間維持率正常")
            
            st.success("✅ 回測計算完成！")
    
    else:
        st.info("👈 請在左側設定參數後，點擊「開始回測」按鈕")

# ============================================================================
# Tab 2: Monte Carlo 模擬
# ============================================================================
with tab2:
    st.header("🔮 未來模擬 (Monte Carlo)")
    st.write("使用蒙地卡羅模擬預測未來投資表現，評估風險與報酬")
    
    # 參數輸入
    col1, col2 = st.columns(2)
    
    with col1:
        mc_mu = st.number_input(
            "預期年化報酬率 (%)",
            value=8.0,
            min_value=-20.0,
            max_value=30.0,
            step=0.5,
            help="歷史平均報酬率，例如：0050 長期約 8-10%"
        ) / 100
    
    with col2:
        mc_sigma = st.number_input(
            "年化波動度 (%)",
            value=15.0,
            min_value=5.0,
            max_value=50.0,
            step=1.0,
            help="歷史波動度，例如：0050 約 15-20%"
        ) / 100
    
    # Monte Carlo 計算按鈕
    if st.button("🎲 執行 Monte Carlo 模擬", type="primary", key="mc_btn"):
        with st.spinner(f'正在執行 {mc_num_sims} 次模擬，請稍候...'):
            
            # 計算加權平均的殖利率（用於完整模擬）
            avg_dividend_yield = np.average(
                [etf_options[etf]['yield'] for etf in selected_etfs],
                weights=[weights[etf] for etf in selected_etfs]
            ) / 100
            
            # 創建 MonteCarloSimulator
            simulator = MonteCarloSimulator(
                mu=mc_mu,
                sigma=mc_sigma,
                initial_capital=initial_capital,
                years=mc_years,
                num_simulations=mc_num_sims,
                monthly_contribution=monthly_contribution,
                random_seed=42
            )
            
            # 選擇模擬模式
            simulation_mode = st.radio(
                "選擇模擬模式",
                options=["快速模擬（簡化版）", "完整模擬（含槓桿與稅務）"],
                index=0,
                help="快速模擬速度快，完整模擬更準確但較慢"
            )
            
            if simulation_mode == "快速模擬（簡化版）":
                # 簡化模擬
                results = simulator.simulate_simple()
                wealth_col = 'Final_Wealth'
            else:
                # 完整模擬
                monthly_calc = MonthlyWealthCalculator(
                    use_leverage=use_leverage,
                    ltv=ltv,
                    maintenance_ratio=maintenance_ratio,
                    liquidation_ratio=liquidation_ratio,
                    margin_interest_rate=margin_interest_rate,
                    transaction_fee_rate_buy=transaction_fee_rate_buy,
                    transaction_fee_rate_sell=transaction_fee_rate_sell,
                    dividend_frequency=dividend_frequency,
                    re_leverage_ratio=re_leverage_ratio,
                    dividend_tax_rate=dividend_tax_rate
                )
                
                # 進度顯示
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                def progress_callback(current, total):
                    progress_bar.progress(current / total)
                    progress_text.text(f"進度: {current}/{total} ({current/total*100:.1f}%)")
                
                results = simulator.simulate_with_calculator(
                    calculator=monthly_calc,
                    dividend_yield=avg_dividend_yield,
                    progress_callback=progress_callback
                )
                
                progress_bar.empty()
                progress_text.empty()
                wealth_col = 'Final_Net_Equity'
            
            # ========================================
            # 顯示 Monte Carlo 結果
            # ========================================
            
            # 1. 總覽指標
            st.subheader("📊 Monte Carlo 模擬結果總覽")
            
            stats = simulator.analyze_results(results, wealth_col)
            percentiles = stats['percentiles']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="中位數（50%）",
                    value=f"NT$ {percentiles['P50']:,.0f}"
                )
            
            with col2:
                st.metric(
                    label="最佳情況（95%）",
                    value=f"NT$ {percentiles['P95']:,.0f}"
                )
            
            with col3:
                st.metric(
                    label="最差情況（5%）",
                    value=f"NT$ {percentiles['P5']:,.0f}"
                )
            
            with col4:
                if 'liquidation_rate' in stats:
                    st.metric(
                        label="斷頭機率",
                        value=f"{stats['liquidation_rate']:.2f}%"
                    )
                else:
                    st.metric(
                        label="95% 信賴最小值",
                        value=f"NT$ {percentiles['P5']:,.0f}"
                    )
            
            # 2. 摘要表格
            st.subheader("📈 關鍵百分位數分析")
            summary_table = simulator.get_summary_table(results, wealth_col)
            st.dataframe(summary_table, use_container_width=True, hide_index=True)
            
            # 3. 財富分布直方圖
            st.subheader("📊 最終財富分布")
            
            fig_hist = go.Figure()
            
            wealth = results[wealth_col]
            
            # 繪製直方圖
            fig_hist.add_trace(go.Histogram(
                x=wealth,
                nbinsx=50,
                name='頻率',
                marker_color='lightblue',
                opacity=0.7
            ))
            
            # 標記百分位數
            fig_hist.add_vline(
                x=percentiles['P5'],
                line_dash="dash",
                line_color="red",
                annotation_text=f"5%: ${percentiles['P5']:,.0f}",
                annotation_position="top"
            )
            
            fig_hist.add_vline(
                x=percentiles['P50'],
                line_dash="dash",
                line_color="green",
                annotation_text=f"中位數: ${percentiles['P50']:,.0f}",
                annotation_position="top"
            )
            
            fig_hist.add_vline(
                x=percentiles['P95'],
                line_dash="dash",
                line_color="blue",
                annotation_text=f"95%: ${percentiles['P95']:,.0f}",
                annotation_position="top"
            )
            
            fig_hist.update_layout(
                title=f'最終財富分布 ({mc_num_sims} 次模擬)',
                xaxis_title='最終財富 (NT$)',
                yaxis_title='頻率',
                showlegend=False
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # 4. 信賴區間圖（模擬路徑樣本）
            st.subheader("🎯 信賴區間預測")
            
            # 重新生成部分路徑用於可視化（最多 100 條）
            sample_simulator = MonteCarloSimulator(
                mu=mc_mu,
                sigma=mc_sigma,
                initial_capital=initial_capital,
                years=mc_years,
                num_simulations=min(100, mc_num_sims),
                monthly_contribution=monthly_contribution,
                random_seed=42
            )
            
            sample_results = sample_simulator.simulate_simple()
            returns = sample_simulator.generate_return_paths()
            
            # 計算每條路徑的財富演進
            wealth_paths = np.zeros((min(100, mc_num_sims), mc_years * 12 + 1))
            wealth_paths[:, 0] = initial_capital
            
            for sim in range(min(100, mc_num_sims)):
                wealth = initial_capital
                for month in range(mc_years * 12):
                    wealth *= (1 + returns[sim, month])
                    wealth += monthly_contribution
                    wealth_paths[sim, month + 1] = wealth
            
            # 計算百分位數曲線
            months = np.arange(mc_years * 12 + 1)
            p5 = np.percentile(wealth_paths, 5, axis=0)
            p50 = np.percentile(wealth_paths, 50, axis=0)
            p95 = np.percentile(wealth_paths, 95, axis=0)
            
            fig_paths = go.Figure()
            
            # 繪製信賴區間（陰影區域）
            fig_paths.add_trace(go.Scatter(
                x=months / 12,
                y=p95,
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig_paths.add_trace(go.Scatter(
                x=months / 12,
                y=p5,
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(0, 123, 255, 0.2)',
                fill='tonexty',
                name='5%-95% 信賴區間',
                hoverinfo='skip'
            ))
            
            # 繪製中位數線
            fig_paths.add_trace(go.Scatter(
                x=months / 12,
                y=p50,
                mode='lines',
                name='中位數 (50%)',
                line=dict(color='rgb(0, 123, 255)', width=3)
            ))
            
            # 繪製本金累積線
            principal_line = initial_capital + monthly_contribution * months
            fig_paths.add_trace(go.Scatter(
                x=months / 12,
                y=principal_line,
                mode='lines',
                name='累計本金',
                line=dict(color='rgb(255, 193, 7)', width=2, dash='dot')
            ))
            
            fig_paths.update_layout(
                title=f'財富演進預測（{mc_years} 年）',
                xaxis_title='年數',
                yaxis_title='財富 (NT$)',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig_paths, use_container_width=True)
            
            # 5. 風險評估
            st.subheader("⚠️ 風險評估")
            
            total_contribution = initial_capital + monthly_contribution * mc_years * 12
            loss_probability = (results[wealth_col] < total_contribution).mean() * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="虧損機率",
                    value=f"{loss_probability:.2f}%",
                    help="最終資產低於累計投入本金的機率"
                )
            
            with col2:
                if 'ROI' in results.columns:
                    roi_mean = results['ROI'].mean()
                    st.metric(
                        label="平均報酬率",
                        value=f"{roi_mean:.2f}%"
                    )
            
            if loss_probability > 10:
                st.warning(f"⚠️ 注意：虧損機率較高 ({loss_probability:.1f}%)，請考慮調整投資策略")
            elif loss_probability > 5:
                st.info(f"💡 虧損機率適中 ({loss_probability:.1f}%)，建議謹慎評估風險承受能力")
            else:
                st.success(f"✅ 虧損機率較低 ({loss_probability:.1f}%)，投資策略相對穩健")
            
            st.success(f"✅ Monte Carlo 模擬完成！（執行了 {mc_num_sims} 次模擬）")
    
    else:
        st.info("👈 請在左側設定參數後，點擊「執行 Monte Carlo 模擬」按鈕")
        
        st.markdown("""
        ### 📖 Monte Carlo 模擬說明
        
        #### 🎯 什麼是 Monte Carlo 模擬？
        蒙地卡羅模擬是一種統計方法，透過大量隨機模擬來預測未來可能的投資結果。
        
        #### 💡 如何使用？
        1. **設定預期報酬率**：根據歷史數據或合理預期（例如：0050 約 8-10%）
        2. **設定波動度**：反映市場風險（例如：0050 約 15-20%）
        3. **選擇模擬次數**：越多越準確（建議 1000 次以上）
        4. **選擇模擬模式**：
           - 快速模擬：速度快，適合初步評估
           - 完整模擬：包含槓桿、稅務等，更準確但較慢
        
        #### 📊 如何解讀結果？
        - **中位數（50%）**：一半的模擬結果高於此值，一半低於此值
        - **最佳情況（95%）**：只有 5% 的模擬結果優於此值
        - **最差情況（5%）**：只有 5% 的模擬結果劣於此值
        - **信賴區間**：陰影區域代表 90% 的可能結果範圍
        
        #### ⚠️ 注意事項
        - 模擬基於歷史數據，不保證未來表現
        - 黑天鵝事件（如金融危機）可能不在模擬範圍內
        - 建議結合歷史回測一起評估
        """)

# ============================================================================
# Footer
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.caption("ETF 回測計算器 V2.0 | Powered by Streamlit")
st.sidebar.caption("⚠️ 本工具僅供參考，不構成投資建議")
