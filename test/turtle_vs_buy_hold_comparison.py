#!/usr/bin/env python3
"""
海龜策略與買進持有策略五年回測比較
比較股票: CRWD, QQQ, ARKK, ARKW, AAPL, MSFT, GOOGL
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import fetch_data
from strategies.turtle_strategy import TurtleStrategy
from strategies.buy_and_hold_strategy import BuyAndHoldStrategy
from backtest_engine import BacktestEngine


def run_strategy_comparison():
    """執行海龜策略與買進持有策略的比較回測"""
    
    # 股票清單
    symbols = ['CRWD', 'QQQ', 'ARKK', 'ARKW', 'AAPL', 'MSFT', 'GOOGL']
    
    # 設定回測期間（五年）
    period = '5y'
    initial_capital = 100000
    
    # 結果儲存
    results = []
    
    print(f"開始進行五年回測比較 ({len(symbols)} 支股票)")
    print("=" * 80)
    
    for symbol in symbols:
        print(f"\n正在回測 {symbol}...")
        
        try:
            # 獲取數據
            data = fetch_data(symbol, period=period)
            
            if data is None or len(data) < 100:
                print(f"警告: {symbol} 數據不足，跳過")
                continue
            
            # 初始化策略
            turtle_strategy = TurtleStrategy(initial_capital=initial_capital)
            buy_hold_strategy = BuyAndHoldStrategy(initial_capital=initial_capital)
            
            # 初始化回測引擎
            engine = BacktestEngine()
            
            # 執行海龜策略回測
            turtle_result = engine.run_backtest(turtle_strategy, data, symbol)
            
            # 執行買進持有策略回測
            buy_hold_result = engine.run_backtest(buy_hold_strategy, data, symbol)
            
            # 計算買進持有基準
            start_price = data.iloc[0]['Close']
            end_price = data.iloc[-1]['Close']
            buy_hold_return = (end_price - start_price) / start_price
            
            # 整理結果
            turtle_perf = turtle_result['performance']
            buy_hold_perf = buy_hold_result['performance']
            
            result_row = {
                'Symbol': symbol,
                'Turtle_Total_Return': turtle_perf['total_return'],
                'Turtle_Annual_Return': turtle_perf['annualized_return'],
                'Turtle_Sharpe': turtle_perf['sharpe_ratio'],
                'Turtle_Max_DD': turtle_perf['max_drawdown'],
                'Turtle_Trades': turtle_perf['total_trades'],
                'BuyHold_Total_Return': buy_hold_perf['total_return'],
                'BuyHold_Annual_Return': buy_hold_perf['annualized_return'],
                'BuyHold_Sharpe': buy_hold_perf['sharpe_ratio'],
                'BuyHold_Max_DD': buy_hold_perf['max_drawdown'],
                'BuyHold_Trades': buy_hold_perf['total_trades'],
                'Outperformance': turtle_perf['total_return'] - buy_hold_perf['total_return'],
                'Data_Points': len(data)
            }
            
            results.append(result_row)
            
            print(f"✓ {symbol} 完成 - 海龜: {turtle_perf['total_return']:.2%}, 買進持有: {buy_hold_perf['total_return']:.2%}")
            
        except Exception as e:
            print(f"✗ {symbol} 錯誤: {str(e)}")
            continue
    
    # 轉換為 DataFrame
    if not results:
        print("沒有成功的回測結果")
        return None
    
    results_df = pd.DataFrame(results)
    
    return results_df


def print_comparison_results(results_df):
    """打印比較結果"""
    if results_df is None or len(results_df) == 0:
        print("沒有結果可以顯示")
        return
    
    print("\n" + "=" * 100)
    print("海龜策略 vs 買進持有策略 - 五年回測比較結果")
    print("=" * 100)
    
    # 績效比較表格
    print(f"\n{'股票':<8} {'海龜總報酬':<12} {'買進持有總報酬':<15} {'超額報酬':<12} {'海龜夏普':<10} {'買進持有夏普':<12}")
    print("-" * 85)
    
    for _, row in results_df.iterrows():
        print(f"{row['Symbol']:<8} {row['Turtle_Total_Return']:<12.2%} "
              f"{row['BuyHold_Total_Return']:<15.2%} {row['Outperformance']:<12.2%} "
              f"{row['Turtle_Sharpe']:<10.2f} {row['BuyHold_Sharpe']:<12.2f}")
    
    # 統計摘要
    print("\n" + "=" * 50)
    print("統計摘要")
    print("=" * 50)
    
    turtle_wins = sum(results_df['Outperformance'] > 0)
    total_stocks = len(results_df)
    
    print(f"總計股票數: {total_stocks}")
    print(f"海龜策略勝出: {turtle_wins} ({turtle_wins/total_stocks:.1%})")
    print(f"買進持有勝出: {total_stocks - turtle_wins} ({(total_stocks-turtle_wins)/total_stocks:.1%})")
    
    print(f"\n平均績效:")
    print(f"海龜策略平均總報酬: {results_df['Turtle_Total_Return'].mean():.2%}")
    print(f"買進持有平均總報酬: {results_df['BuyHold_Total_Return'].mean():.2%}")
    print(f"平均超額報酬: {results_df['Outperformance'].mean():.2%}")
    
    print(f"\n風險指標:")
    print(f"海龜策略平均最大回撤: {results_df['Turtle_Max_DD'].mean():.2%}")
    print(f"買進持有平均最大回撤: {results_df['BuyHold_Max_DD'].mean():.2%}")
    
    print(f"\n海龜策略平均交易次數: {results_df['Turtle_Trades'].mean():.1f}")


def save_results_to_csv(results_df, filename=None):
    """儲存結果到 CSV 檔案"""
    if results_df is None:
        return
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"turtle_vs_buyhold_comparison_{timestamp}.csv"
    
    results_df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n結果已儲存至: {filename}")


def main():
    """主函數"""
    print("開始執行海龜策略與買進持有策略比較")
    
    # 執行回測比較
    results = run_strategy_comparison()
    
    if results is not None:
        # 打印結果
        print_comparison_results(results)
        
        # 儲存結果
        save_results_to_csv(results)
        
        print(f"\n回測完成! 共比較了 {len(results)} 支股票")
    else:
        print("回測失敗，沒有產生結果")


if __name__ == "__main__":
    main()