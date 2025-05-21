import akshare as ak
print("获取金融数据演示")

# 获取股票列表
print("\n1. 获取A股上市公司基本信息")
stock_info = ak.stock_info_a_code_name()
print(stock_info.head())

# 获取实时行情
print("\n2. 获取股票实时行情数据")
stock_quote = ak.stock_zh_a_spot_em()
print(stock_quote.head())

# 获取个股历史数据
print("\n3. 获取个股历史数据-贵州茅台")
maotai_hist = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date="20240401", end_date="20240520", adjust="")
print(maotai_hist.head())

# 获取财务指标
print("\n4. 获取财务指标数据-贵州茅台")
try:
    financial_indicator = ak.stock_financial_analysis_indicator(symbol="600519")
    print(financial_indicator.head())
except Exception as e:
    print(f"获取财务指标失败: {e}")
