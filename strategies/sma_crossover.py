import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class SMAcrossoverStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy."""
    
    def __init__(self, name: str = "SMA Crossover", short_window: int = 20, 
                 long_window: int = 50, initial_capital: float = 100000):
        super().__init__(name, initial_capital)
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA indicators."""
        df = data.copy()
        df[f'SMA_{self.short_window}'] = df['Close'].rolling(window=self.short_window).mean()
        df[f'SMA_{self.long_window}'] = df['Close'].rolling(window=self.long_window).mean()
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on SMA crossover."""
        df = self.calculate_indicators(data)
        
        # Initialize signals
        df['signal'] = 0
        df['position'] = 0
        
        # Generate signals when short SMA crosses above/below long SMA
        short_col = f'SMA_{self.short_window}'
        long_col = f'SMA_{self.long_window}'
        
        # Buy signal: short SMA crosses above long SMA
        df.loc[df[short_col] > df[long_col], 'signal'] = 1
        
        # Sell signal: short SMA crosses below long SMA
        df.loc[df[short_col] < df[long_col], 'signal'] = -1
        
        # Calculate position changes
        df['position'] = df['signal'].diff()
        
        return df