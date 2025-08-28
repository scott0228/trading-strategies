#!/usr/bin/env python3
"""
台股 0050 ETF 海龜交易策略回測程式

使用 twstock 獲取台股資料，應用海龜交易策略進行回測分析。
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 匯入自製模組
from tw_stock_utils import fetch_tw_stock_data, get_tw_stock_info, print_tw_summary
from strategies.turtle_strategy import TurtleStrategy
from backtest_engine import BacktestEngine


def main():
    """主要執行函數"""
    
    print("="*80)
    print("台股 0050 ETF 海龜交易策略回測系統")
    print("="*80)
    
    # 設定參數
    symbol = "0050"
    initial_capital = 1000000  # 100萬台幣
    
    # 獲取 0050 基本資訊
    stock_info = get_tw_stock_info(symbol)
    print(f"標的：{symbol} - {stock_info.get('name', '元大台灣50')}")
    
    # 步驟 1: 獲取資料
    print("\n步驟 1: 獲取台股資料")
    print("-" * 40)
    
    try:
        # 獲取近 3 年資料 (2022-2025)
        data = fetch_tw_stock_data(symbol, start_year=2022, start_month=1)
        
        if data.empty:
            print("❌ 無法獲取資料，程式結束")
            return
            
        print(f"✅ 成功獲取 {len(data)} 筆交易日資料")
        
        # 顯示資料基本統計
        print(f"\n資料統計摘要:")
        print(f"期間：{data.index.min().strftime('%Y-%m-%d')} 至 {data.index.max().strftime('%Y-%m-%d')}")
        print(f"最高價：NT$ {data['High'].max():.2f}")
        print(f"最低價：NT$ {data['Low'].min():.2f}")
        print(f"最新收盤價：NT$ {data['Close'].iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"❌ 資料獲取失敗: {e}")
        return
    
    # 步驟 2: 設定策略參數
    print(f"\n步驟 2: 設定海龜策略參數")
    print("-" * 40)
    
    # 根據台股特性調整參數
    turtle_strategy = TurtleStrategy(
        name="台股海龜策略",
        entry_window=20,        # 20日突破
        exit_window=10,         # 10日出場  
        atr_window=20,          # ATR 期間
        stop_loss_multiplier=2.0,  # 2倍ATR止損
        initial_capital=initial_capital
    )
    
    print(f"✅ 策略設定完成")
    print(f"   進場窗口: {turtle_strategy.entry_window} 日")
    print(f"   出場窗口: {turtle_strategy.exit_window} 日")
    print(f"   止損倍數: {turtle_strategy.stop_loss_multiplier} 倍ATR")
    print(f"   初始資本: NT$ {initial_capital:,}")
    
    # 步驟 3: 執行回測
    print(f"\n步驟 3: 執行回測")
    print("-" * 40)
    
    try:
        # 建立回測引擎
        engine = BacktestEngine(
            initial_capital=initial_capital,
            commission=0.001425  # 台股手續費約 0.1425%
        )
        
        print("⏳ 正在執行回測...")
        
        # 執行回測
        result = engine.run_backtest(turtle_strategy, data, symbol)
        
        print("✅ 回測執行完成")
        
    except Exception as e:
        print(f"❌ 回測執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 步驟 4: 分析結果
    print(f"\n步驟 4: 回測結果分析")
    print("-" * 40)
    
    # 顯示詳細結果
    print_tw_summary(symbol, result)
    
    # 顯示訊號統計
    signals_data = result.get('signals_data')
    if signals_data is not None and not signals_data.empty:
        buy_signals = signals_data[signals_data['signal'] == 1]
        sell_signals = signals_data[signals_data['signal'] == -1]
        
        print(f"\n交易訊號統計:")
        print(f"買入訊號: {len(buy_signals)} 次")
        print(f"賣出訊號: {len(sell_signals)} 次")
        
        if len(buy_signals) > 0:
            print(f"首次買入: {buy_signals.index[0].strftime('%Y-%m-%d')}")
            print(f"最後賣出: {sell_signals.index[-1].strftime('%Y-%m-%d') if len(sell_signals) > 0 else '持有中'}")
    
    # 步驟 5: 績效比較
    print(f"\n步驟 5: 與買入持有策略比較")
    print("-" * 40)
    
    try:
        # 計算買入持有策略報酬
        buy_hold_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
        
        strategy_return = result['performance'].get('total_return', 0)
        
        print(f"海龜策略總報酬率：{strategy_return:.2%}")
        print(f"買入持有總報酬率：{buy_hold_return:.2%}")
        print(f"策略超額報酬：{strategy_return - buy_hold_return:.2%}")
        
        if strategy_return > buy_hold_return:
            print("🎉 海龜策略表現優於買入持有!")
        else:
            print("📉 海龜策略表現不如買入持有")
            
    except Exception as e:
        print(f"績效比較計算錯誤: {e}")
    
    # 步驟 6: 風險分析
    print(f"\n步驟 6: 風險分析")
    print("-" * 40)
    
    performance = result.get('performance', {})
    max_dd = performance.get('max_drawdown', 0)
    sharpe = performance.get('sharpe_ratio', 0)
    volatility = performance.get('volatility', 0)
    
    print(f"最大回撤: {max_dd:.2%} {'⚠️  高風險' if max_dd > 0.1 else '✅ 風險可控'}")
    print(f"夏普比率: {sharpe:.3f} {'🎯 優秀' if sharpe > 1 else '📊 普通' if sharpe > 0.5 else '⚠️  需改善'}")
    print(f"年化波動率: {volatility:.2%}")
    
    print(f"\n{'='*80}")
    print("回測完成! 🎊")
    print(f"{'='*80}")


if __name__ == "__main__":
    # 設定中文字體
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Helvetica']  
    plt.rcParams['axes.unicode_minus'] = False
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式被用戶中斷")
    except Exception as e:
        print(f"\n程式執行發生錯誤: {e}")
        import traceback
        traceback.print_exc()