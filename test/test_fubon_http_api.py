#!/usr/bin/env python3
"""
測試富邦HTTP API獲取歷史資料
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    from fubon_neo.sdk import FubonSDK
    FUBON_AVAILABLE = True
except ImportError:
    FUBON_AVAILABLE = False


def load_config():
    """載入配置檔案"""
    config_path = os.path.join(project_root, 'config', 'telegram_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def test_fubon_historical_api():
    """測試富邦歷史資料API"""
    print("=" * 60)
    print("富邦歷史資料HTTP API測試")
    print("=" * 60)
    
    if not FUBON_AVAILABLE:
        print("❌ 富邦 neo SDK 未安裝")
        return
    
    config = load_config()
    fubon_config = config.get('fubon_api', {})
    
    try:
        # 初始化SDK並登入
        sdk = FubonSDK()
        print("✅ FubonSDK 初始化成功")
        
        accounts = sdk.login(
            fubon_config['account'],
            fubon_config['password'],
            fubon_config['cert_path'],
            fubon_config['cert_password']
        )
        
        if not accounts.is_success:
            print(f"❌ 登入失敗: {accounts.message}")
            return
        
        print("✅ 登入成功")
        
        # 初始化即時行情
        sdk.init_realtime()
        print("✅ 即時行情初始化成功")
        
        # 檢查SDK屬性
        print(f"\n🔍 檢查SDK屬性...")
        print(f"SDK屬性: {[attr for attr in dir(sdk) if not attr.startswith('_')]}")
        
        # 檢查是否有marketdata屬性
        if hasattr(sdk, 'marketdata'):
            print("✅ 找到 marketdata 屬性")
            marketdata = sdk.marketdata
            print(f"Marketdata 屬性: {[attr for attr in dir(marketdata) if not attr.startswith('_')]}")
            
            # 檢查是否有rest_client
            if hasattr(marketdata, 'rest_client'):
                print("✅ 找到 rest_client 屬性")
                rest_client = marketdata.rest_client
                print(f"RestClient 屬性: {[attr for attr in dir(rest_client) if not attr.startswith('_')]}")
                
                # 檢查是否有stock
                if hasattr(rest_client, 'stock'):
                    print("✅ 找到 stock 屬性")
                    stock = rest_client.stock
                    print(f"Stock 屬性: {[attr for attr in dir(stock) if not attr.startswith('_')]}")
                    
                    # 檢查是否有historical
                    if hasattr(stock, 'historical'):
                        print("✅ 找到 historical 屬性")
                        historical = stock.historical
                        print(f"Historical 屬性: {[attr for attr in dir(historical) if not attr.startswith('_')]}")
                        
                        # 測試獲取歷史資料
                        if hasattr(historical, 'candles'):
                            print("\n📊 測試獲取歷史K線資料...")
                            test_symbols = ['2330', '2454']
                            
                            for symbol in test_symbols:
                                print(f"\n--- 測試 {symbol} ---")
                                try:
                                    # 計算日期範圍 (最近3個月)
                                    end_date = datetime.now()
                                    start_date = end_date - timedelta(days=90)
                                    
                                    result = historical.candles(
                                        symbol=symbol,
                                        **{
                                            "from": start_date.strftime('%Y-%m-%d'),
                                            "to": end_date.strftime('%Y-%m-%d'),
                                            "timeframe": "D"  # 日K
                                        }
                                    )
                                    
                                    if result and hasattr(result, 'data') and result.data:
                                        print(f"✅ 成功獲取 {len(result.data)} 筆歷史資料")
                                        print(f"資料格式: {result.data[0] if result.data else 'N/A'}")
                                    elif result and hasattr(result, 'is_success'):
                                        print(f"❌ API調用失敗: {getattr(result, 'message', 'Unknown error')}")
                                    else:
                                        print(f"⚠️ 返回格式異常: {result}")
                                        
                                except Exception as e:
                                    print(f"❌ 獲取 {symbol} 歷史資料失敗: {e}")
                        else:
                            print("❌ 找不到 candles 方法")
                    else:
                        print("❌ 找不到 historical 屬性")
                else:
                    print("❌ 找不到 stock 屬性")
            else:
                print("❌ 找不到 rest_client 屬性")
        else:
            print("❌ 找不到 marketdata 屬性")
        
        # 登出
        sdk.logout()
        print("\n✅ 測試完成，已登出")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")


def main():
    """主函數"""
    print("🚀 開始富邦歷史資料HTTP API測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_fubon_historical_api()
    
    print(f"\n" + "=" * 60)
    print("🏁 測試完成")
    print("=" * 60)


if __name__ == "__main__":
    main()