# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os

from .crawl import crawl_tool
from .python_repl import python_repl_tool
from .search import (
    tavily_search_tool,
    duckduckgo_search_tool,
    brave_search_tool,
    arxiv_search_tool,
)
from .tts import VolcengineTTS
from .finance import (
    get_stock_info_tool,
    get_stock_price_tool,
    get_financial_report_tool,
    analyze_financials_tool,
    get_technical_indicators_tool,
    get_investment_recommendation_tool,
    finance_tools_list
)
from src.config import SELECTED_SEARCH_ENGINE, SearchEngine

# Map search engine names to their respective tools
search_tool_mappings = {
    SearchEngine.TAVILY.value: tavily_search_tool,
    SearchEngine.DUCKDUCKGO.value: duckduckgo_search_tool,
    SearchEngine.BRAVE_SEARCH.value: brave_search_tool,
    SearchEngine.ARXIV.value: arxiv_search_tool,
}

web_search_tool = search_tool_mappings.get(SELECTED_SEARCH_ENGINE, tavily_search_tool)

__all__ = [
    "crawl_tool",
    "web_search_tool",
    "python_repl_tool",
    "VolcengineTTS",
    "get_stock_info_tool",
    "get_stock_price_tool",
    "get_financial_report_tool",
    "analyze_financials_tool",
    "get_technical_indicators_tool",
    "get_investment_recommendation_tool",
    "finance_tools_list"
]
