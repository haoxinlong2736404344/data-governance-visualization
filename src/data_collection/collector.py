"""
数据采集模块
用于从多个数据源采集、加载和预处理数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataCollector:
    """
    数据采集器 - 从多个数据源采集数据
    支持生成模拟数据和加载真实数据
    """
    
    def __init__(self):
        """初始化数据采集器"""
        self.data_sources = []
        self.collected_data = None
        
    def generate_sample_sales_data(self, rows=1000):
        """
        生成样本销售数据
        
        Args:
            rows (int): 生成的数据行数，默认1000条
            
        Returns:
            pd.DataFrame: 生成的销售数据框
        """
        np.random.seed(42)
        
        data = {
            'order_id': [f'ORD{i:06d}' for i in range(1, rows + 1)],
            'order_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) 
                          for _ in range(rows)],
            'customer_id': [f'CUST{i % 200:04d}' for i in range(1, rows + 1)],
            'product_id': [f'PROD{np.random.randint(1, 50):03d}' for _ in range(rows)],
            'quantity': np.random.randint(1, 20, rows),
            'unit_price': np.random.uniform(10, 500, rows),
            'region': np.random.choice(['华东', '华北', '华南', '华中', '西部'], rows),
            'channel': np.random.choice(['线上', '门店', '经销商'], rows),
            'sales_amount': np.random.uniform(100, 5000, rows),
            'discount_rate': np.random.uniform(0, 0.3, rows),
        }
        
        df = pd.DataFrame(data)
        
        # 添加一些数据缺陷（用于后续数据质量评估）
        df.loc[np.random.choice(df.index, 50, replace=False), 'unit_price'] = np.nan
        df.loc[np.random.choice(df.index, 30, replace=False), 'customer_id'] = 'CUST0000'
        
        self.collected_data = df
        return df
    
    def load_from_csv(self, filepath):
        """
        从CSV文件加载数据
        
        Args:
            filepath (str): CSV文件路径
            
        Returns:
            pd.DataFrame: 加载的数据框
        """
        try:
            self.collected_data = pd.read_csv(filepath)
            return self.collected_data
        except FileNotFoundError:
            print(f"错误：文件 {filepath} 不存在")
            return None
    
    def get_data_summary(self):
        """
        获取数据摘要信息
        
        Returns:
            dict: 包含行数、列数、列名、数据类型等的摘要信息
        """
        if self.collected_data is None:
            return None
            
        return {
            'total_rows': len(self.collected_data),
            'total_columns': len(self.collected_data.columns),
            'columns': self.collected_data.columns.tolist(),
            'dtypes': self.collected_data.dtypes.to_dict(),
            'memory_usage': int(self.collected_data.memory_usage(deep=True).sum()),
        }
    
    def get_data(self):
        """
        获取采集的数据
        
        Returns:
            pd.DataFrame: 采集的数据框
        """
        return self.collected_data
    
    def preview_data(self, head=5):
        """
        预览数据前几行
        
        Args:
            head (int): 预览行数，默认5行
            
        Returns:
            pd.DataFrame: 数据预览
        """
        if self.collected_data is None:
            return None
        return self.collected_data.head(head)
