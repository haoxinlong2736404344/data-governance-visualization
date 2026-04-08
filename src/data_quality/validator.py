"""
数据质量验证模块
用于检查和评估数据的完整性、唯一性和有效性
"""

import pandas as pd
import numpy as np


class DataQualityValidator:
    """
    数据质量验证器
    评估数据的完整性、唯一性、有效性等质量指标
    """
    
    def __init__(self, dataframe):
        """
        初始化验证器
        
        Args:
            dataframe (pd.DataFrame): 待验证的数据框
        """
        self.df = dataframe
        self.quality_metrics = {}
        
    def check_completeness(self):
        """
        检查数据完整性
        计算每列的缺失数据数量和缺失率
        
        Returns:
            dict: 包含缺失数据统计的字典
        """
        metrics = {}
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            missing_rate = missing_count / len(self.df)
            metrics[col] = {
                'missing_count': int(missing_count),
                'missing_rate': float(missing_rate),
                'completeness': float(1 - missing_rate)
            }
        return metrics
    
    def check_uniqueness(self):
        """
        检查数据唯一性
        检测重复数据
        
        Returns:
            dict: 包含唯一性统计的字典
        """
        metrics = {}
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                unique_count = self.df[col].nunique()
                duplicate_count = len(self.df) - unique_count
                metrics[col] = {
                    'unique_count': int(unique_count),
                    'duplicate_count': int(duplicate_count),
                    'duplicate_rate': float(duplicate_count / len(self.df)) if len(self.df) > 0 else 0.0
                }
        return metrics
    
    def check_validity(self):
        """
        检查数据有效性
        验证数值列的范围和分布
        
        Returns:
            dict: 包含有效性统计的字典
        """
        metrics = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            valid_data = self.df[col].dropna()
            if len(valid_data) > 0:
                metrics[col] = {
                    'min': float(valid_data.min()),
                    'max': float(valid_data.max()),
                    'mean': float(valid_data.mean()),
                    'median': float(valid_data.median()),
                    'std': float(valid_data.std()),
                    'valid_count': int(len(valid_data))
                }
        return metrics
    
    def generate_quality_report(self):
        """
        生成完整的数据质量报告
        
        Returns:
            dict: 包含所有质量指标的报告字典
        """
        completeness = self.check_completeness()
        uniqueness = self.check_uniqueness()
        validity = self.check_validity()
        
        # 计算总体质量评分
        all_completeness_scores = [m['completeness'] for m in completeness.values()]
        overall_completeness = np.mean(all_completeness_scores)
        
        report = {
            'report_time': pd.Timestamp.now().isoformat(),
            'total_records': len(self.df),
            'overall_quality_score': float(overall_completeness * 100),
            'completeness_metrics': completeness,
            'uniqueness_metrics': uniqueness,
            'validity_metrics': validity,
            'issues': self._identify_issues(completeness, uniqueness)
        }
        
        return report
    
    def _identify_issues(self, completeness, uniqueness):
        """
        识别数据质量问题
        
        Args:
            completeness (dict): 完整性指标
            uniqueness (dict): 唯一性指标
            
        Returns:
            list: 发现的问题列表
        """
        issues = []
        
        # 检查缺失数据过多
        for col, metrics in completeness.items():
            if metrics['missing_rate'] > 0.05:  # 缺失率超过5%
                issues.append({
                    'column': col,
                    'issue_type': '缺失数据过多',
                    'severity': '高',
                    'description': f'{col}列缺失率达{metrics["missing_rate"]*100:.2f}%'
                })
        
        # 检查重复数据过多
        for col, metrics in uniqueness.items():
            if metrics['duplicate_rate'] > 0.3:  # 重复率超过30%
                issues.append({
                    'column': col,
                    'issue_type': '重复数据',
                    'severity': '中',
                    'description': f'{col}列重复率达{metrics["duplicate_rate"]*100:.2f}%'
                })
        
        return issues
    
    def get_quality_score(self):
        """
        获取数据质量评分
        
        Returns:
            float: 质量评分（0-100）
        """
        completeness = self.check_completeness()
        all_completeness_scores = [m['completeness'] for m in completeness.values()]
        return float(np.mean(all_completeness_scores) * 100)
