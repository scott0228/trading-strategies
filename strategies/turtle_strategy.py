import pandas as pd
from .base_strategy import BaseStrategy
from utils import calculate_atr

class TurtleStrategy(BaseStrategy):
    """
    實作海龜交易策略。
    
    系統一：
    - 進場：突破20日高點時買入。
    - 出場：跌破10日低點時賣出。
    """
    def __init__(self, name: str = "海龜策略", entry_window: int = 20, 
                 exit_window: int = 10, atr_window: int = 20, stop_loss_multiplier: float = 2.0, 
                 initial_capital: float = 100000):
        super().__init__(name, initial_capital)
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.atr_window = atr_window
        self.stop_loss_multiplier = stop_loss_multiplier

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算海龜策略所需指標。
        
        - 20日高點作為進場訊號。
        - 10日低點作為出場訊號。
        - ATR 用於停損。
        """
        df = data.copy()
        df['entry_high'] = df['High'].rolling(window=self.entry_window).max().shift(1)
        df['exit_low'] = df['Low'].rolling(window=self.exit_window).min().shift(1)
        df['atr'] = calculate_atr(df, window=self.atr_window)
        
        # 根據 ATR 計算部位大小
        df['position_size'] = (self.initial_capital * 0.01) / df['atr']
        
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        根據海龜策略產生買賣訊號。
        """
        df = self.calculate_indicators(data)
        
        df['signal'] = 0
        
        # 買進訊號：價格突破20日高點
        df.loc[df['Close'] > df['entry_high'], 'signal'] = 1
        
        # 賣出訊號：價格跌破10日低點
        df.loc[df['Close'] < df['exit_low'], 'signal'] = -1
        
        # 根據 ATR 加入停損
        # 這是一個簡化的實作。完整的實作會為每個部位追蹤停損水準。
        if 'atr' in df.columns:
            df['stop_loss'] = df['Close'] - self.stop_loss_multiplier * df['atr']
            df.loc[df['Close'] < df['stop_loss'].shift(1), 'signal'] = -1

        df['position'] = df['signal'].diff()
        
        return df
