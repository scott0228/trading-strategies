"""Utility functions for trading strategies."""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional
import os


def fetch_data(symbol: str, period: str = '2y', interval: str = '1d') -> pd.DataFrame:
    """Fetch stock data using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")
            
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def fetch_multiple_symbols(symbols: List[str], period: str = '2y', 
                          interval: str = '1d') -> Dict[str, pd.DataFrame]:
    """Fetch data for multiple symbols."""
    data_dict = {}
    
    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        data = fetch_data(symbol, period, interval)
        if not data.empty:
            data_dict[symbol] = data
        else:
            print(f"Failed to fetch data for {symbol}")
    
    return data_dict


def save_data(data: pd.DataFrame, symbol: str, directory: str = 'data') -> None:
    """Save data to CSV file."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{symbol}.csv")
    data.to_csv(filepath)
    print(f"Data saved to {filepath}")


def load_data(symbol: str, directory: str = 'data') -> Optional[pd.DataFrame]:
    """Load data from CSV file."""
    filepath = os.path.join(directory, f"{symbol}.csv")
    
    if os.path.exists(filepath):
        return pd.read_csv(filepath, index_col=0, parse_dates=True)
    else:
        print(f"No saved data found for {symbol}")
        return None


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate returns from price series."""
    return prices.pct_change().dropna()


def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """Calculate volatility from returns."""
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(252)  # Assuming 252 trading days per year
    return vol


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio."""
    excess_returns = returns.mean() * 252 - risk_free_rate
    volatility = calculate_volatility(returns)
    
    return excess_returns / volatility if volatility > 0 else 0


def plot_price_and_signals(data: pd.DataFrame, strategy_name: str = "Strategy"):
    """Plot price data with trading signals."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Price plot
    ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1)
    
    # Add SMA lines if available
    sma_cols = [col for col in data.columns if col.startswith('SMA_')]
    for col in sma_cols:
        ax1.plot(data.index, data[col], label=col, alpha=0.7)
    
    # Add buy/sell signals
    if 'position' in data.columns:
        buy_signals = data[data['position'] > 0]
        sell_signals = data[data['position'] < 0]
        
        ax1.scatter(buy_signals.index, buy_signals['Close'], 
                   marker='^', color='green', s=100, label='Buy Signal')
        ax1.scatter(sell_signals.index, sell_signals['Close'], 
                   marker='v', color='red', s=100, label='Sell Signal')
    
    ax1.set_title(f'{strategy_name} - Price and Signals')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Volume plot
    if 'Volume' in data.columns:
        ax2.bar(data.index, data['Volume'], alpha=0.7, color='blue')
        ax2.set_title('Volume')
        ax2.set_ylabel('Volume')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_performance_comparison(strategies_results: Dict[str, Dict[str, Any]]):
    """Plot performance comparison between strategies."""
    if not strategies_results:
        print("No strategy results to plot")
        return
    
    metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'volatility']
    strategy_names = list(strategies_results.keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, metric in enumerate(metrics):
        values = [strategies_results[name].get(metric, 0) for name in strategy_names]
        
        bars = axes[i].bar(strategy_names, values)
        axes[i].set_title(f'{metric.replace("_", " ").title()}')
        axes[i].tick_params(axis='x', rotation=45)
        
        # Color bars based on metric (green for good, red for bad)
        if metric in ['total_return', 'sharpe_ratio']:
            colors = ['green' if v > 0 else 'red' for v in values]
        else:  # max_drawdown, volatility (lower is better)
            colors = ['red' if v > 0.1 else 'orange' if v > 0.05 else 'green' for v in values]
        
        for bar, color in zip(bars, colors):
            bar.set_color(color)
            bar.set_alpha(0.7)
    
    plt.tight_layout()
    plt.show()


def print_strategy_summary(strategy_name: str, results: Dict[str, Any]):
    """Print a formatted summary of strategy results."""
    print(f"\n{'='*50}")
    print(f"Strategy: {strategy_name}")
    print(f"{'='*50}")
    
    if not results:
        print("No results available")
        return
    
    print(f"Total Return: {results.get('total_return', 0):.2%}")
    print(f"Annualized Return: {results.get('annualized_return', 0):.2%}")
    print(f"Volatility: {results.get('volatility', 0):.2%}")
    print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.3f}")
    print(f"Max Drawdown: {results.get('max_drawdown', 0):.2%}")
    print(f"Total Trades: {results.get('total_trades', 0)}")
    print(f"{'='*50}")