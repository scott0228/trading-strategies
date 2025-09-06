import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.turtle_strategy import TurtleStrategy
from utils import fetch_data
from utils.fubon_data_fetcher import FubonDataFetcher, create_fubon_fetcher


class TurtleSignalChecker:
    """海龜策略訊號檢查器"""
    
    def __init__(self, config: Dict = None):
        self.strategy = TurtleStrategy()
        self.config = config or {}
        self.fubon_fetcher = None
        
        # 初始化富邦API（如果有設定）
        if config and config.get('fubon_api', {}).get('enabled', False):
            try:
                self.fubon_fetcher = create_fubon_fetcher(config)
            except Exception as e:
                print(f"初始化富邦API失敗: {e}")
                self.fubon_fetcher = None
    
    def _fetch_stock_data(self, symbol: str, period: str = '3mo') -> Optional[pd.DataFrame]:
        """根據股票類型獲取資料"""
        # 判斷是台股還是美股
        is_tw_stock = symbol.isdigit()  # 台股代碼通常是數字
        
        if is_tw_stock:
            # 優先使用富邦API獲取台股資料
            if self.fubon_fetcher and self.fubon_fetcher.logged_in:
                print(f"使用富邦API獲取 {symbol} 台股資料")
                data = self.fubon_fetcher.fetch_historical_data(symbol, period)
                if data is not None:
                    return data
                print(f"富邦API獲取失敗，嘗試使用Yahoo Finance")
            
            # 富邦API失敗或未設定時，嘗試Yahoo Finance台股格式
            print(f"使用Yahoo Finance獲取 {symbol} 台股資料")
            # 台股在Yahoo Finance的格式通常是 XXXX.TW 或 XXXX.TWO
            for suffix in ['.TW', '.TWO']:
                try:
                    data = fetch_data(f"{symbol}{suffix}", period=period)
                    if data is not None and len(data) > 0:
                        print(f"✓ 成功獲取 {symbol}{suffix} 資料")
                        return data
                except:
                    continue
            
            # 如果都失敗，嘗試原始代碼
            return fetch_data(symbol, period=period)
        else:
            print(f"使用Yahoo Finance獲取 {symbol} 美股資料")
            return fetch_data(symbol, period=period)
    
    def check_latest_signal(self, symbol: str, lookback_days: int = 30) -> Dict:
        """檢查最新的交易訊號"""
        try:
            # 獲取足夠的歷史資料來計算指標
            data = self._fetch_stock_data(symbol, period='3mo')
            if data is None or len(data) < lookback_days:
                data_len = len(data) if data is not None else 0
                return {
                    'symbol': symbol,
                    'has_signal': False,
                    'error': f'數據不足，僅有 {data_len} 天資料'
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
                    'current_price': float(data.iloc[-1]['Close']),
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
                'price': float(latest_signal['Close']),
                'current_price': float(data.iloc[-1]['Close']),
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
    
    def check_multiple_symbols(self, symbols: List[str] = None, 
                              us_symbols: List[str] = None, 
                              tw_symbols: List[str] = None) -> Dict[str, Dict]:
        """檢查多個標的的交易訊號"""
        results = {}
        
        # 如果傳入單一 symbols 列表，使用舊的邏輯
        if symbols:
            for symbol in symbols:
                print(f"檢查 {symbol} 的交易訊號...")
                results[symbol] = self.check_latest_signal(symbol)
            return results
        
        # 新的邏輯：分別處理美股和台股
        all_symbols = []
        if us_symbols:
            all_symbols.extend(us_symbols)
        if tw_symbols:
            all_symbols.extend(tw_symbols)
        
        for symbol in all_symbols:
            stock_type = "台股" if symbol.isdigit() else "美股"
            print(f"檢查 {symbol} ({stock_type}) 的交易訊號...")
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