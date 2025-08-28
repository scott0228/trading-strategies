#!/usr/bin/env python3
"""
快速台股海龜策略測試程式
"""

import sys
import os

# 處理路徑問題
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tw_stock_utils import fetch_tw_stock_data, print_tw_summary
from strategies.turtle_strategy import TurtleStrategy
from backtest_engine import BacktestEngine


def quick_test_tw_stock(symbol: str, start_year: int = 2023, capital: int = 1000000):
    """快速測試台股海龜策略"""
    
    print(f"快速測試 {symbol} 海龜策略...")
    
    # 獲取資料
    data = fetch_tw_stock_data(symbol, start_year=start_year)
    
    if data.empty:
        print(f"無法獲取 {symbol} 資料")
        return
    
    # 建立策略和引擎
    strategy = TurtleStrategy(initial_capital=capital)
    engine = BacktestEngine(commission=0.001425)  # 台股手續費
    
    # 執行回測
    result = engine.run_backtest(strategy, data, symbol)
    
    # 顯示結果
    print_tw_summary(symbol, result)
    
    # 買入持有比較
    buy_hold = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
    strategy_return = result['performance']['total_return']
    
    print(f"\n策略 vs 買入持有:")
    print(f"海龜策略: {strategy_return:.2%}")
    print(f"買入持有: {buy_hold:.2%}")
    print(f"超額報酬: {strategy_return - buy_hold:.2%}")


if __name__ == "__main__":
    # 測試多個台股標的
    symbols = ["0050", "0056", "2330"]  # 台灣50, 高股息, 台積電
    
    for symbol in symbols:
        try:
            quick_test_tw_stock(symbol, start_year=2023)
            print("\n" + "="*60 + "\n")
        except Exception as e:
            print(f"{symbol} 測試失敗: {e}")
            continue