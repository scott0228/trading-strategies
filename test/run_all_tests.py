#!/usr/bin/env python3
"""
執行所有測試的主程式
"""

import sys
import os
import time
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.append('..')

def run_test_module(module_name, description):
    """執行單個測試模組"""
    print(f"\n{'='*80}")
    print(f"🧪 {description}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        if module_name == "test_notebook_imports":
            from test_notebook_imports import main
        elif module_name == "test_all_strategies":
            from test_all_strategies import main
        elif module_name == "test_tw_stocks":
            from test_tw_stocks import main
        else:
            print(f"❌ 未知的測試模組: {module_name}")
            return False
        
        success = main()
        end_time = time.time()
        
        duration = end_time - start_time
        if success:
            print(f"✅ {description} 通過 (耗時: {duration:.2f}秒)")
        else:
            print(f"❌ {description} 失敗 (耗時: {duration:.2f}秒)")
        
        return success
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ {description} 執行錯誤: {e} (耗時: {duration:.2f}秒)")
        return False


def main():
    """執行所有測試"""
    
    print("🚀 開始執行完整測試套件")
    print(f"⏰ 測試開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定義所有測試
    tests = [
        ("test_notebook_imports", "Jupyter Notebook Import 測試"),
        ("test_all_strategies", "所有交易策略功能測試"),
        ("test_tw_stocks", "台股交易策略測試")
    ]
    
    results = {}
    total_start_time = time.time()
    
    # 執行所有測試
    for test_module, test_description in tests:
        result = run_test_module(test_module, test_description)
        results[test_description] = result
        
        # 測試之間稍作停頓
        time.sleep(1)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # 生成測試報告
    print(f"\n{'='*100}")
    print("🏁 測試套件執行完成")
    print(f"{'='*100}")
    
    print(f"⏰ 總執行時間: {total_duration:.2f} 秒")
    print(f"🕒 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 統計結果
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\n📊 測試結果統計:")
    print(f"   總測試數: {total}")
    print(f"   通過數: {passed}")
    print(f"   失敗數: {total - passed}")
    print(f"   成功率: {passed/total*100:.1f}%")
    
    # 詳細結果
    print(f"\n📋 詳細結果:")
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"   {test_name}: {status}")
    
    # 總結
    if passed == total:
        print(f"\n🎉 所有測試通過！系統運作正常")
        print(f"✨ 可以開始使用交易策略回測系統")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗")
        print(f"🔧 請檢查失敗的測試並修正問題")
        return False


def show_help():
    """顯示使用說明"""
    print("""
🔧 測試套件使用說明
==================

執行所有測試:
  python run_all_tests.py

單獨執行測試:
  python test_notebook_imports.py    # Notebook Import 測試
  python test_all_strategies.py      # 策略功能測試
  python test_tw_stocks.py          # 台股測試

測試內容:
  1. Import 模組測試 - 檢查所有必要模組是否正確匯入
  2. 策略功能測試 - 測試所有交易策略的完整功能
  3. 台股系統測試 - 測試台股資料獲取和策略回測

注意事項:
  - 測試需要網路連線以獲取市場資料
  - 台股測試可能需要較長時間
  - 部分測試結果可能因市場狀況而異
    """)


if __name__ == "__main__":
    try:
        # 檢查命令列參數
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
            show_help()
            sys.exit(0)
        
        # 執行測試
        success = main()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n⛔ 測試被用戶中斷")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 測試執行過程發生未預期錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)