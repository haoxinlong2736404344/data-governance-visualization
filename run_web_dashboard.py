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


def load_static_reports():
    """加载 main.py 生成的静态报告，用于 Web 页整合展示"""
    reports = {}
    file_map = {
        'quality_report.json': 'reports/quality_report.json',
        'kpi_report.json': 'reports/kpi_report.json',
        'metadata.json': 'reports/metadata.json',
        'executive_summary.json': 'reports/executive_summary.json',
    }
    for name, path in file_map.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                reports[name] = json.load(f)
    return reports


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
        }
        print(f"[OK] 已生成 {len(charts)} 张图表")

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

        # 启动Web仪表板
        print("\n" + "=" * 70)
        print("[OK] 所有数据已准备就绪！")
        print("=" * 70)

        dashboard = WebDashboard('DataGovernancePlatform')
        static_reports = load_static_reports()
        if static_reports:
            print(f"[OK] 已加载 {len(static_reports)} 份静态报告用于整合展示")
        else:
            print("[提示] 未检测到静态报告文件，将仅展示实时结果")
        dashboard.set_data(quality_report, kpi_report, charts, governance_flow, static_reports=static_reports)

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