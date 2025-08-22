from strategies.turtle_strategy import TurtleStrategy
from backtest_engine import BacktestEngine
from utils import fetch_data, plot_price_and_signals, print_strategy_summary

def main():
    """主函數，用於執行回測。"""
    # 1. 獲取數據
    symbol = "QQQ"
    data = fetch_data(symbol, period="5y")

    if data.empty:
        print(f"無法獲取 {symbol} 的數據。正在退出。")
        return

    # 2. 初始化策略和回測引擎
    turtle_strategy = TurtleStrategy()
    backtest_engine = BacktestEngine(initial_capital=100000)

    # 3. 執行回測
    results = backtest_engine.run_backtest(turtle_strategy, data, symbol)

    # 4. 打印和繪製結果
    if results:
        print_strategy_summary(turtle_strategy.name, results['performance'])
        # 打印交易以供分析
        import pandas as pd
        trades_df = pd.DataFrame(results['trades'])
        print("\n交易：")
        print(trades_df.to_string())
        plot_price_and_signals(results['signals_data'], turtle_strategy.name)


if __name__ == "__main__":
    main()