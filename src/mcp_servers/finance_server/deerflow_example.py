"""
Example integration of Finance MCP Server with DeerFlow

This script demonstrates how to integrate the Finance MCP Server
with the DeerFlow framework for AI-driven financial research.
"""
import os
import sys
import asyncio
import json
from typing import Dict, Any, List

# Adjust path to find modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Finance MCP Server integration
from mcp_servers.finance_server.integration import FinanceServerIntegration


class DeerFlowSimulator:
    """
    Simulates the DeerFlow framework for demonstration purposes
    
    In a real implementation, this would be replaced with actual DeerFlow classes.
    """
    
    def __init__(self):
        """Initialize the DeerFlow simulator"""
        self.mcp_servers = {}
        self.available_tools = {}
        
    def register_mcp_server(self, name: str, description: str, tools: List[str], integration: Any) -> None:
        """
        Register an MCP server with the framework
        
        Args:
            name: Name of the MCP server
            description: Description of the MCP server
            tools: List of tool names provided by the server
            integration: Integration object for the server
        """
        self.mcp_servers[name] = {
            "description": description,
            "tools": tools,
            "integration": integration
        }
        
        print(f"Registered MCP server: {name}")
        print(f"Available tools: {', '.join(tools)}")
    
    async def run_agent_simulation(self) -> None:
        """
        Simulate an agent using the Finance MCP Server
        
        This method demonstrates how a DeerFlow agent might interact
        with the Finance MCP Server to perform financial research.
        """
        print("\n=== DeerFlow Agent Simulation ===")
        print("Agent: I need to analyze Maotai (600519) for potential investment.")
        
        # Check if finance server is registered
        if "finance" not in self.mcp_servers:
            print("Agent: Finance MCP Server not available.")
            return
            
        finance_integration = self.mcp_servers["finance"]["integration"]
        
        # Step 1: Get basic stock information
        print("\nAgent: Getting basic information about Maotai...")
        success, stock_info = await finance_integration.send_request(
            "get_stock_info", 
            {"symbol": "600519", "market": "A"}
        )
        
        if success:
            # Format data for agent consumption
            formatted_info = await finance_integration.format_stock_data_for_deerflow(stock_info)
            print(f"Agent: Received basic information about Maotai.")
            print(f"Company name: {stock_info.get('公司名称', 'N/A')}")
            print(f"Industry: {stock_info.get('所处行业', 'N/A')}")
        else:
            print(f"Agent: Failed to get stock information. Error: {stock_info}")
            return
            
        # Step 2: Get price history
        print("\nAgent: Getting recent price history...")
        success, price_data = await finance_integration.send_request(
            "get_stock_price",
            {"symbol": "600519", "period": "daily"}
        )
        
        if success and isinstance(price_data, list):
            latest_price = price_data[0].get("收盘", "N/A") if price_data else "N/A"
            print(f"Agent: Latest price: {latest_price}")
            print(f"Agent: Retrieved {len(price_data)} days of price history.")
        
        # Step 3: Get financial reports
        print("\nAgent: Analyzing financial statements...")
        success, financial_data = await finance_integration.send_request(
            "get_financial_report",
            {"symbol": "600519", "report_type": "all", "periods": 2}
        )
        
        if success:
            balance_sheet_count = len(financial_data.get("balance_sheet", []))
            income_stmt_count = len(financial_data.get("income_statement", []))
            cashflow_count = len(financial_data.get("cash_flow", []))
            
            print(f"Agent: Retrieved {balance_sheet_count} balance sheets, " +
                  f"{income_stmt_count} income statements, and " +
                  f"{cashflow_count} cash flow statements.")
        
        # Step 4: Calculate technical indicators
        print("\nAgent: Calculating technical indicators...")
        success, indicators = await finance_integration.send_request(
            "calc_technical_indicators",
            {"symbol": "600519", "indicators": ["MACD", "RSI"]}
        )
        
        if success and "RSI" in indicators:
            latest_rsi = indicators["RSI"]["rsi"][-1] if indicators["RSI"]["rsi"] else "N/A"
            print(f"Agent: Latest RSI value: {latest_rsi}")
        
        # Step 5: Get fundamental analysis
        print("\nAgent: Performing fundamental analysis...")
        success, analysis = await finance_integration.send_request(
            "analyze_financials",
            {"symbol": "600519", "include_market_ratios": True}
        )
        
        if success and "profitability_ratios" in analysis:
            net_margin = analysis["profitability_ratios"].get("net_margin", "N/A")
            debt_to_equity = analysis["solvency_ratios"].get("debt_to_equity", "N/A") if "solvency_ratios" in analysis else "N/A"
            
            print(f"Agent: Net profit margin: {net_margin}%")
            print(f"Agent: Debt-to-equity ratio: {debt_to_equity}")
        
        # Step 6: Make investment decision
        print("\nAgent: Based on the financial data analysis, I recommend:")
        print("  - Strong profitability indicators")
        print("  - Healthy balance sheet with low debt")
        print("  - Technical indicators suggest [further analysis needed]")
        print("  - Overall: Consider for long-term investment portfolio")


async def main():
    """Main function to demonstrate integration"""
    # Create DeerFlow simulator
    deerflow = DeerFlowSimulator()
    
    # Create and register Finance MCP Server integration
    finance_integration = FinanceServerIntegration()
    
    try:
        # Start server
        await finance_integration.start_server()
        
        # Register with DeerFlow
        finance_integration.register_with_deerflow(deerflow)
        
        # Run agent simulation
        await deerflow.run_agent_simulation()
        
    finally:
        # Stop server
        await finance_integration.stop_server()
        print("\nDemo complete. Server stopped.")


if __name__ == "__main__":
    asyncio.run(main()) 