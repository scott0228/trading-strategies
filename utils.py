"""交易策略的工具函數。"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional
import os

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def fetch_data(symbol: str, period: str = '2y', interval: str = '1d') -> pd.DataFrame:
    """使用 yfinance 獲取股票數據。"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            raise ValueError(f"找不到商品 {symbol} 的數據")
            
        return data
    except Exception as e:
        print(f"獲取 {symbol} 數據時發生錯誤： {e}")
        return pd.DataFrame()


def fetch_multiple_symbols(symbols: List[str], period: str = '2y', 
                          interval: str = '1d') -> Dict[str, pd.DataFrame]:
    """獲取多個商品的數據。"""
    data_dict = {}
    
    for symbol in symbols:
        print(f"正在獲取 {symbol} 的數據...")
        data = fetch_data(symbol, period, interval)
        if not data.empty:
            data_dict[symbol] = data
        else:
            print(f"無法獲取 {symbol} 的數據")
    
    return data_dict


def save_data(data: pd.DataFrame, symbol: str, directory: str = 'data') -> None:
    """將數據保存到 CSV 文件。"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{symbol}.csv")
    data.to_csv(filepath)
    print(f"數據已保存到 {filepath}")


def load_data(symbol: str, directory: str = 'data') -> Optional[pd.DataFrame]:
    """從 CSV 文件加載數據。"""
    filepath = os.path.join(directory, f"{symbol}.csv")
    
    if os.path.exists(filepath):
        return pd.read_csv(filepath, index_col=0, parse_dates=True)
    else:
        print(f"找不到 {symbol} 的已保存數據")
        return None


def calculate_returns(prices: pd.Series) -> pd.Series:
    """從價格序列計算回報率。"""
    return prices.pct_change().dropna()


def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """從回報率計算波動率。"""
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(252)  # 假設每年有252個交易日
    return vol


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """計算夏普比率。"""
    excess_returns = returns.mean() * 252 - risk_free_rate
    volatility = calculate_volatility(returns)
    
    return excess_returns / volatility if volatility > 0 else 0

def calculate_atr(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """計算平均真實波幅（ATR）。"""
    df = data.copy()
    df['high_low'] = df['High'] - df['Low']
    df['high_close'] = np.abs(df['High'] - df['Close'].shift())
    df['low_close'] = np.abs(df['Low'] - df['Close'].shift())
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    atr = df['true_range'].rolling(window=window).mean()
    return atr


def plot_price_and_signals(data: pd.DataFrame, strategy_name: str = "Strategy"):
    """繪製價格數據和交易訊號。"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # 價格圖
    ax1.plot(data.index, data['Close'], label='收盤價', linewidth=1)
    
    # 如果有，新增 SMA 線
    sma_cols = [col for col in data.columns if col.startswith('SMA_')]
    for col in sma_cols:
        ax1.plot(data.index, data[col], label=col, alpha=0.7)
    
    # 新增買賣訊號
    if 'position' in data.columns:
        buy_signals = data[data['position'] > 0]
        sell_signals = data[data['position'] < 0]
        
        ax1.scatter(buy_signals.index, buy_signals['Close'], 
                   marker='^', color='green', s=100, label='買進訊號')
        ax1.scatter(sell_signals.index, sell_signals['Close'], 
                   marker='v', color='red', s=100, label='賣出訊號')
    
    ax1.set_title(f'{strategy_name} - 價格與訊號')
    ax1.set_ylabel('價格')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 成交量圖
    if 'Volume' in data.columns:
        ax2.bar(data.index, data['Volume'], alpha=0.7, color='blue')
        ax2.set_title('成交量')
        ax2.set_ylabel('成交量')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_performance_comparison(strategies_results: Dict[str, Dict[str, Any]]):
    """繪製策略績效比較圖。"""
    if not strategies_results:
        print("沒有策略結果可供繪製")
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
        
        # 根據指標為長條圖上色（綠色為佳，紅色為差）
        if metric in ['total_return', 'sharpe_ratio']:
            colors = ['green' if v > 0 else 'red' for v in values]
        else:  # max_drawdown, volatility (越低越好)
            colors = ['red' if v > 0.1 else 'orange' if v > 0.05 else 'green' for v in values]
        
        for bar, color in zip(bars, colors):
            bar.set_color(color)
            bar.set_alpha(0.7)
    
    plt.tight_layout()
    plt.show()


def print_strategy_summary(strategy_name: str, results: Dict[str, Any]):
    """打印格式化的策略結果摘要。"""
    print(f"\n{'='*50}")
    print(f"策略： {strategy_name}")
    print(f"{'='*50}")
    
    if not results:
        print("沒有可用的結果")
        return
    
    print(f"總回報率： {results.get('total_return', 0):.2%}")
    print(f"年化回報率： {results.get('annualized_return', 0):.2%}")
    print(f"波動率： {results.get('volatility', 0):.2%}")
    print(f"夏普比率： {results.get('sharpe_ratio', 0):.3f}")
    print(f"最大回撤： {results.get('max_drawdown', 0):.2%}")
    print(f"總交易次數： {results.get('total_trades', 0)}")
    print(f"{'='*50}")

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