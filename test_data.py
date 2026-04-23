import pandas as pd
# 导入你写好的数据采集模块
from src.data_collection.collector import DataCollector

# 1. 实例化采集器并生成数据（使用默认的 1000 行，避免报错）
print("="*15, "1. 标准化后的数据预览 (df.head)", "="*15)
collector = DataCollector()
df = collector.generate_sample_sales_data() # 不传参数，默认生成1000行

# 打印前5行数据，展示列名已经变成 order_id, order_date 等
print(df.head())
print("\n")

# 2. 打印数据类型信息
print("="*15, "2. 标准化后的数据类型 (df.info)", "="*15)
# 展示 datetime 和 float64 等格式转换成功
df.info()