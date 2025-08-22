# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Environment Setup
```bash
# Install dependencies and create virtual environment
uv sync

# Start Jupyter notebooks for interactive development
uv run jupyter notebook

# Run quick strategy tests
python turtle_demo.py
```

### Testing Strategies
```bash
# Test strategies on different symbols
python -c "
from utils import fetch_data
from strategies.turtle_strategy import TurtleStrategy
from backtest_engine import BacktestEngine

data = fetch_data('QQQ', period='2y')
strategy = TurtleStrategy(initial_capital=100000)
engine = BacktestEngine()
result = engine.run_backtest(strategy, data, 'QQQ')
print(f'Total Return: {result[\"performance\"][\"total_return\"]:.2%}')
"
```

## Architecture Overview

### Core Components

**BaseStrategy (strategies/base_strategy.py)** - Abstract base class for all trading strategies
- Must implement `generate_signals()` and `calculate_indicators()` 
- Handles portfolio tracking, trade execution, and performance metrics
- Key attributes: `capital`, `positions`, `trades`, `portfolio_value`

**BacktestEngine (backtest_engine.py)** - Orchestrates strategy backtesting
- Executes trades based on strategy signals
- Applies commission and slippage
- Returns performance metrics, trades, and portfolio value history
- Default: 10% position sizing, 0.1% commission

**Configuration (config/config.py)** - Centralized settings
- `DATA_CONFIG`: Yahoo Finance settings, caching
- `BACKTEST_CONFIG`: Commission, slippage, risk-free rate
- `STRATEGY_CONFIGS`: Default parameters for each strategy type
- `DEFAULT_SYMBOLS`: Popular stocks/ETFs for testing

### Strategy Development Pattern

1. **Inherit BaseStrategy** - All strategies extend this abstract class
2. **Implement calculate_indicators()** - Add technical indicators to DataFrame
3. **Implement generate_signals()** - Generate buy/sell signals (position column)
4. **Signal Format**: 
   - `position = 1`: Buy signal
   - `position = -1`: Sell signal  
   - `position = 0`: No action

### Data Flow
1. `fetch_data()` gets OHLCV data from Yahoo Finance
2. Strategy `calculate_indicators()` adds technical indicators
3. Strategy `generate_signals()` produces position signals
4. `BacktestEngine` executes trades and tracks performance
5. Results include trades, portfolio value, and performance metrics

## Critical Implementation Notes

### Donchian Channel Breakout Bug
**Common Issue**: Using same-day channel values for breakout detection
```python
# WRONG - will never trigger breakouts
entry_upper = df.iloc[i]['Entry_Upper']  # includes today's high
if current_high > entry_upper:  # never true

# CORRECT - use previous day's channel
entry_upper = df.iloc[i-1]['Entry_Upper']  # previous day's channel
if current_high > entry_upper:  # proper breakout detection
```

### Position Sizing Logic
- Default: 10% of capital per trade in BacktestEngine
- Turtle Strategy: Uses ATR-based volatility sizing
- Override by modifying `position_size_pct` in BacktestEngine

### Performance Metrics
- **Total Return**: (Final Value / Initial Value) - 1
- **Annualized Return**: Geometric mean over 252 trading days
- **Sharpe Ratio**: Annualized excess return / volatility
- **Max Drawdown**: Peak-to-trough loss percentage

## Available Strategies

### SMA Crossover (strategies/sma_crossover.py)
- Buy when short SMA > long SMA
- Sell when short SMA < long SMA
- Default: 20/50 day crossover

### Turtle Strategy (strategies/turtle_strategy.py)
- Donchian channel breakout system
- ATR-based stop losses and position sizing
- Pyramid scaling (up to 4 units)
- **Critical**: Uses previous day's channels for breakout detection

## Data Sources
- **Primary**: Yahoo Finance via `yfinance` library
- **Supported**: Stocks, ETFs, indices, crypto (append -USD)
- **Popular symbols**: AAPL, GOOGL, SPY, QQQ, BTC-USD
- **Periods**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

## Development Workflow
1. Create strategy in `strategies/` inheriting BaseStrategy
2. Test using notebooks in `notebooks/`
3. Add configuration to `config/config.py`
4. Use `utils.py` functions for data fetching and visualization
5. Run backtests via BacktestEngine