# 海龜策略每日監控與 Telegram 通知設定

## 功能說明

自動監控 CRWD 和 QQQ 的海龜策略交易訊號，當有買賣訊號時發送 Telegram 通知。

## 檔案結構

```
├── utils/
│   ├── telegram_notifier.py    # Telegram 通知功能
│   └── signal_checker.py       # 訊號檢查邏輯
├── scripts/
│   ├── daily_signal_monitor.py # 每日監控主程式
│   └── setup_crontab.sh       # Crontab 排程設定
├── config/
│   └── telegram_config.json.example  # Telegram 配置範例
└── .env.example               # 環境變數範例
```

## 設定步驟

### 1. 建立 Telegram Bot

1. 在 Telegram 中找到 @BotFather
2. 發送 `/newbot` 建立新機器人
3. 按指示設定機器人名稱
4. 獲取 Bot Token (格式: `123456789:ABCdefGHI...`)

### 2. 獲取 Chat ID

1. 將機器人加入群組或私訊機器人
2. 在瀏覽器開啟: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 找到 `"chat":{"id":...}` 的數字即為 Chat ID

### 3. 配置設定

**方法一: 使用配置檔案**
```bash
cp config/telegram_config.json.example config/telegram_config.json
# 編輯 config/telegram_config.json 填入 Bot Token 和 Chat ID
```

**方法二: 使用環境變數**
```bash
cp .env.example .env
# 編輯 .env 填入設定
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### 4. 測試運行

```bash
# 手動測試
python3 scripts/daily_signal_monitor.py
```

### 5. 設定排程

```bash
# 自動設定 crontab (推薦)
./scripts/setup_crontab.sh

# 或手動添加到 crontab
crontab -e
```

## 排程時間說明

- **09:30 (台北時間)**: 台股開盤後檢查
- **05:30 (台北時間)**: 美股收盤後檢查
- **僅工作日執行**: 週一到週五

## 通知內容

### 交易訊號通知
```
🟢 海龜策略交易訊號

📈 股票代號: CRWD
📊 訊號類型: 買入
💰 當前價格: $250.50
⏰ 時間: 2024-01-15 09:30:00

📅 訊號日期: 2024-01-15
📈 突破價位: $248.20

⚠️ 此為系統自動通知，請自行判斷投資決策
```

### 每日摘要
```
📊 每日海龜策略檢查摘要
⏰ 2024-01-15 09:30:00

🟢 CRWD: BUY @ $250.50
⚪ QQQ: 無訊號

📈 今日共 1 個交易訊號
```

## 故障排除

### 常見問題

1. **ModuleNotFoundError**: 確保在正確的虛擬環境中運行
2. **Telegram 通知失敗**: 檢查 Bot Token 和 Chat ID 是否正確
3. **數據獲取失敗**: 檢查網路連線和 Yahoo Finance API

### 除錯指令

```bash
# 檢查 crontab 設定
crontab -l

# 查看執行日誌
tail -f logs/daily_monitor.log

# 手動測試單一標的
python3 -c "
from utils.signal_checker import TurtleSignalChecker
checker = TurtleSignalChecker()
result = checker.check_latest_signal('CRWD')
print(result)
"
```

## 自訂設定

### 修改監控標的

編輯 `scripts/daily_signal_monitor.py` 中的 `symbols` 列表:

```python
symbols = ['CRWD', 'QQQ', 'AAPL', 'TSLA']  # 添加更多標的
```

### 調整檢查頻率

修改 crontab 時間設定或運行 `./scripts/setup_crontab.sh` 重新設定。

### 關閉每日摘要

在 `config/telegram_config.json` 中設定:
```json
{
  "send_daily_summary": false
}
```