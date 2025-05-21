# Finance MCP Server

A Model Context Protocol (MCP) server for financial data, specifically focused on Chinese A-shares and Hong Kong stock markets.

## Overview

This Finance MCP Server provides a set of tools for financial data retrieval and analysis through the Model Context Protocol (MCP) interface. It leverages AKShare as the data source backend to provide comprehensive financial information.

## Features

- **Stock Information**: Basic company info, industry classification, market cap, etc.
- **Historical Prices**: Daily, weekly, or monthly price history with customizable date ranges
- **Financial Reports**: Balance sheets, income statements, and cash flow statements
- **Industry Analysis**: Industry rankings and competitive landscape
- **Technical Indicators**: Support for common technical analysis indicators (MACD, RSI, etc.)

## Architecture

The server follows a layered architecture:

1. **Tool Definitions**: JSON schema definitions for each financial tool
2. **Adapter Layer**: Standardizes data retrieval from AKShare
3. **Server Layer**: Handles MCP protocol requests, response formatting, and caching
4. **Cache Layer**: Provides efficient data caching with time-to-live (TTL)

## Installation

### Prerequisites

- Python 3.7+
- AKShare library

### Setup

```bash
# Install dependencies
pip install akshare pandas

# Navigate to the server directory
cd src/mcp_servers/finance_server
```

## Usage

### Starting the Server

The server can be run directly with Python:

```bash
python server.py
```

### Using the Client

A sample client implementation is provided in `client_example.py`:

```python
import asyncio
from client_example import FinanceMCPClient

async def main():
    client = FinanceMCPClient()
    
    # Get stock information
    stock_info = await client.get_stock_info("600519", "A")
    print(stock_info)
    
    # Get stock prices
    stock_prices = await client.get_stock_price("600519", "daily", "20220101", "20220201")
    print(stock_prices)
    
    await client.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Tools

### 1. get_stock_info

Retrieves basic information about a stock.

Parameters:
- `symbol`: Stock code (e.g., "600519" or "00700")
- `market`: Optional stock market identifier ("A" or "HK")

### 2. get_stock_price

Retrieves historical price data.

Parameters:
- `symbol`: Stock code
- `period`: Data frequency ("daily", "weekly", "monthly")
- `start_date`: Optional start date in YYYYMMDD format
- `end_date`: Optional end date in YYYYMMDD format

### 3. get_financial_report

Retrieves financial report data.

Parameters:
- `symbol`: Stock code
- `report_type`: Report type ("balance", "income", "cashflow", "all")
- `periods`: Number of reporting periods to retrieve (default: 4)

### 4. calc_technical_indicators

Calculates technical indicators for a stock.

Parameters:
- `symbol`: Stock code
- `indicators`: List of indicators to calculate (e.g., ["MA", "MACD", "RSI"])
- `period`: Data frequency ("daily", "weekly", "monthly")

### 5. get_industry_analysis

Retrieves industry analysis data.

Parameters:
- `industry`: Industry name or code
- `metric`: Optional analysis metric ("pe", "pb", "roe", etc.)

## Integration with DeerFlow

This server is designed to be integrated with the DeerFlow research framework, allowing AI models to access financial data through the MCP interface.

## License

This project is part of the DeerFlow research framework. 