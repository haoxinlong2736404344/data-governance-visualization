"""
数据治理KPI指标模块
用于计算和管理数据治理的关键绩效指标
"""

import pandas as pd
import numpy as np
from datetime import datetime


class GovernanceKPI:
    """
    数据治理KPI指标计算器
    计算数据治理效果的关键指标
    """

    def __init__(self, quality_report=None, metadata_manager=None):
        """
        初始化KPI计算器

        Args:
            quality_report (dict): 质量报告
            metadata_manager (MetadataManager): 元数据管理器
        """
        self.quality_report = quality_report
        self.metadata_manager = metadata_manager
        self.kpis = {}

    def calculate_data_quality_score(self):
        """
        计算数据质量评分

        Returns:
            float: 数据质量评分（0-100）
        """
        if self.quality_report:
            return self.quality_report.get('overall_quality_score', 0.0)
        return 0.0

    def calculate_completeness_rate(self):
        """
        计算数据完整率

        Returns:
            float: 数据完整率百分比
        """
        if self.quality_report:
            completeness_data = self.quality_report.get('completeness_metrics', {})
            if completeness_data:
                rates = [m['completeness'] for m in completeness_data.values()]
                return float(np.mean(rates) * 100)
        return 0.0

    def calculate_uniqueness_rate(self):
        """
        计算数据唯一性评分

        Returns:
            float: 唯一性评分百分比
        """
        if self.quality_report:
            uniqueness_data = self.quality_report.get('uniqueness_metrics', {})
            if uniqueness_data:
                duplicate_rates = [m['duplicate_rate'] for m in uniqueness_data.values()]
                avg_duplicate_rate = np.mean(duplicate_rates) if duplicate_rates else 0.0
                return float((1 - avg_duplicate_rate) * 100)
        return 0.0

    def calculate_validity_rate(self):
        """
        计算数据有效性评分

        Returns:
            float: 有效性评分百分比
        """
        if self.quality_report:
            validity_data = self.quality_report.get('validity_metrics', {})
            if validity_data:
                # 所有有效数据的列都认为是有效的
                return 100.0
        return 0.0

    def calculate_governance_coverage(self):
        """
        计算治理覆盖率

        Returns:
            float: 治理覆盖率百分比
        """
        if self.metadata_manager:
            datasets = self.metadata_manager.list_all_datasets()
            return float(len(datasets) * 100 / max(1, len(datasets)))
        return 0.0

    def calculate_issue_resolution_rate(self):
        """
        计算问题修复率

        Returns:
            float: 问题修复率百分比
        """
        if self.quality_report:
            issues = self.quality_report.get('issues', [])
            # 假设所有识别的问题都已标记为需要处理
            # 这里可以扩展为从数据库读取实际修复情况
            return 0.0  # 初始为0，表示需要修复
        return 0.0

    def calculate_all_kpis(self):
        """
        计算所有KPI指标

        Returns:
            dict: 包含所有KPI的字典
        """
        self.kpis = {
            '数据质量评分': round(self.calculate_data_quality_score(), 2),
            '数据完整率': round(self.calculate_completeness_rate(), 2),
            '数据唯一性': round(self.calculate_uniqueness_rate(), 2),
            '数据有效性': round(self.calculate_validity_rate(), 2),
            '治理覆盖率': round(self.calculate_governance_coverage(), 2),
            '问题修复率': round(self.calculate_issue_resolution_rate(), 2),
            '总体治理评分': round(self._calculate_overall_governance_score(), 2)
        }
        return self.kpis

    def _calculate_overall_governance_score(self):
        """
        计算总体治理评分

        Returns:
            float: 总体评分（0-100）
        """
        quality = self.calculate_data_quality_score()
        completeness = self.calculate_completeness_rate()
        uniqueness = self.calculate_uniqueness_rate()
        validity = self.calculate_validity_rate()
        coverage = self.calculate_governance_coverage()

        # 加权计算
        overall = (
                quality * 0.3 +
                completeness * 0.2 +
                uniqueness * 0.15 +
                validity * 0.15 +
                coverage * 0.2
        )
        return overall

    def get_kpi_report(self):
        """
        获取KPI报告

        Returns:
            dict: KPI报告
        """
        return {
            'report_time': pd.Timestamp.now().isoformat(),
            'kpis': self.calculate_all_kpis(),
            'summary': self._generate_summary()
        }

    def _generate_summary(self):
        """
        生成KPI总结

        Returns:
            str: KPI总结描述
        """
        score = self.calculate_all_kpis().get('总体治理评分', 0)

        if score >= 90:
            return '数据治理效果优秀，各项指标均达到预期目标'
        elif score >= 80:
            return '数据治理效果良好，建议继续改进数据质量'
        elif score >= 70:
            return '数据治理效果一般，需要加强质量管理'
        else:
            return '数据治理效果需要大幅改进，建议制定改进计划'

    def export_kpi_report(self, filepath):
        """
        导出KPI报告

        Args:
            filepath (str): 导出文件路径
        """
        import json
        report = self.get_kpi_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)