import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str, initial_capital: float = 100000):
        self.name = name
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_value = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on market data."""
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the strategy."""
        pass
    
    def execute_trade(self, symbol: str, quantity: int, price: float, timestamp: pd.Timestamp):
        """Execute a trade and update portfolio."""
        trade_value = quantity * price
        
        if symbol not in self.positions:
            self.positions[symbol] = 0
            
        self.positions[symbol] += quantity
        self.capital -= trade_value
        
        trade_record = {
            'timestamp': timestamp,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'capital_after': self.capital
        }
        self.trades.append(trade_record)
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate current portfolio value."""
        positions_value = sum(
            quantity * current_prices.get(symbol, 0) 
            for symbol, quantity in self.positions.items()
        )
        return self.capital + positions_value
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.portfolio_value:
            return {}
            
        portfolio_series = pd.Series(self.portfolio_value)
        returns = portfolio_series.pct_change().dropna()
        
        total_return = (portfolio_series.iloc[-1] / portfolio_series.iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_series)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        max_drawdown = 0
        peak = portfolio_series.iloc[0]
        for value in portfolio_series:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trades)
        }