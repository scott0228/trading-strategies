"""台股資料獲取工具函數。"""

import pandas as pd
import twstock
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')


def fetch_tw_stock_data(symbol: str, start_year: int = 2022, 
                       start_month: int = 1) -> pd.DataFrame:
    """
    使用 twstock 獲取台股資料。
    
    Args:
        symbol: 股票代號 (如 '0050', '2330')
        start_year: 開始年份
        start_month: 開始月份
        
    Returns:
        包含 OHLCV 資料的 DataFrame，格式與 yfinance 相容
    """
    try:
        print(f"正在獲取 {symbol} 的資料...")
        
        # 建立 twstock Stock 物件
        stock = twstock.Stock(symbol)
        
        # 從指定時間獲取資料
        data = stock.fetch_from(start_year, start_month)
        
        if not data:
            raise ValueError(f"無法獲取 {symbol} 的資料")
        
        # 轉換為 DataFrame
        df_data = []
        for d in data:
            df_data.append({
                'Date': d.date,
                'Open': float(d.open),
                'High': float(d.high), 
                'Low': float(d.low),
                'Close': float(d.close),
                'Volume': int(d.capacity)
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        
        # 確保資料按日期排序
        df.sort_index(inplace=True)
        
        print(f"成功獲取 {len(df)} 筆 {symbol} 資料")
        print(f"資料範圍: {df.index.min()} 到 {df.index.max()}")
        
        return df
        
    except Exception as e:
        print(f"獲取 {symbol} 資料時發生錯誤: {e}")
        return pd.DataFrame()


def get_tw_stock_info(symbol: str) -> Dict[str, Any]:
    """
    獲取台股基本資訊。
    
    Args:
        symbol: 股票代號
        
    Returns:
        包含股票基本資訊的字典
    """
    try:
        # 獲取股票名稱和基本資訊
        if symbol in twstock.codes:
            stock_info = twstock.codes[symbol]
            return {
                'symbol': symbol,
                'name': stock_info.name,
                'industry': stock_info.group,
                'market': stock_info.market
            }
        else:
            return {'symbol': symbol, 'name': f'股票代號 {symbol}'}
            
    except Exception as e:
        print(f"獲取 {symbol} 基本資訊時發生錯誤: {e}")
        return {'symbol': symbol, 'name': f'股票代號 {symbol}'}


def calculate_tw_returns(prices: pd.Series) -> pd.Series:
    """計算台股報酬率（考慮台股特性）。"""
    return prices.pct_change().dropna()


def print_tw_summary(symbol: str, results: Dict[str, Any]):
    """打印台股回測結果摘要。"""
    stock_info = get_tw_stock_info(symbol)
    
    print(f"\n{'='*60}")
    print(f"台股回測結果：{symbol} - {stock_info.get('name', symbol)}")
    print(f"{'='*60}")
    
    if not results:
        print("沒有可用的結果")
        return
    
    performance = results.get('performance', {})
    
    print(f"總回報率：{performance.get('total_return', 0):.2%}")
    print(f"年化回報率：{performance.get('annualized_return', 0):.2%}")
    print(f"波動率：{performance.get('volatility', 0):.2%}")
    print(f"夏普比率：{performance.get('sharpe_ratio', 0):.3f}")
    print(f"最大回撤：{performance.get('max_drawdown', 0):.2%}")
    print(f"總交易次數：{performance.get('total_trades', 0)}")
    
    if 'final_capital' in performance:
        print(f"最終資本：NT$ {performance['final_capital']:,.0f}")
    
    trades = results.get('trades', [])
    if trades:
        print(f"\n前5筆交易記錄：")
        for i, trade in enumerate(trades[:5]):
            action = "買入" if trade['quantity'] > 0 else "賣出"
            print(f"  {i+1}. {trade['timestamp'].strftime('%Y-%m-%d')}: "
                  f"{action} {abs(trade['quantity'])} 股 @ NT${trade['price']:.2f}")
    
    print(f"{'='*60}")


def save_tw_data(data: pd.DataFrame, symbol: str, directory: str = 'tw_data') -> None:
    """保存台股資料到 CSV。"""
    import os
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{symbol}_tw.csv")
    data.to_csv(filepath, encoding='utf-8-sig')  # 使用 utf-8-sig 支持中文
    print(f"台股資料已保存到 {filepath}")


def load_tw_data(symbol: str, directory: str = 'tw_data') -> Optional[pd.DataFrame]:
    """從 CSV 載入台股資料。"""
    import os
    filepath = os.path.join(directory, f"{symbol}_tw.csv")
    
    if os.path.exists(filepath):
        return pd.read_csv(filepath, index_col=0, parse_dates=True, encoding='utf-8-sig')
    else:
        print(f"找不到 {symbol} 的已保存台股資料")
        return None