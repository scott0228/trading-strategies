"""Configuration settings for trading strategies."""

import os
from typing import Dict, Any

# Data settings
DATA_CONFIG = {
    'default_period': '2y',
    'default_interval': '1d',
    'data_source': 'yahoo',
    'cache_data': True,
    'data_directory': 'data'
}

# Backtesting settings
BACKTEST_CONFIG = {
    'initial_capital': 100000,
    'commission': 0.001,  # 0.1% commission
    'slippage': 0.0005,   # 0.05% slippage
    'risk_free_rate': 0.02,  # 2% risk-free rate
}

# Strategy parameters
STRATEGY_CONFIGS = {
    'sma_crossover': {
        'short_window': 20,
        'long_window': 50,
        'position_size': 0.1  # 10% of capital per trade
    },
    'rsi_strategy': {
        'rsi_period': 14,
        'oversold_level': 30,
        'overbought_level': 70,
        'position_size': 0.1
    },
    'bollinger_bands': {
        'window': 20,
        'num_std': 2,
        'position_size': 0.1
    }
}

# Popular symbols for testing
DEFAULT_SYMBOLS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
    'SPY', 'QQQ', 'IWM', 'VTI', 'BTC-USD'
]

def get_config(config_type: str) -> Dict[str, Any]:
    """Get configuration by type."""
    configs = {
        'data': DATA_CONFIG,
        'backtest': BACKTEST_CONFIG,
        'strategies': STRATEGY_CONFIGS
    }
    return configs.get(config_type, {})