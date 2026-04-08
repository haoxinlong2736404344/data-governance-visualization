#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动Web仪表板脚本
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.data_collection.collector import DataCollector
from src.data_quality.validator import DataQualityValidator
from src.data_governance.metadata import MetadataManager
from src.data_governance.kpi import GovernanceKPI
from src.visualization.charts import ChartGenerator
from src.visualization.governance_flow import GovernanceFlow
from src.visualization.web_dashboard import WebDashboard


def main():
    try:
        print("=" * 70)
        print("🌐 启动数据治理Web仪表板")
        print("=" * 70)

        # 1. 准备数据
        print("\n[1/6] 准备数据...")
        collector = DataCollector()
        sales_data = collector.generate_sample_sales_data(rows=1000)
        print(f"✓ 已采集 {len(sales_data)} 条数据")

        # 2. 质量评估
        print("[2/6] 质量评估...")
        validator = DataQualityValidator(sales_data)
        quality_report = validator.generate_quality_report()
        print(f"✓ 质量评分：{quality_report['overall_quality_score']:.2f}/100")

        # 3. 数据治理
        print("[3/6] 数据治理...")
        metadata_mgr = MetadataManager()
        metadata_mgr.register_dataset('sales_2024', sales_data, '销售数据', '数据团队', ['销售'])
        print("✓ 元数据已注册")

        # 4. 生成图表
        print("[4/6] 生成图表...")
        chart_gen = ChartGenerator()
        charts = {
            'completeness': chart_gen.generate_completeness_chart(quality_report),
            'region_sales': chart_gen.generate_sales_by_region(sales_data),
            'channel_analysis': chart_gen.generate_channel_comparison(sales_data),
            'sales_trend': chart_gen.generate_sales_trend(sales_data),
        }
        print(f"✓ 已生成 {len(charts)} 张图表")

        # 5. 生成KPI
        print("[5/6] 计算KPI指标...")
        kpi_calc = GovernanceKPI(quality_report, metadata_mgr)
        kpi_report = kpi_calc.get_kpi_report()
        print(f"✓ KPI评分：{kpi_report['kpis']['总体治理评分']:.2f}")

        # 6. 治理流程
        print("[6/6] 治理流程...")
        flow = GovernanceFlow()
        governance_flow = flow.generate_governance_flow_diagram()
        print("✓ 治理流程已生成")

        # 启动Web仪表板
        print("\n" + "=" * 70)
        print("✓ 所有数据已准备就绪！")
        print("=" * 70)

        dashboard = WebDashboard('DataGovernancePlatform')
        dashboard.set_data(quality_report, kpi_report, charts, governance_flow)

        print("\n🌐 Web仪表板启动中...")
        print("📍 访问地址：http://127.0.0.1:5000")
        print("⚠️  按 Ctrl+C 停止服务器\n")

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
        print("\n\n👋 Web仪表板已关闭")