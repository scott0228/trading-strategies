#!/bin/bash

# 海龜策略每日訊號監控 - Crontab 設定腳本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONITOR_SCRIPT="$PROJECT_ROOT/scripts/daily_signal_monitor.py"
PYTHON_PATH="$(which python3)"

echo "=== 海龜策略監控 Crontab 設定 ==="
echo "專案路径: $PROJECT_ROOT"
echo "監控腳本: $MONITOR_SCRIPT"
echo "Python 路径: $PYTHON_PATH"
echo

# 檢查腳本是否存在
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "❌ 錯誤: 找不到監控腳本 $MONITOR_SCRIPT"
    exit 1
fi

# 檢查 Python 是否存在
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ 錯誤: 找不到 Python3"
    exit 1
fi

# 生成 crontab 條目
CRON_ENTRY="# 海龜策略每日訊號檢查 - 每個交易日 09:30 (台股開盤後)
30 9 * * 1-5 cd $PROJECT_ROOT && $PYTHON_PATH $MONITOR_SCRIPT >> $PROJECT_ROOT/logs/daily_monitor.log 2>&1

# 美股盤後檢查 - 每個交易日 05:30 (台北時間, 美股收盤後)
30 5 * * 2-6 cd $PROJECT_ROOT && $PYTHON_PATH $MONITOR_SCRIPT >> $PROJECT_ROOT/logs/daily_monitor.log 2>&1"

# 創建 logs 目錄
mkdir -p "$PROJECT_ROOT/logs"

# 顯示當前 crontab
echo "目前的 crontab 設定:"
crontab -l 2>/dev/null || echo "(無現有 crontab 設定)"
echo

# 詢問是否添加
echo "準備添加以下 crontab 條目:"
echo "$CRON_ENTRY"
echo
read -p "是否添加這些排程設定? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 備份現有 crontab
    BACKUP_FILE="$PROJECT_ROOT/crontab_backup_$(date +%Y%m%d_%H%M%S)"
    crontab -l > "$BACKUP_FILE" 2>/dev/null
    echo "✅ 現有 crontab 已備份至: $BACKUP_FILE"
    
    # 添加新的 crontab 條目
    (crontab -l 2>/dev/null; echo; echo "$CRON_ENTRY") | crontab -
    echo "✅ Crontab 設定已添加"
    echo
    echo "新的 crontab 設定:"
    crontab -l
    echo
    echo "📋 排程說明:"
    echo "  - 每個交易日 09:30 (台北時間) - 台股開盤後檢查"
    echo "  - 每個交易日 05:30 (台北時間) - 美股收盤後檢查"
    echo "  - 日誌檔案: $PROJECT_ROOT/logs/daily_monitor.log"
    echo
    echo "⚠️  記得設定 Telegram Bot Token 和 Chat ID:"
    echo "  1. 複製 config/telegram_config.json.example 為 config/telegram_config.json"
    echo "  2. 或設定環境變數 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID"
else
    echo "❌ 取消設定"
fi

echo
echo "=== 手動測試指令 ==="
echo "cd $PROJECT_ROOT && python3 scripts/daily_signal_monitor.py"