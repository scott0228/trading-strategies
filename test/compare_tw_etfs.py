#!/usr/bin/env python3
"""
比較台股 ETF 海龜策略表現
0050 vs 006208
"""

import sys
import os

# 處理路徑問題
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pandas as pd
from tw_stock_utils import fetch_tw_stock_data, get_tw_stock_info
from strategies.turtle_strategy import TurtleStrategy
from backtest_engine import BacktestEngine


def compare_tw_etfs():
    """比較台股 ETF 的海龜策略表現"""
    
    etfs = {
        '0050': '元大台灣50',
        '006208': '富邦台50'
    }
    
    results = {}
    
    print("="*80)
    print("台股 ETF 海龜策略比較分析")
    print("="*80)
    
    for symbol, name in etfs.items():
        print(f"\n處理 {symbol} - {name}...")
        
        try:
            # 獲取資料
            data = fetch_tw_stock_data(symbol, start_year=2022)
            
            if data.empty:
                print(f"❌ {symbol} 無法獲取資料")
                continue
            
            # 執行回測
            strategy = TurtleStrategy(initial_capital=1000000)
            engine = BacktestEngine(commission=0.001425)
            result = engine.run_backtest(strategy, data, symbol)
            
            # 計算買入持有報酬
            buy_hold_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
            
            # 儲存結果
            results[symbol] = {
                'name': name,
                'data_points': len(data),
                'period': f"{data.index.min().strftime('%Y-%m-%d')} 至 {data.index.max().strftime('%Y-%m-%d')}",
                'price_range': f"NT$ {data['Low'].min():.2f} - {data['High'].max():.2f}",
                'current_price': data['Close'].iloc[-1],
                'strategy_return': result['performance']['total_return'],
                'buy_hold_return': buy_hold_return,
                'excess_return': result['performance']['total_return'] - buy_hold_return,
                'sharpe_ratio': result['performance']['sharpe_ratio'],
                'max_drawdown': result['performance']['max_drawdown'],
                'total_trades': result['performance']['total_trades'],
                'final_capital': result['performance'].get('final_capital', 0),
                'annualized_return': result['performance']['annualized_return'],
                'volatility': result['performance']['volatility']
            }
            
            print(f"✅ {symbol} 處理完成")
            
        except Exception as e:
            print(f"❌ {symbol} 處理失敗: {e}")
            continue
    
    # 顯示比較結果
    print(f"\n{'='*80}")
    print("詳細比較結果")
    print(f"{'='*80}")
    
    if len(results) >= 2:
        # 建立比較表格
        df_comparison = pd.DataFrame.from_dict(results, orient='index')
        
        print(f"\n📊 基本資訊比較:")
        print(f"{'項目':<15} {'0050':<20} {'006208':<20}")
        print("-" * 55)
        for symbol in results.keys():
            if symbol in df_comparison.index:
                r = results[symbol]
                print(f"{'全名':<15} {r['name']:<20}")
                print(f"{'資料點數':<15} {r['data_points']:<20}")
                print(f"{'當前股價':<15} NT$ {r['current_price']:<17.2f}")
                print(f"{'價格範圍':<15} {r['price_range']:<20}")
                print()
                break
        
        print(f"📈 績效比較:")
        metrics = [
            ('海龜策略報酬', 'strategy_return', '%'),
            ('買入持有報酬', 'buy_hold_return', '%'),
            ('超額報酬', 'excess_return', '%'),
            ('年化報酬', 'annualized_return', '%'),
            ('夏普比率', 'sharpe_ratio', ''),
            ('最大回撤', 'max_drawdown', '%'),
            ('波動率', 'volatility', '%'),
            ('交易次數', 'total_trades', '次'),
            ('最終資本', 'final_capital', 'NT$')
        ]
        
        print(f"{'指標':<15} {'0050':<20} {'006208':<20} {'勝出':<10}")
        print("-" * 70)
        
        for metric_name, metric_key, unit in metrics:
            if all(symbol in results and metric_key in results[symbol] for symbol in ['0050', '006208']):
                val_0050 = results['0050'][metric_key]
                val_006208 = results['006208'][metric_key]
                
                if unit == '%':
                    str_0050 = f"{val_0050:.2%}"
                    str_006208 = f"{val_006208:.2%}"
                elif unit == 'NT$':
                    str_0050 = f"NT$ {val_0050:,.0f}"
                    str_006208 = f"NT$ {val_006208:,.0f}"
                elif metric_key == 'total_trades':
                    str_0050 = f"{val_0050} 次"
                    str_006208 = f"{val_006208} 次"
                else:
                    str_0050 = f"{val_0050:.3f}"
                    str_006208 = f"{val_006208:.3f}"
                
                # 判斷勝出者 (注意回撤越小越好)
                if metric_key == 'max_drawdown':
                    winner = "0050" if val_0050 < val_006208 else "006208"
                else:
                    winner = "0050" if val_0050 > val_006208 else "006208"
                
                print(f"{metric_name:<15} {str_0050:<20} {str_006208:<20} {winner:<10}")
        
        print(f"\n🏆 總結:")
        if results['0050']['strategy_return'] > results['006208']['strategy_return']:
            print(f"• 海龜策略報酬：0050 勝出 ({results['0050']['strategy_return']:.2%} vs {results['006208']['strategy_return']:.2%})")
        else:
            print(f"• 海龜策略報酬：006208 勝出 ({results['006208']['strategy_return']:.2%} vs {results['0050']['strategy_return']:.2%})")
        
        if results['0050']['sharpe_ratio'] > results['006208']['sharpe_ratio']:
            print(f"• 風險調整報酬：0050 勝出 (夏普比率 {results['0050']['sharpe_ratio']:.3f} vs {results['006208']['sharpe_ratio']:.3f})")
        else:
            print(f"• 風險調整報酬：006208 勝出 (夏普比率 {results['006208']['sharpe_ratio']:.3f} vs {results['0050']['sharpe_ratio']:.3f})")
            
        if results['0050']['max_drawdown'] < results['006208']['max_drawdown']:
            print(f"• 風險控制：0050 勝出 (最大回撤 {results['0050']['max_drawdown']:.2%} vs {results['006208']['max_drawdown']:.2%})")
        else:
            print(f"• 風險控制：006208 勝出 (最大回撤 {results['006208']['max_drawdown']:.2%} vs {results['0050']['max_drawdown']:.2%})")
    
    else:
        print("❌ 無法進行比較，需要至少兩個有效結果")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    compare_tw_etfs()