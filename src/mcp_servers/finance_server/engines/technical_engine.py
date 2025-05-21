"""
Technical analysis engine for financial data

This module provides functions for calculating technical indicators
and performing technical analysis on price data.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any


class TechnicalAnalysisEngine:
    """
    Engine for technical analysis of price data
    """
    
    def process_indicators(self, price_df: pd.DataFrame, indicators: List[str]) -> Dict[str, Any]:
        """
        Calculate technical indicators for price data
        
        Args:
            price_df: DataFrame with price data (must contain OHLC data)
            indicators: List of indicators to calculate
            
        Returns:
            Dictionary with calculated indicators
        """
        result = {"indicators": {}}
        
        # Make sure we have the right column names
        # Handle both English and Chinese column names
        required_cols = {
            'open': ['open', 'Open', '开盘', '开盘价'],
            'high': ['high', 'High', '高', '最高价'],
            'low': ['low', 'Low', '低', '最低价'],
            'close': ['close', 'Close', '收盘', '收盘价'],
            'volume': ['volume', 'Volume', '成交量', '成交额']
        }
        
        # Standardize column names
        column_mapping = {}
        for std_name, possible_names in required_cols.items():
            for col_name in possible_names:
                if col_name in price_df.columns:
                    column_mapping[col_name] = std_name
                    break
        
        # If we don't have all required columns, return error
        if len(column_mapping) < 4:  # Need at least OHLC
            return {"error": "Price data missing required columns (OHLC)"}
        
        # Create copy with standardized columns
        df = price_df.rename(columns=column_mapping).copy()
        
        # Convert index to datetime if not already
        if not isinstance(df.index, pd.DatetimeIndex):
            # Try to find date column
            date_cols = [col for col in df.columns if any(date_term in col.lower() 
                        for date_term in ['date', 'time', '日期', '时间'])]
            
            if date_cols:
                df.set_index(date_cols[0], inplace=True)
                try:
                    df.index = pd.to_datetime(df.index)
                except:
                    pass
        
        # Process each requested indicator
        for indicator in indicators:
            try:
                if indicator.upper() == 'MA':
                    # Moving Averages (5, 10, 20, 60 days)
                    periods = [5, 10, 20, 60]
                    ma_dict = {}
                    for period in periods:
                        ma_dict[f'MA{period}'] = df['close'].rolling(window=period).mean().tolist()
                    result["indicators"]["MA"] = ma_dict
                
                elif indicator.upper() == 'EMA':
                    # Exponential Moving Averages (5, 10, 20, 60 days)
                    periods = [5, 10, 20, 60]
                    ema_dict = {}
                    for period in periods:
                        ema_dict[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean().tolist()
                    result["indicators"]["EMA"] = ema_dict
                
                elif indicator.upper() == 'MACD':
                    # MACD (12, 26, 9)
                    ema12 = df['close'].ewm(span=12, adjust=False).mean()
                    ema26 = df['close'].ewm(span=26, adjust=False).mean()
                    macd_line = ema12 - ema26
                    signal_line = macd_line.ewm(span=9, adjust=False).mean()
                    histogram = macd_line - signal_line
                    
                    result["indicators"]["MACD"] = {
                        "macd_line": macd_line.tolist(),
                        "signal_line": signal_line.tolist(),
                        "histogram": histogram.tolist()
                    }
                
                elif indicator.upper() == 'RSI':
                    # RSI (14 days)
                    delta = df['close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    
                    avg_gain = gain.rolling(window=14).mean()
                    avg_loss = loss.rolling(window=14).mean()
                    
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    
                    result["indicators"]["RSI"] = rsi.tolist()
                
                elif indicator.upper() == 'BOLLINGER':
                    # Bollinger Bands (20, 2)
                    period = 20
                    std_dev = 2
                    
                    sma = df['close'].rolling(window=period).mean()
                    rolling_std = df['close'].rolling(window=period).std()
                    
                    upper_band = sma + (rolling_std * std_dev)
                    lower_band = sma - (rolling_std * std_dev)
                    
                    result["indicators"]["BOLLINGER"] = {
                        "middle_band": sma.tolist(),
                        "upper_band": upper_band.tolist(),
                        "lower_band": lower_band.tolist()
                    }
                
                elif indicator.upper() == 'ATR':
                    # Average True Range (14 days)
                    period = 14
                    
                    # Calculate True Range
                    tr1 = df['high'] - df['low']
                    tr2 = abs(df['high'] - df['close'].shift())
                    tr3 = abs(df['low'] - df['close'].shift())
                    
                    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
                    atr = tr.rolling(window=period).mean()
                    
                    result["indicators"]["ATR"] = atr.tolist()
                
                elif indicator.upper() == 'STOCHASTIC':
                    # Stochastic Oscillator (14, 3, 3)
                    k_period = 14
                    d_period = 3
                    
                    low_min = df['low'].rolling(window=k_period).min()
                    high_max = df['high'].rolling(window=k_period).max()
                    
                    k = 100 * ((df['close'] - low_min) / (high_max - low_min))
                    d = k.rolling(window=d_period).mean()
                    
                    result["indicators"]["STOCHASTIC"] = {
                        "k_line": k.tolist(),
                        "d_line": d.tolist()
                    }
                    
                elif indicator.upper() == 'OBV':
                    # On-Balance Volume
                    if 'volume' in df.columns:
                        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
                        result["indicators"]["OBV"] = obv.tolist()
                    else:
                        result["indicators"]["OBV"] = {"error": "Volume data not available"}
                
            except Exception as e:
                result["indicators"][indicator] = {"error": str(e)}
        
        # Add dates for reference
        try:
            if isinstance(df.index, pd.DatetimeIndex):
                result["dates"] = df.index.strftime('%Y-%m-%d').tolist()
            elif 'date' in df.columns:
                result["dates"] = df['date'].tolist()
            else:
                # Just use integers if no date information
                result["dates"] = list(range(len(df)))
        except:
            result["dates"] = list(range(len(df)))
        
        return result 