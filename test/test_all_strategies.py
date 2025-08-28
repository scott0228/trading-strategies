#!/usr/bin/env python3
"""
測試所有交易策略的完整功能
"""

import sys
import os

# 處理路徑問題
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pandas as pd
from utils import fetch_data
from strategies.sma_crossover import SMAcrossoverStrategy
from strategies.turtle_strategy import TurtleStrategy
from strategies.pullback_buy_strategy import PullbackBuyStrategy
from strategies.chu_chia_hung_strategy import ChuChiaHungStrategy
from backtest_engine import BacktestEngine


def test_strategy(strategy, data, symbol, engine):
    """測試單個策略"""
    try:
        print(f"  測試 {strategy.name}...")
        result = engine.run_backtest(strategy, data, symbol)
        
        perf = result['performance']
        signals_data = result['signals_data']
        
        # 檢查基本結果
        if 'total_return' not in perf:
            return False, "缺少 total_return 指標"
        
        if signals_data.empty:
            return False, "沒有產生訊號資料"
        
        # 統計交易訊號
        buy_signals = len(signals_data[signals_data['signal'] == 1])
        sell_signals = len(signals_data[signals_data['signal'] == -1])
        
        result_summary = {
            'total_return': perf['total_return'],
            'sharpe_ratio': perf.get('sharpe_ratio', 0),
            'max_drawdown': perf.get('max_drawdown', 0),
            'total_trades': perf.get('total_trades', 0),
            'buy_signals': buy_signals,
            'sell_signals': sell_signals
        }
        
        return True, result_summary
        
    except Exception as e:
        return False, str(e)


def test_all_strategies():
    """測試所有策略"""
    print("="*80)
    print("測試所有交易策略")
    print("="*80)
    
    # 準備測試資料
    symbols = ['SPY', 'AAPL']  # 測試多個標的
    period = '1y'
    
    # 創建策略列表
    strategies = [
        SMAcrossoverStrategy(name="SMA 20/50 交叉策略"),
        TurtleStrategy(name="海龜突破策略"),
        PullbackBuyStrategy(name="回撤買入策略"),
        ChuChiaHungStrategy(name="朱家泓策略")
    ]
    
    engine = BacktestEngine(initial_capital=100000, commission=0.001)
    
    all_results = {}
    
    for symbol in symbols:
        print(f"\n📊 測試標的: {symbol}")
        print("-" * 60)
        
        try:
            # 獲取資料
            data = fetch_data(symbol, period=period)
            if data.empty:
                print(f"❌ 無法獲取 {symbol} 資料")
                continue
            
            print(f"✅ 獲取 {len(data)} 筆 {symbol} 資料")
            
            symbol_results = {}
            
            for strategy in strategies:
                success, result = test_strategy(strategy, data, symbol, engine)
                
                if success:
                    symbol_results[strategy.name] = result
                    print(f"  ✅ {strategy.name}: {result['total_return']:.2%} 回報, "
                          f"{result['total_trades']} 交易")
                else:
                    print(f"  ❌ {strategy.name}: {result}")
            
            all_results[symbol] = symbol_results
            
        except Exception as e:
            print(f"❌ 測試 {symbol} 時發生錯誤: {e}")
            continue
    
    return all_results


def create_summary_report(results):
    """創建測試結果摘要報告"""
    
    if not results:
        print("❌ 沒有測試結果可供分析")
        return
    
    print(f"\n{'='*80}")
    print("測試結果摘要報告")
    print(f"{'='*80}")
    
    # 統計每個策略的表現
    strategy_stats = {}
    
    for symbol, symbol_results in results.items():
        for strategy_name, metrics in symbol_results.items():
            if strategy_name not in strategy_stats:
                strategy_stats[strategy_name] = []
            strategy_stats[strategy_name].append({
                'symbol': symbol,
                'return': metrics['total_return'],
                'sharpe': metrics['sharpe_ratio'],
                'trades': metrics['total_trades']
            })
    
    # 顯示各策略統計
    for strategy_name, stats in strategy_stats.items():
        print(f"\n🎯 {strategy_name}:")
        
        returns = [s['return'] for s in stats]
        sharpes = [s['sharpe'] for s in stats]
        trades = [s['trades'] for s in stats]
        
        if returns:
            avg_return = sum(returns) / len(returns)
            avg_sharpe = sum(sharpes) / len(sharpes)
            total_trades = sum(trades)
            
            print(f"  平均回報率: {avg_return:.2%}")
            print(f"  平均夏普比率: {avg_sharpe:.3f}")
            print(f"  總交易次數: {total_trades}")
            print(f"  測試標的數: {len(stats)}")
    
    # 找出最佳策略
    best_strategy = None
    best_avg_return = float('-inf')
    
    for strategy_name, stats in strategy_stats.items():
        returns = [s['return'] for s in stats]
        if returns:
            avg_return = sum(returns) / len(returns)
            if avg_return > best_avg_return:
                best_avg_return = avg_return
                best_strategy = strategy_name
    
    if best_strategy:
        print(f"\n🏆 最佳策略: {best_strategy}")
        print(f"   平均回報率: {best_avg_return:.2%}")


def create_detailed_table(results):
    """創建詳細的結果表格"""
    
    if not results:
        return
    
    print(f"\n{'='*100}")
    print("詳細結果表格")
    print(f"{'='*100}")
    
    # 表格標題
    headers = ['標的', '策略', '總回報(%)', '夏普比率', '最大回撤(%)', '交易次數']
    header_line = f"{'標的':<8} {'策略':<20} {'總回報(%)':<12} {'夏普比率':<10} {'最大回撤(%)':<12} {'交易次數':<8}"
    print(header_line)
    print("-" * len(header_line))
    
    for symbol, symbol_results in results.items():
        for strategy_name, metrics in symbol_results.items():
            row = f"{symbol:<8} {strategy_name:<20} {metrics['total_return']:>10.2%} " \
                  f"{metrics['sharpe_ratio']:>9.3f} {metrics['max_drawdown']:>10.2%} " \
                  f"{metrics['total_trades']:>7d}"
            print(row)


def main():
    """主測試函數"""
    
    try:
        # 執行所有策略測試
        results = test_all_strategies()
        
        if results:
            # 創建摘要報告
            create_summary_report(results)
            
            # 創建詳細表格
            create_detailed_table(results)
            
            print(f"\n🎉 策略測試完成!")
            return True
        else:
            print("❌ 沒有成功的測試結果")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
        sys.exit(1)