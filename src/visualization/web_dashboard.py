"""
Web仪表板模块
使用Flask创建实时Web仪表板
"""

from flask import Flask, jsonify
import json
import os


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

    def set_data(self, quality_report, kpi_report, charts, governance_flow):
        """设置仪表板数据"""
        self.quality_report = quality_report
        self.kpi_report = kpi_report
        self.charts = charts
        self.governance_flow = governance_flow

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

    def render_dashboard_html(self):
        """生成仪表板HTML"""
        quality_score = self.quality_report.get('overall_quality_score', 0)
        total_records = self.quality_report.get('total_records', 0)
        issues_count = len(self.quality_report.get('issues', []))

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>数据治理Web仪表板</title>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; }}
                body {{ font-family: 'Microsoft YaHei', Arial; background: #f5f5f5; }}
                
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 40px; 
                    text-align: center; 
                }}
                .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
                
                .container {{ 
                    max-width: 1600px; 
                    margin: 20px auto; 
                    padding: 0 20px; 
                }}
                
                .grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 30px; 
                }}
                
                .card {{ 
                    background: white; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                    padding: 20px; 
                }}
                
                .card h2 {{ 
                    font-size: 18px; 
                    margin-bottom: 15px; 
                    color: #333; 
                    border-bottom: 2px solid #667eea; 
                    padding-bottom: 10px; 
                }}
                
                .card-full {{ grid-column: 1 / -1; }}
                .chart-container {{ width: 100%; height: 400px; }}
                
                .quality-score {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    text-align: center; 
                    padding: 40px; 
                    border-radius: 8px; 
                }}
                
                .score-value {{ 
                    font-size: 64px; 
                    font-weight: bold; 
                    margin: 20px 0; 
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
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f5f5f5; font-weight: bold; }}
                
                .footer {{ 
                    text-align: center; 
                    padding: 30px; 
                    color: #999; 
                    font-size: 12px; 
                    margin-top: 40px; 
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 数据治理Web仪表板</h1>
                <p>电商销售数据治理与分析平台</p>
            </div>
            
            <div class="container">
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
                        <div id="issues-table" style="padding: 20px; text-align: center; color: #999;">加载中...</div>
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
                                xAxis: {{ type: 'category', data: d.completeness.xAxis }},
                                yAxis: {{ type: 'value', max: 100 }},
                                series: d.completeness.series,
                                tooltip: {{ trigger: 'axis' }}
                            }});
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
                    }});
                
                // 加载问题清单
                fetch('/api/quality')
                    .then(r => r.json())
                    .then(d => {{
                        const issues = d.issues;
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
            </script>
        </body>
        </html>
        """
        return html

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """运行Web仪表板"""
        self.setup_routes()
        print(f"\n🌐 Web仪表板已启动！")
        print(f"📍 访问地址：http://{host}:{port}")
        print(f"⚠️  按 Ctrl+C 停止服务器")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)