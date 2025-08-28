# 測試目錄說明

這個目錄包含所有的測試程式，用於驗證交易策略回測系統的功能。

## 測試程式清單

### 🧪 核心測試
- **`test_notebook_imports.py`** - Jupyter Notebook Import 測試
  - 測試所有必要模組是否正確匯入
  - 驗證策略實例化功能
  - 提供正確的 Notebook 程式碼模板

- **`test_all_strategies.py`** - 所有交易策略功能測試
  - 測試所有策略的回測功能
  - 比較不同策略的表現
  - 生成詳細的測試報告

### 📊 台股測試
- **`test_tw_stocks.py`** - 台股交易策略測試
  - 測試台股資料獲取功能
  - 比較台股 ETF 表現 (0050 vs 006208)
  - 測試熱門台股策略表現

### 🔧 工具程式
- **`quick_tw_test.py`** - 快速台股測試工具
- **`compare_tw_etfs.py`** - 台股 ETF 比較分析

### 🚀 執行程式
- **`run_all_tests.py`** - 執行所有測試的主程式

## 使用方法

### 執行所有測試
```bash
cd test
python run_all_tests.py
```

### 執行單個測試
```bash
# Notebook Import 測試
python test_notebook_imports.py

# 策略功能測試
python test_all_strategies.py

# 台股測試
python test_tw_stocks.py
```

### 快速台股測試
```bash
python quick_tw_test.py
```

## 測試內容

### 1. Notebook Import 測試
- ✅ 基本模組 (pandas, numpy, matplotlib)
- ✅ 策略模組 (所有交易策略)
- ✅ 核心模組 (回測引擎, 工具函數)
- ✅ 台股模組 (twstock 相關功能)
- ✅ 策略實例化測試
- ✅ 完整回測流程測試

### 2. 策略功能測試
- 📈 **SMA 交叉策略** - 移動平均線交叉
- 🐢 **海龜策略** - Donchian Channel 突破
- 📉 **回撤買入策略** - 趨勢回撤後買入
- 📊 **朱家泓策略** - 回後買上漲策略

### 3. 台股測試
- 🇹🇼 **0050** (元大台灣50)
- 🇹🇼 **006208** (富邦台50)  
- 🇹🇼 **2330** (台積電)
- 🇹🇼 **2317** (鴻海)
- 🇹🇼 **2454** (聯發科)

## 測試結果解讀

### 成功指標
- ✅ 所有 import 正常
- ✅ 策略可以正常實例化
- ✅ 回測可以正常執行
- ✅ 產生合理的績效指標

### 常見問題
- ❌ **ImportError** - 檢查模組路徑和類別名稱
- ❌ **KeyError** - 檢查資料欄位名稱
- ❌ **NetworkError** - 檢查網路連線
- ❌ **DataError** - 檢查市場資料可用性

## 注意事項

1. **網路需求**: 測試需要網路連線來獲取市場資料
2. **執行時間**: 完整測試可能需要數分鐘時間
3. **市場時間**: 台股測試結果可能因市場開閉時間而異
4. **資料更新**: Yahoo Finance 和 twstock 資料可能有延遲

## 測試環境要求

### 必要套件
```
pandas
numpy
matplotlib
yfinance
twstock
lxml
```

### Python 版本
- Python 3.8+
- 建議使用 Python 3.11

## 故障排除

### Import 錯誤
1. 確保在正確目錄執行 (`test/` 目錄下)
2. 檢查 `sys.path.append('..')` 是否正確
3. 確認所有套件已安裝

### 資料獲取錯誤
1. 檢查網路連線
2. 嘗試更換測試標的
3. 確認 Yahoo Finance API 可用

### 台股測試錯誤
1. 確認 twstock 套件已安裝
2. 檢查 lxml 相依套件
3. 嘗試更換台股標的

## 貢獻指南

添加新測試時請遵循:
1. 使用描述性的函數名稱
2. 添加適當的錯誤處理
3. 更新 README 文檔
4. 在 `run_all_tests.py` 中註冊新測試