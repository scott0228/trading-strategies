"""交易策略回測引擎。"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy


class BacktestEngine:
    """簡單的交易策略回測引擎。"""
    
    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = {}
    
    def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame, 
                    symbol: str = "STOCK") -> Dict[str, Any]:
        """為給定策略執行回測。"""
        
        # 產生訊號
        signals_data = strategy.generate_signals(data)
        
        # 重設策略狀態
        strategy.capital = strategy.initial_capital
        strategy.positions = {}
        strategy.trades = []
        strategy.portfolio_value = []
        
        current_position = 0
        
        for i, (timestamp, row) in enumerate(signals_data.iterrows()):
            current_price = row['Close']
            
            # 如果沒有足夠的數據用於指標，則跳過
            if pd.isna(current_price) or pd.isna(row.get('position', 0)):
                strategy.portfolio_value.append(
                    strategy.get_portfolio_value({symbol: current_price})
                )
                continue
            
            position_change = row.get('position', 0)
            
            # 根據部位變化執行交易
            if position_change != 0:
                # 計算部位大小
                if 'position_size' in row and not pd.isna(row['position_size']):
                    shares = int(row['position_size'])
                else:
                    # 如果策略未指定，則使用預設部位大小
                    position_size_pct = 0.1
                    trade_value = self.initial_capital * position_size_pct
                    shares = int(trade_value / current_price) if current_price > 0 else 0
                
                if position_change > 0 and current_position <= 0:  # 買進訊號
                    if shares > 0:
                        cost = shares * current_price * (1 + self.commission)
                        if cost <= strategy.capital:
                            # 先扣除现金（包含手续费）
                            strategy.capital -= cost
                            # 记录交易（不包含手续费，因为已经在上面扣除）
                            trade_record = {
                                'timestamp': timestamp,
                                'symbol': symbol,
                                'quantity': shares,
                                'price': current_price,
                                'value': shares * current_price,
                                'capital_after': strategy.capital
                            }
                            strategy.trades.append(trade_record)
                            # 更新持仓
                            if symbol not in strategy.positions:
                                strategy.positions[symbol] = 0
                            strategy.positions[symbol] += shares
                            current_position = shares
                
                elif position_change < 0 and current_position > 0:  # 賣出訊號
                    if current_position > 0:
                        revenue = current_position * current_price * (1 - self.commission)
                        # 增加现金（扣除手续费）
                        strategy.capital += revenue
                        # 记录交易
                        trade_record = {
                            'timestamp': timestamp,
                            'symbol': symbol,
                            'quantity': -current_position,
                            'price': current_price,
                            'value': -(current_position * current_price),
                            'capital_after': strategy.capital
                        }
                        strategy.trades.append(trade_record)
                        # 更新持仓
                        strategy.positions[symbol] = 0
                        current_position = 0
            
            # 記錄投資組合價值
            portfolio_val = strategy.get_portfolio_value({symbol: current_price})
            strategy.portfolio_value.append(portfolio_val)
        
        # 計算最終績效指標
        performance = strategy.get_performance_metrics()
        
        # 新增額外的回測特定指標
        if strategy.portfolio_value:
            portfolio_series = pd.Series(strategy.portfolio_value)
            performance['final_capital'] = portfolio_series.iloc[-1]
            performance['total_return_pct'] = (portfolio_series.iloc[-1] / self.initial_capital - 1) * 100
        
        self.results[strategy.name] = performance
        
        return {
            'performance': performance,
            'trades': strategy.trades,
            'portfolio_value': strategy.portfolio_value,
            'signals_data': signals_data
        }
    
    def run_multiple_backtests(self, strategies: List[BaseStrategy], 
                             data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        """為多個策略和商品執行回測。"""
        all_results = {}
        
        for symbol, data in data_dict.items():
            symbol_results = {}
            
            for strategy in strategies:
                print(f"執行回測： {strategy.name} on {symbol}")
                
                try:
                    result = self.run_backtest(strategy, data, symbol)
                    symbol_results[strategy.name] = result
                except Exception as e:
                    print(f"執行 {strategy.name} on {symbol} 時發生錯誤： {e}")
                    symbol_results[strategy.name] = {
                        'performance': {},
                        'trades': [],
                        'portfolio_value': [],
                        'signals_data': pd.DataFrame()
                    }
            
            all_results[symbol] = symbol_results
        
        return all_results
    
    def get_summary_results(self) -> pd.DataFrame:
        """獲取所有回測結果的摘要。"""
        if not self.results:
            return pd.DataFrame()
        
        summary_data = []
        for strategy_name, performance in self.results.items():
            summary_data.append({
                'Strategy': strategy_name,
                'Total Return (%)': performance.get('total_return', 0) * 100,
                'Annualized Return (%)': performance.get('annualized_return', 0) * 100,
                'Volatility (%)': performance.get('volatility', 0) * 100,
                'Sharpe Ratio': performance.get('sharpe_ratio', 0),
                'Max Drawdown (%)': performance.get('max_drawdown', 0) * 100,
                'Total Trades': performance.get('total_trades', 0),
                'Final Capital': performance.get('final_capital', 0)
            })
        
        return pd.DataFrame(summary_data).round(2)