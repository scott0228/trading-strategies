#!/usr/bin/env python3
"""
富邦API資料獲取測試程式
測試富邦neo API的各項功能
"""

import json
import os
import sys
from datetime import datetime
import pandas as pd

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.fubon_data_fetcher import FubonDataFetcher, FUBON_AVAILABLE


def load_config():
    """載入配置檔案"""
    config_path = os.path.join(project_root, 'config', 'telegram_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def test_fubon_connection(config):
    """測試富邦API連線"""
    print("=" * 60)
    print("富邦 neo API 連線測試")
    print("=" * 60)
    
    if not FUBON_AVAILABLE:
        print("❌ 富邦 neo SDK 未安裝")
        return None
    
    fubon_config = config.get('fubon_api', {})
    if not fubon_config.get('enabled', False):
        print("❌ 富邦 API 未啟用")
        return None
    
    # 檢查必要參數
    required_fields = ['account', 'password', 'cert_path', 'cert_password']
    missing_fields = [field for field in required_fields if not fubon_config.get(field)]
    
    if missing_fields:
        print(f"❌ 缺少必要配置: {', '.join(missing_fields)}")
        return None
    
    try:
        # 建立富邦資料獲取器
        fetcher = FubonDataFetcher()
        
        # 嘗試登入
        login_success = fetcher.login(
            account=fubon_config['account'],
            password=fubon_config['password'],
            cert_path=fubon_config['cert_path'],
            cert_password=fubon_config['cert_password']
        )
        
        if login_success:
            print("✅ 富邦 API 連線成功")
            return fetcher
        else:
            print("❌ 富邦 API 登入失敗")
            return None
            
    except Exception as e:
        print(f"❌ 富邦 API 連線錯誤: {e}")
        return None


def test_historical_data(fetcher, test_symbols):
    """測試歷史資料獲取"""
    print("\n" + "=" * 60)
    print("歷史資料獲取測試")
    print("=" * 60)
    
    if not fetcher or not fetcher.logged_in:
        print("❌ 富邦 API 未登入，跳過歷史資料測試")
        return
    
    for symbol in test_symbols:
        print(f"\n🔍 測試 {symbol} 歷史資料獲取...")
        
        try:
            # 測試不同期間
            periods = ['3mo', '6mo', '1y']
            for period in periods:
                print(f"  期間: {period}")
                data = fetcher.fetch_historical_data(symbol, period)
                
                if data is not None and len(data) > 0:
                    print(f"    ✅ 成功獲取 {len(data)} 筆資料")
                    print(f"    📅 資料範圍: {data.index[0].date()} 至 {data.index[-1].date()}")
                    print(f"    📊 最新收盤價: ${data['Close'].iloc[-1]:.2f}")
                    
                    # 檢查資料完整性
                    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                    missing_cols = [col for col in required_cols if col not in data.columns]
                    if missing_cols:
                        print(f"    ⚠️ 缺少欄位: {missing_cols}")
                    else:
                        print(f"    ✅ 資料完整性檢查通過")
                else:
                    print(f"    ❌ 無法獲取資料")
                    
        except Exception as e:
            print(f"    ❌ 獲取失敗: {e}")


def test_real_time_quotes(fetcher, test_symbols):
    """測試即時報價"""
    print("\n" + "=" * 60)
    print("即時報價測試")
    print("=" * 60)
    
    if not fetcher or not fetcher.logged_in:
        print("❌ 富邦 API 未登入，跳過即時報價測試")
        return
    
    for symbol in test_symbols:
        print(f"\n📈 測試 {symbol} 即時報價...")
        
        try:
            quote = fetcher.get_current_quote(symbol)
            
            if quote:
                print(f"    ✅ 成功獲取即時報價")
                print(f"    💰 現價: ${quote['current_price']:.2f}")
                print(f"    📊 開盤: ${quote['open']:.2f}")
                print(f"    📈 最高: ${quote['high']:.2f}")
                print(f"    📉 最低: ${quote['low']:.2f}")
                print(f"    📦 成交量: {quote['volume']:,}")
                print(f"    🔄 漲跌: ${quote['change']:.2f} ({quote['change_percent']:.2f}%)")
                print(f"    ⏰ 時間: {quote['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"    ❌ 無法獲取即時報價")
                
        except Exception as e:
            print(f"    ❌ 獲取失敗: {e}")


def test_stock_info(fetcher, test_symbols):
    """測試股票基本資訊"""
    print("\n" + "=" * 60)
    print("股票基本資訊測試")
    print("=" * 60)
    
    if not fetcher or not fetcher.logged_in:
        print("❌ 富邦 API 未登入，跳過基本資訊測試")
        return
    
    for symbol in test_symbols:
        print(f"\n🏢 測試 {symbol} 基本資訊...")
        
        try:
            info = fetcher.get_stock_info(symbol)
            
            if info:
                print(f"    ✅ 成功獲取基本資訊")
                print(f"    🏷️ 代碼: {info['symbol']}")
                print(f"    📛 名稱: {info['name']}")
                print(f"    🏛️ 交易所: {info['exchange']}")
                print(f"    🏪 市場: {info['market']}")
                print(f"    📋 類型: {info['type']}")
                print(f"    🏭 產業: {info['industry']}")
            else:
                print(f"    ❌ 無法獲取基本資訊")
                
        except Exception as e:
            print(f"    ❌ 獲取失敗: {e}")


def test_market_status(fetcher):
    """測試市場狀態檢查"""
    print("\n" + "=" * 60)
    print("市場狀態檢查")
    print("=" * 60)
    
    if not fetcher:
        print("❌ 富邦 API 未初始化")
        return
    
    try:
        is_open = fetcher.is_market_open()
        current_time = datetime.now()
        
        print(f"📅 當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕘 週幾: {['週一', '週二', '週三', '週四', '週五', '週六', '週日'][current_time.weekday()]}")
        
        if is_open:
            print("✅ 台股市場 - 開市中")
        else:
            print("❌ 台股市場 - 休市中")
            
    except Exception as e:
        print(f"❌ 市場狀態檢查失敗: {e}")


def run_comprehensive_test():
    """執行完整測試"""
    print("🚀 開始富邦 neo API 功能測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 載入配置
    config = load_config()
    
    # 測試股票清單
    test_symbols = ['2330', '2454', '2881', '6505']  # 台積電、聯發科、富邦金、台達電
    
    # 建立連線
    fetcher = test_fubon_connection(config)
    
    # 執行各項測試
    test_historical_data(fetcher, test_symbols)
    test_real_time_quotes(fetcher, test_symbols)
    test_stock_info(fetcher, test_symbols)
    test_market_status(fetcher)
    
    # 關閉連線
    if fetcher:
        fetcher.close()
    
    print("\n" + "=" * 60)
    print("🏁 測試完成")
    print("=" * 60)


def quick_test():
    """快速測試單一功能"""
    print("🔥 富邦 API 快速測試")
    
    config = load_config()
    fetcher = test_fubon_connection(config)
    
    if fetcher and fetcher.logged_in:
        # 測試台積電資料
        print(f"\n📊 測試台積電(2330)資料獲取...")
        data = fetcher.fetch_historical_data('2330', '3mo')
        
        if data is not None:
            print(f"✅ 成功獲取 {len(data)} 筆歷史資料")
            print(f"📈 最新價格: ${data['Close'].iloc[-1]:.2f}")
            
            # 顯示最近5天資料
            print("\n最近5天收盤價:")
            recent_data = data.tail(5)
            for date, row in recent_data.iterrows():
                print(f"  {date.strftime('%Y-%m-%d')}: ${row['Close']:.2f}")
        
        fetcher.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        quick_test()
    else:
        run_comprehensive_test()