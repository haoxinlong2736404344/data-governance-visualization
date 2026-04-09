#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动Web仪表板脚本
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from src.data_collection.collector import DataCollector
from src.data_collection.public_retail_dataset import PublicRetailDatasetLoader
from src.data_quality.validator import DataQualityValidator
from src.data_governance.metadata import MetadataManager
from src.data_governance.kpi import GovernanceKPI
from src.visualization.charts import ChartGenerator
from src.visualization.governance_flow import GovernanceFlow
from src.visualization.web_dashboard import WebDashboard
from main import build_governance_before_after
import pandas as pd


def build_static_reports(quality_report, kpi_report, metadata_registry, executive_summary):
    """构建静态报告快照（直接由当前Web会话生成）"""
    return {
        'quality_report.json': quality_report,
        'kpi_report.json': kpi_report,
        'metadata.json': metadata_registry,
        'executive_summary.json': executive_summary,
    }


def main():
    try:
        print("=" * 70)
        print("启动数据治理Web仪表板")
        print("=" * 70)

        # 1. 准备数据
        print("\n[1/6] 准备数据...")
        collector = DataCollector()
        source_name = "模拟数据"
        try:
            public_loader = PublicRetailDatasetLoader()
            sales_data, source_name = public_loader.load_best_available()
        except Exception as e:
            print(f"[提示] 真实数据加载失败，回退到模拟数据：{e}")
            sales_data = collector.generate_sample_sales_data(rows=1000)

        print(f"[OK] 已采集 {len(sales_data)} 条数据")
        print(f"[OK] 数据来源：{source_name}")

        # 2. 质量评估
        print("[2/6] 质量评估...")
        validator = DataQualityValidator(sales_data)
        quality_report = validator.generate_quality_report()
        print(f"[OK] 质量评分：{quality_report['overall_quality_score']:.2f}/100")

        # 3. 数据治理
        print("[3/6] 数据治理...")
        metadata_mgr = MetadataManager()
        metadata_mgr.register_dataset('sales_2024', sales_data, '销售数据', '数据团队', ['销售'])
        print("[OK] 元数据已注册")

        # 4. 生成图表
        print("[4/6] 生成图表...")
        chart_gen = ChartGenerator()
        charts = {
            'completeness': chart_gen.generate_completeness_chart(quality_report),
            'region_sales': chart_gen.generate_sales_by_region(sales_data),
            'channel_analysis': chart_gen.generate_channel_comparison(sales_data),
            'sales_trend': chart_gen.generate_sales_trend(sales_data),
            'governance_improvement': build_governance_before_after(sales_data),
        }
        print(f"[OK] 已生成 {len(charts)} 张图表")

        display_quality_report = dict(quality_report)
        before_report_for_display = charts.get('governance_improvement', {}).get('before_report', {})
        if before_report_for_display:
            display_quality_report['issues'] = before_report_for_display.get('issues', [])
            display_quality_report['overall_quality_score'] = before_report_for_display.get(
                'overall_quality_score', display_quality_report.get('overall_quality_score', 0.0)
            )
            display_quality_report['total_records'] = before_report_for_display.get(
                'total_records', display_quality_report.get('total_records', 0)
            )

        # 5. 生成KPI
        print("[5/6] 计算KPI指标...")
        kpi_calc = GovernanceKPI(quality_report, metadata_mgr)
        kpi_report = kpi_calc.get_kpi_report()
        print(f"[OK] KPI评分：{kpi_report['kpis']['总体治理评分']:.2f}")

        # 6. 治理流程
        print("[6/6] 治理流程...")
        flow = GovernanceFlow()
        governance_flow = flow.generate_governance_flow_diagram()
        print("[OK] 治理流程已生成")

        profile = {
            'total_records': int(len(sales_data)),
            'total_sales': float(sales_data['sales_amount'].sum()) if 'sales_amount' in sales_data.columns else 0.0,
            'region_count': int(sales_data['region'].nunique()) if 'region' in sales_data.columns else 0,
            'region_type_count': int(sales_data['region_type'].nunique()) if 'region_type' in sales_data.columns else int(sales_data['region'].nunique()) if 'region' in sales_data.columns else 0,
            'city_count': int(sales_data['city'].nunique()) if 'city' in sales_data.columns else 0,
            'channel_count': int(sales_data['channel'].nunique()) if 'channel' in sales_data.columns else 0,
            'date_start': str(pd.to_datetime(sales_data['order_date'], errors='coerce').min().date()) if 'order_date' in sales_data.columns else '-',
            'date_end': str(pd.to_datetime(sales_data['order_date'], errors='coerce').max().date()) if 'order_date' in sales_data.columns else '-',
        }
        business_context = {
            'audience': '数据治理负责人、运营经理、数据分析师',
            'problem': '解决交易数据缺失/重复导致的报表不可信问题，并量化治理成效',
            'data_source': source_name.replace('Superstore Sales（区域+渠道维度丰富）', 'Superstore 销售公开数据集').replace('Supermarket Sales（含渠道字段）', '超市销售公开数据集').replace('UCI Online Retail', 'UCI 在线零售数据集'),
            'timeliness_note': '当前为公开历史样例数据（便于复现实验），系统支持替换为近一年业务数据进行同口径治理分析',
        }
        executive_summary = {
            'data_source': business_context['data_source'],
            'timeliness_note': business_context['timeliness_note'],
            'profile': profile,
            'quality_score': display_quality_report['overall_quality_score'],
            'issue_count': len(display_quality_report.get('issues', [])),
            'governance_improvement': charts.get('governance_improvement', {}).get('detail', {}),
        }

        # 启动Web仪表板
        print("\n" + "=" * 70)
        print("[OK] 所有数据已准备就绪！")
        print("=" * 70)

        dashboard = WebDashboard('DataGovernancePlatform')
        static_reports = build_static_reports(quality_report, kpi_report, metadata_mgr.metadata_registry, executive_summary)
        print(f"[OK] 已整合 {len(static_reports)} 份静态结果到Web展示")
        dashboard.set_data(
            display_quality_report,
            kpi_report,
            charts,
            governance_flow,
            static_reports=static_reports,
            business_context=business_context,
            profile=profile
        )

        print("\nWeb仪表板启动中...")
        print("访问地址：http://127.0.0.1:5000")
        print("按 Ctrl+C 停止服务器\n")

        dashboard.run(host='127.0.0.1', port=5000, debug=False)

    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWeb仪表板已关闭")