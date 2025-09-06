#!/usr/bin/env python3
"""
富邦neo API 簡單測試程式
測試實際可用的功能
"""

import json
import os
import sys
from datetime import datetime

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


def test_basic_connection():
    """測試基本連線功能"""
    print("=" * 60)
    print("富邦 neo SDK 基本功能測試")
    print("=" * 60)
    
    if not FUBON_AVAILABLE:
        print("❌ 富邦 neo SDK 未安裝")
        return None
    
    config = load_config()
    fubon_config = config.get('fubon_api', {})
    
    if not fubon_config.get('enabled', False):
        print("❌ 富邦 API 未啟用")
        return None
    
    try:
        # 初始化SDK
        sdk = FubonSDK()
        print("✅ FubonSDK 初始化成功")
        
        # 檢查憑證檔案
        cert_path = fubon_config.get('cert_path', '')
        if not os.path.exists(cert_path):
            print(f"❌ 憑證檔案不存在: {cert_path}")
            return None
        else:
            print(f"✅ 憑證檔案存在: {cert_path}")
        
        # 嘗試登入
        print("🔐 嘗試登入...")
        accounts = sdk.login(
            fubon_config['account'],
            fubon_config['password'],
            fubon_config['cert_path'],
            fubon_config['cert_password']
        )
        
        if accounts.is_success:
            print("✅ 登入成功!")
            print(f"帳戶數量: {len(accounts.data)}")
            for i, account in enumerate(accounts.data):
                print(f"  帳戶 {i+1}: {account.name} - {account.account} ({account.account_type})")
            
            # 檢查SDK可用功能
            print(f"\n🔍 SDK 可用功能:")
            available_attrs = [attr for attr in dir(sdk) if not attr.startswith('_')]
            for attr in available_attrs:
                print(f"  - {attr}")
            
            # 測試即時行情初始化
            try:
                print(f"\n📊 嘗試初始化即時行情...")
                sdk.init_realtime()
                print("✅ 即時行情初始化成功")
            except Exception as e:
                print(f"❌ 即時行情初始化失敗: {e}")
            
            # 檢查股票相關功能
            if hasattr(sdk, 'stock'):
                print(f"\n📈 股票功能:")
                stock_obj = sdk.stock
                stock_attrs = [attr for attr in dir(stock_obj) if not attr.startswith('_')]
                for attr in stock_attrs:
                    print(f"  - {attr}")
            
            # 檢查帳務功能
            if hasattr(sdk, 'accounting'):
                print(f"\n💰 帳務功能:")
                accounting_obj = sdk.accounting
                accounting_attrs = [attr for attr in dir(accounting_obj) if not attr.startswith('_')]
                for attr in accounting_attrs:
                    print(f"  - {attr}")
            
            return sdk, accounts
            
        else:
            print(f"❌ 登入失敗: {accounts.message}")
            return None
            
    except Exception as e:
        print(f"❌ 連線測試失敗: {e}")
        return None


def test_account_info(sdk, accounts):
    """測試帳戶資訊查詢"""
    print(f"\n" + "=" * 60)
    print("帳戶資訊查詢測試")
    print("=" * 60)
    
    if not sdk or not accounts or not accounts.is_success:
        print("❌ 無有效的SDK或帳戶資訊")
        return
    
    account = accounts.data[0]  # 使用第一個帳戶
    
    try:
        # 測試庫存查詢
        if hasattr(sdk, 'accounting') and hasattr(sdk.accounting, 'inventories'):
            print("🔍 查詢庫存...")
            inventories = sdk.accounting.inventories(account)
            if inventories.is_success:
                print(f"✅ 庫存查詢成功，共 {len(inventories.data)} 筆")
                for i, inv in enumerate(inventories.data[:3]):  # 只顯示前3筆
                    print(f"  庫存 {i+1}: {inv}")
                    # 檢查庫存物件的屬性
                    print(f"    屬性: {[attr for attr in dir(inv) if not attr.startswith('_')]}")
            else:
                print(f"❌ 庫存查詢失敗: {inventories.message}")
        
        # 測試未實現損益
        if hasattr(sdk, 'accounting') and hasattr(sdk.accounting, 'unrealized_gains_and_loses'):
            print("📊 查詢未實現損益...")
            pnl = sdk.accounting.unrealized_gains_and_loses(account)
            if pnl.is_success:
                print(f"✅ 未實現損益查詢成功")
                if pnl.data:
                    print(f"  總計: {len(pnl.data)} 筆")
            else:
                print(f"❌ 未實現損益查詢失敗: {pnl.message}")
        
        # 測試股票報價功能
        if hasattr(sdk, 'stock'):
            test_symbols = ['2330', '00919']  # 台積電、華創
            for symbol in test_symbols:
                print(f"📈 查詢 {symbol} 報價...")
                try:
                    # 測試 query_symbol_quote
                    if hasattr(sdk.stock, 'query_symbol_quote'):
                        quote = sdk.stock.query_symbol_quote(account, symbol)
                        if quote.is_success:
                            print(f"  ✅ 報價查詢成功: {quote.data}")
                        else:
                            print(f"  ❌ 報價查詢失敗: {quote.message}")
                    
                    # 測試 query_symbol_snapshot
                    if hasattr(sdk.stock, 'query_symbol_snapshot'):
                        snapshot = sdk.stock.query_symbol_snapshot(account, symbol)
                        if snapshot.is_success:
                            print(f"  ✅ 快照查詢成功: {snapshot.data}")
                        else:
                            print(f"  ❌ 快照查詢失敗: {snapshot.message}")
                            
                except Exception as e:
                    print(f"  ❌ 查詢 {symbol} 失敗: {e}")
                
    except Exception as e:
        print(f"❌ 帳戶資訊查詢失敗: {e}")


def main():
    """主測試函數"""
    print("🚀 開始富邦 neo SDK 實際功能測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 基本連線測試
    result = test_basic_connection()
    
    if result:
        sdk, accounts = result
        
        # 帳戶資訊測試
        test_account_info(sdk, accounts)
        
        # 登出
        try:
            sdk.logout()
            print("\n✅ 登出成功")
        except Exception as e:
            print(f"\n⚠️ 登出時發生錯誤: {e}")
    
    print(f"\n" + "=" * 60)
    print("🏁 測試完成")
    print("=" * 60)


if __name__ == "__main__":
    main()