"""
Finance tools implementation for DeerFlow

This module implements tools that communicate with the Finance MCP Server,
providing financial data and analysis capabilities to DeerFlow agents.
"""
import os
import sys
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Callable
from functools import wraps

# Add parent directory to path to allow importing from mcp_servers
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.mcp_servers.finance_server.integration import FinanceServerIntegration

# Initialize the Finance MCP Server integration
_finance_integration = FinanceServerIntegration()
_initialized = False

# Initialize the server
async def _init_server():
    """Initialize the finance server and mark it as initialized"""
    global _initialized
    await _finance_integration.start_server()
    _initialized = True

# Singleton integration instance
def get_finance_integration():
    """Get or create the Finance MCP Server integration instance"""
    global _finance_integration, _initialized
    if not _initialized:
        # Just create a flag to note that we should initialize
        # The actual initialization will happen in the finance_tool decorator
        pass
    return _finance_integration


def finance_tool(func: Callable) -> Callable:
    """
    Decorator for finance tools that handles asynchronous execution
    and connection to the Finance MCP Server.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Get integration
        integration = get_finance_integration()
        
        # Initialize the server if needed
        global _initialized
        if not _initialized:
            await _init_server()
        
        # Run the function
        return await func(integration, *args, **kwargs)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Run the async wrapper in a new event loop
        return asyncio.run(async_wrapper(*args, **kwargs))
    
    # Add metadata for the tool
    if not hasattr(wrapper, "metadata"):
        wrapper.metadata = getattr(func, "metadata", {})
    
    return wrapper


@finance_tool
async def get_stock_info_tool(integration, symbol: str, market: Optional[str] = None) -> str:
    """
    Get basic information about a stock
    
    Args:
        symbol: Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'
        market: Stock market: A for A-shares, HK for Hong Kong stocks
    
    Returns:
        JSON string with stock information
    """
    success, result = await integration.send_request(
        "get_stock_info", 
        {"symbol": symbol, "market": market}
    )
    
    if success:
        return json.dumps(result, indent=2, ensure_ascii=False)
    else:
        error_message = result.get("message", "Unknown error")
        return f"Error retrieving stock information: {error_message}"


@finance_tool
async def get_stock_price_tool(
    integration, 
    symbol: str, 
    period: str = "daily", 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> str:
    """
    Get historical price data for a stock
    
    Args:
        symbol: Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'
        period: Data frequency (daily, weekly, monthly)
        start_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format
    
    Returns:
        JSON string with price data
    """
    params = {
        "symbol": symbol,
        "period": period
    }
    
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
        
    success, result = await integration.send_request("get_stock_price", params)
    
    if success:
        # Limit to first 30 records for readability
        limited_result = result[:30] if isinstance(result, list) and len(result) > 30 else result
        return json.dumps(limited_result, indent=2, ensure_ascii=False)
    else:
        error_message = result.get("message", "Unknown error")
        return f"Error retrieving stock prices: {error_message}"


@finance_tool
async def get_financial_report_tool(
    integration, 
    symbol: str, 
    report_type: str, 
    periods: int = 4
) -> str:
    """
    Get financial report data for a company
    
    Args:
        symbol: Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'
        report_type: Report type (balance, income, cashflow, all)
        periods: Number of reporting periods to retrieve
    
    Returns:
        JSON string with financial report data
    """
    params = {
        "symbol": symbol,
        "report_type": report_type,
        "periods": periods
    }
        
    success, result = await integration.send_request("get_financial_report", params)
    
    if success:
        return json.dumps(result, indent=2, ensure_ascii=False)
    else:
        error_message = result.get("message", "Unknown error")
        return f"Error retrieving financial report: {error_message}"


@finance_tool
async def analyze_financials_tool(
    integration, 
    symbol: str, 
    include_market_ratios: bool = True
) -> str:
    """
    Analyze financial statements and calculate financial ratios
    
    Args:
        symbol: Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'
        include_market_ratios: Whether to include market-based ratios
    
    Returns:
        JSON string with financial analysis results
    """
    params = {
        "symbol": symbol,
        "include_market_ratios": include_market_ratios
    }
        
    success, result = await integration.send_request("analyze_financials", params)
    
    if success:
        return json.dumps(result, indent=2, ensure_ascii=False)
    else:
        error_message = result.get("message", "Unknown error")
        return f"Error analyzing financials: {error_message}"


@finance_tool
async def get_technical_indicators_tool(
    integration, 
    symbol: str, 
    indicators: List[str] = None, 
    period: str = "daily"
) -> str:
    """
    Calculate technical indicators for a stock
    
    Args:
        symbol: Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'
        indicators: List of indicators to calculate (MA, MACD, RSI, KDJ, BOLL)
        period: Data frequency (daily, weekly, monthly)
    
    Returns:
        JSON string with calculated indicators
    """
    if indicators is None:
        indicators = ["MA", "MACD", "RSI"]
        
    params = {
        "symbol": symbol,
        "indicators": indicators,
        "period": period
    }
        
    success, result = await integration.send_request("calc_technical_indicators", params)
    
    if success:
        return json.dumps(result, indent=2, ensure_ascii=False)
    else:
        error_message = result.get("message", "Unknown error")
        return f"Error calculating technical indicators: {error_message}"


@finance_tool
async def get_investment_recommendation_tool(integration, symbol: str) -> str:
    """
    Generate an investment recommendation based on comprehensive analysis
    
    Args:
        symbol: Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'
    
    Returns:
        JSON string with investment recommendation
    """
    # This uses the high-level function from the integration
    result = await integration.get_investment_recommendation(symbol)
    return json.dumps(result, indent=2, ensure_ascii=False)


# List of all finance tools
finance_tools_list = [
    get_stock_info_tool,
    get_stock_price_tool,
    get_financial_report_tool,
    analyze_financials_tool,
    get_technical_indicators_tool,
    get_investment_recommendation_tool
] 