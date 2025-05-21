"""
Financial tools definitions for the Finance MCP Server.
This file defines the available tools and their parameters.
"""

# Tool definitions for market data
STOCK_INFO_TOOL = {
    "name": "get_stock_info",
    "description": "Get basic information about a stock, including company profile, industry classification, market cap, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string", 
                "description": "Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'"
            },
            "market": {
                "type": "string",
                "enum": ["A", "HK"],
                "description": "Stock market: A for A-shares, HK for Hong Kong stocks"
            }
        },
        "required": ["symbol"]
    }
}

STOCK_PRICE_TOOL = {
    "name": "get_stock_price",
    "description": "Get historical price data for a stock",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string", 
                "description": "Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'"
            },
            "period": {
                "type": "string",
                "enum": ["daily", "weekly", "monthly"],
                "description": "Data frequency: daily, weekly, or monthly"
            },
            "start_date": {
                "type": "string",
                "description": "Start date in YYYYMMDD format"
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYYMMDD format"
            }
        },
        "required": ["symbol"]
    }
}

# Tool definitions for financial reports
FINANCIAL_REPORT_TOOL = {
    "name": "get_financial_report",
    "description": "Get financial report data for a company",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string", 
                "description": "Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'"
            },
            "report_type": {
                "type": "string",
                "enum": ["balance", "income", "cashflow", "all"],
                "description": "Report type: balance sheet, income statement, cash flow statement, or all"
            },
            "periods": {
                "type": "integer",
                "description": "Number of reporting periods to retrieve, default is 4"
            }
        },
        "required": ["symbol", "report_type"]
    }
}

# Tool definitions for technical analysis
TECHNICAL_INDICATORS_TOOL = {
    "name": "calc_technical_indicators",
    "description": "Calculate technical indicators for a stock",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string", 
                "description": "Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'"
            },
            "indicators": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["MA", "MACD", "RSI", "KDJ", "BOLL"]
                },
                "description": "List of technical indicators to calculate"
            },
            "period": {
                "type": "string",
                "enum": ["daily", "weekly", "monthly"],
                "description": "Data frequency: daily, weekly, or monthly"
            }
        },
        "required": ["symbol", "indicators"]
    }
}

# Tool definitions for industry analysis
INDUSTRY_ANALYSIS_TOOL = {
    "name": "get_industry_analysis",
    "description": "Get industry analysis data including rankings and competitive landscape",
    "parameters": {
        "type": "object",
        "properties": {
            "industry": {
                "type": "string",
                "description": "Industry name or code"
            },
            "metric": {
                "type": "string",
                "enum": ["pe", "pb", "roe", "growth", "profit_margin"],
                "description": "Analysis metric: pe (price-to-earnings), pb (price-to-book), roe (return on equity), growth, or profit_margin"
            }
        },
        "required": ["industry"]
    }
}

# Tool definition for fundamental analysis
FINANCIAL_ANALYSIS_TOOL = {
    "name": "analyze_financials",
    "description": "Analyze financial statements and calculate financial ratios",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string", 
                "description": "Stock code. For A-shares use format like '600519' or 'SH600519', for HK stocks use format like '00700'"
            },
            "include_market_ratios": {
                "type": "boolean",
                "description": "Whether to include market-based ratios (requires current stock price and shares outstanding)"
            }
        },
        "required": ["symbol"]
    }
}

# Collection of all financial tools
FINANCE_TOOLS = [
    STOCK_INFO_TOOL,
    STOCK_PRICE_TOOL,
    FINANCIAL_REPORT_TOOL,
    TECHNICAL_INDICATORS_TOOL,
    INDUSTRY_ANALYSIS_TOOL,
    FINANCIAL_ANALYSIS_TOOL
] 