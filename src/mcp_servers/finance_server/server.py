"""
Finance MCP Server implementation
"""
import json
import asyncio
import sys
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
import os
import importlib.util

# Get the absolute path of the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Import the tools module using importlib
tools_path = os.path.join(current_dir, "tools.py")
spec = importlib.util.spec_from_file_location("tools", tools_path)
tools_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools_module)
FINANCE_TOOLS = tools_module.FINANCE_TOOLS

# Import other modules using absolute imports
from src.mcp_servers.finance_server.adapters.akshare_adapter import AKShareAdapter
from src.mcp_servers.finance_server.utils.cache import DataCache
from src.mcp_servers.finance_server.engines.technical_engine import TechnicalAnalysisEngine
from src.mcp_servers.finance_server.engines.fundamental_engine import FundamentalAnalysisEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("finance_mcp_server")


class FinanceMCPServer:
    """
    Finance MCP Server implementation
    
    Implements a Model Context Protocol (MCP) server for financial data,
    using AKShare as the data source.
    """
    
    def __init__(self):
        """Initialize the server"""
        self.tools = {tool["name"]: tool for tool in FINANCE_TOOLS}
        self.adapter = AKShareAdapter()
        self.cache = DataCache()
        self.technical_engine = TechnicalAnalysisEngine()
        self.fundamental_engine = FundamentalAnalysisEngine()
        
        # Map tool names to handler methods
        self.handlers = {
            "get_stock_info": self._handle_get_stock_info,
            "get_stock_price": self._handle_get_stock_price,
            "get_financial_report": self._handle_get_financial_report,
            "calc_technical_indicators": self._handle_calc_technical_indicators,
            "get_industry_analysis": self._handle_get_industry_analysis,
            "analyze_financials": self._handle_analyze_financials
        }
        
        logger.info("Finance MCP Server initialized")
    
    def _generate_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Generate a cache key from tool name and parameters"""
        # Create a deterministic string representation of the parameters
        param_str = json.dumps(params, sort_keys=True)
        return f"{tool_name}:{param_str}"
    
    def _get_ttl_for_tool(self, tool_name: str) -> int:
        """Get appropriate TTL (in seconds) for each tool"""
        ttl_map = {
            "get_stock_info": 86400,  # 1 day
            "get_stock_price": 3600,  # 1 hour
            "get_financial_report": 86400 * 7,  # 1 week
            "calc_technical_indicators": 3600,  # 1 hour
            "get_industry_analysis": 86400  # 1 day
        }
        return ttl_map.get(tool_name, 3600)  # Default to 1 hour
    
    async def _handle_get_stock_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_stock_info requests"""
        symbol = params.get("symbol")
        market = params.get("market")
        
        # Check cache
        cache_key = self._generate_cache_key("get_stock_info", params)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # Get data from adapter
        result = self.adapter.get_stock_info(symbol, market)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=self._get_ttl_for_tool("get_stock_info"))
        
        return result
    
    async def _handle_get_stock_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_stock_price requests"""
        symbol = params.get("symbol")
        period = params.get("period", "daily")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        
        # Check cache
        cache_key = self._generate_cache_key("get_stock_price", params)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # Get data from adapter
        result = self.adapter.get_stock_price(symbol, period, start_date, end_date)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=self._get_ttl_for_tool("get_stock_price"))
        
        return result
    
    async def _handle_get_financial_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_financial_report requests"""
        symbol = params.get("symbol")
        report_type = params.get("report_type")
        periods = params.get("periods", 4)
        
        # Check cache
        cache_key = self._generate_cache_key("get_financial_report", params)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # Get data from adapter
        result = self.adapter.get_financial_report(symbol, report_type, periods)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=self._get_ttl_for_tool("get_financial_report"))
        
        return result
    
    async def _handle_calc_technical_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calc_technical_indicators requests"""
        symbol = params.get("symbol")
        indicators = params.get("indicators", ["MA", "MACD", "RSI"])
        period = params.get("period", "daily")
        
        # Check cache
        cache_key = self._generate_cache_key("calc_technical_indicators", params)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # Get price data first
        price_data = self.adapter.get_stock_price(symbol, period)
        
        # Convert to DataFrame for technical analysis
        if not price_data or isinstance(price_data, dict) and "error" in price_data:
            return {"error": "Failed to retrieve price data for technical analysis"}
            
        df = pd.DataFrame(price_data)
        
        # Calculate indicators
        result = self.technical_engine.process_indicators(df, indicators)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=self._get_ttl_for_tool("calc_technical_indicators"))
        
        return result
    
    async def _handle_get_industry_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_industry_analysis requests"""
        industry = params.get("industry")
        metric = params.get("metric")
        
        # Check cache
        cache_key = self._generate_cache_key("get_industry_analysis", params)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # Get data from adapter
        result = self.adapter.get_industry_analysis(industry, metric)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=self._get_ttl_for_tool("get_industry_analysis"))
        
        return result
    
    async def _handle_analyze_financials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analyze_financials requests"""
        symbol = params.get("symbol")
        include_market_ratios = params.get("include_market_ratios", False)
        
        # Check cache
        cache_key = self._generate_cache_key("analyze_financials", params)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data
        
        # Get financial report data
        financial_data = await self._handle_get_financial_report({
            "symbol": symbol,
            "report_type": "all",
            "periods": 4
        })
        
        if not financial_data or "error" in financial_data:
            return {"error": f"Failed to retrieve financial data for {symbol}"}
            
        # Initialize parameters for analysis
        balance_sheet = financial_data.get("balance_sheet", [])
        income_statement = financial_data.get("income_statement", [])
        cash_flow = financial_data.get("cash_flow", [])
        
        # Get stock price and shares outstanding if needed for market ratios
        stock_price = None
        shares_outstanding = None
        
        if include_market_ratios:
            # Get latest stock info
            stock_info = await self._handle_get_stock_info({"symbol": symbol})
            if stock_info and "error" not in stock_info:
                # Get price data
                price_data = await self._handle_get_stock_price({"symbol": symbol, "period": "daily"})
                if price_data and isinstance(price_data, list) and price_data:
                    # Get latest price
                    latest_price = price_data[0].get("收盘", None) or price_data[0].get("close", None)
                    if latest_price:
                        stock_price = float(latest_price)
                
                # Try to find shares outstanding from stock info
                # Key names will depend on the actual structure from AKShare
                for key in ["总股本", "股本", "total_shares", "shares_outstanding"]:
                    if key in stock_info:
                        shares_value = stock_info.get(key, "0")
                        # Convert various formats to float
                        try:
                            # Handle formats like "10.5亿" or "10.5万"
                            if isinstance(shares_value, str):
                                if "亿" in shares_value:
                                    shares_outstanding = float(shares_value.replace("亿", "")) * 100000000
                                elif "万" in shares_value:
                                    shares_outstanding = float(shares_value.replace("万", "")) * 10000
                                else:
                                    shares_outstanding = float(shares_value)
                            else:
                                shares_outstanding = float(shares_value)
                            break
                        except (ValueError, TypeError):
                            continue
        
        # Perform financial analysis
        analysis_result = self.fundamental_engine.analyze_financial_statements(
            balance_sheet=balance_sheet,
            income_statement=income_statement,
            cash_flow=cash_flow,
            stock_price=stock_price,
            shares_outstanding=shares_outstanding
        )
        
        # Cache result
        self.cache.set(cache_key, analysis_result, ttl=self._get_ttl_for_tool("get_financial_report"))
        
        return analysis_result
    
    async def handle_request(self, request_str: str) -> str:
        """
        Handle an MCP request
        
        Args:
            request_str: JSON string with the request
            
        Returns:
            JSON string with the response
        """
        try:
            # Parse the request
            request = json.loads(request_str)
            
            # Extract request info
            request_id = request.get("id")
            tool_name = request.get("name")
            params = request.get("parameters", {})
            
            logger.info(f"Processing request {request_id} for tool {tool_name}")
            
            # Check if the tool exists
            if tool_name not in self.handlers:
                error_response = {
                    "id": request_id,
                    "error": {
                        "message": f"Unknown tool: {tool_name}",
                        "code": "UNKNOWN_TOOL"
                    }
                }
                return json.dumps(error_response)
            
            # Call the handler
            try:
                handler = self.handlers[tool_name]
                result = await handler(params)
                
                # Prepare response
                response = {
                    "id": request_id,
                    "result": result
                }
                
                return json.dumps(response)
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}", exc_info=True)
                error_response = {
                    "id": request_id,
                    "error": {
                        "message": f"Error processing request: {str(e)}",
                        "code": "PROCESSING_ERROR"
                    }
                }
                return json.dumps(error_response)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request")
            return json.dumps({"error": {"message": "Invalid JSON", "code": "INVALID_JSON"}})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return json.dumps({"error": {"message": f"Unexpected error: {str(e)}", "code": "INTERNAL_ERROR"}})


async def mcp_server_loop():
    """Main server loop"""
    server = FinanceMCPServer()
    
    # Process stdin/stdout in a loop
    while True:
        try:
            # Read a line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                # End of input
                break
                
            # Process the request
            response = await server.handle_request(line.strip())
            
            # Write the response to stdout
            print(response, flush=True)
            
        except Exception as e:
            logger.error(f"Error in server loop: {str(e)}", exc_info=True)
            # Try to recover and continue
            continue


def main():
    """Entry point for the server"""
    try:
        asyncio.run(mcp_server_loop())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 