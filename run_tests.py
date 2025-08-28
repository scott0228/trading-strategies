#!/usr/bin/env python3
"""
在根目錄執行測試的便利腳本
"""

import os
import sys
import subprocess


def main():
    """執行測試套件"""
    
    # 確保在正確目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(current_dir, 'test')
    
    if not os.path.exists(test_dir):
        print("❌ 找不到 test 目錄")
        return False
    
    # 切換到 test 目錄並執行測試
    original_dir = os.getcwd()
    
    try:
        os.chdir(test_dir)
        print(f"📂 切換到測試目錄: {test_dir}")
        
        # 執行完整測試套件
        result = subprocess.run([sys.executable, 'run_all_tests.py'], 
                              capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {e}")
        return False
        
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⛔ 測試被用戶中斷")
        sys.exit(1)