"""数据质量验证模块测试"""

import unittest
import pandas as pd
from src.data_quality.validator import DataQualityValidator


class TestDataQualityValidator(unittest.TestCase):
    """测试数据质量验证器"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'col1': [1, 2, 3, None, 5],
            'col2': ['a', 'b', 'c', 'a', 'b']
        })
        self.validator = DataQualityValidator(self.df)
    
    def test_check_completeness(self):
        """测试完整性检查"""
        metrics = self.validator.check_completeness()
        self.assertIn('col1', metrics)
        self.assertIn('col2', metrics)
    
    def test_generate_quality_report(self):
        """测试生成质量报告"""
        report = self.validator.generate_quality_report()
        self.assertIn('overall_quality_score', report)
        self.assertIn('completeness_metrics', report)


if __name__ == '__main__':
    unittest.main()
