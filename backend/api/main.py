"""
SmartWealth AI - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import etf, backtest, advisor, simulation

app = FastAPI(
    title="SmartWealth AI API",
    description="台股 ETF 投資分析 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "SmartWealth AI API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 註冊路由
app.include_router(etf.router, prefix="/api/v1/etf", tags=["ETF"])
app.include_router(backtest.router, prefix="/api/v1/backtest", tags=["Backtest"])
app.include_router(advisor.router, prefix="/api/v1/advisor", tags=["Advisor"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
