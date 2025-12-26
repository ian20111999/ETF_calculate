import streamlit as st
import datetime
import plotly.graph_objects as go
from monthly_calculator import MonthlyWealthCalculator
from data_loader import get_etf_options, get_current_price
from backtester import HistoricalDataFetcher, BacktestCalculator

st.set_page_config(page_title="台股 ETF 回測計算器", layout="wide")

st.title("🇹🇼 台股 ETF 累積與槓桿回測計算器")
st.caption("使用真實歷史數據回測您的投資策略 | 💡 採用月度計算，配息時機更真實")

# Sidebar
st.sidebar.header("⚙️ 參數設定")

# 1. 標的選擇
etf_options = get_etf_options()
selected_etf_key = st.sidebar.selectbox("📈 選擇 ETF 標的", options=list(etf_options.keys()), format_func=lambda x: etf_options[x]["name"])
selected_etf_data = etf_options[selected_etf_key]

# 獲取當前市場價格
yahoo_symbol = selected_etf_data.get("yahoo_symbol", "0050.TW")

# 使用 cache 避免每次調整參數都重新抓取股價 (TTL 設定為 1 小時)
@st.cache_data(ttl=3600)
def get_cached_price(symbol):
    return get_current_price(symbol)

fetched_price = get_cached_price(yahoo_symbol)

if fetched_price is not None:
    default_price = fetched_price
    price_help = "✅ 已自動獲取最新收盤價，您也可以手動調整"
else:
    default_price = 100.0  # 預設值，提示用戶修改
    price_help = "⚠️ 無法獲取即時股價，請手動輸入"
    st.sidebar.warning("無法連接報價伺服器，請手動確認股價")

# 改為 number_input 讓用戶可以修改，或在抓取失敗時手動輸入
current_market_price = st.sidebar.number_input("💹 當前股價 (元)", value=float(default_price), step=0.1, format="%.2f", help=price_help)

# 自動填入參數
expected_yield = st.sidebar.number_input("💰 預期年殖利率 (%)", value=selected_etf_data["yield"], step=0.1)

# 2. 投資計畫與回測設定
st.sidebar.subheader("💼 投資計畫")
initial_capital = st.sidebar.number_input("初始資金 (元)", value=1000000, step=10000)
monthly_contribution = st.sidebar.number_input("每月定投 (元)", value=20000, step=1000)

st.sidebar.subheader("📊 回測設定")
st.sidebar.caption("使用真實歷史股價變動回測")
current_year = datetime.datetime.now().year - 1  # 自動使用去年作為最後完整年份

