"""
AI Advisor API Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from data.fetcher import get_etf_options

router = APIRouter()


class AdvisorRequest(BaseModel):
    age: int
    risk_level: str  # "保守", "穩健", "積極"
    goal: str  # "退休", "買房", "存第一桶金"
    monthly_savings: float


@router.post("/recommend")
def get_recommendation(request: AdvisorRequest):
    """取得 AI 投資建議"""
    
    # 計算投資期限
    if request.goal == "退休":
        investment_horizon = max(65 - request.age, 5)
    elif request.goal == "買房":
        investment_horizon = 10 if request.age < 35 else 7
    else:
        investment_horizon = 5
    
    portfolio = {}
    use_leverage = False
    ltv = 0
    strategy_name = ""
    description = ""
    
    # 積極型策略
    if "積極" in request.risk_level:
        if request.age < 35:
            portfolio = {"0050": 70, "0056": 20, "00919": 10}
            use_leverage = True
            ltv = 50
            strategy_name = "🚀 積極成長型"
            description = "年輕且風險承受度高，適合追求成長。70% 市值型 + 30% 高股息，並使用適度槓桿。"
        elif request.age < 50:
            portfolio = {"0050": 60, "0056": 30, "00878": 10}
            use_leverage = True
            ltv = 40
            strategy_name = "⚡ 成長平衡型"
            description = "追求成長但需兼顧風險控制。60% 市值型 + 40% 高股息，適度槓桿。"
        else:
            portfolio = {"0050": 40, "0056": 40, "00878": 20}
            use_leverage = False
            strategy_name = "🎯 穩健積極型"
            description = "年齡較高，建議降低風險。40% 市值型 + 60% 高股息，不使用槓桿。"
    
    # 穩健型策略
    elif "穩健" in request.risk_level:
        if request.age < 40:
            portfolio = {"0050": 50, "0056": 30, "00878": 20}
            strategy_name = "⚖️ 均衡配置型"
            description = "平衡成長與穩定的經典配置。50% 市值型 + 50% 高股息。"
        else:
            portfolio = {"0050": 30, "0056": 40, "00878": 30}
            strategy_name = "🛡️ 防禦穩健型"
            description = "偏重高股息，降低波動。30% 市值型 + 70% 高股息。"
    
    # 保守型策略
    else:
        if request.goal == "退休" or request.age > 50:
            portfolio = {"0056": 50, "00878": 50}
            strategy_name = "🏰 保守收息型"
            description = "極度保守，重視資本保全。100% 高股息 ETF。"
        else:
            portfolio = {"0050": 30, "0056": 40, "00878": 30}
            strategy_name = "🌱 保守成長型"
            description = "保守但保留適度成長空間。30% 市值型 + 70% 高股息。"
    
    # 短期投資取消槓桿
    if investment_horizon < 5 and use_leverage:
        use_leverage = False
        ltv = 0
        description += " 由於投資期限較短，已取消槓桿建議。"
    
    # 計算預期報酬
    etf_options = get_etf_options()
    avg_yield = np.average(
        [etf_options[etf]["yield"] for etf in portfolio.keys()],
        weights=[portfolio[etf] for etf in portfolio.keys()]
    )
    
    market_return = 8.0
    if use_leverage:
        expected_return = market_return * (1 + ltv / 100) - (ltv / 100 * 6.5)
    else:
        expected_return = market_return
    
    # 計算預期財富
    years = investment_horizon
    monthly = request.monthly_savings
    annual_return = expected_return / 100
    months = years * 12
    monthly_return = (1 + annual_return) ** (1/12) - 1
    
    future_value = 0.0
    for _ in range(months):
        future_value = (future_value + monthly) * (1 + monthly_return)
    
    total_contribution = monthly * months
    
    return {
        "success": True,
        "data": {
            "strategy_name": strategy_name,
            "portfolio": portfolio,
            "use_leverage": use_leverage,
            "ltv": ltv,
            "investment_horizon": investment_horizon,
            "expected_return": round(expected_return, 1),
            "avg_dividend_yield": round(avg_yield, 1),
            "description": description,
            "projected_wealth": {
                "total_contribution": round(total_contribution),
                "final_wealth": round(future_value),
                "profit": round(future_value - total_contribution)
            }
        }
    }
