# Action 2 完成：核心邏輯解耦

## 🎯 重構目標
將原本 `monthly_calculator.py` 中混雜的稅務和風險管理邏輯解耦，創建獨立、可測試的模組。

## ✅ 完成項目

### 1. 新模組：`core/tax.py` - TaxCalculator

**功能**：
- ✅ 補充保費計算（單次股利 > 20,000 TWD 課徵 2.11%）
- ✅ **[NEW]** 股利所得稅抵減（8.5%，年度上限 80,000 TWD）
- ✅ 年度抵減額度追蹤
- ✅ 淨稅務影響計算

**使用範例**：
```python
from core.tax import TaxCalculator

tax_calc = TaxCalculator(
    dividend_tax_rate=2.11,        # 補充保費率
    dividend_tax_threshold=20000,   # 補充保費門檻
    dividend_credit_rate=8.5,       # 稅務抵減率
    annual_dividend_credit_cap=80000 # 年度抵減上限
)

# 計算股利稅務
result = tax_calc.calculate_dividend_tax(
    cash_dividend=25000,  # 領取 25,000 元股利
    current_year=2024
)

print(f"補充保費: {result['supplementary_premium']:.2f}")  # 527.50
print(f"稅務抵減: {result['tax_credit']:.2f}")          # 2125.00
print(f"淨影響: {result['net_tax_impact']:.2f}")        # +1597.50 (正向現金流)
```

**關鍵特性**：
- 稅務抵減是**正向現金流**，可用於再投資
- 自動追蹤年度累計額度，防止超過上限
- 提供年度稅務摘要

---

### 2. 新模組：`core/risk.py` - RiskEngine

**功能**：
- ✅ 維持率計算
- ✅ 追繳保證金檢查
- ✅ 強制平倉（斷頭）檢查
- ✅ 再槓桿機會評估
- ✅ 斷頭影響計算
- ✅ 追繳需求計算

**使用範例**：
```python
from core.risk import RiskEngine

risk_engine = RiskEngine(
    maintenance_ratio=130,  # 維持率門檻 130%
    liquidation_ratio=120,  # 斷頭線 120%
    re_leverage_ratio=180,  # 再槓桿門檻 180%
    ltv=60                  # 質押成數 60%
)

# 計算維持率
ratio = risk_engine.calculate_maintenance_ratio(
    stock_value=130000,  # 股票市值
    loan_amount=100000   # 貸款金額
)
print(f"維持率: {ratio:.2%}")  # 130.00%

# 風險檢查
print(f"需要追繳? {risk_engine.check_margin_call(ratio)}")      # False
print(f"觸發斷頭? {risk_engine.check_liquidation(ratio)}")      # False
print(f"可再槓桿? {risk_engine.check_re_leverage_opportunity(ratio)}")  # False

# 計算追繳需求
if risk_engine.check_margin_call(ratio):
    requirement = risk_engine.calculate_margin_call_requirement(
        stock_value=120000,
        loan_amount=100000,
        available_cash=5000,
        shares=100,
        share_price=1200,
        sell_fee_rate=0.004425
    )
    print(f"需要補充: {requirement['value_to_add']:.2f}")
```

**關鍵特性**：
- 完整的槓桿風險管理邏輯
- 可計算斷頭和追繳的詳細影響
- 支援現金和賣股兩種追繳方式

---

### 3. 重構：`core/calculator.py` - MonthlyWealthCalculator

**變更**：
```python
# Before: 硬編碼稅務計算
if cash_dividend > self.dividend_tax_threshold:
    dividend_tax = cash_dividend * self.dividend_tax_rate

# After: 使用 TaxCalculator
tax_result = self.tax_calculator.calculate_dividend_tax(cash_dividend, current_year)
dividend_tax = tax_result['supplementary_premium']
tax_credit = tax_result['tax_credit']  # 新增：稅務抵減
```

```python
# Before: 硬編碼風險計算
maintenance_ratio = stock_value / loan
if maintenance_ratio < self.liquidation_ratio_threshold:
    # ... 複雜的計算邏輯

# After: 使用 RiskEngine
maintenance_ratio = self.risk_engine.calculate_maintenance_ratio(stock_value, loan)
if self.risk_engine.check_liquidation(maintenance_ratio):
    liquidation_result = self.risk_engine.calculate_liquidation_impact(...)
```

**新增返回值**：
```python
return {
    # ... 原有欄位
    "Tax Credit": tax_credit,  # 新增：稅務抵減金額
}
```

---

## 📊 架構優勢對比

