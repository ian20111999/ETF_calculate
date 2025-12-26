import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data.fetcher import get_etf_options

st.set_page_config(
    page_title="AI 投資顧問",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'ai_recommendation' not in st.session_state:
    st.session_state.ai_recommendation = None

st.title("🤖 AI 智能投資顧問")
st.caption("回答幾個問題，讓 AI 為您打造專屬投資組合")

# ============================================================================
# Recommendation Engine
# ============================================================================
def recommend_portfolio(age: int, risk_level: str, goal: str, monthly_savings: float):
    """
    規則基礎的投資組合推薦引擎
    
    Args:
        age: 年齡
        risk_level: 風險承受度（保守、穩健、積極）
        goal: 投資目標（退休、買房、存第一桶金）
        monthly_savings: 每月可存金額
    
    Returns:
        dict: 包含 portfolio, leverage, strategy_name, description
    """
    
    # 計算投資期限（年）
    if goal == "退休":
        investment_horizon = max(65 - age, 5)  # 至少5年
    elif goal == "買房":
        investment_horizon = 10 if age < 35 else 7
    else:  # 存第一桶金
        investment_horizon = 5
    
    # 根據年齡、風險、目標決定策略
    portfolio = {}
    use_leverage = False
    ltv = 0
    strategy_name = ""
    description = ""
    
    # ========== 積極型策略 ==========
    if risk_level == "積極 - 追求高報酬":
        if age < 35:
            # 年輕 + 積極：高成長配置 + 適度槓桿
            portfolio = {'0050': 70, '0056': 20, '00919': 10}
            use_leverage = True
            ltv = 50
            strategy_name = "🚀 積極成長型"
            description = """
            **策略分析**：
            - 您年輕且風險承受度高，適合追求成長
            - 70% 配置市值型 ETF (0050) 追求資本利得
            - 20% 高股息 ETF (0056) 提供穩定現金流
            - 10% 科技主題 (00919) 增加成長動能
            - 建議使用適度槓桿（50% LTV）放大報酬
            
            **風險提示**：波動較大，需承受短期虧損可能
            """
        elif age < 50:
            # 中年 + 積極：平衡成長
            portfolio = {'0050': 60, '0056': 30, '00878': 10}
            use_leverage = True
            ltv = 40
            strategy_name = "⚡ 成長平衡型"
            description = """
            **策略分析**：
            - 追求成長但需兼顧風險控制
            - 60% 市值型 (0050) 作為核心持倉
            - 40% 高股息 (0056 + 00878) 降低波動
            - 適度槓桿（40% LTV）提升效率
            
            **風險提示**：中等風險，適合定期檢視
            """
        else:
            # 接近退休 + 積極：穩健為主
            portfolio = {'0050': 40, '0056': 40, '00878': 20}
            use_leverage = False
            ltv = 0
            strategy_name = "🎯 穩健積極型"
            description = """
            **策略分析**：
            - 年齡較高，建議降低風險
            - 40% 市值型保留成長空間
            - 60% 高股息提供穩定收入
            - 不建議使用槓桿
            
            **風險提示**：相對穩健，但仍有波動
            """
    
    # ========== 穩健型策略 ==========
    elif risk_level == "穩健 - 可接受波動":
        if age < 40:
            portfolio = {'0050': 50, '0056': 30, '00878': 20}
            use_leverage = False
            ltv = 0
            strategy_name = "⚖️ 均衡配置型"
            description = """
            **策略分析**：
            - 平衡成長與穩定的經典配置
            - 50% 市值型追求長期成長
            - 50% 高股息提供現金流與緩衝
            - 不使用槓桿，降低風險
            
            **風險提示**：波動適中，適合長期持有
            """
        else:
            portfolio = {'0050': 30, '0056': 40, '00878': 30}
            use_leverage = False
            ltv = 0
            strategy_name = "🛡️ 防禦穩健型"
            description = """
            **策略分析**：
            - 偏重高股息，降低波動
            - 30% 市值型保留成長性
            - 70% 高股息提供穩定配息
            - 適合追求現金流的投資人
            
            **風險提示**：低波動，但成長有限
            """
    
    # ========== 保守型策略 ==========
    else:  # 保守 - 不想賠錢
        if goal == "退休" or age > 50:
            portfolio = {'0056': 50, '00878': 50}
            use_leverage = False
            ltv = 0
            strategy_name = "🏰 保守收息型"
            description = """
            **策略分析**：
            - 極度保守，重視資本保全
            - 100% 高股息 ETF
            - 追求穩定配息，降低波動
            - 絕不使用槓桿
            
            **風險提示**：最低風險，但報酬有限
            """
        else:
            portfolio = {'0050': 30, '0056': 40, '00878': 30}
            use_leverage = False
            ltv = 0
            strategy_name = "🌱 保守成長型"
            description = """
            **策略分析**：
            - 保守但保留適度成長空間
            - 30% 市值型適度參與市場
            - 70% 高股息降低波動
            - 適合風險承受度低的投資人
            
            **風險提示**：低風險低報酬
            """
    
    # 根據投資期限微調
    if investment_horizon < 5 and use_leverage:
        use_leverage = False
        ltv = 0
        description += "\n\n⚠️ **特別提醒**：投資期限較短，已取消槓桿建議"
    
    # 根據每月存款額度建議
    if monthly_savings < 10000:
        description += f"\n\n💡 **建議**：您的月存款 ${monthly_savings:,.0f} 元較少，建議先累積至少 10 萬元再開始投資，或考慮提高每月投入金額。"
    elif monthly_savings > 50000:
        description += f"\n\n🎉 **太棒了**：您的月存款 ${monthly_savings:,.0f} 元相當充裕，長期複利效果將非常可觀！"
    
    return {
        'portfolio': portfolio,
        'use_leverage': use_leverage,
        'ltv': ltv,
        'strategy_name': strategy_name,
        'description': description,
        'investment_horizon': investment_horizon
    }

# ============================================================================
# Input Section - The Interview
# ============================================================================
st.markdown("---")
st.header("📋 投資人問卷")
st.write("請回答以下問題，我們將為您量身打造投資策略")

col1, col2 = st.columns(2)

with col1:
    age = st.slider(
        "1️⃣ 您的年齡？",
        min_value=20,
        max_value=80,
        value=30,
        step=1,
        help="年齡會影響投資期限與風險承受能力"
    )
    
    goal = st.selectbox(
        "2️⃣ 您的投資目標？",
        options=["存第一桶金", "買房", "退休"],
        help="不同目標需要不同的投資策略"
    )

with col2:
    monthly_savings = st.number_input(
        "3️⃣ 每月能存多少？（元）",
        min_value=1000,
        max_value=500000,
        value=20000,
        step=1000,
        help="每月定期投入的金額"
    )
    
    risk_level = st.selectbox(
        "4️⃣ 您的風險承受度？",
        options=[
            "保守 - 不想賠錢",
            "穩健 - 可接受波動",
            "積極 - 追求高報酬"
        ],
        index=1,
        help="風險承受度決定資產配置比例"
    )

# Calculate button
st.markdown("---")

if st.button("🧠 生成 AI 投資建議", type="primary", use_container_width=True):
    with st.spinner("AI 正在分析您的需求..."):
        # Generate recommendation
        recommendation = recommend_portfolio(age, risk_level, goal, monthly_savings)
        st.session_state.ai_recommendation = recommendation
        
        # Store parameters for backtest
        st.session_state.ai_age = age
        st.session_state.ai_goal = goal
        st.session_state.ai_monthly_savings = monthly_savings
        st.session_state.ai_risk_level = risk_level

# ============================================================================
# Output Section - The Report
# ============================================================================
if st.session_state.ai_recommendation:
    rec = st.session_state.ai_recommendation
    
    st.success("✅ AI 分析完成！")
    
    # Strategy Name Header
    st.markdown("---")
    st.markdown(f"## {rec['strategy_name']}")
    
    # Description
    st.markdown(rec['description'])
    
    # Key Metrics
    st.markdown("---")
    st.subheader("📊 推薦配置總覽")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "投資期限",
            f"{rec['investment_horizon']} 年",
            help="根據您的年齡和目標計算"
        )
    
    with col2:
        st.metric(
            "資產類別",
            f"{len(rec['portfolio'])} 種",
            help="分散投資降低風險"
        )
    
    with col3:
        leverage_status = "是" if rec['use_leverage'] else "否"
        st.metric(
            "使用槓桿",
            leverage_status,
            help=f"質押成數: {rec['ltv']}%" if rec['use_leverage'] else "不使用槓桿更安全"
        )
    
    with col4:
        # Calculate expected return (simplified)
        etf_options = get_etf_options()
        avg_yield = np.average(
            [etf_options[etf]['yield'] for etf in rec['portfolio'].keys()],
            weights=[rec['portfolio'][etf] for etf in rec['portfolio'].keys()]
        )
        market_return = 8.0  # 假設市場年化報酬
        if rec['use_leverage']:
            expected_return = market_return * (1 + rec['ltv']/100) - (rec['ltv']/100 * 6.5)
        else:
            expected_return = market_return
        
        st.metric(
            "預期年化報酬",
            f"{expected_return:.1f}%",
            help="基於歷史數據的估算，不保證未來表現"
        )
    
    # Portfolio Pie Chart
    st.markdown("---")
    st.subheader("🥧 投資組合配置")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create pie chart
        labels = []
        values = []
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
        
        for i, (etf, weight) in enumerate(rec['portfolio'].items()):
            etf_name = etf_options[etf]['name']
            labels.append(f"{etf_name} ({etf})")
            values.append(weight)
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors[:len(labels)]),
            textinfo='label+percent',
            textfont_size=14,
            hole=0.3
        )])
        
        fig.update_layout(
            title="資產配置比例",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📝 配置明細")
        
        for etf, weight in rec['portfolio'].items():
            etf_data = etf_options[etf]
            st.write(f"**{etf_data['name']}** ({etf})")
            st.progress(weight / 100, text=f"{weight}%")
            st.caption(f"殖利率: {etf_data['yield']}%")
            st.write("")
        
        if rec['use_leverage']:
            st.warning(f"⚡ 建議使用 {rec['ltv']}% 質押槓桿")
        else:
            st.info("✅ 不使用槓桿，風險較低")
    
    # Expected Performance
    st.markdown("---")
    st.subheader("💰 預期投資成果（假設）")
    
    # Simple projection
    years = rec['investment_horizon']
    monthly = st.session_state.ai_monthly_savings
    annual_return = expected_return / 100
    
    # Calculate future value with monthly contributions
    months = years * 12
    monthly_return = (1 + annual_return) ** (1/12) - 1
    
    future_value = 0
    for month in range(months):
        future_value = (future_value + monthly) * (1 + monthly_return)
    
    total_contribution = monthly * months
    profit = future_value - total_contribution
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "累計投入",
            f"NT$ {total_contribution:,.0f}",
            help=f"每月 ${monthly:,.0f} × {months} 個月"
        )
    
    with col2:
        st.metric(
            f"{years} 年後預期資產",
            f"NT$ {future_value:,.0f}",
            delta=f"+{(future_value/total_contribution - 1)*100:.1f}%"
        )
    
    with col3:
        st.metric(
            "預期獲利",
            f"NT$ {profit:,.0f}",
            help="未扣除稅費和手續費"
        )
    
    st.info(f"💡 假設年化報酬 {expected_return:.1f}%，每月定投 ${monthly:,.0f} 元，{years} 年後可累積約 ${future_value:,.0f} 元")
    
    # Call to Action
    st.markdown("---")
    st.subheader("🚀 下一步行動")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📈 帶入回測實驗室", type="primary", use_container_width=True):
            # Store portfolio config in session state for backtest page
            st.session_state.backtest_portfolio = rec['portfolio']
            st.session_state.backtest_leverage = rec['use_leverage']
            st.session_state.backtest_ltv = rec['ltv']
            st.session_state.backtest_monthly = monthly
            st.session_state.from_ai_advisor = True
            
            st.success("✅ 配置已保存！正在跳轉...")
            st.switch_page("pages/2_🧪_Backtest_Lab.py")
    
    with col2:
        if st.button("🔮 模擬未來表現", use_container_width=True):
            # Store for Monte Carlo page
            st.session_state.mc_portfolio = rec['portfolio']
            st.session_state.mc_leverage = rec['use_leverage']
            st.session_state.mc_monthly = monthly
            st.session_state.from_ai_advisor = True
            
            st.success("✅ 配置已保存！正在跳轉...")
            st.switch_page("pages/3_🔮_Crystal_Ball.py")
    
    with col3:
        if st.button("🔄 重新設計", use_container_width=True):
            st.session_state.ai_recommendation = None
            st.rerun()
    
    # Risk Disclaimer
    st.markdown("---")
    st.warning("""
    ⚠️ **重要提示**：
    - 以上建議基於規則引擎，僅供參考
    - 預期報酬基於歷史數據，不保證未來表現
    - 實際投資前請諮詢專業理財顧問
    - 投資有風險，請謹慎評估自身狀況
    """)

