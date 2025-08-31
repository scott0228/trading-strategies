import requests
import json
import os
from typing import Optional
from datetime import datetime


class TelegramNotifier:
    """Telegram 通知發送器"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """發送 Telegram 訊息"""
        if not self.bot_token or not self.chat_id:
            print("❌ Telegram bot token 或 chat ID 未設定")
            return False
            
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            print("✅ Telegram 訊息發送成功")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Telegram 訊息發送失敗: {e}")
            return False
    
    def send_trading_signal(self, symbol: str, signal_type: str, 
                          current_price: float, additional_info: str = "") -> bool:
        """發送交易訊號通知"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 使用不同的 emoji 表示買賣訊號
        emoji = "🟢" if signal_type.upper() == "BUY" else "🔴"
        action = "買入" if signal_type.upper() == "BUY" else "賣出"
        
        message = f"""
{emoji} *海龜策略交易訊號*

📈 股票代號: `{symbol}`
📊 訊號類型: *{action}*
💰 當前價格: `${current_price:.2f}`
⏰ 時間: `{timestamp}`

{additional_info}

⚠️ *此為系統自動通知，請自行判斷投資決策*
        """.strip()
        
        return self.send_message(message)
    
    def send_daily_summary(self, symbols: list, results: dict) -> bool:
        """發送每日檢查摘要"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"📊 *每日海龜策略檢查摘要*\n⏰ {timestamp}\n\n"
        
        signal_count = 0
        for symbol in symbols:
            if symbol in results:
                result = results[symbol]
                if result['has_signal']:
                    signal_count += 1
                    emoji = "🟢" if result['signal_type'] == "BUY" else "🔴"
                    message += f"{emoji} `{symbol}`: {result['signal_type']} @ ${result['price']:.2f}\n"
                else:
                    message += f"⚪ `{symbol}`: 無訊號\n"
        
        if signal_count == 0:
            message += "\n✅ 今日無交易訊號"
        else:
            message += f"\n📈 今日共 {signal_count} 個交易訊號"
            
        return self.send_message(message)