### Before (V1.0)
```
monthly_calculator.py (194 lines)
├─ __init__: 稅務參數、風險參數混在一起
├─ run_monthly_cycle: 
│   ├─ 股價計算
│   ├─ [內嵌] 股利稅務計算
│   ├─ 利息計算
│   ├─ [內嵌] 維持率檢查
│   ├─ [內嵌] 追繳邏輯
│   ├─ [內嵌] 斷頭邏輯
│   └─ [內嵌] 再槓桿邏輯
```

### After (V2.0)
```
core/
├── calculator.py (225 lines) - 協調器
│   └─ run_monthly_cycle: 
│       ├─ 股價計算
│       ├─ tax_calculator.calculate_dividend_tax()  # 委派
│       ├─ 利息計算
│       └─ risk_engine.check_xxx()  # 委派
│
├── tax.py (120 lines) - 獨立稅務邏輯
│   └── TaxCalculator
│       ├─ calculate_dividend_tax()
│       ├─ reset_annual_tracking()
│       └─ get_annual_summary()
│
└── risk.py (235 lines) - 獨立風險邏輯
    └── RiskEngine
        ├─ calculate_maintenance_ratio()
        ├─ check_liquidation()
        ├─ check_margin_call()
        ├─ calculate_liquidation_impact()
        ├─ calculate_margin_call_requirement()
        └─ check_re_leverage_opportunity()
```

---

## 🎯 測試驗證

### 稅務計算測試
```bash
✅ TaxCalculator: 股利 25,000 元
   補充保費: 527.50      # 25000 * 2.11% = 527.5
   稅務抵減: 2125.00     # 25000 * 8.5% = 2125
   淨影響: +1597.50      # 正向現金流！
```

### 風險管理測試
```bash
✅ RiskEngine: 維持率 = 130.00%
   需要追繳? False
   觸發斷頭? False
```

### 完整月度計算測試
```bash
✅ 月度計算完成（配息月）
股價: 100.99
持股: 110.67
股票市值: 11176.57
貸款: 6000.00
淨資產: 5176.57
現金股利: 102.00
補充保費: 0.00          # 股利 < 20000，無需繳納
稅務抵減: 8.67          # 8.5% 的抵減，可再投資
維持率: 186.28%
```

---

## 💡 新功能：稅務抵減 (Tax Credit)

### 什麼是股利所得稅抵減？
根據台灣稅法，股利收入可享有 **8.5% 的稅額抵減**，這是一項**正向現金流**：

**範例**：
- 領取股利：100,000 元
- 補充保費（-）：2,110 元（2.11%，超過 20,000 門檻）
- 稅務抵減（+）：8,500 元（8.5%）
- **淨收入**：106,390 元 = 100,000 - 2,110 + 8,500

### 年度上限
- 每年最高抵減：80,000 元
- 自動追蹤累計使用額度
- 超過上限部分不予抵減

### 實際影響
在回測中，稅務抵減會：
1. 增加配息月份的現金流入
2. 這些現金會被自動再投資
3. 長期累積可觀的複利效果

---

## 🔧 整合到現有系統

### 向後兼容
原有的 `app.py` 和 `engine.py` **無需修改主要邏輯**，因為：
- `MonthlyWealthCalculator` 的接口保持不變
- 只需要傳遞額外的 `year` 參數（已在 `engine.py` 自動添加）

### 新參數（可選）
```python
calculator = MonthlyWealthCalculator(
    # ... 原有參數
    dividend_tax_rate=2.11,      # 預設值
    dividend_credit_rate=8.5,    # [NEW] 預設值
)
```

---

## 📈 未來擴展性

### 稅務模組可擴展為：
- [ ] 綜合所得稅試算（不同級距）
- [ ] 分離課稅 vs 合併課稅比較
- [ ] 二代健保費用計算
- [ ] 海外股利扣抵

### 風險模組可擴展為：
- [ ] VaR (Value at Risk) 計算
- [ ] CVaR (Conditional VaR)
- [ ] 壓力測試情境
- [ ] 動態調整維持率策略

---

## 🎉 總結

### 完成度
- ✅ TaxCalculator 實作完成並測試通過
- ✅ RiskEngine 實作完成並測試通過
- ✅ MonthlyWealthCalculator 重構完成
- ✅ 新增稅務抵減功能（8.5%）
- ✅ 所有變更已提交到 GitHub

### 架構改善
1. **單一職責原則**：每個類別專注一項功能
2. **可測試性**：可獨立測試稅務和風險邏輯
3. **可擴展性**：易於添加新的稅務規則和風險指標
4. **可讀性**：代碼更清晰易懂

### 實際效益
- 稅務抵減為投資者帶來額外的正向現金流
- 更精確的風險管理計算
- 為進階功能（多資產、情境分析）奠定基礎

**Action 2 完成！準備好進入 Phase 3 和 Phase 4！** 🚀
