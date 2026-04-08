"""
可视化图表生成模块
用于生成交互式的ECharts图表
"""

import json
import pandas as pd
from datetime import datetime


class ChartGenerator:
    """
    图表生成器
    创建用于HTML仪表板的ECharts图表配置
    """
    
    @staticmethod
    def generate_quality_scorecard(quality_report):
        """
        生成质量评分卡
        
        Args:
            quality_report (dict): 质量报告
            
        Returns:
            dict: 评分卡配置
        """
        score = quality_report['overall_quality_score']
        return {
            'type': 'gauge',
            'title': '数据质量总体评分',
            'score': score,
            'max_score': 100,
            'color': 'green' if score > 80 else ('orange' if score > 60 else 'red')
        }
    
    @staticmethod
    def generate_completeness_chart(quality_report):
        """
        生成完整性分析图
        
        Args:
            quality_report (dict): 质量报告
            
        Returns:
            dict: 完整性图表配置
        """
        completeness_data = quality_report['completeness_metrics']
        
        chart = {
            'type': 'bar',
            'title': '数据完整性分析',
            'xAxis': list(completeness_data.keys()),
            'yAxis': [m['completeness'] * 100 for m in completeness_data.values()],
            'series': [{
                'name': '完整性(%)',
                'data': [m['completeness'] * 100 for m in completeness_data.values()],
                'type': 'bar',
                'itemStyle': {'color': '#5470C6'}
            }]
        }
        return chart
    
    @staticmethod
    def generate_data_quality_issue_table(quality_report):
        """
        生成数据质量问题表
        
        Args:
            quality_report (dict): 质量报告
            
        Returns:
            dict: 问题表格配置
        """
        issues = quality_report['issues']
        
        if not issues:
            return {
                'type': 'table',
                'title': '数据质量问题',
                'data': [],
                'message': '暂无数据质量问题'
            }
        
        return {
            'type': 'table',
            'title': '数据质量问题',
            'columns': ['列名', '问题类型', '严重程度', '描述'],
            'data': [
                [
                    issue['column'],
                    issue['issue_type'],
                    issue['severity'],
                    issue['description']
                ] for issue in issues
            ]
        }
    
    @staticmethod
    def generate_sales_by_region(dataframe):
        """
        生成区域销售分析图
        
        Args:
            dataframe (pd.DataFrame): 销售数据
            
        Returns:
            dict: 区域销售图表配置
        """
        if 'region' not in dataframe.columns or 'sales_amount' not in dataframe.columns:
            return {'type': 'empty', 'message': '缺少必要列'}
            
        region_sales = dataframe.groupby('region')['sales_amount'].sum().sort_values(ascending=False)
        if len(region_sales) > 10:
            top_regions = region_sales.head(10)
            others_sum = float(region_sales.iloc[10:].sum())
            if others_sum > 0:
                top_regions['其他区域'] = others_sum
            region_sales = top_regions
        
        chart = {
            'type': 'pie',
            'title': '各地区销售占比',
            'data': [
                {'value': float(value), 'name': region}
                for region, value in region_sales.items()
            ]
        }
        return chart
    
    @staticmethod
    def generate_sales_trend(dataframe):
        """
        生成销售趋势图
        
        Args:
            dataframe (pd.DataFrame): 销售数据
            
        Returns:
            dict: 销售趋势图表配置
        """
        if 'order_date' not in dataframe.columns or 'sales_amount' not in dataframe.columns:
            return {'type': 'empty', 'message': '缺少必要列'}
            
        df_copy = dataframe.copy()
        df_copy['date'] = pd.to_datetime(df_copy['order_date']).dt.date
        daily_sales = df_copy.groupby('date')['sales_amount'].sum().sort_index()
        
        chart = {
            'type': 'line',
            'title': '每日销售趋势',
            'xAxis': [str(date) for date in daily_sales.index],
            'series': [{
                'name': '销售额',
                'data': [float(value) for value in daily_sales.values],
                'type': 'line',
                'smooth': True
            }]
        }
        return chart
    
    @staticmethod
    def generate_channel_comparison(dataframe):
        """
        生成渠道对比分析
        
        Args:
            dataframe (pd.DataFrame): 销售数据
            
        Returns:
            dict: 渠道对比图表配置
        """
        if 'channel' not in dataframe.columns or 'sales_amount' not in dataframe.columns:
            return {'type': 'empty', 'message': '缺少必要列'}
            
        channel_analysis = dataframe.groupby('channel').agg({
            'sales_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        chart = {
            'type': 'bar',
            'title': '销售渠道分析',
            'xAxis': channel_analysis['channel'].tolist(),
            'series': [
                {
                    'name': '销售额',
                    'data': [float(v) for v in channel_analysis['sales_amount'].values],
                    'type': 'bar',
                    'itemStyle': {'color': '#5470C6'}
                },
                {
                    'name': '订单数',
                    'data': [int(v) for v in channel_analysis['order_id'].values],
                    'type': 'line',
                    'itemStyle': {'color': '#91CC75'}
                }
            ]
        }
        return chart
