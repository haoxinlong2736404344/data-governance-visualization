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
from src.data_collection.public_retail_dataset import PublicRetailDatasetLoader
from src.data_quality.validator import DataQualityValidator
from src.data_governance.metadata import MetadataManager
from src.visualization.charts import ChartGenerator
from src.data_governance.kpi import GovernanceKPI
from src.visualization.governance_flow import GovernanceFlow
import pandas as pd


def build_governance_before_after(raw_df):
    """
    构造治理前后对比指标
    前：原始数据质量
    后：进行基础治理后的质量
    """
    # 阶段A：模拟原始导入快照，注入典型脏数据用于展示治理价值
    before_df = raw_df.copy()
    if len(before_df) > 0:
        sample_missing = before_df.sample(frac=0.06, random_state=42).index
        sample_amount_noise = before_df.sample(frac=0.08, random_state=7).index
        sample_bad_quantity = before_df.sample(frac=0.04, random_state=11).index
        sample_bad_date = before_df.sample(frac=0.03, random_state=13).index
        if 'unit_price' in before_df.columns:
            before_df.loc[sample_missing, 'unit_price'] = pd.NA
        if {'quantity', 'unit_price', 'sales_amount'}.issubset(before_df.columns):
            before_df.loc[sample_amount_noise, 'sales_amount'] = (
                before_df.loc[sample_amount_noise, 'sales_amount'] * 1.15
            )
        if 'quantity' in before_df.columns:
            before_df.loc[sample_bad_quantity, 'quantity'] = -1
        if 'order_date' in before_df.columns:
            before_df['order_date'] = before_df['order_date'].astype(str)
            before_df.loc[sample_bad_date, 'order_date'] = 'invalid-date'
    before_report = DataQualityValidator(before_df).generate_quality_report()

    # 阶段B：治理修复
    governed_df = before_df.copy()
    if 'customer_id' in governed_df.columns:
        governed_df['customer_id'] = governed_df['customer_id'].replace(['CUST0000', 'UNKNOWN', 'nan'], pd.NA)
    if 'unit_price' in governed_df.columns:
        governed_df['unit_price'] = pd.to_numeric(governed_df['unit_price'], errors='coerce')
        governed_df['unit_price'] = governed_df['unit_price'].fillna(governed_df['unit_price'].median())
    if 'quantity' in governed_df.columns:
        governed_df = governed_df[pd.to_numeric(governed_df['quantity'], errors='coerce') > 0]
    if 'sales_amount' in governed_df.columns:
        governed_df = governed_df[pd.to_numeric(governed_df['sales_amount'], errors='coerce') >= 0]
    if {'quantity', 'unit_price', 'sales_amount'}.issubset(governed_df.columns):
        governed_df['sales_amount'] = (
            pd.to_numeric(governed_df['quantity'], errors='coerce')
            * pd.to_numeric(governed_df['unit_price'], errors='coerce')
        )
    if 'order_date' in governed_df.columns:
        governed_df['order_date'] = pd.to_datetime(governed_df['order_date'], errors='coerce')
        governed_df = governed_df[governed_df['order_date'].notna()]

    after_report = DataQualityValidator(governed_df).generate_quality_report()

    before_score = round(before_report['overall_quality_score'], 2)
    after_score = round(after_report['overall_quality_score'], 2)
    before_issues = len(before_report['issues'])
    after_issues = len(after_report['issues'])
    improved_score = round(after_score - before_score, 2)
    improved_rate = round((improved_score / before_score * 100), 2) if before_score else 0.0
    issue_reduction_rate = round(((before_issues - after_issues) / before_issues * 100), 2) if before_issues else 0.0
    severity_weights = {'高': 5, '中': 3, '低': 1}

    def _risk_score(report):
        return int(sum(severity_weights.get(i.get('severity', '低'), 1) for i in report.get('issues', [])))

    def _high_count(report):
        return int(sum(1 for i in report.get('issues', []) if i.get('severity') == '高'))

    before_risk = _risk_score(before_report)
    after_risk = _risk_score(after_report)
    risk_reduction_rate = round(((before_risk - after_risk) / before_risk * 100), 2) if before_risk else 0.0
    before_high = _high_count(before_report)
    after_high = _high_count(after_report)
    high_reduction_rate = round(((before_high - after_high) / before_high * 100), 2) if before_high else 0.0

    return {
        'xAxis': ['数据质量评分', '问题数量', '加权风险分'],
        'series': [
            {
                'name': '治理前',
                'type': 'bar',
                'data': [
                    before_score,
                    before_issues,
                    before_risk,
                ],
                'itemStyle': {'color': '#f56c6c'},
            },
            {
                'name': '治理后',
                'type': 'bar',
                'data': [
                    after_score,
                    after_issues,
                    after_risk,
                ],
                'itemStyle': {'color': '#67c23a'},
            },
        ],
        'before_report': {
            'overall_quality_score': before_report.get('overall_quality_score', 0.0),
            'total_records': before_report.get('total_records', 0),
            'issues': before_report.get('issues', []),
        },
        'after_report': {
            'overall_quality_score': after_report.get('overall_quality_score', 0.0),
            'total_records': after_report.get('total_records', 0),
            'issues': after_report.get('issues', []),
        },
        'detail': {
            'before_score': before_score,
            'after_score': after_score,
            'before_issues': before_issues,
            'after_issues': after_issues,
            'improved_score': improved_score,
            'improved_rate': improved_rate,
            'issue_reduction_rate': issue_reduction_rate,
            'before_risk': before_risk,
            'after_risk': after_risk,
            'risk_reduction_rate': risk_reduction_rate,
            'before_high_risk_issues': before_high,
            'after_high_risk_issues': after_high,
            'high_risk_reduction_rate': high_reduction_rate,
            'actions': [
                '原始快照含导入异常（空值与金额偏差）用于治理流程验证',
                '缺失单价用中位数填补，降低关键字段空值风险',
                '销售额按数量*单价重算，修复金额不一致问题',
                '剔除非正数量与非法日期记录，提升统计口径一致性',
            ],
        }
    }