else:
    st.info("👆 請先填寫問卷並點擊「生成 AI 投資建議」")

# ============================================================================
# Educational Content (Below the fold)
# ============================================================================
st.markdown("---")
st.markdown("## 📚 投資知識補充")

col1, col2 = st.columns(2)

with col1:
    with st.expander("🎓 為什麼需要資產配置？"):
        st.write("""
        **分散風險**：不把雞蛋放在同一個籃子
        - 市值型 ETF：追求長期成長
        - 高股息 ETF：提供穩定現金流
        - 組合配置：降低整體波動
        
        **適應生命週期**：
        - 年輕時：可承受較高風險，偏重成長
        - 中年時：平衡成長與收入
        - 退休前：降低風險，重視現金流
        """)
    
    with st.expander("💰 什麼是槓桿投資？"):
        st.write("""
        **槓桿定義**：透過質押股票借款，放大投資金額
        
        **優勢**：
        - 放大報酬率
        - 提高資金使用效率
        
        **風險**：
        - 放大虧損
        - 需支付利息成本
        - 可能追繳或斷頭
        
        **建議**：
        - 年輕且風險承受度高者適用
        - 質押成數不宜過高（建議 < 60%）
        - 密切關注維持率
        """)

with col2:
    with st.expander("📊 如何解讀 AI 建議？"):
        st.write("""
        **配置比例**：
        - 反映風險與報酬的平衡
        - 市值型比例越高，成長性越強但波動越大
        - 高股息比例越高，穩定性越高但成長有限
        
        **槓桿建議**：
        - AI 會根據年齡和風險承受度決定
        - 保守型投資人不建議使用
        - 積極型年輕投資人可適度使用
        
        **預期報酬**：
        - 基於歷史數據估算
        - 不保證未來表現
        - 僅供參考
        """)
    
    with st.expander("🎯 投資目標如何影響策略？"):
        st.write("""
        **存第一桶金**（短期 5 年）：
        - 相對保守，降低風險
        - 不建議槓桿
        - 重視資本保全
        
        **買房**（中期 7-10 年）：
        - 平衡配置
        - 可適度使用槓桿
        - 兼顧成長與穩定
        
        **退休**（長期 10+ 年）：
        - 年輕時積極，接近退休時保守
        - 長期可承受波動
        - 複利效果顯著
        """)