# 讓用戶選擇回測年數（從現在往回推）
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
📌 回測計算方式：
• 時間範圍：{backtest_start_year} - {backtest_end_year} 年（{duration_years} 年真實數據）
• 每年報酬率：該年實際股價漲跌幅
• 配息殖利率：{expected_yield}%（您設定）
• 質押機制：完整模擬（維持率、追繳、再槓桿）
""")

# 3. 配息頻率
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
    index=1,  # 預設季配
    help="0050為半年配，0056/00878為季配或月配"
)
dividend_frequency = dividend_freq_map[dividend_freq_display]

# 4. 槓桿設定
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

# 5. 交易與稅費
st.sidebar.subheader("💸 交易與稅費")
transaction_fee_rate_buy = st.sidebar.number_input("買入手續費 (%)", value=0.1425, step=0.01, format="%.4f",
                                                   help="券商手續費約 0.1425%")
transaction_fee_rate_sell = st.sidebar.number_input("賣出手續費+證交稅 (%)", value=0.4425, step=0.01, format="%.4f",
                                                    help="手續費 0.1425% + 證交稅 0.3%")
dividend_tax_rate = st.sidebar.number_input("股利補充保費 (%)", value=2.11, step=0.01, format="%.2f",
                                            help="單次領取股利超過 2 萬元需繳納 2.11% 補充保費")

def display_summary_metrics(final_df, comparison_df):
    """
    Displays the main summary metrics of the backtest results.

    Args:
        final_df (pd.DataFrame): The DataFrame containing the final backtest results.
        comparison_df (pd.DataFrame or None): The DataFrame for the baseline strategy for comparison.
    """
    st.header("📊 回測結果總覽")
    
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

def display_annual_returns_table(final_df):
    """
    Displays a table of annual returns based on the backtest data.

    Args:
        final_df (pd.DataFrame): The DataFrame containing the final backtest results.
    """
    if 'Annual Return' in final_df.columns:
        st.subheader("📅 歷年報酬率（真實數據）")
        annual_view = final_df[final_df['Month'] == 12].copy()
        if 'Calendar_Year' in annual_view.columns:
            display_cols = ['Calendar_Year', 'Annual Return', 'Net Equity', 'Principal']
            annual_display = annual_view[display_cols].copy()
            annual_display.columns = ['西元年份', '該年報酬率(%)', '期末淨資產', '累計本金']
            annual_display['該年報酬率(%)'] = annual_display['該年報酬率(%)'].round(2)
            annual_display['期末淨資產'] = annual_display['期末淨資產'].apply(lambda x: f"NT$ {x:,.0f}")
            annual_display['累計本金'] = annual_display['累計本金'].apply(lambda x: f"NT$ {x:,.0f}")
            st.dataframe(annual_display, use_container_width=True, hide_index=True)

def display_charts(final_df, comparison_df, strategy_name, baseline_name, backtest_start_year, backtest_end_year, ticker):
    """
    Displays the wealth trend chart and the annual returns bar chart.

    Args:
        final_df (pd.DataFrame): The DataFrame for the main strategy.
        comparison_df (pd.DataFrame or None): The DataFrame for the baseline strategy.
        strategy_name (str): The name of the main strategy.
        baseline_name (str or None): The name of the baseline strategy.
        backtest_start_year (int): The starting year of the backtest.
        backtest_end_year (int): The ending year of the backtest.
        ticker (str): The ETF ticker symbol.
    """
    # === 累積財富折線圖 ===
    st.subheader("📈 累積財富趨勢")
    
    fig = go.Figure()
    
    # 繪製主策略線
    fig.add_trace(go.Scatter(
        x=final_df['Year'],
        y=final_df['Net Equity'],
        mode='lines',
        name=strategy_name,
        line=dict(color='rgb(0, 123, 255)', width=3),
        hovertemplate='%{y:,.0f} 元<extra></extra>'
    ))
    
    # 如果有對比數據
    if comparison_df is not None:
        fig.add_trace(go.Scatter(
            x=comparison_df['Year'],
            y=comparison_df['Net Equity'],
            mode='lines',
            name=baseline_name,
            line=dict(color='rgb(108, 117, 125)', width=2, dash='dash'),
            hovertemplate='%{y:,.0f} 元<extra></extra>'
        ))
    
    # 繪製累計本金線
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
    
    # === 年度報酬率柱狀圖 ===
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
                title=f'{ticker} 歷年報酬率',
                xaxis_title='年份',
                yaxis_title='報酬率 (%)',
                hovermode='x',
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)

def display_detailed_data(final_df, use_leverage):
    """
    Displays a detailed data table of the backtest results.

    Args:
        final_df (pd.DataFrame): The DataFrame containing the final backtest results.
        use_leverage (bool): A flag indicating whether leverage was used.
    """
    st.subheader("📋 詳細數據表")
    
    # 準備顯示用的 DataFrame
    final_df_display = final_df.copy()
    
    # 根據是否有Calendar_Year欄位選擇要顯示的欄位
    if 'Calendar_Year' in final_df_display.columns:
        display_columns = ['Calendar_Year', 'Month', 'Net Equity', 'Principal', 'Shares', 'Share Price', 
                         'Cash Dividend', 'Stock Dividend', 'Dividend Tax']
        
        # 如果是槓桿模式，加入槓桿相關欄位
        if use_leverage and 'Loan Amount' in final_df_display.columns:
            display_columns.extend(['Loan Amount', 'Maintenance Ratio'])
        
        # 如果有年度報酬率，也加入
        if 'Annual Return' in final_df_display.columns:
            display_columns.insert(2, 'Annual Return')
        
        final_df_display = final_df_display[display_columns]
        
        # 重新命名欄位為中文
        column_rename = {
            'Calendar_Year': '西元年份',
            'Month': '月份',
            'Annual Return': '該年報酬率(%)',
            'Net Equity': '淨資產',
            'Principal': '累計本金',
            'Shares': '持股數',
            'Share Price': '股價',
            'Cash Dividend': '現金股利',
            'Stock Dividend': '股票股利',
            'Dividend Tax': '股利稅',
            'Loan Amount': '融資金額',
            'Maintenance Ratio': '維持率(%)'
        }
        final_df_display.columns = [column_rename.get(col, col) for col in final_df_display.columns]
        
        # 格式化數字
        for col in final_df_display.columns:
            if col in ['淨資產', '累計本金', '現金股利', '股票股利', '股利稅', '融資金額']:
                final_df_display[col] = final_df_display[col].apply(lambda x: f"NT$ {x:,.0f}")
            elif col == '股價':
                final_df_display[col] = final_df_display[col].apply(lambda x: f"NT$ {x:.2f}")
            elif col in ['持股數']:
                final_df_display[col] = final_df_display[col].apply(lambda x: f"{x:,.2f}")
            elif col in ['該年報酬率(%)', '維持率(%)']:
                final_df_display[col] = final_df_display[col].apply(lambda x: f"{x:.2f}")
    
    # 顯示資料表（預設只顯示年底數據）
    show_all_months = st.checkbox("顯示每月詳細數據", value=False)
    
    if show_all_months:
        st.dataframe(final_df_display, use_container_width=True, hide_index=True)
    else:
        # 只顯示每年12月的數據
        if '西元年份' in final_df_display.columns and '月份' in final_df_display.columns:
            yearly_data = final_df_display[final_df_display['月份'] == 12]
            st.dataframe(yearly_data, use_container_width=True, hide_index=True)

def display_leverage_warnings(df_with_leverage, maintenance_ratio, liquidation_ratio):
    """
    Displays warnings related to margin calls or liquidations if leverage was used.

    Args:
        df_with_leverage (pd.DataFrame): The DataFrame from the leveraged backtest.
        maintenance_ratio (float): The maintenance ratio threshold.
        liquidation_ratio (float): The liquidation ratio threshold.
    """
    # 檢查是否有追繳或斷頭記錄
    if 'Loan Amount' in df_with_leverage.columns:
        has_margin_call = (df_with_leverage['Maintenance Ratio'] < maintenance_ratio).any()
        has_liquidation = (df_with_leverage['Maintenance Ratio'] < liquidation_ratio).any()
        
        if has_liquidation:
            st.error("⚠️ **警告：回測期間發生斷頭事件！** 維持率曾低於斷頭線，實際操作中會被強制平倉，造成嚴重損失。")
        elif has_margin_call:
            st.warning("⚠️ **注意：回測期間曾發生追繳！** 維持率曾低於維持率門檻，需補足保證金。")
        else:
            st.success("✅ 回測期間維持率正常，未發生追繳或斷頭事件。")

# 計算按鈕
if st.sidebar.button("🚀 開始回測", type="primary"):
    # 執行計算
    with st.spinner('正在獲取歷史數據並進行回測...'):
        ticker = yahoo_symbol
        
        # 1. 獲取歷史數據
        fetcher = HistoricalDataFetcher()
        historical_returns = fetcher.fetch_monthly_returns(
            ticker=ticker,
            start_year=backtest_start_year,
            end_year=backtest_end_year
        )
        
        if historical_returns.empty:
            st.error(f"❌ 無法獲取 {ticker} 在 {backtest_start_year}-{backtest_end_year} 的歷史數據，請檢查日期範圍或代碼是否正確")
            st.stop()
        
        # 2. 設定計算器並執行回測
        monthly_calc_instance = MonthlyWealthCalculator(
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
            monthly_calculator=monthly_calc_instance,
            historical_returns=historical_returns
        )
        
        df_regular, df_with_leverage = backtest_calc.run_backtest(
            initial_capital=initial_capital,
            monthly_contribution=monthly_contribution,
            dividend_yield=expected_yield,
            use_leverage_from_ui=use_leverage
        )
        
        if df_regular.empty:
            st.error("❌ 回測計算失敗，沒有產生任何數據。")
            st.stop()

        # 3. 準備顯示數據
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
        
        # 4. 顯示結果
        display_summary_metrics(final_df, comparison_df)
        display_annual_returns_table(final_df)
        display_charts(final_df, comparison_df, strategy_name, baseline_name, backtest_start_year, backtest_end_year, ticker)
        display_detailed_data(final_df, use_leverage)
        
        if use_leverage:
            display_leverage_warnings(df_with_leverage, maintenance_ratio, liquidation_ratio)
        
        st.success("✅ 回測計算完成！")

else:
    st.info("👈 請在左側設定參數後，點擊「開始回測」按鈕")
    
    # 顯示範例說明
    st.markdown("""
    ### 📖 使用說明
    
    #### 🎯 回測功能
    - **真實數據**：使用 Yahoo Finance 的歷史股價數據
    - **月度計算**：採用月度複利和配息，更貼近真實投資體驗
    - **完整模擬**：包含交易手續費、證交稅、股利稅等所有成本
    - **槓桿機制**：完整模擬質押融資、維持率、追繳、斷頭等台灣股市規則
    
    #### 💡 建議設定
    - **0050**：半年配息（6月、12月）
    - **0056/00878**：季配或月配
    - **質押成數**：建議不超過 60%（保守）
    - **維持率門檻**：130%（券商標準）
    - **斷頭線**：120%（強制平倉）
    
    #### ⚠️ 風險提示
    1. 歷史數據不代表未來表現
    2. 槓桿會放大收益，也會放大風險
    3. 務必保持足夠的維持率，避免追繳或斷頭
    4. 本工具僅供參考，不構成投資建議
    """)