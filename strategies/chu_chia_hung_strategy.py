
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class ChuChiaHungStrategy(BaseStrategy):
    """
    實作朱家泓「回後買上漲」策略。
    
    策略邏輯：
    1. 確認上升趨勢（20MA > 60MA，且60MA向上）
    2. 價格回撤至20日均線附近
    3. 出現量增價漲訊號
    """
    def __init__(self, name: str = "朱家泓回後買上漲策略", initial_capital: float = 100000):
        super().__init__(name, initial_capital)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算策略所需技術指標。
        """
        df = data.copy()
        
        # 移動平均線
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        # 成交量移動平均
        df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
        
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        根據「回後買上漲」策略產生交易訊號。
        """
        df = self.calculate_indicators(data)
        
        df['signal'] = 0
        df['position'] = 0
        
        position = 0
        
        for i in range(60, len(df)):  # 從第60天開始，確保有足夠數據
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            # 跳過沒有足夠數據的情況
            if pd.isna(row['MA20']) or pd.isna(row['MA60']):
                continue
            
            # 條件1：上升趨勢確認
            uptrend = (row['MA20'] > row['MA60'] and 
                      row['MA60'] > prev_row['MA60'])
            
            # 條件2：回撤至20MA附近（在20MA上下3%範圍內）
            pullback = (row['Low'] <= row['MA20'] * 1.03 and 
                       row['Close'] > row['MA20'])
            
            # 條件3：量增價漲
            volume_increase = row['Volume'] > row['Volume_MA5']
            price_increase = row['Close'] > row['Open']  # 收盤價高於開盤價
            buy_signal = volume_increase and price_increase
            
            # 買入條件
            if (position == 0 and 
                uptrend and pullback and buy_signal):
                
                df.iloc[i, df.columns.get_loc('signal')] = 1
                df.iloc[i, df.columns.get_loc('position')] = 1
                position = 1
            
            # 賣出條件：價格跌破20MA
            elif (position > 0 and 
                  row['Close'] < row['MA20']):
                
                df.iloc[i, df.columns.get_loc('signal')] = -1
                df.iloc[i, df.columns.get_loc('position')] = -1
                position = 0
        
        return df
