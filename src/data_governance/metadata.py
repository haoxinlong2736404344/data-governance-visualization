"""
数据治理元数据管理模块
用于管理数据集的元信息、生成数据字典等
"""

import pandas as pd
import json
from datetime import datetime


class MetadataManager:
    """
    元数据管理器
    管理数据集的元信息、列级元数据和数据字典
    """
    
    def __init__(self):
        """初始化元数据管理器"""
        self.metadata_registry = {}
        
    def register_dataset(self, dataset_name, dataframe, description, owner, tags=None):
        """
        注册数据集元数据
        
        Args:
            dataset_name (str): 数据集名称
            dataframe (pd.DataFrame): 数据框
            description (str): 数据集描述
            owner (str): 数据集所有者
            tags (list): 数据集标签，默认为None
            
        Returns:
            dict: 注册的元数据
        """
        metadata = {
            'dataset_name': dataset_name,
            'description': description,
            'owner': owner,
            'created_time': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'record_count': len(dataframe),
            'column_count': len(dataframe.columns),
            'columns': self._extract_column_metadata(dataframe),
            'tags': tags or [],
            'data_classification': 'internal',
            'quality_score': 0.0
        }
        
        self.metadata_registry[dataset_name] = metadata
        return metadata
    
    def _extract_column_metadata(self, dataframe):
        """
        提取列级元数据
        
        Args:
            dataframe (pd.DataFrame): 数据框
            
        Returns:
            list: 列级元数据列表
        """
        columns_meta = []
        
        for col in dataframe.columns:
            col_meta = {
                'column_name': col,
                'data_type': str(dataframe[col].dtype),
                'nullable': bool(dataframe[col].isna().any()),
                'unique_values': int(dataframe[col].nunique())
            }
            columns_meta.append(col_meta)
        
        return columns_meta
    
    def get_dataset_metadata(self, dataset_name):
        """
        获取数据集元数据
        
        Args:
            dataset_name (str): 数据集名称
            
        Returns:
            dict: 数据集元数据，如果不存在则返回None
        """
        return self.metadata_registry.get(dataset_name)
    
    def list_all_datasets(self):
        """
        列出所有注册的数据集
        
        Returns:
            list: 数据集名称列表
        """
        return list(self.metadata_registry.keys())
    
    def generate_data_dictionary(self):
        """
        生成数据字典
        包含所有已注册数据集的所有字段信息
        
        Returns:
            pd.DataFrame: 数据字典数据框
        """
        dictionary = []
        
        for dataset_name, metadata in self.metadata_registry.items():
            for col in metadata['columns']:
                dictionary.append({
                    'dataset': dataset_name,
                    'column': col['column_name'],
                    'type': col['data_type'],
                    'owner': metadata['owner'],
                    'nullable': col['nullable'],
                    'unique_values': col['unique_values']
                })
        
        return pd.DataFrame(dictionary)
    
    def update_quality_score(self, dataset_name, quality_score):
        """
        更新数据集质量评分
        
        Args:
            dataset_name (str): 数据集名称
            quality_score (float): 质量评分
        """
        if dataset_name in self.metadata_registry:
            self.metadata_registry[dataset_name]['quality_score'] = quality_score
            self.metadata_registry[dataset_name]['last_modified'] = datetime.now().isoformat()
    
    def export_metadata(self, filepath):
        """
        导出元数据为JSON文件
        
        Args:
            filepath (str): 导出文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_registry, f, ensure_ascii=False, indent=2, default=str)
