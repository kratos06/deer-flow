"""
Integration module for connecting Finance MCP Server with DeerFlow framework

This module handles the integration between the Finance MCP Server and
the DeerFlow framework, allowing DeerFlow agents to access financial data
through a standardized interface.
"""
import os
import sys
import asyncio
import subprocess
import json
from typing import Dict, Any, List, Tuple, Optional, Union


class FinanceServerIntegration:
    """
    Integration class for the Finance MCP Server
    
    Provides methods for DeerFlow to interact with financial data.
    """
    
    def __init__(self, server_path: str = None):
        """
        Initialize the integration
        
        Args:
            server_path: Optional path to the server script
        """
        # Determine server path
        if server_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.server_path = os.path.join(current_dir, "server.py")
        else:
            self.server_path = server_path
            
        # Initialize server process
        self.server_process = None
        self.request_id = 0
        
        # Tool information
        self.tool_names = [
            "get_stock_info",
            "get_stock_price",
            "get_financial_report",
            "calc_technical_indicators",
            "get_industry_analysis",
            "analyze_financials"
        ]
    
    async def start_server(self) -> bool:
        """
        Start the Finance MCP Server
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.server_process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
            )
            print("Finance MCP Server started")
            return True
        except Exception as e:
            print(f"Failed to start Finance MCP Server: {str(e)}")
            return False
    
    async def stop_server(self) -> None:
        """Stop the Finance MCP Server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                await self.server_process.wait()
                self.server_process = None
                print("Finance MCP Server stopped")
            except Exception as e:
                print(f"Error stopping Finance MCP Server: {str(e)}")
    
    async def send_request(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Send a request to the Finance MCP Server
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool
            
        Returns:
            Tuple of (success, result)
        """
        if not self.server_process:
            success = await self.start_server()
            if not success:
                return False, {"error": "Failed to start Finance MCP Server"}
        
        # Generate request ID
        self.request_id += 1
        
        # Create request
        request = {
            "id": str(self.request_id),
            "name": tool_name,
            "parameters": parameters
        }
        
        try:
            # Send request to server
            request_str = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_str.encode())
            await self.server_process.stdin.drain()
            
            # Read response from server
            response_bytes = await self.server_process.stdout.readline()
            response_str = response_bytes.decode().strip()
            
            # Parse response
            response = json.loads(response_str)
            
            # Check for errors
            if "error" in response:
                return False, response["error"]
            
            # Return result
            return True, response.get("result", {})
        except Exception as e:
            return False, {"error": f"Request failed: {str(e)}"}
    
    def register_with_deerflow(self, deerflow_instance: Any) -> None:
        """
        Register the Finance MCP Server with DeerFlow
        
        Args:
            deerflow_instance: Instance of the DeerFlow framework
        """
        deerflow_instance.register_mcp_server(
            name="finance",
            description="Financial data and analysis for Chinese stock markets",
            tools=self.tool_names,
            integration=self
        )
    
    async def format_stock_data_for_deerflow(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format stock data for DeerFlow consumption
        
        Args:
            stock_data: Raw stock data from the server
            
        Returns:
            Formatted data suitable for DeerFlow agents
        """
        # Here you would implement any data transformation needed for DeerFlow
        # For this example, we'll just return the original data
        formatted_data = {
            "company_info": {
                "name": stock_data.get("公司名称", ""),
                "industry": stock_data.get("所处行业", ""),
                "exchange": stock_data.get("交易所", ""),
                "market_cap": stock_data.get("总市值", ""),
                "listing_date": stock_data.get("上市日期", "")
            },
            "financial_summary": {
                "pe_ratio": stock_data.get("市盈率", ""),
                "pb_ratio": stock_data.get("市净率", ""),
                "dividend_yield": stock_data.get("股息率", "")
            }
        }
        return formatted_data
    
    async def get_investment_recommendation(self, symbol: str) -> Dict[str, Any]:
        """
        Generate an investment recommendation for DeerFlow agents
        
        This is a higher-level function that combines multiple API calls
        to generate a comprehensive analysis.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Investment recommendation data
        """
        # Get basic info
        success, stock_info = await self.send_request("get_stock_info", {"symbol": symbol})
        if not success:
            return {"recommendation": "insufficient_data", "reason": "Failed to retrieve stock information"}
        
        # Get financial analysis
        success, analysis = await self.send_request("analyze_financials", {
            "symbol": symbol,
            "include_market_ratios": True
        })
        
        if not success:
            return {"recommendation": "insufficient_data", "reason": "Failed to analyze financials"}
        
        # Get technical indicators
        success, indicators = await self.send_request("calc_technical_indicators", {
            "symbol": symbol,
            "indicators": ["RSI", "MACD"]
        })
        
        # Process data and generate recommendation
        recommendation = {
            "symbol": symbol,
            "company_name": stock_info.get("公司名称", ""),
            "recommendation": "neutral",  # Default
            "confidence": 0.5,  # Default
            "factors": []
        }
        
        # Analyze profitability
        if "profitability_ratios" in analysis:
            net_margin = analysis["profitability_ratios"].get("net_margin", 0)
            if net_margin > 15:
                recommendation["factors"].append({
                    "factor": "high_profitability",
                    "impact": "positive",
                    "value": f"Net margin: {net_margin}%"
                })
                recommendation["recommendation"] = "buy"
                recommendation["confidence"] = 0.7
            elif net_margin < 5:
                recommendation["factors"].append({
                    "factor": "low_profitability",
                    "impact": "negative",
                    "value": f"Net margin: {net_margin}%"
                })
                recommendation["recommendation"] = "sell"
                recommendation["confidence"] = 0.6
        
        # Analyze debt levels
        if "solvency_ratios" in analysis:
            debt_to_equity = analysis["solvency_ratios"].get("debt_to_equity", 0)
            if debt_to_equity > 2:
                recommendation["factors"].append({
                    "factor": "high_debt",
                    "impact": "negative",
                    "value": f"Debt-to-equity: {debt_to_equity}"
                })
                recommendation["confidence"] = min(recommendation["confidence"] + 0.1, 0.9)
            elif debt_to_equity < 0.5:
                recommendation["factors"].append({
                    "factor": "low_debt",
                    "impact": "positive",
                    "value": f"Debt-to-equity: {debt_to_equity}"
                })
        
        # Analyze technical indicators
        if success and "RSI" in indicators:
            rsi = indicators["RSI"]["rsi"][-1] if indicators["RSI"]["rsi"] else None
            if rsi is not None:
                if rsi > 70:
                    recommendation["factors"].append({
                        "factor": "overbought",
                        "impact": "negative",
                        "value": f"RSI: {rsi}"
                    })
                    if recommendation["recommendation"] == "buy":
                        recommendation["recommendation"] = "hold"
                elif rsi < 30:
                    recommendation["factors"].append({
                        "factor": "oversold",
                        "impact": "positive",
                        "value": f"RSI: {rsi}"
                    })
                    if recommendation["recommendation"] == "sell":
                        recommendation["recommendation"] = "hold"
        
        return recommendation


# Example usage
async def example_usage():
    """Example of how to use the integration with DeerFlow"""
    # This is a placeholder function to demonstrate usage
    
    # Create integration
    integration = FinanceServerIntegration()
    
    try:
        # Start server
        await integration.start_server()
        
        # Send a request
        success, result = await integration.send_request(
            "get_stock_info", 
            {"symbol": "600519", "market": "A"}
        )
        
        if success:
            # Format data for DeerFlow
            formatted_data = await integration.format_stock_data_for_deerflow(result)
            print(json.dumps(formatted_data, indent=2, ensure_ascii=False))
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
            
    finally:
        # Stop server
        await integration.stop_server()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage()) 