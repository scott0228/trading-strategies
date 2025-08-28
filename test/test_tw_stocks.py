#!/usr/bin/env python3
"""
台股交易策略測試程式
"""

import sys
import os

# 處理路徑問題
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tw_stock_utils import fetch_tw_stock_data, get_tw_stock_info, print_tw_summary
from strategies.turtle_strategy import TurtleStrategy
from strategies.sma_crossover import SMAcrossoverStrategy
from backtest_engine import BacktestEngine


def test_tw_data_fetch():
    """測試台股資料獲取"""
    print("測試台股資料獲取...")
    
    test_symbols = ['0050', '006208', '2330']
    
    for symbol in test_symbols:
        try:
            print(f"  測試 {symbol}...")
            
            # 獲取股票資訊
            info = get_tw_stock_info(symbol)
            print(f"    ✅ 基本資訊: {info['name']}")
            
            # 獲取資料
            data = fetch_tw_stock_data(symbol, start_year=2023)
            if not data.empty:
                print(f"    ✅ 資料獲取: {len(data)} 筆記錄")
                print(f"    📊 價格範圍: NT${data['Low'].min():.2f} - NT${data['High'].max():.2f}")
            else:
                print(f"    ❌ 無法獲取資料")
                
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")


def test_tw_strategy(symbol, strategy_name="海龜策略"):
    """測試單個台股策略"""
    try:
        print(f"\n🎯 測試 {symbol} - {strategy_name}")
        
        # 獲取資料
        data = fetch_tw_stock_data(symbol, start_year=2023)
        if data.empty:
            print(f"❌ 無法獲取 {symbol} 資料")
            return None
        
        # 創建策略
        if strategy_name == "海龜策略":
            strategy = TurtleStrategy(initial_capital=1000000)
        elif strategy_name == "SMA策略":
            strategy = SMAcrossoverStrategy(initial_capital=1000000)
        else:
            strategy = TurtleStrategy(initial_capital=1000000)
        
        # 執行回測
        engine = BacktestEngine(commission=0.001425)  # 台股手續費
        result = engine.run_backtest(strategy, data, symbol)
        
        # 顯示結果
        print_tw_summary(symbol, result)
        
        # 與買入持有比較
        buy_hold = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
        strategy_return = result['performance']['total_return']
        
        print(f"\n📈 績效比較:")
        print(f"   {strategy_name}: {strategy_return:.2%}")
        print(f"   買入持有: {buy_hold:.2%}")
        print(f"   超額報酬: {strategy_return - buy_hold:.2%}")
        
        return result
        
    except Exception as e:
        print(f"❌ 測試 {symbol} 失敗: {e}")
        return None


def test_tw_etf_comparison():
    """比較台股ETF表現"""
    print(f"\n{'='*80}")
    print("台股 ETF 策略比較")
    print(f"{'='*80}")
    
    etfs = {
        '0050': '元大台灣50',
        '006208': '富邦台50'
    }
    
    results = {}
    
    for symbol, name in etfs.items():
        print(f"\n📊 測試 {symbol} ({name})")
        result = test_tw_strategy(symbol, "海龜策略")
        if result:
            results[symbol] = result['performance']
    
    # 比較結果
    if len(results) >= 2:
        print(f"\n🆚 ETF 比較結果:")
        print(f"{'項目':<15} {'0050':<15} {'006208':<15} {'勝出':<10}")
        print("-" * 60)
        
        metrics = [
            ('總回報率', 'total_return'),
            ('夏普比率', 'sharpe_ratio'),
            ('最大回撤', 'max_drawdown'),
            ('交易次數', 'total_trades')
        ]
        
        for metric_name, key in metrics:
            if key in results['0050'] and key in results['006208']:
                val_0050 = results['0050'][key]
                val_006208 = results['006208'][key]
                
                if key == 'max_drawdown':  # 回撤越小越好
                    winner = "0050" if val_0050 < val_006208 else "006208"
                else:
                    winner = "0050" if val_0050 > val_006208 else "006208"
                
                if key in ['total_return', 'max_drawdown']:
                    print(f"{metric_name:<15} {val_0050:<14.2%} {val_006208:<14.2%} {winner:<10}")
                elif key == 'sharpe_ratio':
                    print(f"{metric_name:<15} {val_0050:<14.3f} {val_006208:<14.3f} {winner:<10}")
                else:
                    print(f"{metric_name:<15} {val_0050:<14} {val_006208:<14} {winner:<10}")


def test_popular_tw_stocks():
    """測試熱門台股"""
    print(f"\n{'='*80}")
    print("熱門台股策略測試")
    print(f"{'='*80}")
    
    popular_stocks = {
        '2330': '台積電',
        '2317': '鴻海',
        '2454': '聯發科'
    }
    
    results = {}
    
    for symbol, name in popular_stocks.items():
        print(f"\n📱 測試 {symbol} ({name})")
        try:
            result = test_tw_strategy(symbol, "海龜策略")
            if result:
                results[symbol] = result['performance']
        except Exception as e:
            print(f"❌ 測試 {symbol} 失敗: {e}")
    
    # 顯示摘要
    if results:
        print(f"\n📋 熱門台股摘要:")
        print(f"{'代號':<8} {'名稱':<10} {'總回報':<12} {'交易次數':<8} {'夏普比率':<10}")
        print("-" * 55)
        
        for symbol, perf in results.items():
            name = popular_stocks.get(symbol, symbol)
            print(f"{symbol:<8} {name:<10} {perf['total_return']:<11.2%} "
                  f"{perf['total_trades']:<8} {perf.get('sharpe_ratio', 0):<9.3f}")


def main():
    """主測試函數"""
    print("="*80)
    print("台股交易策略完整測試")
    print("="*80)
    
    try:
        # 1. 測試資料獲取
        test_tw_data_fetch()
        
        # 2. 測試 ETF 比較
        test_tw_etf_comparison()
        
        # 3. 測試熱門個股
        test_popular_tw_stocks()
        
        print(f"\n🎉 台股策略測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 台股測試發生錯誤: {e}")
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