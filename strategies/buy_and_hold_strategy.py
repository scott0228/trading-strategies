import pandas as pd
from .base_strategy import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):
    """Simple buy-and-hold strategy for benchmarking."""
    
    def __init__(self, initial_capital: float = 100000):
        super().__init__("Buy and Hold", initial_capital)
        self.position_taken = False
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """No technical indicators needed for buy and hold."""
        return data.copy()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals: Buy on first day, hold until end."""
        data = data.copy()
        data['position'] = 0
        
        # Buy on first day only
        if len(data) > 0:
            data.iloc[0, data.columns.get_loc('position')] = 1
            
        return data