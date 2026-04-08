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

        rule_checks = self._check_business_validity_rules()
        metrics['rule_checks'] = rule_checks
        metrics['overall_validity_score'] = self._calculate_validity_score(rule_checks)
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
        
        # 计算总体质量评分（完整性+唯一性+有效性综合）
        completeness_score = self._calculate_completeness_score(completeness)
        uniqueness_score = self._calculate_uniqueness_score()
        validity_score = validity.get('overall_validity_score', 0.0)
        overall_quality_score = (
            completeness_score * 0.5 +
            uniqueness_score * 0.2 +
            validity_score * 0.3
        )
        
        report = {
            'report_time': pd.Timestamp.now().isoformat(),
            'total_records': len(self.df),
            'overall_quality_score': float(overall_quality_score),
            'score_breakdown': {
                'completeness_score': float(completeness_score),
                'uniqueness_score': float(uniqueness_score),
                'validity_score': float(validity_score),
            },
            'completeness_metrics': completeness,
            'uniqueness_metrics': uniqueness,
            'validity_metrics': validity,
            'issues': self._identify_issues(completeness, uniqueness, validity)
        }
        
        return report
    
    def _identify_issues(self, completeness, uniqueness, validity):
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

        rule_checks = validity.get('rule_checks', {})
        for rule_name, rule in rule_checks.items():
            if rule.get('fail_rate', 0) > 0.02:
                issues.append({
                    'column': rule.get('column', '多字段'),
                    'issue_type': f'有效性异常({rule_name})',
                    'severity': '中' if rule['fail_rate'] <= 0.1 else '高',
                    'description': f"{rule.get('description', rule_name)}，失败率{rule['fail_rate']*100:.2f}%"
                })

        return issues

    def _calculate_completeness_score(self, completeness):
        all_completeness_scores = [m['completeness'] for m in completeness.values()]
        return float(np.mean(all_completeness_scores) * 100) if all_completeness_scores else 0.0

    def _calculate_uniqueness_score(self):
        if len(self.df) == 0:
            return 0.0
        duplicate_row_rate = self.df.duplicated().mean()
        return float((1 - duplicate_row_rate) * 100)

    def _check_business_validity_rules(self):
        checks = {}
        total = max(len(self.df), 1)

        if 'quantity' in self.df.columns:
            fail_count = int((pd.to_numeric(self.df['quantity'], errors='coerce') <= 0).sum())
            checks['quantity_positive'] = {
                'column': 'quantity',
                'description': '数量应为正数',
                'fail_count': fail_count,
                'fail_rate': float(fail_count / total),
            }
        if 'unit_price' in self.df.columns:
            fail_count = int((pd.to_numeric(self.df['unit_price'], errors='coerce') <= 0).sum())
            checks['unit_price_positive'] = {
                'column': 'unit_price',
                'description': '单价应为正数',
                'fail_count': fail_count,
                'fail_rate': float(fail_count / total),
            }
        if 'sales_amount' in self.df.columns:
            fail_count = int((pd.to_numeric(self.df['sales_amount'], errors='coerce') <= 0).sum())
            checks['sales_amount_positive'] = {
                'column': 'sales_amount',
                'description': '销售额应为正数',
                'fail_count': fail_count,
                'fail_rate': float(fail_count / total),
            }
        if {'quantity', 'unit_price', 'sales_amount'}.issubset(self.df.columns):
            expected = pd.to_numeric(self.df['quantity'], errors='coerce') * pd.to_numeric(self.df['unit_price'], errors='coerce')
            actual = pd.to_numeric(self.df['sales_amount'], errors='coerce')
            fail_count = int((expected.notna() & actual.notna() & ((actual - expected).abs() > 1e-6)).sum())
            checks['amount_consistency'] = {
                'column': 'sales_amount',
                'description': '销售额与数量*单价应一致',
                'fail_count': fail_count,
                'fail_rate': float(fail_count / total),
            }
        if 'order_date' in self.df.columns:
            parsed = pd.to_datetime(self.df['order_date'], errors='coerce')
            fail_count = int(parsed.isna().sum())
            checks['order_date_valid'] = {
                'column': 'order_date',
                'description': '订单日期应可解析',
                'fail_count': fail_count,
                'fail_rate': float(fail_count / total),
            }

        return checks

    def _calculate_validity_score(self, rule_checks):
        if not rule_checks:
            return 0.0
        pass_rates = [1 - v['fail_rate'] for v in rule_checks.values()]
        return float(np.mean(pass_rates) * 100)
    
    def get_quality_score(self):
        """
        获取数据质量评分
        
        Returns:
            float: 质量评分（0-100）
        """
        return float(self.generate_quality_report()['overall_quality_score'])
