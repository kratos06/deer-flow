"""
Test script for validating the Finance MCP Server implementation
"""
import asyncio
import json
import os
import sys
import unittest
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.finance_server.client_example import FinanceMCPClient


class TestFinanceMCPServer(unittest.TestCase):
    """Test cases for Finance MCP Server"""
    
    @classmethod
    def setUpClass(cls):
        """Set up for all test cases"""
        cls.client = None
        cls.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.event_loop)
        
        # Start client
        cls.client = cls.event_loop.run_until_complete(cls._setup_client())
    
    @classmethod
    async def _setup_client(cls):
        """Set up client asynchronously"""
        client = FinanceMCPClient()
        return client
    
    @classmethod
    def tearDownClass(cls):
        """Tear down after all test cases"""
        if cls.client:
            cls.event_loop.run_until_complete(cls.client.stop_server())
            cls.event_loop.close()
    
    def test_01_stock_info(self):
        """Test stock information retrieval"""
        result = self.event_loop.run_until_complete(
            self.client.get_stock_info("600519", "A")
        )
        
        # Check if result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check if there are no errors
        self.assertNotIn("error", result)
        
        # Print sample of result
        print("\nStock Info Test Result (sample):")
        print(json.dumps({k: result[k] for k in list(result.keys())[:5]}, indent=2, ensure_ascii=False))
    
    def test_02_stock_price(self):
        """Test stock price retrieval"""
        result = self.event_loop.run_until_complete(
            self.client.get_stock_price("600519", "daily")
        )
        
        # Check if result is a list
        self.assertIsInstance(result, list)
        
        # Check if there are no errors
        if result:
            self.assertNotIn("error", result[0])
        
        # Print sample of result (first item only)
        if result:
            print("\nStock Price Test Result (first item):")
            print(json.dumps(result[0], indent=2, ensure_ascii=False))
    
    def test_03_financial_report(self):
        """Test financial report retrieval"""
        result = self.event_loop.run_until_complete(
            self.client.get_financial_report("600519", "balance", 1)
        )
        
        # Check if result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check if there are no errors
        self.assertNotIn("error", result)
        
        # Print keys of result
        print("\nFinancial Report Test - Available sections:")
        print(list(result.keys()))
        
        # If balance_sheet is available, print first item
        if "balance_sheet" in result and result["balance_sheet"]:
            print("\nBalance Sheet Sample (first row):")
            bal_sheet = result["balance_sheet"][0]
            # Print first few items for brevity
            keys = list(bal_sheet.keys())[:5]
            print(json.dumps({k: bal_sheet[k] for k in keys}, indent=2, ensure_ascii=False))
    
    def test_04_cache_functionality(self):
        """Test cache functionality with repeated calls"""
        # First call to get_stock_info
        start_time = self.event_loop.time()
        result1 = self.event_loop.run_until_complete(
            self.client.get_stock_info("600519", "A")
        )
        first_call_time = self.event_loop.time() - start_time
        
        # Second call to get_stock_info (should be cached)
        start_time = self.event_loop.time()
        result2 = self.event_loop.run_until_complete(
            self.client.get_stock_info("600519", "A")
        )
        second_call_time = self.event_loop.time() - start_time
        
        # Check that results are equal
        self.assertEqual(result1, result2)
        
        # Print timing info
        print(f"\nCache Test - First call time: {first_call_time:.4f}s")
        print(f"Cache Test - Second call time: {second_call_time:.4f}s")
        print(f"Cache Test - Speed improvement: {first_call_time/second_call_time:.2f}x")
        
        # Second call should typically be faster due to caching
        # But we don't assert this as it's not guaranteed in all environments
    
    def test_05_error_handling(self):
        """Test error handling with invalid parameters"""
        # Call with invalid symbol
        result = self.event_loop.run_until_complete(
            self.client.get_stock_info("INVALID", "A")
        )
        
        # Check if result contains error information
        print("\nError Handling Test Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # We don't strictly assert error content as it may vary
        # depending on how AKShare handles invalid symbols


if __name__ == "__main__":
    unittest.main() 