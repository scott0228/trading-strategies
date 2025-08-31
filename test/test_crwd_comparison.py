import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import fetch_data
from strategies.turtle_strategy import TurtleStrategy
from strategies.buy_and_hold_strategy import BuyAndHoldStrategy
from backtest_engine import BacktestEngine


def compare_strategies(symbol='CRWD', period='2y', initial_capital=100000):
    """比較海龜策略與買入持有策略的績效"""
    
    # 獲取數據
    data = fetch_data(symbol, period=period)
    print(f'=== {symbol} 策略比較 ({period}) ===')
    print(f'數據範圍: {data.index[0]} 至 {data.index[-1]}')
    print(f'交易日數: {len(data)} 天\n')
    
    # 回測引擎
    engine = BacktestEngine()
    
    # 1. 海龜策略回測
    turtle_strategy = TurtleStrategy(initial_capital=initial_capital)
    turtle_result = engine.run_backtest(turtle_strategy, data, symbol)
    turtle_perf = turtle_result['performance']
    
    # 2. 買入持有策略回測
    buy_hold_strategy = BuyAndHoldStrategy(initial_capital=initial_capital)
    buy_hold_result = engine.run_backtest(buy_hold_strategy, data, symbol)
    buy_hold_perf = buy_hold_result['performance']
    
    # 3. 顯示比較結果
    print('策略績效比較:')
    print('=' * 60)
    print(f'{"指標":<15} {"海龜策略":<15} {"買入持有":<15} {"差異":<15}')
    print('=' * 60)
    
    metrics = [
        ('總報酬率', 'total_return', '%'),
        ('年化報酬率', 'annualized_return', '%'),
        ('夏普比率', 'sharpe_ratio', ''),
        ('最大回撤', 'max_drawdown', '%'),
        ('交易次數', 'total_trades', '')
    ]
    
    for name, key, unit in metrics:
        turtle_val = turtle_perf[key]
        buy_hold_val = buy_hold_perf[key]
        
        if unit == '%':
            turtle_str = f'{turtle_val:.2%}'
            buy_hold_str = f'{buy_hold_val:.2%}'
            diff_str = f'{turtle_val - buy_hold_val:+.2%}'
        else:
            turtle_str = f'{turtle_val:.2f}'
            buy_hold_str = f'{buy_hold_val:.2f}'
            diff_str = f'{turtle_val - buy_hold_val:+.2f}'
            
        print(f'{name:<15} {turtle_str:<15} {buy_hold_str:<15} {diff_str:<15}')
    
    print('=' * 60)
    
    # 4. 最終資產價值
    turtle_final = turtle_result['portfolio_value'][-1]
    buy_hold_final = buy_hold_result['portfolio_value'][-1]
    diff_final = turtle_final - buy_hold_final
    
    print(f'\n最終資產價值:')
    print(f'海龜策略:     ${turtle_final:,.2f}')
    print(f'買入持有:     ${buy_hold_final:,.2f}')
    print(f'差異:         ${diff_final:+,.2f}')
    
    # 5. 勝負判斷
    if turtle_final > buy_hold_final:
        winner = "海龜策略"
        advantage = (turtle_final / buy_hold_final - 1) * 100
    else:
        winner = "買入持有"
        advantage = (buy_hold_final / turtle_final - 1) * 100
    
    print(f'\n結論: {winner} 表現較優，超越 {advantage:.1f}%')
    
    return {
        'turtle': turtle_result,
        'buy_hold': buy_hold_result,
        'winner': winner
    }


if __name__ == "__main__":
    compare_strategies('CRWD', period='2y', initial_capital=100000)