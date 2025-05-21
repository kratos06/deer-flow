"""
AKShare adapter for fetching financial data
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any


class AKShareAdapter:
    """
    Adapter class for AKShare to standardize data retrieval and processing
    """
    
    @staticmethod
    def _standardize_symbol(symbol: str, market: Optional[str] = None) -> str:
        """
        Standardize the stock symbol format for different markets
        
        Args:
            symbol: Stock symbol, e.g., '600519' or 'SH600519'
            market: Optional market indicator ('A' or 'HK')
            
        Returns:
            Standardized symbol
        """
        # Remove any prefix if present
        clean_symbol = symbol.replace("SH", "").replace("SZ", "").replace("sh", "").replace("sz", "")
        
        # If market is not specified, detect from the symbol
        if market is None:
            if clean_symbol.startswith("0") or clean_symbol.startswith("3"):
                return f"SZ{clean_symbol}"
            elif clean_symbol.startswith("6"):
                return f"SH{clean_symbol}"
            elif clean_symbol.startswith("00") or clean_symbol.startswith("08"):
                return clean_symbol  # HK stocks
            else:
                # Default to Shanghai market
                return f"SH{clean_symbol}"
        
        # Apply market prefix if specified
        if market == "A":
            if clean_symbol.startswith("0") or clean_symbol.startswith("3"):
                return f"SZ{clean_symbol}"
            else:
                return f"SH{clean_symbol}"
        elif market == "HK":
            return clean_symbol
            
        return symbol
    
    @staticmethod
    def _default_start_date() -> str:
        """Return default start date (1 year ago)"""
        one_year_ago = datetime.now() - timedelta(days=365)
        return one_year_ago.strftime("%Y%m%d")
    
    @staticmethod
    def _default_end_date() -> str:
        """Return default end date (today)"""
        return datetime.now().strftime("%Y%m%d")
    
    @staticmethod
    def _format_stock_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Convert stock info DataFrame to dictionary"""
        if df.empty:
            return {}
            
        # Convert to dict for easier access
        result = {}
        for _, row in df.iterrows():
            if len(row) >= 2:  # Ensure we have key-value pairs
                result[row.iloc[0]] = row.iloc[1]
        
        return result
    
    @staticmethod
    def _format_stock_price(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert stock price DataFrame to list of dictionaries"""
        if df.empty:
            return []
            
        # Convert DataFrame to list of dicts, handling dates
        return df.to_dict(orient="records")
    
    def get_stock_info(self, symbol: str, market: Optional[str] = None) -> Dict[str, Any]:
        """
        Get basic stock information
        
        Args:
            symbol: Stock symbol, e.g., '600519' or 'SH600519'
            market: Optional market indicator ('A' or 'HK')
            
        Returns:
            Dictionary with stock information
        """
        try:
            std_symbol = self._standardize_symbol(symbol, market)
            
            # Check if it's an A-share or HK stock
            if market == "HK" or (market is None and (symbol.startswith("00") or len(symbol) == 5)):
                # HK stock
                stock_info = ak.stock_hk_info_em(symbol=std_symbol)
                return self._format_stock_info(stock_info)
            else:
                # A-share stock
                stock_info = ak.stock_individual_info_em(symbol=std_symbol)
                return self._format_stock_info(stock_info)
        except Exception as e:
            return {"error": f"Failed to get stock info: {str(e)}"}
    
    def get_stock_price(
        self, symbol: str, period: str = "daily", 
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical stock price data
        
        Args:
            symbol: Stock symbol, e.g., '600519' or 'SH600519'
            period: Data frequency ('daily', 'weekly', 'monthly')
            start_date: Start date in format YYYYMMDD
            end_date: End date in format YYYYMMDD
            
        Returns:
            List of dictionaries with price data
        """
        try:
            std_symbol = self._standardize_symbol(symbol)
            _start_date = start_date or self._default_start_date()
            _end_date = end_date or self._default_end_date()
            
            # Check if it's an A-share or HK stock
            if std_symbol.startswith("00") or len(std_symbol) == 5:
                # HK stock
                price_data = ak.stock_hk_hist(
                    symbol=std_symbol,
                    period=period,
                    start_date=_start_date,
                    end_date=_end_date
                )
                return self._format_stock_price(price_data)
            else:
                # A-share stock
                price_data = ak.stock_zh_a_hist(
                    symbol=std_symbol,
                    period=period,
                    start_date=_start_date,
                    end_date=_end_date,
                    adjust=""
                )
                return self._format_stock_price(price_data)
        except Exception as e:
            return [{"error": f"Failed to get stock price data: {str(e)}"}]
    
    def get_financial_report(
        self, symbol: str, report_type: str, periods: int = 4
    ) -> Dict[str, Any]:
        """
        Get financial report data
        
        Args:
            symbol: Stock symbol, e.g., '600519' or 'SH600519'
            report_type: Report type ('balance', 'income', 'cashflow', 'all')
            periods: Number of reporting periods to retrieve
            
        Returns:
            Dictionary with financial report data
        """
        try:
            std_symbol = self._standardize_symbol(symbol)
            
            # Convert standard symbol format for financial APIs
            if std_symbol.startswith("SH"):
                fin_symbol = f"SH{std_symbol[2:]}"
            elif std_symbol.startswith("SZ"):
                fin_symbol = f"SZ{std_symbol[2:]}"
            else:
                fin_symbol = std_symbol
                
            result = {}
                
            # Get specified report type
            if report_type in ["balance", "all"]:
                balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=fin_symbol)
                result["balance_sheet"] = balance_sheet.head(periods).to_dict(orient="records")
                
            if report_type in ["income", "all"]:
                income_statement = ak.stock_profit_sheet_by_report_em(symbol=fin_symbol)
                result["income_statement"] = income_statement.head(periods).to_dict(orient="records")
                
            if report_type in ["cashflow", "all"]:
                cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=fin_symbol)
                result["cash_flow"] = cash_flow.head(periods).to_dict(orient="records")
                
            return result
        except Exception as e:
            return {"error": f"Failed to get financial report data: {str(e)}"}
    
    def get_industry_analysis(self, industry: str, metric: Optional[str] = None) -> Dict[str, Any]:
        """
        Get industry analysis data
        
        Args:
            industry: Industry name or code
            metric: Analysis metric
            
        Returns:
            Dictionary with industry analysis data
        """
        try:
            # Get industry stocks
            industry_stocks = ak.stock_board_industry_cons_em(symbol=industry)
            
            # Basic industry info
            result = {
                "industry": industry,
                "stock_count": len(industry_stocks),
                "stocks": industry_stocks.to_dict(orient="records")
            }
            
            # Add metrics if specified
            if metric:
                if metric == "pe":
                    industry_pe = ak.stock_board_industry_cons_em(symbol=industry)
                    result["pe_data"] = industry_pe.to_dict(orient="records")
                elif metric == "pb":
                    industry_pb = ak.stock_board_industry_cons_em(symbol=industry)
                    result["pb_data"] = industry_pb.to_dict(orient="records")
                # Additional metrics would be implemented here
                
            return result
        except Exception as e:
            return {"error": f"Failed to get industry analysis data: {str(e)}"} 