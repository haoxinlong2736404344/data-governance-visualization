"""元数据管理模块测试"""

import unittest
import pandas as pd
from src.data_governance.metadata import MetadataManager


class TestMetadataManager(unittest.TestCase):
    """测试元数据管理器"""
    
    def setUp(self):
        self.df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        self.manager = MetadataManager()
    
    def test_register_dataset(self):
        """测试注册数据集"""
        metadata = self.manager.register_dataset(
            'test_dataset',
            self.df,
            '测试数据集',
            '测试用户'
        )
        self.assertEqual(metadata['dataset_name'], 'test_dataset')
    
    def test_list_all_datasets(self):
        """测试列出所有数据集"""
        self.manager.register_dataset('ds1', self.df, 'desc', 'owner')
        datasets = self.manager.list_all_datasets()
        self.assertIn('ds1', datasets)


if __name__ == '__main__':
    unittest.main()