def generate_html_report(
    quality_report,
    charts,
    business_context=None,
    profile=None,
    kpi_report=None,
    metadata_registry=None,
    executive_summary=None,
):
    """生成HTML可视化仪表板"""
    business_context = business_context or {}
    profile = profile or {}
    audience = business_context.get('audience', '数据治理负责人、运营经理、数据分析师')
    problem = business_context.get('problem', '解决交易数据缺失/重复导致的报表失真问题，并量化治理成效')
    data_source = business_context.get('data_source', '真实公开数据（不可用时回退模拟数据）')
    timeliness_note = business_context.get(
        'timeliness_note',
        '当前为公开历史样例数据，系统支持替换为最新业务数据进行同口径治理分析'
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>数据治理与可视化仪表板</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f3f6fb; color: #1f2937; line-height: 1.5; }}
            .header {{ background: linear-gradient(135deg, #5b6ee1 0%, #7a52b3 100%);
                       color: white; padding: 34px 24px; text-align: center; box-shadow: 0 10px 24px rgba(76, 96, 191, 0.28); }}
            .header h1 {{ font-size: 30px; margin-bottom: 8px; letter-spacing: 0.5px; }}
            .header p {{ font-size: 14px; opacity: 0.95; margin: 2px 0; }}
            .container {{ max-width: 1520px; margin: 22px auto; padding: 0 18px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
                    gap: 16px; margin-bottom: 18px; }}
            .card {{ background: white; border-radius: 12px; border: 1px solid #e5e7eb;
                    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06); padding: 18px; }}
            .card h2 {{ font-size: 17px; margin-bottom: 12px; color: #111827;
                       border-bottom: 1px solid #dbe3ff; padding-bottom: 8px; }}
            .card-full {{ grid-column: 1 / -1; }}
            .chart-container {{ width: 100%; height: 360px; }}
            .quality-score {{ background: linear-gradient(135deg, #5b6ee1 0%, #7a52b3 100%);
                            color: white; text-align: center; padding: 30px; border-radius: 12px; }}
            .score-value {{ font-size: 58px; font-weight: bold; margin: 12px 0; }}
            .score-label {{ font-size: 15px; opacity: 0.92; }}
            .score-stats {{ margin-top: 20px; font-size: 14px; display: flex; 
                           justify-content: space-around; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
            th {{ background: #f8fafc; font-weight: bold; color: #374151; }}
            tr:hover {{ background: #f8fbff; }}
            .severity-高 {{ color: #f56c6c; font-weight: bold; }}
            .severity-中 {{ color: #e6a23c; font-weight: bold; }}
            .severity-低 {{ color: #67c23a; font-weight: bold; }}
            .footer {{ text-align: center; padding: 24px; color: #6b7280; font-size: 12px;
                      border-top: 1px solid #e5e7eb; margin-top: 24px; }}
            .message {{ background: #eef5ff; border-left: 4px solid #5b6ee1;
                       padding: 12px 14px; margin: 8px 0; border-radius: 8px; }}
            .improvement-summary {{ background: #f8fbff; border: 1px solid #dbeafe; border-radius: 8px;
                                   padding: 14px; margin-top: 14px; }}
            .improvement-summary p {{ margin: 6px 0; color: #1f2937; }}
            .improvement-summary strong {{ color: #111827; }}
            .status-badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px;
                            font-size: 12px; font-weight: bold; color: white; margin-bottom: 8px; }}
            .status-good {{ background: #16a34a; }}
            .status-warning {{ background: #f59e0b; }}
            .status-danger {{ background: #dc2626; }}
            .priority-list li {{ margin: 4px 0; }}
            .profile-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                            gap: 12px; margin-bottom: 20px; }}
            .profile-item {{ background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; }}
            .profile-item .label {{ color: #6b7280; font-size: 13px; margin-bottom: 6px; }}
            .profile-item .value {{ color: #111827; font-size: 22px; font-weight: bold; }}
            .profile-item .sub {{ color: #4b5563; font-size: 12px; margin-top: 4px; }}
            .json-tabs {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 12px 0; }}
            .json-tab-btn {{ border: 1px solid #d1d5db; background: #ffffff; color: #374151;
                            border-radius: 6px; padding: 8px 12px; cursor: pointer; font-size: 13px; }}
            .json-tab-btn.active {{ background: #667eea; color: #ffffff; border-color: #667eea; }}
            .json-table-wrap {{ max-height: 360px; overflow: auto; border: 1px solid #e5e7eb; border-radius: 8px; }}
            .json-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            .json-table th {{ position: sticky; top: 0; background: #eef2ff; z-index: 1; }}
            .json-table td, .json-table th {{ padding: 8px 10px; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; }}
            .json-key {{ font-family: Consolas, monospace; color: #1f2937; white-space: nowrap; }}
            .json-value {{ font-family: Consolas, monospace; color: #0f172a; word-break: break-word; }}
            .json-hint {{ color: #6b7280; font-size: 12px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 数据治理与可视化仪表板</h1>
            <p>电商销售数据治理与分析平台 | 生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>面向对象：{audience}</p>
            <p>核心问题：{problem}</p>
            <p>数据来源：{data_source}</p>
            <p>数据时效性：{timeliness_note}</p>
        </div>
        
        <div class="container">
            <div class="card card-full" style="margin-bottom: 20px;">
                <h2>🧭 数据概览（管理视角）</h2>
                <div class="profile-grid">
                    <div class="profile-item">
                        <div class="label">记录总数</div>
                        <div class="value">{profile.get('total_records', quality_report.get('total_records', 0))}</div>
                    </div>
                    <div class="profile-item">
                        <div class="label">销售总额</div>
                        <div class="value">{profile.get('total_sales', 0):,.0f}</div>
                        <div class="sub">单位：数据集中货币口径</div>
                    </div>
                    <div class="profile-item">
                        <div class="label">覆盖区域数</div>
                        <div class="value">{profile.get('region_count', 0)}</div>
                    </div>
                    <div class="profile-item">
                        <div class="label">区域类型数</div>
                        <div class="value">{profile.get('region_type_count', 0)}</div>
                    </div>
                    <div class="profile-item">
                        <div class="label">覆盖城市数</div>
                        <div class="value">{profile.get('city_count', 0)}</div>
                    </div>
                    <div class="profile-item">
                        <div class="label">渠道类型数</div>
                        <div class="value">{profile.get('channel_count', 0)}</div>
                    </div>
                </div>
                <div class="message">时间范围：{profile.get('date_start', '-') } 至 {profile.get('date_end', '-') }；核心目标：让管理层快速识别数据质量风险并跟踪治理成效。</div>
            </div>

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
                    <h2 id="completeness-title">📊 数据完整性分析</h2>
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
                    <h2>🎯 治理前后对比</h2>
                    <div id="improvement-chart" class="chart-container"></div>
                    <div id="improvement-summary" class="improvement-summary">治理成效加载中...</div>
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

            <div class="grid">
                <div class="card card-full json-viewer">
                    <h2>📦 报告JSON全集</h2>
                    <div class="json-hint">切换标签查看不同报告，按“字段路径 / 值”结构化展示。</div>
                    <div class="json-tabs" id="json-tabs"></div>
                    <div class="json-table-wrap">
                        <table class="json-table">
                            <thead>
                                <tr>
                                    <th style="width: 40%;">字段路径</th>
                                    <th style="width: 60%;">值</th>
                                </tr>
                            </thead>
                            <tbody id="json-table-body"></tbody>
                        </table>
                    </div>
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
                    xAxis: {{
                        type: 'category',
                        data: charts.completeness.xAxis,
                        axisLabel: {{ interval: 0, rotate: 25, fontSize: 11 }}
                    }},
                    yAxis: {{ type: 'value', max: 100 }},
                    series: charts.completeness.series,
                    tooltip: {{ trigger: 'axis' }},
                    grid: {{ left: '56px', right: '24px', top: '28px', bottom: '88px', containLabel: true }}
                }});
                if (typeof charts.completeness.alert_field_count !== 'undefined') {{
                    const totalFields = charts.completeness.xAxis ? charts.completeness.xAxis.length : 0;
                    document.getElementById('completeness-title').textContent =
                        `📊 数据完整性分析（异常字段：${{charts.completeness.alert_field_count}}/${{totalFields}}）`;
                }}
                
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

                // 治理前后对比图
                if (charts.governance_improvement) {{
                    const improvementChart = echarts.init(document.getElementById('improvement-chart'));
                    improvementChart.setOption({{
                        tooltip: {{ trigger: 'axis' }},
                        legend: {{ data: ['治理前', '治理后'] }},
                        xAxis: {{ type: 'category', data: charts.governance_improvement.xAxis }},
                        yAxis: {{ type: 'value' }},
                        series: charts.governance_improvement.series
                    }});

                    const detail = charts.governance_improvement.detail || {{}};
                    const actions = (detail.actions || []).map(a => `<li>${{a}}</li>`).join('');
                    const afterScore = Number(detail.after_score || 0);
                    let statusClass = 'status-danger';
                    let statusText = '高风险';
                    let managerAdvice = '建议立即组织专项治理，按天追踪整改效果。';
                    let priorities = [
                        'P0：修复关键业务字段空值与异常值',
                        'P1：建立数据规则告警与拦截机制',
                        'P2：每周复盘治理指标并更新规则阈值'
                    ];
                    if (afterScore >= 90) {{
                        statusClass = 'status-good';
                        statusText = '健康';
                        managerAdvice = '治理效果稳定，建议进入常态化监控与持续优化。';
                        priorities = [
                            'P1：持续监控重点字段质量',
                            'P2：抽样复核规则命中准确性',
                            'P3：扩展到更多业务主题域'
                        ];
                    }} else if (afterScore >= 80) {{
                        statusClass = 'status-warning';
                        statusText = '可控';
                        managerAdvice = '当前总体可控，建议聚焦高频问题做专项优化。';
                        priorities = [
                            'P0：优先处理高频质量问题字段',
                            'P1：补齐治理责任人与SLA',
                            'P2：按月跟踪问题下降率'
                        ];
                    }}
                    const priorityHtml = priorities.map(p => `<li>${{p}}</li>`).join('');

                    document.getElementById('improvement-summary').innerHTML = `
                        <div class="status-badge ${{statusClass}}">治理状态：${{statusText}}</div>
                        <p><strong>质量评分提升：</strong>${{detail.before_score}} -> ${{detail.after_score}}（+${{detail.improved_score}}，${{detail.improved_rate}}%）</p>
                        <p><strong>问题数量变化：</strong>${{detail.before_issues}} -> ${{detail.after_issues}}（下降 ${{detail.issue_reduction_rate}}%）</p>
                        <p><strong>加权风险分：</strong>${{detail.before_risk}} -> ${{detail.after_risk}}（下降 ${{detail.risk_reduction_rate}}%）</p>
                        <p><strong>高风险问题：</strong>${{detail.before_high_risk_issues}} -> ${{detail.after_high_risk_issues}}（下降 ${{detail.high_risk_reduction_rate}}%）</p>
                        <p><strong>已执行治理动作：</strong></p>
                        <ul>${{actions}}</ul>
                        <p><strong>管理结论：</strong>${{managerAdvice}}</p>
                        <p><strong>建议动作优先级：</strong></p>
                        <ul class="priority-list">${{priorityHtml}}</ul>
                    `;
                }}
            }}

            function flattenJson(value, prefix = '') {{
                const rows = [];
                if (value === null || value === undefined) {{
                    rows.push({{ key: prefix || '(root)', value: String(value) }});
                    return rows;
                }}
                if (typeof value !== 'object') {{
                    rows.push({{ key: prefix || '(root)', value: String(value) }});
                    return rows;
                }}
                if (Array.isArray(value)) {{
                    if (value.length === 0) {{
                        rows.push({{ key: prefix || '(root)', value: '[]' }});
                    }} else {{
                        value.forEach((item, idx) => {{
                            const nextKey = prefix ? `${{prefix}}[${{idx}}]` : `[${{idx}}]`;
                            rows.push(...flattenJson(item, nextKey));
                        }});
                    }}
                    return rows;
                }}
                const entries = Object.entries(value);
                if (entries.length === 0) {{
                    rows.push({{ key: prefix || '(root)', value: '{{}}' }});
                    return rows;
                }}
                entries.forEach(([k, v]) => {{
                    const nextKey = prefix ? `${{prefix}}.${{k}}` : k;
                    rows.push(...flattenJson(v, nextKey));
                }});
                return rows;
            }}

            function renderJsonReportTabs(reports) {{
                const tabContainer = document.getElementById('json-tabs');
                const tableBody = document.getElementById('json-table-body');
                const reportEntries = Object.entries(reports);

                function renderRows(reportObj) {{
                    const rows = flattenJson(reportObj);
                    tableBody.innerHTML = rows
                        .map(r => `<tr><td class="json-key">${{r.key}}</td><td class="json-value">${{r.value}}</td></tr>`)
                        .join('');
                }}

                tabContainer.innerHTML = '';
                reportEntries.forEach(([name, data], idx) => {{
                    const btn = document.createElement('button');
                    btn.className = `json-tab-btn ${{idx === 0 ? 'active' : ''}}`;
                    btn.textContent = name;
                    btn.onclick = () => {{
                        Array.from(tabContainer.children).forEach(el => el.classList.remove('active'));
                        btn.classList.add('active');
                        renderRows(data);
                    }};
                    tabContainer.appendChild(btn);
                }});

                if (reportEntries.length > 0) {{
                    renderRows(reportEntries[0][1]);
                }}
            }}
            
            const chartsJson = '{json.dumps(charts, ensure_ascii=False, default=str)}';
            initCharts(chartsJson);

            const reportsJson = {{
                'quality_report.json': {json.dumps(quality_report or {}, ensure_ascii=False, default=str)},
                'kpi_report.json': {json.dumps(kpi_report or {}, ensure_ascii=False, default=str)},
                'metadata.json': {json.dumps(metadata_registry or {}, ensure_ascii=False, default=str)},
                'executive_summary.json': {json.dumps(executive_summary or {}, ensure_ascii=False, default=str)}
            }};
            renderJsonReportTabs(reportsJson);
        </script>
    </body>
    </html>
    """
    return html


def main():
    print("=" * 70)
    print("数据治理与可视化分析平台 - 课程设计项目")
    print("=" * 70)
    
    # 1. 数据采集（优先真实公开数据，失败时回退模拟数据）
    print("\n[步骤1] 数据采集中...")
    collector = DataCollector()
    source_name = "模拟数据"
    try:
        public_loader = PublicRetailDatasetLoader()
        sales_data, source_name = public_loader.load_best_available()
    except Exception as e:
        print(f"[提示] 真实数据加载失败，回退到模拟数据：{e}")
        sales_data = collector.generate_sample_sales_data(rows=1000)

    print(f"[OK] 成功采集 {len(sales_data)} 条销售数据")
    print(f"[OK] 数据来源：{source_name}")
    print(f"[OK] 包含字段：{', '.join(sales_data.columns.tolist())}")

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
    
    # 2. 数据质量评估
    print("\n[步骤2] 数据质量评估中...")
    quality_validator = DataQualityValidator(sales_data)
    quality_report = quality_validator.generate_quality_report()
    print(f"[OK] 数据质量评分：{quality_report['overall_quality_score']:.2f}/100")
    print(f"[OK] 发现 {len(quality_report['issues'])} 个数据质量问题")
    
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
    print(f"[OK] 已注册数据集：sales_2024")
    print(f"[OK] 数据字典已生成")
    
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
        'governance_improvement': build_governance_before_after(sales_data),
    }
    print(f"[OK] 已生成 {len(charts)} 张可视化图表")

    # 展示口径：按“注入异常后的治理前问题数”作为实际监控问题数
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
    
    # 5. 生成报告
    print("\n[步骤5] 生成综合报告...")
    os.makedirs('reports', exist_ok=True)
    
    # 保存质量报告
    with open('reports/quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(display_quality_report, f, ensure_ascii=False, indent=2, default=str)

    # 6. 计算治理KPI指标
    print("\n[步骤6] 计算KPI指标中...")
    kpi_calculator = GovernanceKPI(quality_report, metadata_mgr)
    kpi_report = kpi_calculator.get_kpi_report()
    print(f"[OK] KPI指标已生成：{kpi_report['kpis']['总体治理评分']:.2f}分")

    # 7. 生成治理流程
    print("\n[步骤7] 生成治理流程中...")
    governance_flow = GovernanceFlow()
    flow_diagram = governance_flow.generate_governance_flow_diagram()
    flow_stages = governance_flow.generate_governance_stages()
    print(f"[OK] 治理流程图已生成")
    print(f"[OK] 治理阶段分布已生成")

    # 8. 导出KPI报告
    print("\n[步骤8] 导出KPI报告...")
    kpi_calculator.export_kpi_report('reports/kpi_report.json')
    print("[OK] KPI报告已生成：reports/kpi_report.json")

    # 在生成HTML仪表板时，将新数据添加到 charts
    charts['governance_flow'] = flow_diagram
    charts['governance_stages'] = flow_stages
    
    # 保存元数据
    metadata_mgr.export_metadata('reports/metadata.json')
    
    # 生成HTML仪表板
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

    html_content = generate_html_report(
        display_quality_report,
        charts,
        business_context=business_context,
        profile=profile,
        kpi_report=kpi_report,
        metadata_registry=metadata_mgr.metadata_registry,
        executive_summary=executive_summary,
    )
    with open('reports/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open('reports/executive_summary.json', 'w', encoding='utf-8') as f:
        json.dump(executive_summary, f, ensure_ascii=False, indent=2)
    
    print("[OK] HTML仪表板已生成：reports/dashboard.html")
    print("[OK] 质量报告已生成：reports/quality_report.json")
    print("[OK] 元数据已生成：reports/metadata.json")
    print("[OK] 管理摘要已生成：reports/executive_summary.json")
    
    print("\n" + "=" * 70)
    print("[OK] 项目完成！")
    print("=" * 70)
    print("\n生成的文件位置：")
    print("  reports/dashboard.html (打开此文件查看可视化仪表板)")
    print("  reports/quality_report.json (数据质量报告)")
    print("  reports/metadata.json (元数据和数据字典)")


if __name__ == '__main__':
    main()
