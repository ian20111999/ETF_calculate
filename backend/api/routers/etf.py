"""
ETF API Router
"""
from fastapi import APIRouter
from typing import Optional
import sys
import os

# 確保可以導入 core 和 data 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from data.fetcher import get_etf_options, get_current_price

router = APIRouter()


@router.get("/")
def get_all_etfs():
    """取得所有支援的 ETF 資訊"""
    etf_options = get_etf_options()
    return {
        "success": True,
        "data": etf_options
    }


@router.get("/{symbol}")
def get_etf_detail(symbol: str):
    """取得單一 ETF 詳細資訊"""
    etf_options = get_etf_options()
    
    if symbol not in etf_options:
        return {
            "success": False,
            "error": f"ETF {symbol} not found"
        }
    
    return {
        "success": True,
        "data": etf_options[symbol]
    }


@router.get("/{symbol}/price")
def get_etf_price(symbol: str):
    """取得 ETF 當前價格"""
    etf_options = get_etf_options()
    
    if symbol not in etf_options:
        return {
            "success": False,
            "error": f"ETF {symbol} not found"
        }
    
    yahoo_symbol = etf_options[symbol]["yahoo_symbol"]
    price = get_current_price(yahoo_symbol)
    
    if price is None:
        return {
            "success": False,
            "error": f"Unable to fetch price for {symbol}"
        }
    
    return {
        "success": True,
        "data": {
            "symbol": symbol,
            "yahoo_symbol": yahoo_symbol,
            "price": price
        }
    }
