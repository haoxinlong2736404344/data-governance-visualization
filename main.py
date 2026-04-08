#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据治理与可视化分析平台 - 主程序
Data Governance and Visualization Platform - Main Program
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from src.data_collection.collector import DataCollector
from src.data_quality.validator import DataQualityValidator
from src.data_governance.metadata import MetadataManager
from src.visualization.charts import ChartGenerator
from src.data_governance.kpi import GovernanceKPI
from src.visualization.governance_flow import GovernanceFlow
import pandas as pd


def generate_html_report(quality_report, charts):
    """生成HTML可视化仪表板"""
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>数据治理与可视化仪表板</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; }}
            body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 40px; text-align: center; }}
            .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
            .header p {{ font-size: 14px; opacity: 0.9; }}
            .container {{ max-width: 1400px; margin: 20px auto; padding: 0 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); 
                    gap: 20px; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                    padding: 20px; }}
            .card h2 {{ font-size: 18px; margin-bottom: 15px; color: #333; 
                       border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            .card-full {{ grid-column: 1 / -1; }}
            .chart-container {{ width: 100%; height: 400px; }}
            .quality-score {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; text-align: center; padding: 40px; border-radius: 8px; }}
            .score-value {{ font-size: 64px; font-weight: bold; margin: 20px 0; }}
            .score-label {{ font-size: 16px; opacity: 0.9; }}
            .score-stats {{ margin-top: 20px; font-size: 14px; display: flex; 
                           justify-content: space-around; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f5f5f5; font-weight: bold; color: #333; }}
            tr:hover {{ background: #f9f9f9; }}
            .severity-高 {{ color: #f56c6c; font-weight: bold; }}
            .severity-中 {{ color: #e6a23c; font-weight: bold; }}
            .severity-低 {{ color: #67c23a; font-weight: bold; }}
            .footer {{ text-align: center; padding: 30px; color: #999; font-size: 12px; 
                      border-top: 1px solid #ddd; margin-top: 40px; }}
            .message {{ background: #f0f9ff; border-left: 4px solid #667eea; 
                       padding: 15px; margin: 10px 0; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 数据治理与可视化仪表板</h1>
            <p>电商销售数据治理与分析平台 | 生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="container">
            <!-- 质量评分卡 -->
            <div class="grid">
                <div class="card card-full">
                    <h2>📈 数据质量评分</h2>
                    <div class="quality-score">
                        <div class="score-value">{quality_report['overall_quality_score']:.1f}</div>
                        <div class="score-label">总体质量评分</div>
                        <div class="score-stats">
                            <div>总记录数: {quality_report['total_records']}</div>
                            <div>发现问题: {len(quality_report['issues'])}</div>
                            <div>质量等级: {'优秀' if quality_report['overall_quality_score'] >= 80 else '良好' if quality_report['overall_quality_score'] >= 60 else '需改进'}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 图表区域 -->
            <div class="grid">
                <div class="card card-full">
                    <h2>📊 数据完整性分析</h2>
                    <div id="completeness-chart" class="chart-container"></div>
                </div>
                
                <div class="card">
                    <h2>🌍 区域销售占比</h2>
                    <div id="region-chart" class="chart-container"></div>
                </div>
                
                <div class="card">
                    <h2>📈 销售渠道分析</h2>
                    <div id="channel-chart" class="chart-container"></div>
                </div>
                
                <div class="card card-full">
                    <h2>📉 销售趋势</h2>
                    <div id="trend-chart" class="chart-container"></div>
                </div>
                
                <div class="card card-full">
                    <h2>⚠️ 数据质量问题清单</h2>
    """
    
    if quality_report['issues']:
        html += """
                    <table>
                        <tr>
                            <th>列名</th>
                            <th>问题类型</th>
                            <th>严重程度</th>
                            <th>描述</th>
                        </tr>
        """
        for issue in quality_report['issues']:
            severity_class = f"severity-{issue['severity']}"
            html += f"""
                        <tr>
                            <td><strong>{issue['column']}</strong></td>
                            <td>{issue['issue_type']}</td>
                            <td><span class="{severity_class}">{issue['severity']}</span></td>
                            <td>{issue['description']}</td>
                        </tr>
            """
        html += """
                    </table>
        """
    else:
        html += """
                    <div class="message">✓ 恭喜！数据质量优秀，暂无严重问题</div>
        """
    
    html += f"""
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2026 数据治理与可视化课程设计项目 | 平台版本 1.0</p>
            <p>用户：郝新龙 | 生成时间：{pd.Timestamp.now().isoformat()}</p>
        </div>
        
        <script>
            function initCharts(chartsData) {{
                const charts = JSON.parse(chartsData);
                
                // 完整性图表
                const completenessChart = echarts.init(document.getElementById('completeness-chart'));
                completenessChart.setOption({{
                    title: {{ text: '' }},
                    xAxis: {{ type: 'category', data: charts.completeness.xAxis }},
                    yAxis: {{ type: 'value', max: 100 }},
                    series: charts.completeness.series,
                    tooltip: {{ trigger: 'axis' }}
                }});
                
                // 区域销售图
                const regionChart = echarts.init(document.getElementById('region-chart'));
                regionChart.setOption({{
                    title: {{ text: '' }},
                    tooltip: {{ trigger: 'item' }},
                    series: [{{ type: 'pie', data: charts.region_sales.data, radius: ['40%', '70%'] }}]
                }});
                
                // 渠道分析图
                const channelChart = echarts.init(document.getElementById('channel-chart'));
                channelChart.setOption({{
                    title: {{ text: '' }},
                    xAxis: {{ type: 'category', data: charts.channel_analysis.xAxis }},
                    yAxis: [{{ type: 'value' }}, {{ type: 'value' }}],
                    series: charts.channel_analysis.series,
                    tooltip: {{ trigger: 'axis' }}
                }});
                
                // 销售趋势图
                const trendChart = echarts.init(document.getElementById('trend-chart'));
                trendChart.setOption({{
                    title: {{ text: '' }},
                    xAxis: {{ type: 'category', data: charts.sales_trend.xAxis }},
                    yAxis: {{ type: 'value' }},
                    series: charts.sales_trend.series,
                    tooltip: {{ trigger: 'axis' }},
                    grid: {{ left: '60px', right: '40px', top: '40px', bottom: '80px' }}
                }});
            }}
            
            const chartsJson = '{json.dumps(charts, ensure_ascii=False, default=str)}';
            initCharts(chartsJson);
        </script>
    </body>
    </html>
    """
    return html


def main():
    print("=" * 70)
    print("数据治理与可视化分析平台 - 课程设计项目")
    print("=" * 70)
    
    # 1. 数据采集
    print("\n[步骤1] 数据采集中...")
    collector = DataCollector()
    sales_data = collector.generate_sample_sales_data(rows=1000)
    print(f"✓ 成功采集 {len(sales_data)} 条销售数据")
    print(f"✓ 包含字段：{', '.join(sales_data.columns.tolist())}")
    
    # 2. 数据质量评估
    print("\n[步骤2] 数据质量评估中...")
    quality_validator = DataQualityValidator(sales_data)
    quality_report = quality_validator.generate_quality_report()
    print(f"✓ 数据质量评分：{quality_report['overall_quality_score']:.2f}/100")
    print(f"✓ 发现 {len(quality_report['issues'])} 个数据质量问题")
    
    # 3. 数据治理
    print("\n[步骤3] 数据治理中...")
    metadata_mgr = MetadataManager()
    dataset_meta = metadata_mgr.register_dataset(
        dataset_name='sales_2024',
        dataframe=sales_data,
        description='2024年电商销售数据集',
        owner='数据治理团队',
        tags=['销售', '电商', '关键数据']
    )
    metadata_mgr.update_quality_score('sales_2024', quality_report['overall_quality_score'])
    print(f"✓ 已注册数据集：sales_2024")
    print(f"✓ 数据字典已生成")
    
    # 4. 生成可视化
    print("\n[步骤4] 生成可视化图表中...")
    chart_gen = ChartGenerator()
    
    charts = {
        'quality_score': chart_gen.generate_quality_scorecard(quality_report),
        'completeness': chart_gen.generate_completeness_chart(quality_report),
        'issues': chart_gen.generate_data_quality_issue_table(quality_report),
        'region_sales': chart_gen.generate_sales_by_region(sales_data),
        'sales_trend': chart_gen.generate_sales_trend(sales_data),
        'channel_analysis': chart_gen.generate_channel_comparison(sales_data),
    }
    print(f"✓ 已生成 {len(charts)} 张可视化图表")
    
    # 5. 生成报告
    print("\n[步骤5] 生成综合报告...")
    os.makedirs('reports', exist_ok=True)
    
    # 保存质量报告
    with open('reports/quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2, default=str)

    # 6. 计算治理KPI指标
    print("\n[步骤6] 计算KPI指标中...")
    kpi_calculator = GovernanceKPI(quality_report, metadata_mgr)
    kpi_report = kpi_calculator.get_kpi_report()
    print(f"✓ KPI指标已生成：{kpi_report['kpis']['总体治理评分']:.2f}分")

    # 7. 生成治理流程
    print("\n[步骤7] 生成治理流程中...")
    governance_flow = GovernanceFlow()
    flow_diagram = governance_flow.generate_governance_flow_diagram()
    flow_stages = governance_flow.generate_governance_stages()
    print(f"✓ 治理流程图已生成")
    print(f"✓ 治理阶段分布已生成")

    # 8. 导出KPI报告
    print("\n[步骤8] 导出KPI报告...")
    kpi_calculator.export_kpi_report('reports/kpi_report.json')
    print("✓ KPI报告已生成：reports/kpi_report.json")

    # 在生成HTML仪表板时，将新数据添加到 charts
    charts['governance_flow'] = flow_diagram
    charts['governance_stages'] = flow_stages
    
    # 保存元数据
    metadata_mgr.export_metadata('reports/metadata.json')
    
    # 生成HTML仪表板
    html_content = generate_html_report(quality_report, charts)
    with open('reports/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ HTML仪表板已生成：reports/dashboard.html")
    print("✓ 质量报告已生成：reports/quality_report.json")
    print("✓ 元数据已生成：reports/metadata.json")
    
    print("\n" + "=" * 70)
    print("✓ 项目完成！")
    print("=" * 70)
    print("\n生成的文件位置：")
    print("  📊 reports/dashboard.html (打开此文件查看可视化仪表板)")
    print("  📄 reports/quality_report.json (数据质量报告)")
    print("  📋 reports/metadata.json (元数据和数据字典)")


if __name__ == '__main__':
    main()
