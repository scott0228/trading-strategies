import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import fetch_data
from strategies.turtle_strategy import TurtleStrategy


class TurtleSignalChecker:
    """海龜策略訊號檢查器"""
    
    def __init__(self):
        self.strategy = TurtleStrategy()
    
    def check_latest_signal(self, symbol: str, lookback_days: int = 30) -> Dict:
        """檢查最新的交易訊號"""
        try:
            # 獲取足夠的歷史資料來計算指標
            data = fetch_data(symbol, period='3mo')
            if len(data) < lookback_days:
                return {
                    'symbol': symbol,
                    'has_signal': False,
                    'error': f'數據不足，僅有 {len(data)} 天資料'
                }
            
            # 計算指標並生成訊號
            data_with_indicators = self.strategy.calculate_indicators(data)
            data_with_signals = self.strategy.generate_signals(data_with_indicators)
            
            # 檢查最近幾天是否有訊號
            recent_data = data_with_signals.tail(lookback_days)
            latest_signals = recent_data[recent_data['position'] != 0]
            
            if len(latest_signals) == 0:
                return {
                    'symbol': symbol,
                    'has_signal': False,
                    'current_price': float(data.iloc[-1]['close']),
                    'last_check': datetime.now().isoformat()
                }
            
            # 獲取最新訊號
            latest_signal = latest_signals.iloc[-1]
            signal_date = latest_signal.name
            signal_type = "BUY" if latest_signal['position'] > 0 else "SELL"
            
            # 檢查訊號是否為今天或昨天（考慮市場收盤時間）
            today = datetime.now().date()
            signal_date_only = signal_date.date()
            is_recent_signal = (today - signal_date_only).days <= 1
            
            return {
                'symbol': symbol,
                'has_signal': is_recent_signal,
                'signal_type': signal_type,
                'signal_date': signal_date.strftime('%Y-%m-%d'),
                'price': float(latest_signal['close']),
                'current_price': float(data.iloc[-1]['close']),
                'entry_upper': float(latest_signal.get('Entry_Upper', 0)),
                'entry_lower': float(latest_signal.get('Entry_Lower', 0)),
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'has_signal': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def check_multiple_symbols(self, symbols: List[str]) -> Dict[str, Dict]:
        """檢查多個標的的交易訊號"""
        results = {}
        for symbol in symbols:
            print(f"檢查 {symbol} 的交易訊號...")
            results[symbol] = self.check_latest_signal(symbol)
        return results
    
    def get_signal_summary(self, symbol: str, signal_data: Dict) -> str:
        """生成訊號摘要文字"""
        if not signal_data.get('has_signal', False):
            return f"{symbol}: 無交易訊號"
        
        signal_type = signal_data['signal_type']
        price = signal_data['price']
        signal_date = signal_data['signal_date']
        
        action = "買入" if signal_type == "BUY" else "賣出"
        
        summary = f"{symbol}: {action}訊號 @ ${price:.2f} ({signal_date})"
        
        # 添加突破資訊
        if signal_type == "BUY" and 'entry_upper' in signal_data:
            summary += f"\n  📈 向上突破 ${signal_data['entry_upper']:.2f}"
        elif signal_type == "SELL" and 'entry_lower' in signal_data:
            summary += f"\n  📉 向下跌破 ${signal_data['entry_lower']:.2f}"
            
        return summary