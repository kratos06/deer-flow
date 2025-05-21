"""
Demo script for the Finance MCP Server

This script demonstrates the capabilities of the Finance MCP Server
by running a series of example queries and displaying the results.
"""
import asyncio
import json
from client_example import FinanceMCPClient


async def run_stock_info_demo(client: FinanceMCPClient):
    """Run stock info demo"""
    print("\n===== Stock Info Demo =====")
    print("Getting basic information for Maotai (600519)...")
    
    stock_info = await client.get_stock_info("600519", "A")
    print(json.dumps(stock_info, indent=2, ensure_ascii=False))
    
    print("\nGetting basic information for Tencent (00700, HK)...")
    hk_stock_info = await client.get_stock_info("00700", "HK")
    print(json.dumps(hk_stock_info, indent=2, ensure_ascii=False))


async def run_stock_price_demo(client: FinanceMCPClient):
    """Run stock price demo"""
    print("\n===== Stock Price Demo =====")
    print("Getting recent daily prices for Maotai (600519)...")
    
    stock_prices = await client.get_stock_price("600519", "daily")
    # Show only first 3 records for brevity
    print(json.dumps(stock_prices[:3], indent=2, ensure_ascii=False))


async def run_financial_report_demo(client: FinanceMCPClient):
    """Run financial report demo"""
    print("\n===== Financial Report Demo =====")
    print("Getting balance sheet for Maotai (600519)...")
    
    balance_sheet = await client.get_financial_report("600519", "balance", 1)
    # Show only keys for brevity
    if "balance_sheet" in balance_sheet and balance_sheet["balance_sheet"]:
        print("Balance sheet fields:")
        keys = list(balance_sheet["balance_sheet"][0].keys())
        print(", ".join(keys[:10]) + "...")  # First 10 keys
    
    print("\nGetting income statement for Maotai (600519)...")
    income_stmt = await client.get_financial_report("600519", "income", 1)
    # Show only keys for brevity
    if "income_statement" in income_stmt and income_stmt["income_statement"]:
        print("Income statement fields:")
        keys = list(income_stmt["income_statement"][0].keys())
        print(", ".join(keys[:10]) + "...")  # First 10 keys


async def run_technical_analysis_demo(client: FinanceMCPClient):
    """Run technical analysis demo"""
    print("\n===== Technical Analysis Demo =====")
    print("Calculating technical indicators for Maotai (600519)...")
    
    indicators = await client.calc_technical_indicators("600519", ["MA", "MACD", "RSI"])
    
    # Show simple moving averages
    if "MA" in indicators and "MA5" in indicators["MA"]:
        print("\nMA5 (first 5 values):")
        print(indicators["MA"]["MA5"][:5])
        
    # Show MACD
    if "MACD" in indicators:
        print("\nMACD Line (first 5 values):")
        print(indicators["MACD"]["macd_line"][:5])
        
    # Show RSI
    if "RSI" in indicators:
        print("\nRSI (first 5 values):")
        print(indicators["RSI"]["rsi"][:5])


async def run_fundamental_analysis_demo(client: FinanceMCPClient):
    """Run fundamental analysis demo"""
    print("\n===== Fundamental Analysis Demo =====")
    print("Analyzing financial ratios for Maotai (600519)...")
    
    analysis = await client.analyze_financials("600519")
    
    # Show profitability ratios
    if "profitability_ratios" in analysis:
        print("\nProfitability Ratios:")
        print(json.dumps(analysis["profitability_ratios"], indent=2, ensure_ascii=False))
        
    # Show liquidity ratios
    if "liquidity_ratios" in analysis:
        print("\nLiquidity Ratios:")
        print(json.dumps(analysis["liquidity_ratios"], indent=2, ensure_ascii=False))
        
    # Show solvency ratios
    if "solvency_ratios" in analysis:
        print("\nSolvency Ratios:")
        print(json.dumps(analysis["solvency_ratios"], indent=2, ensure_ascii=False))


async def main():
    """Main demo function"""
    print("Finance MCP Server Demonstration")
    print("--------------------------------")
    
    # Create client
    client = FinanceMCPClient()
    
    try:
        # Run demos
        await run_stock_info_demo(client)
        await run_stock_price_demo(client)
        await run_financial_report_demo(client)
        await run_technical_analysis_demo(client)
        await run_fundamental_analysis_demo(client)
        
    except Exception as e:
        print(f"Error during demo: {str(e)}")
    finally:
        # Stop server
        await client.stop_server()
        print("\nDemo complete. Server stopped.")


if __name__ == "__main__":
    asyncio.run(main()) 