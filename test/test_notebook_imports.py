#!/usr/bin/env python3
"""
測試和修正 Jupyter Notebook 的 import 問題
"""

import sys
import os

# 處理路徑問題 - 無論從哪裡執行都能正確找到模組
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_basic_imports():
    """測試基本模組 import"""
    print("1. 測試基本模組...")
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        print("✅ 數據處理模組正常")
        return True
    except ImportError as e:
        print(f"❌ 基本模組 import 失敗: {e}")
        return False


def test_strategy_imports():
    """測試策略模組 import"""
    print("\n2. 測試策略模組...")
    
    try:
        from strategies.sma_crossover import SMAcrossoverStrategy
        from strategies.turtle_strategy import TurtleStrategy
        from strategies.pullback_buy_strategy import PullbackBuyStrategy
        from strategies.chu_chia_hung_strategy import ChuChiaHungStrategy
        print("✅ 策略模組正常")
        return True
    except ImportError as e:
        print(f"❌ 策略模組 import 失敗: {e}")
        return False


def test_core_modules():
    """測試核心模組 import"""
    print("\n3. 測試核心模組...")
    
    try:
        from backtest_engine import BacktestEngine
        from utils import fetch_data, print_strategy_summary
        from config.config import DEFAULT_SYMBOLS, get_config
        print("✅ 核心模組正常")
        return True
    except ImportError as e:
        print(f"❌ 核心模組 import 失敗: {e}")
        return False


def test_tw_modules():
    """測試台股模組 import"""
    print("\n4. 測試台股模組...")
    
    try:
        from tw_stock_utils import fetch_tw_stock_data, print_tw_summary
        print("✅ 台股模組正常")
        return True
    except ImportError as e:
        print(f"❌ 台股模組 import 失敗: {e}")
        return False


def test_strategy_creation():
    """測試策略實例化"""
    print("\n5. 測試策略創建...")
    
    try:
        from strategies.sma_crossover import SMAcrossoverStrategy
        from strategies.turtle_strategy import TurtleStrategy
        from strategies.pullback_buy_strategy import PullbackBuyStrategy
        from strategies.chu_chia_hung_strategy import ChuChiaHungStrategy
        
        strategies = [
            ("SMA 交叉策略", SMAcrossoverStrategy(name="測試SMA")),
            ("海龜策略", TurtleStrategy(name="測試海龜")),
            ("回撤買上漲策略", PullbackBuyStrategy(name="測試回撤")),
            ("朱家泓策略", ChuChiaHungStrategy(name="測試朱家泓"))
        ]
        
        for name, strategy in strategies:
            print(f"  ✅ {name}: {strategy.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 策略創建失敗: {e}")
        return False


def test_full_workflow():
    """測試完整工作流程"""
    print("\n6. 測試完整回測流程...")
    
    try:
        from utils import fetch_data
        from strategies.turtle_strategy import TurtleStrategy
        from backtest_engine import BacktestEngine
        
        # 獲取少量資料測試
        data = fetch_data('SPY', period='3mo')  # 只獲取3個月資料
        if data.empty:
            print("❌ 無法獲取測試資料")
            return False
        
        # 創建策略和引擎
        strategy = TurtleStrategy(name="測試海龜", initial_capital=100000)
        engine = BacktestEngine()
        
        # 執行回測
        result = engine.run_backtest(strategy, data, 'SPY')
        
        perf = result['performance']
        print(f"  ✅ 回測成功: {perf['total_return']:.2%} 回報")
        return True
        
    except Exception as e:
        print(f"❌ 完整流程測試失敗: {e}")
        return False


def create_notebook_template():
    """創建正確的 notebook 程式碼模板"""
    
    template = '''# 修正後的 Notebook Import 模板

# 1. 基本設定
import sys
import os
sys.path.append('..')  # 重要：添加上層目錄到路徑

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 2. 正確的策略 Import
from strategies.sma_crossover import SMAcrossoverStrategy  # 注意：不是 SmaCrossover
from strategies.turtle_strategy import TurtleStrategy
from strategies.pullback_buy_strategy import PullbackBuyStrategy
from strategies.chu_chia_hung_strategy import ChuChiaHungStrategy

# 3. 核心模組
from backtest_engine import BacktestEngine
from utils import fetch_data, print_strategy_summary
from config.config import DEFAULT_SYMBOLS, get_config

# 4. 台股模組（可選）
from tw_stock_utils import fetch_tw_stock_data, print_tw_summary

# 5. 測試策略創建
print("測試策略創建...")
sma_strategy = SMAcrossoverStrategy(name="SMA 測試")
turtle_strategy = TurtleStrategy(name="海龜測試")
print("✅ 策略創建成功")

# 6. 簡單回測範例
symbol = 'AAPL'
data = fetch_data(symbol, period='6mo')
engine = BacktestEngine()
result = engine.run_backtest(turtle_strategy, data, symbol)
print(f"✅ {symbol} 回測完成: {result['performance']['total_return']:.2%}")
'''
    
    return template


def main():
    """主要測試函數"""
    print("="*60)
    print("Jupyter Notebook Import 測試")
    print("="*60)
    
    tests = [
        test_basic_imports,
        test_strategy_imports, 
        test_core_modules,
        test_tw_modules,
        test_strategy_creation,
        test_full_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "="*60)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！Notebook 應該可以正常運行")
        print("\n正確的 Notebook Import 模板:")
        print("-" * 40)
        print(create_notebook_template())
    else:
        print("❌ 部分測試失敗，請檢查問題並修正")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n測試過程發生錯誤: {e}")
        sys.exit(1)