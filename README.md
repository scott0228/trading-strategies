# 交易策略回測系統

這是一個使用 Python 建立的完整交易策略開發和回測框架，專門用於程式交易策略的開發、測試和分析。

## 功能特色

- 🔄 **策略開發框架** - 基於物件導向的策略開發模式
- 📊 **回測引擎** - 完整的歷史資料回測功能
- 📈 **技術指標** - 常用技術分析指標實現
- 📉 **績效分析** - 詳細的投資績效評估指標
- 🎯 **視覺化** - 價格、信號和績效圖表
- 🔧 **可擴展** - 易於添加新的策略和指標

## 環境需求

- Python 3.11+
- uv (Python 套件管理器)

## 安裝步驟

1. 進入專案目錄：
```bash
cd trading-strategies
```

2. 啟動虛擬環境：
```bash
uv sync
```

3. 啟動 Jupyter Notebook：
```bash
uv run jupyter notebook
```

## 專案結構

```
trading-strategies/
├── strategies/              # 交易策略模組
│   ├── __init__.py
│   ├── base_strategy.py     # 策略基礎類別
│   └── sma_crossover.py     # SMA交叉策略
├── config/                  # 配置文件
│   └── config.py           # 系統配置
├── notebooks/               # Jupyter筆記本
│   └── quick_start_example.ipynb
├── data/                    # 資料存儲目錄
├── test/                    # 測試程式目錄
│   ├── run_all_tests.py    # 執行所有測試
│   ├── test_notebook_imports.py  # Notebook測試
│   ├── test_all_strategies.py    # 策略功能測試
│   ├── test_tw_stocks.py         # 台股測試
│   └── quick_tw_test.py          # 快速台股測試
├── utils.py                # 工具函數
├── backtest_engine.py      # 回測引擎
└── README.md
```

## 快速開始

### 測試系統
```bash
# 測試系統是否正常運作
cd test
python run_all_tests.py

# 快速測試台股
python quick_tw_test.py
```

### 1. 基本使用範例

```python
from utils import fetch_data
from strategies.sma_crossover import SMAcrossoverStrategy
from backtest_engine import BacktestEngine

# 獲取資料
data = fetch_data('AAPL', period='2y')

# 創建策略
strategy = SMAcrossoverStrategy(
    name="SMA 20/50 交叉策略",
    short_window=20,
    long_window=50,
    initial_capital=100000
)

# 運行回測
engine = BacktestEngine()
result = engine.run_backtest(strategy, data, 'AAPL')

# 查看結果
print(f"總回報: {result['performance']['total_return']:.2%}")
```

### 2. 使用 Jupyter Notebook

開啟 `notebooks/quick_start_example.ipynb` 來查看完整的範例教學。

## 內建策略

### SMA 交叉策略 (SMA Crossover)
- **原理**: 短期移動平均線上穿長期移動平均線時買入，下穿時賣出
- **參數**: 
  - `short_window`: 短期移動平均天數 (預設: 20)
  - `long_window`: 長期移動平均天數 (預設: 50)

## 績效指標

系統會自動計算以下績效指標：

- **總回報** (Total Return): 投資期間的總報酬率
- **年化回報** (Annualized Return): 年化報酬率
- **波動率** (Volatility): 價格波動程度
- **夏普比率** (Sharpe Ratio): 風險調整後報酬
- **最大回撤** (Maximum Drawdown): 最大損失幅度
- **交易次數** (Total Trades): 總交易筆數

## 資料來源

- **Yahoo Finance**: 透過 `yfinance` 套件獲取股票資料
- **支援資產類型**: 股票、ETF、指數、加密貨幣等
- **資料頻率**: 日線、週線、月線

## 如何開發新策略

1. 繼承 `BaseStrategy` 類別
2. 實現 `calculate_indicators()` 方法
3. 實現 `generate_signals()` 方法

```python
from strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def calculate_indicators(self, data):
        # 計算技術指標
        pass
    
    def generate_signals(self, data):
        # 生成交易信號
        pass
```

## 配置設定

在 `config/config.py` 中可以調整：

- 資料獲取設定
- 回測參數
- 策略預設參數
- 預設股票清單

## 常用股票代碼

系統預設包含以下熱門股票：
- **美股**: AAPL, GOOGL, MSFT, AMZN, TSLA
- **ETF**: SPY, QQQ, IWM, VTI
- **加密貨幣**: BTC-USD

## 注意事項

1. 回測結果僅供參考，不構成投資建議
2. 實際交易需考慮交易成本、滑價等因素
3. 歷史績效不代表未來表現
4. 建議在模擬環境充分測試後再進行實盤交易

## 擴展功能

未來可以添加的功能：

- [ ] 更多技術指標 (RSI, MACD, 布林通道等)
- [ ] 風險管理模組 (停損、停利、資金管理)
- [ ] 參數優化功能
- [ ] 多資產投資組合回測
- [ ] 實時交易接口
- [ ] 更多績效分析指標

## 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個專案。

## 授權

MIT License