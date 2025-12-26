"""
Monte Carlo Simulation API Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Optional, List
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from simulation.monte_carlo import MonteCarloSimulator
from data.fetcher import get_etf_options

router = APIRouter()


class SimulationRequest(BaseModel):
    portfolio: Dict[str, float] = {"0050": 100}
    initial_capital: float = 1000000
    monthly_contribution: float = 20000
    years: int = 10
    num_simulations: int = 1000
    mu: float = 0.08  # 預期年化報酬率
    sigma: float = 0.15  # 年化波動度


@router.post("/monte-carlo")
def run_monte_carlo(request: SimulationRequest):
    """執行蒙地卡羅模擬"""
    try:
        # 驗證參數
        if request.num_simulations > 5000:
            return {"success": False, "error": "Max simulations is 5000"}
        
        if request.years > 30:
            return {"success": False, "error": "Max years is 30"}
        
        # 建立模擬器
        simulator = MonteCarloSimulator(
            mu=request.mu,
            sigma=request.sigma,
            initial_capital=request.initial_capital,
            years=request.years,
            num_simulations=request.num_simulations,
            monthly_contribution=request.monthly_contribution,
            random_seed=42
        )
        
        # 執行簡化模擬
        results = simulator.simulate_simple()
        
        # 分析結果
        stats = simulator.analyze_results(results, "Final_Wealth")
        percentiles = stats["percentiles"]
        
        # 計算虧損機率
        total_contribution = request.initial_capital + request.monthly_contribution * request.years * 12
        loss_probability = float((results["Final_Wealth"] < total_contribution).mean() * 100)
        
        # 生成部分路徑樣本用於圖表（最多 50 條）
        sample_count = min(50, request.num_simulations)
        sample_simulator = MonteCarloSimulator(
            mu=request.mu,
            sigma=request.sigma,
            initial_capital=request.initial_capital,
            years=request.years,
            num_simulations=sample_count,
            monthly_contribution=request.monthly_contribution,
            random_seed=42
        )
        
        returns = sample_simulator.generate_return_paths()
        months = request.years * 12
        
        wealth_paths = np.zeros((sample_count, months + 1))
        wealth_paths[:, 0] = request.initial_capital
        
        for sim in range(sample_count):
            wealth = request.initial_capital
            for month in range(months):
                wealth *= (1 + returns[sim, month])
                wealth += request.monthly_contribution
                wealth_paths[sim, month + 1] = wealth
        
        # 計算百分位數路徑
        time_points = list(range(0, months + 1, max(1, months // 20)))  # 最多 20 個點
        p5_path = [float(np.percentile(wealth_paths[:, t], 5)) for t in time_points]
        p50_path = [float(np.percentile(wealth_paths[:, t], 50)) for t in time_points]
        p95_path = [float(np.percentile(wealth_paths[:, t], 95)) for t in time_points]
        
        # 取得摘要表
        summary_table = simulator.get_summary_table(results, "Final_Wealth")
        
        return {
            "success": True,
            "data": {
                "percentiles": {
                    "p5": float(percentiles["P5"]),
                    "p25": float(percentiles["P25"]),
                    "p50": float(percentiles["P50"]),
                    "p75": float(percentiles["P75"]),
                    "p95": float(percentiles["P95"])
                },
                "statistics": {
                    "mean": float(stats["mean"]),
                    "std": float(stats["std"]),
                    "min": float(stats["min"]),
                    "max": float(stats["max"]),
                    "loss_probability": loss_probability,
                    "total_contribution": total_contribution
                },
                "paths": {
                    "time_points": [t / 12 for t in time_points],  # 轉為年
                    "p5": p5_path,
                    "p50": p50_path,
                    "p95": p95_path
                },
                "summary_table": summary_table.to_dict(orient="records")
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
