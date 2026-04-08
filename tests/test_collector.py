"""数据采集模块测试"""

import unittest
from src.data_collection.collector import DataCollector


class TestDataCollector(unittest.TestCase):
    """测试数据采集器"""
    
    def setUp(self):
        self.collector = DataCollector()
    
    def test_generate_sample_data(self):
        """测试生成样本数据"""
        data = self.collector.generate_sample_sales_data(rows=100)
        self.assertEqual(len(data), 100)
        self.assertIn('order_id', data.columns)
        self.assertIn('sales_amount', data.columns)
    
    def test_get_data(self):
        """测试获取数据"""
        data = self.collector.generate_sample_sales_data()
        retrieved_data = self.collector.get_data()
        self.assertEqual(len(data), len(retrieved_data))
    
    def test_get_data_summary(self):
        """测试获取数据摘要"""
        self.collector.generate_sample_sales_data()
        summary = self.collector.get_data_summary()
        self.assertIn('total_rows', summary)
        self.assertIn('total_columns', summary)


if __name__ == '__main__':
    unittest.main()
