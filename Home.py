import streamlit as st
import random
from data.fetcher import get_etf_options

# ============================================================================
# Page Configuration
# ============================================================================
st.set_page_config(
    page_title="SmartWealth AI 智慧存股領航員",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Custom CSS for Modern Styling
# ============================================================================
st.markdown("""
<style>
    /* Hero Section */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 2rem;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        height: 100%;
        min-height: 200px;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .feature-card-1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .feature-card-2 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .feature-card-3 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        font-size: 1.1rem;
        opacity: 0.9;
        line-height: 1.6;
    }
    
    /* Quote Section */
    .quote-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 2rem;
        border-radius: 1rem;
        border-left: 4px solid #667eea;
        margin: 2rem 0;
    }
    
    .quote-text {
        font-size: 1.2rem;
        font-style: italic;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .quote-author {
        font-size: 1rem;
        color: #666;
        text-align: right;
    }
    
    /* Stats Section */
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Sidebar Styling */
    .etf-list-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        background: #f8f9fa;
        border-radius: 0.3rem;
        font-size: 0.9rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar - ETF List
# ============================================================================
st.sidebar.title("📊 支援的 ETF 標的")
st.sidebar.markdown("---")

etf_options = get_etf_options()
st.sidebar.markdown("### 🇹🇼 台股 ETF")

for etf_key, etf_data in etf_options.items():
    with st.sidebar.expander(f"{etf_data['name']} ({etf_key})"):
        st.write(f"**代碼**: {etf_data['yahoo_symbol']}")
        st.write(f"**殖利率**: {etf_data['yield']}%")
        st.write(f"**類型**: {'高股息' if '00' in etf_key and int(etf_key[:2]) > 50 else '市值型'}")

st.sidebar.markdown("---")
st.sidebar.info("💡 更多 ETF 標的持續新增中...")

# ============================================================================
# Hero Section
# ============================================================================
st.markdown('<h1 class="hero-title">🚀 SmartWealth AI 智慧存股領航員</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Your Personal AI Investment Copilot | 讓數據科學為您的財富保駕護航</p>', unsafe_allow_html=True)

# ============================================================================
# Quick Stats
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">{}</div>
        <div class="stat-label">支援 ETF</div>
    </div>
    """.format(len(etf_options)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">20+</div>
        <div class="stat-label">歷史年份</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">1000+</div>
        <div class="stat-label">模擬次數</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">V3.0</div>
        <div class="stat-label">系統版本</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# Feature Cards - Main Navigation
# ============================================================================
st.markdown("## 🎯 選擇您的投資旅程")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card feature-card-1">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI 智能規劃</div>
        <div class="feature-desc">
            不知道該買什麼？<br>
            AI 根據您的風險偏好<br>
            量身打造投資組合
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 開始智能規劃", key="btn_advisor", use_container_width=True, type="primary"):
        st.switch_page("pages/1_🤖_AI_Advisor.py")

with col2:
    st.markdown("""
    <div class="feature-card feature-card-2">
        <div class="feature-icon">🧪</div>
        <div class="feature-title">策略實驗室</div>
        <div class="feature-desc">
            已有投資策略？<br>
            使用真實歷史數據<br>
            驗證您的想法
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔬 進入實驗室", key="btn_backtest", use_container_width=True, type="primary"):
        st.switch_page("pages/2_🧪_Backtest_Lab.py")

with col3:
    st.markdown("""
    <div class="feature-card feature-card-3">
        <div class="feature-icon">🔮</div>
        <div class="feature-title">未來模擬</div>
        <div class="feature-desc">
            達成目標的機率？<br>
            蒙地卡羅模擬<br>
            預測未來可能性
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🎲 模擬未來", key="btn_monte_carlo", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🔮_Crystal_Ball.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# Investment Quote (Random)
# ============================================================================
quotes = [
    ("The stock market is a device for transferring money from the impatient to the patient.", "Warren Buffett"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("The four most dangerous words in investing are: 'this time it's different.'", "Sir John Templeton"),
    ("In investing, what is comfortable is rarely profitable.", "Robert Arnott"),
    ("Time in the market beats timing the market.", "Ken Fisher"),
    ("The best investment you can make is in yourself.", "Warren Buffett"),
    ("Wide diversification is only required when investors do not understand what they are doing.", "Warren Buffett"),
    ("投資最重要的是紀律與耐心。", "華倫·巴菲特"),
    ("複利是世界第八大奇蹟。", "阿爾伯特·愛因斯坦"),
    ("不要把所有雞蛋放在同一個籃子裡。", "投資格言"),
]

selected_quote = random.choice(quotes)

st.markdown(f"""
<div class="quote-box">
    <div class="quote-text">"{selected_quote[0]}"</div>
    <div class="quote-author">— {selected_quote[1]}</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Features Overview
# ============================================================================
st.markdown("---")
st.markdown("## ✨ 核心功能特色")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 多資產組合")
    st.write("支援多 ETF 組合配置，自由調整權重比例，建立個人化投資組合。")
    
    st.markdown("### 🎯 真實數據回測")
    st.write("使用 Yahoo Finance 20 年歷史數據，完整模擬配息、手續費、稅務。")

with col2:
    st.markdown("### ⚡ 槓桿模擬")
    st.write("完整模擬台灣股市質押融資規則，包含維持率、追繳、斷頭機制。")
    
    st.markdown("### 🔮 蒙地卡羅模擬")
    st.write("執行 1000+ 次模擬，評估未來可能結果，顯示 5%-95% 信賴區間。")

with col3:
    st.markdown("### 🤖 AI 智能推薦")
    st.write("根據風險偏好與投資目標，AI 自動推薦最適合的 ETF 組合。")
    
    st.markdown("### 📈 互動式圖表")
    st.write("使用 Plotly 打造互動式圖表，清晰呈現財富累積趨勢與風險分析。")

# ============================================================================
# Risk Disclaimer
# ============================================================================
st.markdown("---")
st.warning("""
⚠️ **風險提示**：
- 本工具僅供教育與研究用途，不構成投資建議
- 歷史回測結果不代表未來表現
- 投資有風險，請謹慎評估自身風險承受能力
- 槓桿投資風險更高，可能導致重大損失
- 使用本工具產生的任何投資決策，風險自負
""")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
col1, col2, col3 = st.columns([2, 3, 2])

with col2:
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p><strong>SmartWealth AI V3.0</strong> | Powered by Streamlit & Python</p>
        <p>🚀 Built with ❤️ for smart investors</p>
    </div>
    """, unsafe_allow_html=True)
