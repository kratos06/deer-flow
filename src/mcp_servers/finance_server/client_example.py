"""
Example client for the Finance MCP Server
"""
import json
import asyncio
import subprocess
import sys
from typing import Dict, Any, List, Optional


class FinanceMCPClient:
    """Client for interacting with the Finance MCP Server"""
    
    def __init__(self, server_path: str = "src/mcp_servers/finance_server/server.py"):
        """
        Initialize the client
        
        Args:
            server_path: Path to the server script
        """
        self.server_path = server_path
        self.server_process = None
        self.request_id = 0
    
    async def start_server(self):
        """Start the server subprocess"""
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        print("Server started")
    
    async def stop_server(self):
        """Stop the server subprocess"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            self.server_process = None
            print("Server stopped")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the server
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool
            
        Returns:
            Response from the server
        """
        if not self.server_process:
            await self.start_server()
        
        # Generate request ID
        self.request_id += 1
        
        # Create request
        request = {
            "id": str(self.request_id),
            "name": tool_name,
            "parameters": parameters
        }
        
        # Send request to server
        request_str = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_str.encode())
        await self.server_process.stdin.drain()
        
        # Read response from server
        response_bytes = await self.server_process.stdout.readline()
        response_str = response_bytes.decode().strip()
        
        # Parse and return response
        return json.loads(response_str)
    
    async def get_stock_info(self, symbol: str, market: Optional[str] = None) -> Dict[str, Any]:
        """
        Get basic information about a stock
        
        Args:
            symbol: Stock code
            market: Stock market (A or HK)
            
        Returns:
            Stock information
        """
        parameters = {"symbol": symbol}
        if market:
            parameters["market"] = market
            
        response = await self.call_tool("get_stock_info", parameters)
        return response.get("result", {})
    
    async def get_stock_price(
        self, symbol: str, period: str = "daily", 
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data for a stock
        
        Args:
            symbol: Stock code
            period: Data frequency (daily, weekly, monthly)
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            
        Returns:
            List of price data dictionaries
        """
        parameters = {"symbol": symbol, "period": period}
        if start_date:
            parameters["start_date"] = start_date
        if end_date:
            parameters["end_date"] = end_date
            
        response = await self.call_tool("get_stock_price", parameters)
        return response.get("result", [])
    
    async def get_financial_report(
        self, symbol: str, report_type: str, periods: int = 4
    ) -> Dict[str, Any]:
        """
        Get financial report data for a company
        
        Args:
            symbol: Stock code
            report_type: Report type (balance, income, cashflow, all)
            periods: Number of reporting periods to retrieve
            
        Returns:
            Financial report data
        """
        parameters = {
            "symbol": symbol,
            "report_type": report_type,
            "periods": periods
        }
            
        response = await self.call_tool("get_financial_report", parameters)
        return response.get("result", {})


async def main():
    """Main function to demonstrate client usage"""
    client = FinanceMCPClient()
    
    try:
        # Get stock info
        print("\n=== Getting Stock Info ===")
        stock_info = await client.get_stock_info("600519", "A")
        print(json.dumps(stock_info, indent=2, ensure_ascii=False))
        
        # Get stock price
        print("\n=== Getting Stock Price ===")
        stock_price = await client.get_stock_price("600519", "daily")
        # Only print first 3 records for brevity
        print(json.dumps(stock_price[:3], indent=2, ensure_ascii=False))
        
        # Get financial report
        print("\n=== Getting Financial Report ===")
        financial_report = await client.get_financial_report("600519", "balance", 2)
        print(json.dumps(financial_report, indent=2, ensure_ascii=False))
        
    finally:
        # Stop the server
        await client.stop_server()


if __name__ == "__main__":
    asyncio.run(main()) 