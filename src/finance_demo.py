"""
Finance Analysis Demo for DeerFlow

This script demonstrates the financial analysis capabilities of DeerFlow
by running a sample financial analysis task using the Finance MCP Server.
"""
import asyncio
import argparse
import json
from typing import Dict, Any

from src.agents import financial_analyst_agent
from langchain_core.messages import HumanMessage

# Sample queries for demonstration
SAMPLE_QUERIES = {
    "maotai": "分析贵州茅台(600519)的财务状况和投资价值",
    "tencent": "分析腾讯控股(00700.HK)的财务状况和投资价值",
    "custom": "Please enter a custom query about a Chinese stock"
}


async def run_financial_analysis(query: str) -> str:
    """
    Run financial analysis with the financial analyst agent
    
    Args:
        query: The analysis query to process
        
    Returns:
        The analysis report
    """
    # Prepare the input for the agent
    agent_input = {
        "messages": [
            HumanMessage(content=query)
        ]
    }
    
    # Run the agent on the query
    result = await financial_analyst_agent.ainvoke(agent_input)
    
    # Get the last message as the result
    response_content = result["messages"][-1].content
    
    return response_content


async def main():
    """Main function for the finance demo"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="DeerFlow Financial Analysis Demo")
    parser.add_argument(
        "--query", 
        choices=list(SAMPLE_QUERIES.keys()) + ["custom"],
        default="maotai", 
        help="Select a sample query or 'custom' for custom input"
    )
    parser.add_argument(
        "--custom", 
        type=str, 
        help="Custom analysis query (if --query=custom)"
    )
    
    args = parser.parse_args()
    
    # Determine the query to run
    if args.query == "custom":
        if not args.custom:
            query = input("Enter a financial analysis query: ")
        else:
            query = args.custom
    else:
        query = SAMPLE_QUERIES[args.query]
    
    print(f"\n===== Running Financial Analysis =====")
    print(f"Query: {query}\n")
    
    try:
        # Run the financial analysis
        analysis = await run_financial_analysis(query)
        
        # Print the result
        print("\n===== Financial Analysis Report =====\n")
        print(analysis)
        
    except Exception as e:
        print(f"Error during financial analysis: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 