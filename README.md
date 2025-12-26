# 🇹🇼 台股 ETF 累積與槓桿回測計算器

使用真實歷史數據回測您的投資策略，支援槓桿質押融資模擬。

## ✨ 特色功能

- 📊 **真實歷史回測**：使用 Yahoo Finance 實際股價數據
- 💰 **槓桿模擬**：完整模擬質押融資、維持率、追繳、斷頭機制
- 📈 **多標的支援**：0050、0056、00878、2330 等台股標的
- 💵 **配息計算**：支援年配/半年配/季配/月配
- 🎯 **定期定額**：模擬每月定投策略
- 📉 **風險管理**：追繳保證金與強制平倉機制

## 🏗️ 架構說明 (V2.0)

專案採用模組化三層架構，便於擴展與維護：

```
etf_calculate/
├── app.py                      # Streamlit UI 層
├── core/                       # 業務邏輯層
│   ├── __init__.py
│   ├── engine.py               # 回測引擎 (from backtester.py)
│   ├── calculator.py           # 月度計算器 (from monthly_calculator.py)
│   ├── portfolio.py            # [未來] 多資產配置
│   ├── tax.py                  # [未來] 稅務計算
│   └── risk.py                 # [未來] 風險管理
├── data/                       # 數據層
│   ├── __init__.py
│   ├── fetcher.py              # 數據獲取 (from data_loader.py)
│   └── market_indicators.py    # [未來] 市場指標
├── simulation/                 # 模擬層
│   ├── __init__.py
│   ├── monte_carlo.py          # [未來] 蒙地卡羅模擬
│   └── scenarios.py            # [未來] 情境分析
├── tests/                      # 測試文件
│   ├── test_backtester.py
│   └── test_monthly_calculator.py
└── requirements.txt
```

### 架構設計原則

1. **分層解耦**：UI、業務邏輯、數據存取分離
2. **單一職責**：每個模組專注特定功能
3. **易於擴展**：可輕鬆添加新功能（多資產、稅務、蒙地卡羅）
4. **向後兼容**：保留原有文件（data_loader.py 等）以確保舊代碼可運作

## 🚀 快速開始

### 安裝依賴

```bash
# 創建虛擬環境
python -m venv etfvenv
source etfvenv/bin/activate  # macOS/Linux
# 或 etfvenv\Scripts\activate  # Windows

# 安裝套件
pip install -r requirements.txt
```

### 運行應用

```bash
streamlit run app.py
```

### 運行測試

```bash
pytest tests/
```

## 📦 主要依賴

- `streamlit`: Web UI 框架
- `yfinance`: Yahoo Finance 數據源
- `pandas`: 數據處理
- `plotly`: 互動式圖表
- `pytest`: 測試框架

## 🎯 未來規劃

### Phase 2: 多資產組合
- [ ] `core/portfolio.py`: 支援多標的資產配置
- [ ] 資產相關性分析
- [ ] 動態再平衡機制

### Phase 3: 進階稅務
- [ ] `core/tax.py`: 台灣股利所得稅精確計算
- [ ] 健保補充保費（2.11%）
- [ ] 綜合所得稅試算

### Phase 4: 蒙地卡羅模擬
- [ ] `simulation/monte_carlo.py`: 多路徑模擬
- [ ] `simulation/scenarios.py`: 壓力測試
- [ ] 風險指標計算（VaR, CVaR）

## 📝 使用範例

```python
from core.calculator import MonthlyWealthCalculator
from core.engine import BacktestCalculator, HistoricalDataFetcher
from data.fetcher import get_etf_options, get_current_price

# 獲取 ETF 資訊
etf_options = get_etf_options()
current_price = get_current_price("0050.TW")

# 創建計算器
calculator = MonthlyWealthCalculator(
    use_leverage=True,
    ltv=60.0,
    maintenance_ratio=130.0,
    liquidation_ratio=120.0,
    margin_interest_rate=6.5,
    transaction_fee_rate_buy=0.1425,
    transaction_fee_rate_sell=0.4425,
    dividend_frequency=4,
    re_leverage_ratio=180.0,
    dividend_tax_rate=2.11
)

# 獲取歷史數據
fetcher = HistoricalDataFetcher()
historical_data = fetcher.fetch_monthly_returns("0050.TW", 2014, 2024)

# 執行回測
backtester = BacktestCalculator(calculator, historical_data)
df_regular, df_leverage = backtester.run_backtest(
    initial_capital=1000000,
    monthly_contribution=20000,
    dividend_yield=3.2,
    use_leverage_from_ui=True
)
```

## 🔧 開發

### 代碼風格
- 遵循 PEP 8 規範
- 使用 type hints
- 完整的 docstrings

### 測試覆蓋
```bash
# 運行測試並生成覆蓋率報告
pytest --cov=core --cov=data tests/
```

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## ⚠️ 免責聲明

本工具僅供教育和研究目的，不構成投資建議。投資有風險，請謹慎評估。
