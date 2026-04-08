"""可视化图表生成模块测试"""

import unittest
import pandas as pd
from src.visualization.charts import ChartGenerator
from src.data_quality.validator import DataQualityValidator


class TestChartGenerator(unittest.TestCase):
    """测试图表生成器"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'region': ['华东', '华北', '华南'],
            'sales_amount': [1000, 2000, 1500]
        })
    
    def test_generate_sales_by_region(self):
        """测试生成区域销售图"""
        chart = ChartGenerator.generate_sales_by_region(self.df)
        self.assertEqual(chart['type'], 'pie')
        self.assertIn('data', chart)


if __name__ == '__main__':
    unittest.main()
