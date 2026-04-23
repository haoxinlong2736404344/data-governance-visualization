"""
Web仪表板模块
使用Flask创建实时Web仪表板
"""

from flask import Flask, jsonify
import json
import os
import re
from datetime import datetime


class WebDashboard:
    """
    Web仪表板生成器
    使用Flask创建交互式Web应用
    """

    def __init__(self, app_name='DataGovernance'):
        """初始化Web仪表板"""
        self.app = Flask(app_name)
        self.quality_report = None
        self.kpi_report = None
        self.charts = None
        self.governance_flow = None
        self.static_reports = {}
        self.business_context = {}
        self.profile = {}

    def set_data(
        self,
        quality_report,
        kpi_report,
        charts,
        governance_flow,
        static_reports=None,
        business_context=None,
        profile=None
    ):
        """设置仪表板数据"""
        self.quality_report = quality_report
        self.kpi_report = kpi_report
        self.charts = charts
        self.governance_flow = governance_flow
        self.static_reports = static_reports or {}
        self.business_context = business_context or {}
        self.profile = profile or {}

    def setup_routes(self):
        """设置Flask路由"""
        app = self.app

        @app.route('/')
        def index():
            return self.render_dashboard_html()

        @app.route('/api/quality')
        def api_quality():
            return jsonify(self.quality_report)

        @app.route('/api/kpi')
        def api_kpi():
            return jsonify(self.kpi_report)

        @app.route('/api/charts')
        def api_charts():
            return jsonify(self.charts)

        @app.route('/api/governance-flow')
        def api_governance_flow():
            return jsonify(self.governance_flow)

        @app.route('/api/monitor-alerts')
        def api_monitor_alerts():
            return jsonify(self.build_monitor_alerts())

        @app.route('/api/static-reports')
        def api_static_reports():
            return jsonify(self.static_reports)

    def build_monitor_alerts(self):
        """构建字段级监控告警数据（用于实时轮询展示）"""
        report = self.quality_report or {}
        total = max(int(report.get('total_records', 0)), 1)
        alerts = []

        # 告警口径统一：按问题清单 issues 逐条生成（与页面问题数保持一致）
        for issue in report.get('issues', []):
            field = issue.get('column', '未知字段')
            issue_type = issue.get('issue_type', '')
            desc = issue.get('description', '')

            percent_match = re.search(r'(\d+(\.\d+)?)%', desc)
            fail_rate = (float(percent_match.group(1)) / 100.0) if percent_match else 0.0
            fail_count = int(round(fail_rate * total)) if fail_rate > 0 else 0
            '''
            if '缺失' in issue_type:
                rule = '缺失率阈值'
                threshold = '<= 2%'
            elif '重复' in issue_type:
                rule = '重复率阈值'
                threshold = '<= 30%'
            else:
                rule = issue_type
                threshold = '失败率 <= 2%'
            '''
            if '缺失' in issue_type:
                rule = '缺失率阈值'
                threshold = '<= 5%'  # 修改点：与后台的 5% 对齐
            elif '重复' in issue_type:
                rule = '重复率阈值'
                threshold = '<= 30%'
            else:
                rule = issue_type
                threshold = '失败率 <= 2%'

            # 保留原始严重程度映射，避免状态和问题清单冲突
            severity = issue.get('severity', '低')
            if severity == '高':
                status = '异常'
                level = '高'
                color = '#dc2626'
            elif severity == '中':
                status = '预警'
                level = '中'
                color = '#f59e0b'
            else:
                status = '关注'
                level = '低'
                color = '#2563eb'

            recent_5m = max(1, int(fail_count * 0.08)) if fail_count > 0 else 0
            recent_1h = max(1, int(fail_count * 0.6)) if fail_count > 0 else 0
            alerts.append({
                'field': field,
                'rule': rule,
                'threshold': threshold,
                'current': f"{fail_rate * 100:.2f}%" if fail_rate else '-',
                'fail_rate': round(fail_rate, 4),
                'fail_count': fail_count,
                'total_records': total,
                'recent_5m': recent_5m,
                'recent_1h': recent_1h,
                'level': level,
                'status': status,
                'color': color
            })

        alerts = sorted(alerts, key=lambda x: x['fail_rate'], reverse=True)
        return {
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_alerts': len(report.get('issues', [])),
            'threshold_basis': '阈值依据：参考常见数据质量治理实践，缺失/规则失败率 >2% 进入预警，>10% 判定异常；唯一性重复率 >30% 触发重点告警。',
            'window_note': '监控口径说明：页面每5秒轮询刷新；“近5分钟/近1小时”用于模拟实时监控窗口，便于展示告警趋势与处理优先级。',
            'alerts': alerts
        }

    def _make_alert(self, field, rule, threshold, current, fail_rate, fail_count, total_records):
        if fail_rate > 0.1:
            level = '高'
            status = '异常'
            color = '#dc2626'
        elif fail_rate > 0.02:
            level = '中'
            status = '预警'
            color = '#f59e0b'
        else:
            level = '低'
            status = '关注'
            color = '#2563eb'

        # 用当前失败率估算近时段异常量，强调“监控”语义
        recent_5m = max(1, int(fail_count * 0.08)) if fail_count > 0 else 0
        recent_1h = max(1, int(fail_count * 0.6)) if fail_count > 0 else 0
        return {
            'field': field,
            'rule': rule,
            'threshold': threshold,
            'current': current,
            'fail_rate': round(fail_rate, 4),
            'fail_count': fail_count,
            'total_records': total_records,
            'recent_5m': recent_5m,
            'recent_1h': recent_1h,
            'level': level,
            'status': status,
            'color': color
        }

    def render_dashboard_html(self):
        """生成仪表板HTML"""
        quality_score = self.quality_report.get('overall_quality_score', 0)
        total_records = self.quality_report.get('total_records', 0)
        issues_count = len(self.quality_report.get('issues', []))
        audience = self.business_context.get('audience', '数据治理负责人、运营经理、数据分析师')
        problem = self.business_context.get('problem', '解决交易数据缺失/重复导致的报表不可信问题，并量化治理成效')
        data_source = self.business_context.get('data_source', '公开数据集')
        timeliness_note = self.business_context.get('timeliness_note', '当前为公开历史样例数据，系统支持替换为最新业务数据')

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>数据治理Web仪表板</title>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Microsoft YaHei', Arial; background: #f3f6fb; color: #1f2937; line-height: 1.5; }}
                
                .header {{ 
                    background: linear-gradient(135deg, #5b6ee1 0%, #7a52b3 100%);
                    color: white; 
                    padding: 34px 24px;
                    text-align: center; 
                    box-shadow: 0 10px 24px rgba(76, 96, 191, 0.28);
                }}
                .header h1 {{ font-size: 30px; margin-bottom: 8px; letter-spacing: 0.5px; }}
                
                .container {{ 
                    max-width: 1600px; 
                    margin: 22px auto;
                    padding: 0 18px;
                }}
                
                .grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
                    gap: 16px;
                    margin-bottom: 18px;
                }}
                
                .card {{ 
                    background: white; 
                    border-radius: 12px;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
                    padding: 18px;
                }}
                
                .card h2 {{ 
                    font-size: 17px;
                    margin-bottom: 12px;
                    color: #111827;
                    border-bottom: 1px solid #dbe3ff;
                    padding-bottom: 8px;
                }}
                
                .card-full {{ grid-column: 1 / -1; }}
                .chart-container {{ width: 100%; height: 360px; }}
                
                .quality-score {{ 
                    background: linear-gradient(135deg, #5b6ee1 0%, #7a52b3 100%);
                    color: white; 
                    text-align: center; 
                    padding: 30px;
                    border-radius: 12px;
                }}
                
                .score-value {{ 
                    font-size: 58px;
                    font-weight: bold; 
                    margin: 12px 0;
                }}
                
                .score-stats {{ 
                    margin-top: 20px; 
                    font-size: 14px; 
                    display: flex; 
                    justify-content: space-around; 
                }}
                
                .kpi-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                    gap: 15px; 
                }}
                
                .kpi-item {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    text-align: center; 
                }}
                
                .kpi-value {{ 
                    font-size: 28px; 
                    font-weight: bold; 
                    margin: 10px 0; 
                }}
                
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                th {{ background: #f8fafc; font-weight: bold; color: #374151; }}
                .monitor-meta {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: #f8fafc;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 12px 14px;
                    margin-bottom: 10px;
                    font-size: 13px;
                    color: #374151;
                }}
                .monitor-note {{
                    background: #eff6ff;
                    border: 1px solid #bfdbfe;
                    border-radius: 8px;
                    color: #1e3a8a;
                    padding: 10px 12px;
                    margin-bottom: 10px;
                    font-size: 13px;
                    line-height: 1.5;
                }}
                .status-pill {{
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 999px;
                    color: #fff;
                    font-size: 12px;
                }}
                .json-tabs {{
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    margin: 8px 0 12px 0;
                }}
                .json-tab-btn {{
                    border: 1px solid #d1d5db;
                    background: #ffffff;
                    color: #374151;
                    border-radius: 6px;
                    padding: 8px 12px;
                    cursor: pointer;
                    font-size: 13px;
                }}
                .json-tab-btn.active {{
                    background: #667eea;
                    color: #ffffff;
                    border-color: #667eea;
                }}
                .json-table-wrap {{
                    max-height: 320px;
                    overflow: auto;
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                }}
                .json-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                }}
                .json-table th {{
                    position: sticky;
                    top: 0;
                    background: #eef2ff;
                    z-index: 1;
                }}
                .json-table td, .json-table th {{
                    padding: 8px 10px;
                    border-bottom: 1px solid #e5e7eb;
                    text-align: left;
                    vertical-align: top;
                }}
                .json-key {{
                    font-family: Consolas, monospace;
                    color: #1f2937;
                    white-space: nowrap;
                }}
                .json-value {{
                    font-family: Consolas, monospace;
                    color: #0f172a;
                    word-break: break-word;
                }}
                .footer {{ 
                    text-align: center; 
                    padding: 24px;
                    color: #6b7280;
                    font-size: 12px; 
                    margin-top: 24px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 数据治理Web仪表板</h1>
                <p>电商销售数据治理与分析平台</p>
                <p>面向对象：{audience}</p>
                <p>核心问题：{problem}</p>
                <p>数据来源：{data_source}</p>
                <p>数据时效性：{timeliness_note}</p>
            </div>
            
            <div class="container">
                <div class="card card-full" style="margin-bottom: 16px;">
                    <h2>🧭 数据概览（管理视角）</h2>
                    <div class="kpi-grid">
                        <div class="kpi-item"><div>记录总数</div><div class="kpi-value">{self.profile.get('total_records', total_records)}</div></div>
                        <div class="kpi-item"><div>销售总额</div><div class="kpi-value">{self.profile.get('total_sales', 0):,.0f}</div></div>
                        <div class="kpi-item"><div>覆盖区域数</div><div class="kpi-value">{self.profile.get('region_count', 0)}</div></div>
                        <div class="kpi-item"><div>区域类型数</div><div class="kpi-value">{self.profile.get('region_type_count', 0)}</div></div>
                        <div class="kpi-item"><div>覆盖城市数</div><div class="kpi-value">{self.profile.get('city_count', 0)}</div></div>
                        <div class="kpi-item"><div>渠道类型数</div><div class="kpi-value">{self.profile.get('channel_count', 0)}</div></div>
                    </div>
                </div>

                <!-- 数据质量评分 -->
                <div class="grid">
                    <div class="card card-full">
                        <h2>📈 数据质量评分</h2>
                        <div class="quality-score">
                            <div class="score-value">{quality_score:.1f}</div>
                            <div>总体质量评分</div>
                            <div class="score-stats">
                                <div>总记录数: {total_records}</div>
                                <div>发现问题: {issues_count}</div>
                                <div>质量等级: 优秀</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- KPI指标 -->
                <div class="grid">
                    <div class="card card-full">
                        <h2>📊 关键性能指标 (KPI)</h2>
                        <div class="kpi-grid" id="kpi-grid">
                            <div style="grid-column: 1 / -1; text-align: center; color: #999;">加载中...</div>
                        </div>
                    </div>
                </div>
                
                <!-- 图表 -->
                <div class="grid">
                    <div class="card card-full">
                        <h2>🚨 字段级质量告警监控（每5秒自动刷新）</h2>
                        <div class="monitor-meta">
                            <div id="monitor-time">检查时间：加载中...</div>
                            <div id="monitor-count">告警条数：加载中...</div>
                        </div>
                        <div id="monitor-threshold-basis" class="monitor-note">阈值依据：加载中...</div>
                        <div id="monitor-window-note" class="monitor-note">监控口径说明：加载中...</div>
                        <div id="monitor-table" style="padding: 8px 0; color: #999;">加载中...</div>
                    </div>

                    <div class="card card-full">
                        <h2 id="completeness-title">📊 数据完整性分析</h2>
                        <div id="completeness-chart" class="chart-container"></div>
                        <div id="completeness-summary" class="monitor-note" style="margin-top: 10px;">
                            完整性阈值与异常字段摘要加载中...
                        </div>
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
                        <h2 id="improvement-title">🎯 治理前后对比</h2>
                        <div id="improvement-chart" class="chart-container"></div>
                        <div id="improvement-summary" class="monitor-note" style="margin-top: 10px;">治理成效摘要加载中...</div>
                    </div>
                    
                    <div class="card card-full">
                        <h2>⚠️ 数据质量问题清单</h2>
                        <div id="issues-table" style="padding: 20px; text-align: center; color: #999;">加载中...</div>
                    </div>

                    <div class="card card-full">
                        <h2>📦 静态报告结果（与实时监控整合）</h2>
                        <div class="json-tabs" id="static-json-tabs"></div>
                        <div class="json-table-wrap">
                            <table class="json-table">
                                <thead>
                                    <tr>
                                        <th style="width: 40%;">字段路径</th>
                                        <th style="width: 60%;">值</th>
                                    </tr>
                                </thead>
                                <tbody id="static-json-body"></tbody>
                            </table>
                        </div>
                    </div>

                </div>
            </div>
            
            <div class="footer">
                <p>© 2026 大数据23-1 第一组 数据治理与可视化课程设计项目</p>
            </div>
            
            <script>
                // 加载KPI
                fetch('/api/kpi')
                    .then(r => r.json())
                    .then(d => {{
                        const k = d.kpis;
                        document.getElementById('kpi-grid').innerHTML = `
                            <div class="kpi-item"><div>数据质量评分</div><div class="kpi-value">${{k['数据质量评分']}}</div></div>
                            <div class="kpi-item"><div>数据完整率</div><div class="kpi-value">${{k['数据完整率']}}</div></div>
                            <div class="kpi-item"><div>数据唯一性</div><div class="kpi-value">${{k['数据唯一性']}}</div></div>
                            <div class="kpi-item"><div>治理覆盖率</div><div class="kpi-value">${{k['治理覆盖率']}}</div></div>
                            <div class="kpi-item"><div>总体治理评分</div><div class="kpi-value">${{k['总体治理评分']}}</div></div>
                        `;
                    }});
                
                // 加载图表
                fetch('/api/charts')
                    .then(r => r.json())
                    .then(d => {{
                        if (d.completeness) {{
                            const c = echarts.init(document.getElementById('completeness-chart'));
                            c.setOption({{
                                xAxis: {{
                                    type: 'category',
                                    data: d.completeness.xAxis,
                                    axisLabel: {{ interval: 0, rotate: 25, fontSize: 11 }}
                                }},
                                yAxis: {{ type: 'value', max: 100 }},
                                series: d.completeness.series,
                                tooltip: {{ trigger: 'axis' }},
                                grid: {{ left: '56px', right: '24px', top: '28px', bottom: '88px', containLabel: true }}
                            }});
                            const totalFields = d.completeness.xAxis ? d.completeness.xAxis.length : 0;
                            const alertCount = d.completeness.alert_field_count || 0;
                            document.getElementById('completeness-title').textContent =
                                `📊 数据完整性分析（异常字段：${{alertCount}}/${{totalFields}}）`;
                            const threshold = d.completeness.threshold || 98;
                            const values = (d.completeness.yAxis || []).map(v => Number(v));
                            const fields = d.completeness.xAxis || [];
                            const badFields = fields.filter((_, idx) => values[idx] < threshold);
                            const badText = badFields.length ? badFields.join('、') : '无';
                            document.getElementById('completeness-summary').textContent =
                                `阈值线：${{threshold}}%；低于阈值字段：${{badFields.length}} 个（${{badText}}）。`;
                        }}
                        if (d.region_sales) {{
                            const c = echarts.init(document.getElementById('region-chart'));
                            c.setOption({{
                                tooltip: {{ trigger: 'item' }},
                                series: [{{ type: 'pie', data: d.region_sales.data, radius: ['40%', '70%'] }}]
                            }});
                        }}
                        if (d.channel_analysis) {{
                            const c = echarts.init(document.getElementById('channel-chart'));
                            c.setOption({{
                                xAxis: {{ type: 'category', data: d.channel_analysis.xAxis }},
                                yAxis: [{{ type: 'value' }}, {{ type: 'value' }}],
                                series: d.channel_analysis.series,
                                tooltip: {{ trigger: 'axis' }},
                                grid: {{ left: '60px', right: '80px', top: '20px', bottom: '60px' }}
                            }});
                        }}
                        if (d.sales_trend) {{
                            const c = echarts.init(document.getElementById('trend-chart'));
                            c.setOption({{
                                xAxis: {{ type: 'category', data: d.sales_trend.xAxis }},
                                yAxis: {{ type: 'value' }},
                                series: d.sales_trend.series,
                                tooltip: {{ trigger: 'axis' }},
                                grid: {{ left: '60px', right: '40px', top: '20px', bottom: '80px' }}
                            }});
                        }}
                        if (d.governance_improvement) {{
                            const c = echarts.init(document.getElementById('improvement-chart'));
                            c.setOption({{
                                tooltip: {{ trigger: 'axis' }},
                                legend: {{ data: ['治理前', '治理后'] }},
                                xAxis: {{ type: 'category', data: d.governance_improvement.xAxis }},
                                yAxis: {{ type: 'value' }},
                                series: d.governance_improvement.series,
                                grid: {{ left: '56px', right: '24px', top: '36px', bottom: '52px', containLabel: true }}
                            }});
                            const detail = d.governance_improvement.detail || {{}};
                            document.getElementById('improvement-summary').textContent =
                                `质量评分：${{detail.before_score}} -> ${{detail.after_score}}（+${{detail.improved_score}}，${{detail.improved_rate}}%）；问题数量：${{detail.before_issues}} -> ${{detail.after_issues}}（下降${{detail.issue_reduction_rate}}%）；加权风险分：${{detail.before_risk}} -> ${{detail.after_risk}}（下降${{detail.risk_reduction_rate}}%）；高风险问题：${{detail.before_high_risk_issues}} -> ${{detail.after_high_risk_issues}}（下降${{detail.high_risk_reduction_rate}}%）。`;
                        }}
                    }});
                
                // 加载问题清单
                function loadQualityIssues() {{
                    fetch('/api/quality')
                        .then(r => r.json())
                        .then(d => {{
                            const issues = d.issues || [];
                            if (issues.length === 0) {{
                                document.getElementById('issues-table').innerHTML = '<div style="padding: 20px; color: #67c23a;">✓ 恭喜！数据质量优秀，暂无严重问题</div>';
                            }} else {{
                                let html = '<table><tr><th>列名</th><th>问题类型</th><th>严重程度</th><th>描述</th></tr>';
                                issues.forEach(i => {{
                                    html += `<tr><td><strong>${{i.column}}</strong></td><td>${{i.issue_type}}</td><td>${{i.severity}}</td><td>${{i.description}}</td></tr>`;
                                }});
                                html += '</table>';
                                document.getElementById('issues-table').innerHTML = html;
                            }}
                        }});
                }}

                function loadMonitorAlerts() {{
                    fetch('/api/monitor-alerts')
                        .then(r => r.json())
                        .then(d => {{
                            document.getElementById('monitor-time').textContent = `检查时间：${{d.checked_at}}`;
                            document.getElementById('monitor-count').textContent = `告警条数：${{d.total_alerts}}`;
                            document.getElementById('monitor-threshold-basis').textContent = d.threshold_basis || '阈值依据：暂无';
                            document.getElementById('monitor-window-note').textContent = d.window_note || '监控口径说明：暂无';
                            const alerts = d.alerts || [];
                            if (alerts.length === 0) {{
                                document.getElementById('monitor-table').innerHTML = '<div style="padding: 20px; color: #67c23a;">✓ 当前无字段级告警</div>';
                                return;
                            }}
                            let html = '<table><tr><th>字段</th><th>规则</th><th>当前值</th><th>阈值</th><th>状态</th><th>近5分钟</th><th>近1小时</th></tr>';
                            alerts.forEach(a => {{
                                html += `<tr>
                                    <td><strong>${{a.field}}</strong></td>
                                    <td>${{a.rule}}</td>
                                    <td>${{a.current}}</td>
                                    <td>${{a.threshold}}</td>
                                    <td><span class="status-pill" style="background:${{a.color}}">${{a.status}}/${{a.level}}</span></td>
                                    <td>${{a.recent_5m}}</td>
                                    <td>${{a.recent_1h}}</td>
                                </tr>`;
                            }});
                            html += '</table>';
                            document.getElementById('monitor-table').innerHTML = html;
                        }});
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

                function renderStaticReportsTabs(reports) {{
                    const tabContainer = document.getElementById('static-json-tabs');
                    const tableBody = document.getElementById('static-json-body');
                    const reportEntries = Object.entries(reports || {{}});
                    if (reportEntries.length === 0) {{
                        tableBody.innerHTML = '<tr><td colspan="2">未检测到静态报告文件</td></tr>';
                        return;
                    }}

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
                    renderRows(reportEntries[0][1]);
                }}

                function loadStaticReports() {{
                    fetch('/api/static-reports')
                        .then(r => r.json())
                        .then(d => renderStaticReportsTabs(d))
                        .catch(() => renderStaticReportsTabs({{}}));
                }}

                loadQualityIssues();
                loadMonitorAlerts();
                loadStaticReports();
                setInterval(loadQualityIssues, 5000);
                setInterval(loadMonitorAlerts, 5000);
            </script>
        </body>
        </html>
        """
        return html

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """运行Web仪表板"""
        self.setup_routes()
        print(f"\nWeb仪表板已启动")
        print(f"访问地址：http://{host}:{port}")
        print(f"按 Ctrl+C 停止服务器")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)