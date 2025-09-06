#!/usr/bin/env python3
"""
富邦API資料獲取模組
用於獲取台股歷史資料和即時報價
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

try:
    from fubon_neo.constant import (BSAction, MarketType, OrderType, PriceType,
                                    TimeInForce)
    from fubon_neo.sdk import FubonSDK
    FUBON_AVAILABLE = True
except ImportError:
    FUBON_AVAILABLE = False
    print("警告: 富邦 neo API SDK 未安裝，台股資料獲取功能將不可用")


class FubonDataFetcher:
    """富邦API資料獲取器"""
    
    def __init__(self, account=None, password=None, cert_path=None, cert_password=None):
        self.sdk = None
        self.accounts = None
        self.rest_stock = None
        self.logged_in = False
        
        if not FUBON_AVAILABLE:
            raise ImportError("富邦 neo API SDK 未安裝，請先安裝 fubon_neo 套件")
        
        # 初始化 SDK
        try:
            self.sdk = FubonSDK()
            if account and password and cert_path and cert_password:
                self.login(account, password, cert_path, cert_password)
        except Exception as e:
            print(f"初始化富邦 SDK 失敗: {e}")
    
    def login(self, account: str, password: str, cert_path: str, cert_password: str) -> bool:
        """登入富邦帳戶"""
        try:
            # 檢查憑證檔案是否存在
            if not os.path.exists(cert_path):
                print(f"富邦 API 登入失敗: 憑證檔案不存在 {cert_path}")
                self.logged_in = False
                return False
            
            self.accounts = self.sdk.login(account, password, cert_path, cert_password)
            print(f"富邦 API 登入成功: {self.accounts}")
            
            # 嘗試初始化即時行情
            try:
                self.sdk.init_realtime()
                print("即時行情初始化成功")
            except Exception as realtime_error:
                print(f"即時行情初始化失敗: {realtime_error}")
            
            # 檢查並初始化歷史資料API
            try:
                if hasattr(self.sdk, 'marketdata'):
                    marketdata = self.sdk.marketdata
                    if hasattr(marketdata, 'rest_client'):
                        rest_client = marketdata.rest_client
                        if hasattr(rest_client, 'stock'):
                            stock = rest_client.stock
                            if hasattr(stock, 'historical'):
                                self.rest_stock = stock
                                print("✅ 歷史資料API初始化成功")
                            else:
                                print("⚠️ 找不到historical API")
                        else:
                            print("⚠️ 找不到stock API")
                    else:
                        print("⚠️ 找不到rest_client")
                else:
                    print("⚠️ 找不到marketdata")
                    
                self.logged_in = True
                return True
                
            except Exception as api_error:
                print(f"API初始化失敗: {api_error}")
                self.logged_in = True
                self.rest_stock = None
                return True
                
        except Exception as e:
            print(f"富邦 API 登入失敗: {e}")
            self.logged_in = False
            return False
    
    def fetch_historical_data(self, symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
        """
        獲取台股歷史資料
        
        Args:
            symbol: 台股代碼 (如 "2330")
            period: 資料期間 (目前富邦API限制為1年內)
        
        Returns:
            包含 OHLCV 資料的 DataFrame
        """
        if not self.logged_in:
            print("錯誤: 富邦 API 未登入")
            return None
        
        # 檢查是否有歷史資料API
        if not self.rest_stock or not hasattr(self.rest_stock, 'historical'):
            print(f"警告: 富邦歷史資料API不可用，{symbol} 無法取得歷史資料")
            return None
        
        try:
            # 計算日期範圍
            end_date = datetime.now()
            if period == '1y':
                start_date = end_date - timedelta(days=365)
            elif period == '6mo':
                start_date = end_date - timedelta(days=180)
            elif period == '3mo':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=365)  # 預設一年
            
            # 格式化日期
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # 使用富邦歷史資料API獲取K線資料
            result = self.rest_stock.historical.candles(
                symbol=symbol,
                **{
                    "from": from_date,
                    "to": to_date,
                    "timeframe": "D"  # 日K線
                }
            )
            
            # 檢查返回結果
            if not result or not result.get('data'):
                print(f"警告: {symbol} 無歷史資料")
                return None
            
            # 轉換為 DataFrame
            candle_data = result['data']
            df = pd.DataFrame(candle_data)
            
            # 標準化欄位名稱
            column_mapping = {
                'date': 'Date',
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            
            # 重新命名欄位
            df = df.rename(columns=column_mapping)
            
            # 確保日期為 datetime 格式
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
            
            # 確保數值欄位為浮點數
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 排序
            df = df.sort_index()
            
            print(f"✅ {symbol} 獲取 {len(df)} 筆富邦歷史資料")
            return df
            
        except Exception as e:
            print(f"獲取 {symbol} 富邦歷史資料失敗: {e}")
            return None
    
    def get_current_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        獲取即時報價（使用富邦SDK的實際功能）
        
        Args:
            symbol: 台股代碼
        
        Returns:
            包含即時報價資訊的字典
        """
        if not self.logged_in or not self.accounts:
            print("錯誤: 富邦 API 未登入")
            return None
        
        try:
            account = self.accounts.data[0]  # 使用第一個帳戶
            
            # 使用 query_symbol_quote 獲取報價
            if hasattr(self.sdk, 'stock') and hasattr(self.sdk.stock, 'query_symbol_quote'):
                quote_result = self.sdk.stock.query_symbol_quote(account, symbol)
                
                if quote_result.is_success and quote_result.data:
                    quote_data = quote_result.data
                    
                    # 提取有效的報價資料
                    return {
                        'symbol': symbol,
                        'current_price': quote_data.last_price if quote_data.last_price else quote_data.reference_price,
                        'reference_price': quote_data.reference_price,
                        'open': quote_data.open_price,
                        'high': quote_data.high_price,
                        'low': quote_data.low_price,
                        'volume': quote_data.total_volume,
                        'bid_price': quote_data.bid_price,
                        'bid_volume': quote_data.bid_volume,
                        'ask_price': quote_data.ask_price,
                        'ask_volume': quote_data.ask_volume,
                        'status': quote_data.status,
                        'market': quote_data.market,
                        'timestamp': datetime.now()
                    }
                else:
                    print(f"警告: {symbol} 報價查詢失敗: {quote_result.message}")
                    return None
            else:
                print("警告: 富邦SDK不支援報價查詢功能")
                return None
                
        except Exception as e:
            print(f"獲取 {symbol} 即時報價失敗: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        獲取股票基本資訊
        
        Args:
            symbol: 台股代碼
        
        Returns:
            股票基本資訊字典
        """
        if not self.logged_in:
            print("錯誤: 富邦 API 未登入")
            return None
        
        try:
            # 富邦SDK的報價資料包含部分基本資訊
            quote = self.get_current_quote(symbol)
            if quote:
                return {
                    'symbol': symbol,
                    'market': quote.get('market', ''),
                    'status': quote.get('status', ''),
                    'reference_price': quote.get('reference_price', 0)
                }
            else:
                return None
                
        except Exception as e:
            print(f"獲取 {symbol} 基本資訊失敗: {e}")
            return None
    
    def is_market_open(self) -> bool:
        """檢查台股市場是否開市"""
        now = datetime.now()
        
        # 檢查是否為週末
        if now.weekday() >= 5:  # 週六、週日
            return False
        
        # 檢查交易時間 (9:00-13:30)
        market_open = now.replace(hour=9, minute=0, second=0)
        market_close = now.replace(hour=13, minute=30, second=0)
        
        return market_open <= now <= market_close
    
    def close(self):
        """關閉連線"""
        if self.sdk:
            try:
                # 富邦SDK沒有明確的關閉方法，這裡重置狀態
                self.logged_in = False
                self.accounts = None
                self.rest_stock = None
                print("富邦 API 連線已關閉")
            except Exception as e:
                print(f"關閉富邦 API 連線時發生錯誤: {e}")


# 工具函數
def create_fubon_fetcher(config: Dict[str, Any]) -> Optional[FubonDataFetcher]:
    """
    根據設定建立富邦資料獲取器
    
    Args:
        config: 包含富邦API設定的字典
    
    Returns:
        FubonDataFetcher 實例或 None
    """
    if not FUBON_AVAILABLE:
        return None
    
    fubon_config = config.get('fubon_api', {})
    if not fubon_config.get('enabled', False):
        return None
    
    try:
        fetcher = FubonDataFetcher()
        
        # 如果有登入資訊，嘗試登入
        account = fubon_config.get('account')
        password = fubon_config.get('password') 
        cert_path = fubon_config.get('cert_path')
        cert_password = fubon_config.get('cert_password')
        
        if all([account, password, cert_path, cert_password]):
            if fetcher.login(account, password, cert_path, cert_password):
                return fetcher
        
        # 如果沒有登入資訊或登入失敗，返回未登入的實例
        return fetcher
        
    except Exception as e:
        print(f"建立富邦資料獲取器失敗: {e}")
        return None