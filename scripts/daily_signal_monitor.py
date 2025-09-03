#!/usr/bin/env python3
"""
每日海龜策略訊號監控腳本
用於檢查 CRWD 和 QQQ 的交易訊號並發送 Telegram 通知
"""

import json
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.signal_checker import TurtleSignalChecker
from utils.telegram_notifier import TelegramNotifier


def load_config():
    """載入配置檔案"""
    config_path = os.path.join(project_root, 'config', 'telegram_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def main():
    """主要執行函數"""
    print(f"=== 海龜策略每日訊號檢查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 設定要監控的股票
    symbols = ['CRWD', 'QQQ', 'ARKK', 'ARKW', 'AAPL', 'MSFT', 'GOOGL']
    
    # 初始化訊號檢查器
    checker = TurtleSignalChecker()
    
    # 初始化 Telegram 通知器
    config = load_config()
    notifier = TelegramNotifier(
        bot_token=config.get('bot_token'),
        chat_id=config.get('chat_id')
    )
    
    # 檢查所有標的的訊號
    results = checker.check_multiple_symbols(symbols)
    
    # 統計結果
    signals_found = []
    errors = []
    
    for symbol, result in results.items():
        if result.get('error'):
            errors.append(f"{symbol}: {result['error']}")
            print(f"❌ {symbol}: 檢查失敗 - {result['error']}")
        elif result.get('has_signal'):
            signals_found.append((symbol, result))
            summary = checker.get_signal_summary(symbol, result)
            print(f"🎯 發現訊號: {summary}")
        else:
            print(f"✅ {symbol}: 無交易訊號")
    
    # 發送個別訊號通知
    for symbol, signal_data in signals_found:
        signal_type = signal_data['signal_type']
        price = signal_data['current_price']
        
        # 生成額外資訊
        additional_info = f"📅 訊號日期: {signal_data['signal_date']}\n"
        if 'entry_upper' in signal_data and signal_type == 'BUY':
            additional_info += f"📈 突破價位: ${signal_data['entry_upper']:.2f}\n"
        elif 'entry_lower' in signal_data and signal_type == 'SELL':
            additional_info += f"📉 跌破價位: ${signal_data['entry_lower']:.2f}\n"
        
        notifier.send_trading_signal(
            symbol=symbol,
            signal_type=signal_type,
            current_price=price,
            additional_info=additional_info
        )
    
    # 發送每日摘要
    if config.get('send_daily_summary', True):
        notifier.send_daily_summary(symbols, results)
    
    # 顯示執行結果
    print(f"\n=== 執行結果 ===")
    print(f"檢查標的: {', '.join(symbols)}")
    print(f"發現訊號: {len(signals_found)} 個")
    print(f"錯誤數量: {len(errors)} 個")
    
    if errors:
        print("錯誤詳情:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"執行完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()