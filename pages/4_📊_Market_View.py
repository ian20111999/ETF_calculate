import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data.fetcher import get_etf_options, get_current_price

st.set_page_config(
    page_title="市場資訊看板",
    page_icon="📊",
    layout="wide"
)

st.title("📊 市場資訊看板")
st.caption("即時掌握 ETF 市場動態與關鍵數據")

# ============================================================================
# Coming Soon Message
# ============================================================================
st.info("🚧 **功能開發中** | 此頁面即將推出，敬請期待！")

st.markdown("---")

# ============================================================================
# Preview: ETF Price Dashboard
# ============================================================================
st.markdown("## 📈 ETF 即時報價（預覽）")

etf_options = get_etf_options()

# Create tabs for different ETF categories
tab1, tab2 = st.tabs(["🏛️ 市值型 ETF", "💰 高股息 ETF"])

with tab1:
    st.subheader("市值型 ETF")
    
    market_etfs = ["0050"]
    cols = st.columns(len(market_etfs))
    
    for i, etf_key in enumerate(market_etfs):
        with cols[i]:
            etf_data = etf_options[etf_key]
            ticker = etf_data['yahoo_symbol']
            
            # Try to fetch current price
            try:
                price = get_current_price(ticker)
                if price:
                    st.metric(
                        label=etf_data['name'],
                        value=f"NT$ {price:.2f}",
                        delta="載入中...",
                        help=f"殖利率: {etf_data['yield']}%"
                    )
                else:
                    st.metric(label=etf_data['name'], value="N/A")
            except:
                st.metric(label=etf_data['name'], value="N/A")

with tab2:
    st.subheader("高股息 ETF")
    
    dividend_etfs = ["0056", "00878", "00919"]
    cols = st.columns(len(dividend_etfs))
    
    for i, etf_key in enumerate(dividend_etfs):
        with cols[i]:
            etf_data = etf_options[etf_key]
            ticker = etf_data['yahoo_symbol']
            
            try:
                price = get_current_price(ticker)
                if price:
                    st.metric(
                        label=etf_data['name'],
                        value=f"NT$ {price:.2f}",
                        delta="載入中...",
                        help=f"殖利率: {etf_data['yield']}%"
                    )
                else:
                    st.metric(label=etf_data['name'], value="N/A")
            except:
                st.metric(label=etf_data['name'], value="N/A")

# ============================================================================
# Preview: Market Trends
# ============================================================================
st.markdown("---")
st.markdown("## 📉 市場趨勢分析（預覽）")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 近期表現")
    st.write("功能開發中...")
    st.info("將顯示各 ETF 近 1 個月、3 個月、6 個月的表現排行")

with col2:
    st.markdown("### 波動度分析")
    st.write("功能開發中...")
    st.info("將顯示各 ETF 的歷史波動度與風險指標")

# ============================================================================
# Preview: Features List
# ============================================================================
st.markdown("---")
st.markdown("## ✨ 即將推出的功能")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 即時報價")
    st.write("""
    - 即時股價更新
    - 漲跌幅與成交量
    - 日內價格走勢圖
    - 技術指標（MA, RSI）
    """)

with col2:
    st.markdown("### 📈 歷史走勢")
    st.write("""
    - 可調整時間範圍
    - 多 ETF 比較圖表
    - 績效排行榜
    - 相關性分析
    """)

with col3:
    st.markdown("### 📰 市場新聞")
    st.write("""
    - ETF 相關新聞
    - 配息公告
    - 成分股調整
    - 市場分析報告
    """)

# ============================================================================
# Temporary: ETF Comparison Tool
# ============================================================================
st.markdown("---")
st.markdown("## 🔍 ETF 比較工具（示範）")

selected_compare = st.multiselect(
    "選擇要比較的 ETF",
    options=list(etf_options.keys()),
    default=["0050", "0056"],
    format_func=lambda x: etf_options[x]["name"]
)

if selected_compare:
    comparison_data = []
    for etf_key in selected_compare:
        etf_data = etf_options[etf_key]
        comparison_data.append({
            "ETF": etf_data['name'],
            "代碼": etf_key,
            "Yahoo 代碼": etf_data['yahoo_symbol'],
            "預期殖利率 (%)": etf_data['yield'],
            "類型": "高股息" if int(etf_key[:2]) > 50 else "市值型"
        })
    
    df_compare = pd.DataFrame(comparison_data)
    st.dataframe(df_compare, use_container_width=True, hide_index=True)
else:
    st.info("請至少選擇一個 ETF 進行比較")

# ============================================================================
# Educational Content
# ============================================================================
st.markdown("---")
st.markdown("## 📚 ETF 知識補給站")

with st.expander("💡 市值型 ETF vs 高股息 ETF"):
    st.write("""
    **市值型 ETF**（如 0050）：
    - 追蹤市值最大的公司
    - 重視資本利得（股價上漲）
    - 適合長期投資、追求成長
    - 波動度相對較高
    
    **高股息 ETF**（如 0056、00878）：
    - 挑選高股息殖利率公司
    - 重視現金流（配息）
    - 適合追求穩定收入
    - 波動度相對較低
    
    **選擇建議**：
    - 年輕投資人：市值型為主（成長空間大）
    - 退休族群：高股息為主（穩定現金流）
    - 平衡配置：兩者搭配（50/50 或 60/40）
    """)

with st.expander("📊 如何看懂 ETF 資訊？"):
    st.write("""
    **關鍵指標**：
    
    1. **股價**：當前市場價格
    2. **殖利率**：年度配息 ÷ 股價
    3. **費用率**：管理費用佔比（越低越好）
    4. **追蹤誤差**：與指數的差異
    5. **成交量**：流動性指標
    
    **查看資訊管道**：
    - 投信公司官網
    - 證交所公開資訊
    - Yahoo Finance
    - 各券商 APP
    """)

st.markdown("---")
st.info("💡 **提示**：市場看板功能預計在下一個版本推出，將提供更完整的市場資訊！")

# ============================================================================
# Quick Links
# ============================================================================
st.markdown("---")
st.markdown("## 🔗 相關連結")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 官方網站")
    st.markdown("- [元大投信](https://www.yuantafunds.com/)")
    st.markdown("- [國泰投信](https://www.cathaysite.com.tw/)")
    st.markdown("- [復華投信](https://www.fhtrust.com.tw/)")

with col2:
    st.markdown("### 資訊查詢")
    st.markdown("- [台灣證交所](https://www.twse.com.tw/)")
    st.markdown("- [MoneyDJ](https://www.moneydj.com/)")
    st.markdown("- [Yahoo 財經](https://tw.stock.yahoo.com/)")

with col3:
    st.markdown("### 學習資源")
    st.markdown("- [綠角財經筆記](http://greenhornfinancefootnote.blogspot.com/)")
    st.markdown("- [ETF 台灣](https://www.etf.com.tw/)")
    st.markdown("- [理財學伴](https://www.facebook.com/richmentor/)")
