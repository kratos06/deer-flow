"""
Finance MCP Server for DeerFlow

This package provides financial data capabilities for the DeerFlow research framework,
specifically focusing on Chinese A-shares and Hong Kong stock markets using AKShare.
"""

from .server import FinanceMCPServer, main
from .integration import FinanceServerIntegration

__all__ = ['FinanceMCPServer', 'FinanceServerIntegration', 'main']
