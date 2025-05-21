"""
Fundamental analysis engine for financial data

This module provides functions for analyzing financial statements and calculating
financial ratios, valuations, and other fundamental metrics.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any


class FundamentalAnalysisEngine:
    """
    Engine for fundamental analysis of financial statements
    """
    
    @staticmethod
    def calculate_profitability_ratios(income_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate profitability ratios from income statement data
        
        Args:
            income_data: Income statement data
            
        Returns:
            Dictionary with profitability ratios
        """
        try:
            # Extract values for calculation
            total_revenue = income_data.get("营业总收入", 0) or income_data.get("营业收入", 0)
            net_income = income_data.get("净利润", 0)
            gross_profit = income_data.get("毛利润", 0) or (
                total_revenue - income_data.get("营业成本", 0)
            )
            operating_income = income_data.get("营业利润", 0)
            
            # Calculate ratios
            gross_margin = (gross_profit / total_revenue) if total_revenue else 0
            operating_margin = (operating_income / total_revenue) if total_revenue else 0
            net_margin = (net_income / total_revenue) if total_revenue else 0
            
            return {
                "gross_margin": round(gross_margin * 100, 2),  # As percentage
                "operating_margin": round(operating_margin * 100, 2),
                "net_margin": round(net_margin * 100, 2)
            }
        except Exception as e:
            return {"error": f"Failed to calculate profitability ratios: {str(e)}"}
    
    @staticmethod
    def calculate_liquidity_ratios(balance_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate liquidity ratios from balance sheet data
        
        Args:
            balance_data: Balance sheet data
            
        Returns:
            Dictionary with liquidity ratios
        """
        try:
            # Extract values for calculation
            current_assets = balance_data.get("流动资产合计", 0)
            current_liabilities = balance_data.get("流动负债合计", 0)
            cash = balance_data.get("货币资金", 0)
            short_term_investments = balance_data.get("交易性金融资产", 0) or 0
            accounts_receivable = balance_data.get("应收账款", 0) or 0
            
            # Calculate ratios
            current_ratio = (current_assets / current_liabilities) if current_liabilities else 0
            quick_ratio = ((cash + short_term_investments + accounts_receivable) / current_liabilities) if current_liabilities else 0
            cash_ratio = ((cash + short_term_investments) / current_liabilities) if current_liabilities else 0
            
            return {
                "current_ratio": round(current_ratio, 2),
                "quick_ratio": round(quick_ratio, 2),
                "cash_ratio": round(cash_ratio, 2)
            }
        except Exception as e:
            return {"error": f"Failed to calculate liquidity ratios: {str(e)}"}
    
    @staticmethod
    def calculate_solvency_ratios(balance_data: Dict[str, Any], income_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate solvency ratios from balance sheet and income statement data
        
        Args:
            balance_data: Balance sheet data
            income_data: Income statement data
            
        Returns:
            Dictionary with solvency ratios
        """
        try:
            # Extract values for calculation
            total_assets = balance_data.get("资产总计", 0)
            total_liabilities = balance_data.get("负债合计", 0)
            shareholders_equity = balance_data.get("所有者权益合计", 0)
            ebit = income_data.get("利润总额", 0) + income_data.get("财务费用", 0)
            interest_expense = income_data.get("利息支出", 0) or income_data.get("财务费用", 0) / 2  # Approximation if not available
            
            # Calculate ratios
            debt_ratio = (total_liabilities / total_assets) if total_assets else 0
            debt_to_equity = (total_liabilities / shareholders_equity) if shareholders_equity else 0
            interest_coverage = (ebit / interest_expense) if interest_expense else 0
            
            return {
                "debt_ratio": round(debt_ratio, 2),
                "debt_to_equity": round(debt_to_equity, 2),
                "interest_coverage": round(interest_coverage, 2)
            }
        except Exception as e:
            return {"error": f"Failed to calculate solvency ratios: {str(e)}"}
    
    @staticmethod
    def calculate_efficiency_ratios(
        balance_data: Dict[str, Any], 
        income_data: Dict[str, Any],
        prev_balance_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Calculate efficiency ratios from financial statement data
        
        Args:
            balance_data: Current period balance sheet data
            income_data: Current period income statement data
            prev_balance_data: Previous period balance sheet data (for avg calculations)
            
        Returns:
            Dictionary with efficiency ratios
        """
        try:
            # Extract values for calculation
            total_assets = balance_data.get("资产总计", 0)
            total_revenue = income_data.get("营业总收入", 0) or income_data.get("营业收入", 0)
            net_income = income_data.get("净利润", 0)
            
            # Calculate average total assets if previous data available
            avg_total_assets = (total_assets + prev_balance_data.get("资产总计", total_assets)) / 2 if prev_balance_data else total_assets
            
            # Calculate inventory turnover
            inventory = balance_data.get("存货", 0)
            cogs = income_data.get("营业成本", 0)
            inventory_turnover = (cogs / inventory) if inventory else 0
            
            # Calculate asset turnover
            asset_turnover = (total_revenue / avg_total_assets) if avg_total_assets else 0
            
            # Calculate return on assets (ROA)
            roa = (net_income / avg_total_assets) if avg_total_assets else 0
            
            return {
                "inventory_turnover": round(inventory_turnover, 2),
                "asset_turnover": round(asset_turnover, 2),
                "return_on_assets": round(roa * 100, 2)  # As percentage
            }
        except Exception as e:
            return {"error": f"Failed to calculate efficiency ratios: {str(e)}"}
    
    @staticmethod
    def calculate_market_ratios(
        income_data: Dict[str, Any],
        balance_data: Dict[str, Any],
        stock_price: float,
        shares_outstanding: float
    ) -> Dict[str, float]:
        """
        Calculate market-based ratios
        
        Args:
            income_data: Income statement data
            balance_data: Balance sheet data
            stock_price: Current stock price
            shares_outstanding: Number of shares outstanding
            
        Returns:
            Dictionary with market-based ratios
        """
        try:
            # Extract values for calculation
            net_income = income_data.get("净利润", 0)
            shareholders_equity = balance_data.get("所有者权益", 0) or balance_data.get("所有者权益合计", 0)
            
            # Calculate EPS
            eps = net_income / shares_outstanding if shares_outstanding else 0
            
            # Calculate P/E ratio
            pe_ratio = stock_price / eps if eps else 0
            
            # Calculate book value per share
            book_value_per_share = shareholders_equity / shares_outstanding if shares_outstanding else 0
            
            # Calculate P/B ratio
            pb_ratio = stock_price / book_value_per_share if book_value_per_share else 0
            
            # Calculate market cap
            market_cap = stock_price * shares_outstanding
            
            return {
                "eps": round(eps, 2),
                "pe_ratio": round(pe_ratio, 2),
                "book_value_per_share": round(book_value_per_share, 2),
                "pb_ratio": round(pb_ratio, 2),
                "market_cap": market_cap
            }
        except Exception as e:
            return {"error": f"Failed to calculate market ratios: {str(e)}"}
    
    def analyze_financial_statements(
        self,
        balance_sheet: List[Dict[str, Any]],
        income_statement: List[Dict[str, Any]],
        cash_flow: Optional[List[Dict[str, Any]]] = None,
        stock_price: Optional[float] = None,
        shares_outstanding: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial statement analysis
        
        Args:
            balance_sheet: Balance sheet data for multiple periods
            income_statement: Income statement data for multiple periods
            cash_flow: Cash flow statement data (optional)
            stock_price: Current stock price (optional, for market ratios)
            shares_outstanding: Number of shares outstanding (optional, for market ratios)
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        if not balance_sheet or not income_statement:
            return {"error": "Missing required financial statements"}
            
        # Use the most recent period for calculations
        current_balance = balance_sheet[0] if balance_sheet else {}
        current_income = income_statement[0] if income_statement else {}
        
        # Use the second most recent period for comparative calculations
        prev_balance = balance_sheet[1] if len(balance_sheet) > 1 else None
        
        # Calculate various ratio categories
        profitability = self.calculate_profitability_ratios(current_income)
        liquidity = self.calculate_liquidity_ratios(current_balance)
        solvency = self.calculate_solvency_ratios(current_balance, current_income)
        efficiency = self.calculate_efficiency_ratios(current_balance, current_income, prev_balance)
        
        # Calculate market ratios if price and shares data available
        market = {}
        if stock_price is not None and shares_outstanding is not None:
            market = self.calculate_market_ratios(current_income, current_balance, stock_price, shares_outstanding)
        
        # Compile results
        analysis = {
            "profitability_ratios": profitability,
            "liquidity_ratios": liquidity,
            "solvency_ratios": solvency,
            "efficiency_ratios": efficiency
        }
        
        if market:
            analysis["market_ratios"] = market
            
        return analysis 