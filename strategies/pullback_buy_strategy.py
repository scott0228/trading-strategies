import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from utils import calculate_atr


class PullbackBuyStrategy(BaseStrategy):
    """
    回撤買上漲策略。
    
    策略邏輯：
    1. 確認長期上升趨勢（價格高於50日均線）
    2. 檢測價格回撤（從近期高點回撤指定百分比）
    3. 在關鍵支撐位附近買入（20日均線附近）
    4. 價格反彈確認後進場
    5. 設定止盈止損出場
    """
    
    def __init__(self, name: str = "回撤買上漲策略", 
                 trend_window: int = 50,
                 support_window: int = 20,
                 pullback_threshold: float = 0.05,  # 5% 回撤
                 rsi_window: int = 14,
                 rsi_oversold: int = 30,
                 atr_window: int = 20,
                 stop_loss_multiplier: float = 2.0,
                 take_profit_multiplier: float = 3.0,
                 initial_capital: float = 100000):
        super().__init__(name, initial_capital)
        self.trend_window = trend_window
        self.support_window = support_window
        self.pullback_threshold = pullback_threshold
        self.rsi_window = rsi_window
        self.rsi_oversold = rsi_oversold
        self.atr_window = atr_window
        self.stop_loss_multiplier = stop_loss_multiplier
        self.take_profit_multiplier = take_profit_multiplier
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """計算 RSI 指標。"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算策略所需指標。
        """
        df = data.copy()
        
        # 移動平均線
        df['trend_ma'] = df['Close'].rolling(window=self.trend_window).mean()
        df['support_ma'] = df['Close'].rolling(window=self.support_window).mean()
        
        # RSI
        df['rsi'] = self.calculate_rsi(df, self.rsi_window)
        
        # ATR
        df['atr'] = calculate_atr(df, window=self.atr_window)
        
        # 計算近期高點（回看20天）
        df['recent_high'] = df['High'].rolling(window=20).max()
        
        # 計算回撤百分比
        df['pullback_pct'] = (df['recent_high'] - df['Close']) / df['recent_high']
        
        # 趋勢確認：價格高於長期均線
        df['uptrend'] = df['Close'] > df['trend_ma']
        
        # 支撐確認：價格接近短期均線（在±3%範圍內）
        df['near_support'] = np.abs(df['Close'] - df['support_ma']) / df['support_ma'] < 0.03
        
        # 回撤確認：回撤超過閾值
        df['pullback_signal'] = df['pullback_pct'] >= self.pullback_threshold
        
        # RSI 超賣
        df['rsi_oversold'] = df['rsi'] < self.rsi_oversold
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        根據回撤買上漲策略產生買賣訊號。
        """
        df = self.calculate_indicators(data)
        
        df['signal'] = 0
        df['position'] = 0
        
        position = 0
        entry_price = 0
        stop_loss_price = 0
        take_profit_price = 0
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # 跳過沒有足夠歷史數據的前期
            if (pd.isna(row['trend_ma']) or pd.isna(row['support_ma']) or 
                pd.isna(row['rsi']) or pd.isna(row['atr'])):
                continue
            
            # 買入條件：
            # 1. 沒有部位
            # 2. 上升趨勢確認
            # 3. 發生回撤
            # 4. 價格接近支撐位
            # 5. RSI 超賣
            # 6. 價格開始反彈（當日收盤價 > 昨日收盤價）
            if (position == 0 and 
                row['uptrend'] and 
                row['pullback_signal'] and 
                row['near_support'] and 
                row['rsi_oversold'] and
                i > 0 and row['Close'] > df.iloc[i-1]['Close']):
                
                df.iloc[i, df.columns.get_loc('signal')] = 1
                df.iloc[i, df.columns.get_loc('position')] = 1
                position = 1
                entry_price = row['Close']
                stop_loss_price = entry_price - self.stop_loss_multiplier * row['atr']
                take_profit_price = entry_price + self.take_profit_multiplier * row['atr']
            
            # 賣出條件：
            # 1. 有部位
            # 2. 觸及止損或止盈
            # 3. 或趨勢轉弱（價格跌破長期均線）
            elif (position > 0 and (
                row['Low'] <= stop_loss_price or  # 觸及止損
                row['High'] >= take_profit_price or  # 觸及止盈  
                not row['uptrend']  # 趨勢轉弱
            )):
                df.iloc[i, df.columns.get_loc('signal')] = -1
                df.iloc[i, df.columns.get_loc('position')] = -1
                position = 0
                entry_price = 0
                stop_loss_price = 0
                take_profit_price = 0
        
        return df